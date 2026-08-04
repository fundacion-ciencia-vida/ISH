from __future__ import annotations

import copy
import mimetypes
import secrets
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Header, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from scripts.content_store import ContentValidationError, normalize_content_bundle, sanitize_rich_html, validate_content_bundle

from .auth import (
    AUTH_COOKIE,
    SESSION_TTL_SECONDS,
    LocalAuthError,
    LocalCredentialStore,
    LocalLoginLimiter,
    LocalSessionStore,
)
from .config import (
    PUBLISH_BRANCH,
    REPOSITORY_URL,
    configured_workspace,
    editor_edition,
    editor_edition_catalog,
)
from .credentials import CredentialStore
from .workspace import EditorError, Workspace, clone_workspace


SECTION_CATALOG: list[dict[str, Any]] = [
    {"type": "rich_text", "label": "Texto enriquecido", "description": "Contenido con formato basico y avanzado.", "data": {"eyebrow": "Section", "heading": "Section heading", "body_html": "<p>Write the section content here.</p>", "actions": []}},
    {"type": "split_text", "label": "Texto en columnas", "description": "Titulo a la izquierda y contenido a la derecha.", "variant": "intro", "data": {"eyebrow": "Section", "heading": "Section heading", "paragraphs": ["Write the section content here."], "actions": []}},
    {"type": "heading_text", "label": "Encabezado y texto", "description": "Bloque centrado para una introduccion breve.", "variant": "data", "data": {"eyebrow": "Section", "heading": "Section heading", "paragraphs": ["Write the section content here."]}},
    {"type": "media_split", "label": "Texto e imagen", "description": "Contenido junto a una imagen o plataforma externa.", "variant": "intro", "data": {"eyebrow": "Section", "heading": "Section heading", "paragraphs": ["Write the section content here."], "image": "ui/social-preview.jpg", "image_alt": "", "caption": "", "actions": []}},
    {"type": "single_image", "label": "Imagen destacada", "description": "Una imagen amplia con pie de foto.", "variant": "intro", "data": {"image": "ui/social-preview.jpg", "alt": "", "caption": "Image caption"}},
    {"type": "gallery", "label": "Galeria", "description": "Cuadricula de imagenes con pies de foto.", "variant": "intro", "data": {"eyebrow": "Gallery", "heading": "Image gallery", "items": []}},
    {"type": "feature_grid", "label": "Lista destacada", "description": "Elementos numerados con titulo, texto y enlace.", "variant": "data", "data": {"eyebrow": "Highlights", "heading": "Section heading", "items": []}},
    {"type": "fee_table", "label": "Tabla de valores", "description": "Tabla responsive para tarifas u otros valores.", "variant": "data", "data": {"eyebrow": "Fees", "heading": "Section heading", "paragraphs": [], "caption": "Fees", "columns": [{"label": "Category"}, {"label": "Value"}], "rows": []}},
    {"type": "cta", "label": "Llamado a la accion", "description": "Titulo y botones para una accion principal.", "data": {"eyebrow": "Next step", "heading": "Section heading", "actions": []}},
]

PAGE_CATALOG: list[dict[str, Any]] = [
    {
        "id": "content",
        "label": "Pagina de contenido",
        "description": "Portada y un bloque principal de texto enriquecido.",
        "sections": [
            {
                "type": "rich_text",
                "data": {
                    "eyebrow": "Section",
                    "heading": "Section heading",
                    "body_html": "<p>Write the page content here.</p>",
                    "actions": [],
                },
            }
        ],
    },
    {
        "id": "information",
        "label": "Pagina informativa",
        "description": "Portada, introduccion en columnas y lista de contenidos destacados.",
        "sections": [
            {
                "type": "split_text",
                "variant": "intro",
                "data": {
                    "eyebrow": "Overview",
                    "heading": "Section heading",
                    "paragraphs": ["Write the section content here."],
                    "actions": [],
                },
            },
            {
                "type": "feature_grid",
                "variant": "data",
                "data": {
                    "eyebrow": "Highlights",
                    "heading": "Key information",
                    "items": [
                        {
                            "number": "01",
                            "title": "First item",
                            "description": "Add a concise description.",
                            "link_label": "Learn more",
                            "url": "#",
                        }
                    ],
                },
            },
        ],
    },
    {
        "id": "gallery",
        "label": "Pagina con galeria",
        "description": "Portada, introduccion breve y una galeria editable.",
        "sections": [
            {
                "type": "heading_text",
                "variant": "data",
                "data": {
                    "eyebrow": "Introduction",
                    "heading": "Section heading",
                    "paragraphs": ["Introduce the gallery here."],
                },
            },
            {
                "type": "gallery",
                "variant": "intro",
                "data": {"eyebrow": "Gallery", "heading": "Image gallery", "items": []},
            },
        ],
    },
]


class BundleRequest(BaseModel):
    bundle: dict[str, Any]
    snapshot: bool = False


class PublishRequest(BaseModel):
    bundle: dict[str, Any]
    message: str = Field(default="Update site content", max_length=160)


class TokenRequest(BaseModel):
    token: str = Field(min_length=8, max_length=512)


class LocalSetupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=10, max_length=256)


class LocalLoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=256)


class LocalPasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=256)
    new_password: str = Field(min_length=10, max_length=256)


class CloneRequest(BaseModel):
    destination: str = Field(min_length=1, max_length=1000)


class RestoreRequest(BaseModel):
    identifier: str


def _sanitize_bundle(payload: dict[str, Any]) -> dict[str, Any]:
    clean = copy.deepcopy(payload)

    def visit(value: Any, key: str = "") -> Any:
        if isinstance(value, dict):
            return {item_key: visit(item_value, item_key) for item_key, item_value in value.items()}
        if isinstance(value, list):
            return [visit(item, key) for item in value]
        if isinstance(value, str) and key.endswith("_html"):
            return sanitize_rich_html(value)
        return value

    clean = visit(clean)
    normalize_content_bundle(clean)
    validate_content_bundle(clean)
    return clean


class EditorState:
    def __init__(self, workspace_path: Path | None, setup_token: str, auth_path: Path | None) -> None:
        self.setup_token = setup_token
        self.local_auth = LocalCredentialStore(auth_path)
        self.local_sessions = LocalSessionStore()
        self.local_login_limiter = LocalLoginLimiter()
        self.credentials = CredentialStore()
        self.workspace = Workspace(workspace_path) if workspace_path else None

    def require_workspace(self) -> Workspace:
        if self.workspace is None:
            raise EditorError("Primero debes clonar el repositorio del sitio.")
        self.workspace.assert_valid()
        return self.workspace


def create_app(
    *,
    workspace_path: Path | None = None,
    session_token: str | None = None,
    auth_path: Path | None = None,
    ui_root: Path | None = None,
) -> FastAPI:
    token = session_token or secrets.token_urlsafe(32)
    state = EditorState(workspace_path or configured_workspace(), token, auth_path)
    app = FastAPI(title="ISH Editor", version="0.1.0", docs_url=None, redoc_url=None)
    app.state.editor = state
    app.state.session_token = token
    static_root = ui_root or Path(__file__).resolve().parent / "ui" / "dist"

    def set_local_session(response: Response) -> None:
        response.set_cookie(
            AUTH_COOKIE,
            state.local_sessions.create(),
            max_age=SESSION_TTL_SECONDS,
            httponly=True,
            samesite="strict",
            secure=False,
            path="/",
        )

    @app.middleware("http")
    async def protect_local_api(request: Request, call_next):
        public_api = {"/api/health", "/api/auth/status", "/api/auth/setup", "/api/auth/login", "/api/auth/logout"}
        protected = (request.url.path.startswith("/api/") and request.url.path not in public_api) or request.url.path.startswith("/preview")
        if protected and not state.local_sessions.valid(request.cookies.get(AUTH_COOKIE, "")):
            return JSONResponse(status_code=401, content={"detail": "Inicia sesion para usar el editor local."})
        return await call_next(request)

    @app.exception_handler(EditorError)
    async def editor_error_handler(_: Request, exc: EditorError):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(ContentValidationError)
    async def content_error_handler(_: Request, exc: ContentValidationError):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(LocalAuthError)
    async def local_auth_error_handler(_: Request, exc: LocalAuthError):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        return {"ok": True, "workspace": str(state.workspace.root) if state.workspace else None}

    @app.get("/api/auth/status")
    def local_auth_status(request: Request) -> dict[str, bool]:
        supplied = request.headers.get("x-ish-setup", "")
        can_setup = not state.local_auth.configured and bool(supplied) and secrets.compare_digest(supplied, state.setup_token)
        return {
            "configured": state.local_auth.configured,
            "authenticated": state.local_sessions.valid(request.cookies.get(AUTH_COOKIE, "")),
            "can_setup": can_setup,
        }

    @app.post("/api/auth/setup")
    def local_auth_setup(request: LocalSetupRequest, response: Response, x_ish_setup: str = Header(default="")) -> dict[str, bool]:
        if state.local_auth.configured:
            raise EditorError("Las credenciales locales ya fueron configuradas.")
        if not x_ish_setup or not secrets.compare_digest(x_ish_setup, state.setup_token):
            raise HTTPException(status_code=403, detail="Enlace de configuracion local invalido.")
        state.local_auth.setup(request.username, request.password)
        set_local_session(response)
        return {"authenticated": True}

    @app.post("/api/auth/login")
    def local_auth_login(credentials: LocalLoginRequest, request: Request, response: Response) -> dict[str, bool]:
        client_key = request.client.host if request.client else "local"
        retry_after = state.local_login_limiter.retry_after(client_key)
        if retry_after:
            raise HTTPException(
                status_code=429,
                detail=f"Demasiados intentos. Espera {retry_after} segundos.",
                headers={"Retry-After": str(retry_after)},
            )
        if not state.local_auth.verify(credentials.username, credentials.password):
            retry_after = state.local_login_limiter.failed(client_key)
            if retry_after:
                raise HTTPException(
                    status_code=429,
                    detail=f"Demasiados intentos. Espera {retry_after} segundos.",
                    headers={"Retry-After": str(retry_after)},
                )
            raise HTTPException(status_code=401, detail="Usuario o contrasena incorrectos.")
        state.local_login_limiter.clear(client_key)
        set_local_session(response)
        return {"authenticated": True}

    @app.post("/api/auth/password")
    def local_auth_password(request: LocalPasswordChangeRequest, response: Response) -> dict[str, bool]:
        state.local_auth.change_password(request.current_password, request.new_password)
        state.local_sessions.revoke_all()
        set_local_session(response)
        return {"authenticated": True}

    @app.post("/api/auth/logout")
    def local_auth_logout(request: Request, response: Response) -> dict[str, bool]:
        state.local_sessions.revoke(request.cookies.get(AUTH_COOKIE, ""))
        response.delete_cookie(AUTH_COOKIE, path="/")
        return {"authenticated": False}

    @app.get("/api/bootstrap")
    def bootstrap() -> dict[str, Any]:
        try:
            workspace_status = state.workspace.status() if state.workspace else None
        except EditorError:
            state.workspace = None
            workspace_status = None
        credential_status = state.credentials.status()
        ssh_ready = bool(state.workspace and state.workspace.publish_remote())
        edition = editor_edition()
        custom_site = bool(edition["advanced_features"])
        return {
            "repository": REPOSITORY_URL,
            "branch": PUBLISH_BRANCH,
            "suggested_workspace": str(Path.home() / "Documents" / "ISH-Website"),
            "workspace": workspace_status,
            "credentials": {
                "configured": credential_status.configured or ssh_ready,
                "persistent": credential_status.persistent or ssh_ready,
                "method": "token" if credential_status.configured else "ssh" if ssh_ready else "none",
            },
            "edition": edition,
            "edition_catalog": editor_edition_catalog(),
            "features": {"custom_site": custom_site},
            "section_catalog": SECTION_CATALOG if custom_site else [],
            "page_catalog": PAGE_CATALOG if custom_site else [],
        }

    @app.post("/api/token")
    def save_token(request: TokenRequest) -> dict[str, Any]:
        status = state.credentials.set(request.token)
        return {"configured": status.configured, "persistent": status.persistent}

    @app.delete("/api/token")
    def delete_token() -> dict[str, bool]:
        state.credentials.delete()
        return {"configured": False}

    @app.post("/api/clone")
    def clone(request: CloneRequest) -> dict[str, Any]:
        github_token = state.credentials.get()
        if not github_token:
            raise EditorError("Configura el token de GitHub antes de clonar.")
        state.workspace = clone_workspace(Path(request.destination), github_token)
        return state.workspace.status()

    @app.get("/api/content")
    def content() -> dict[str, Any]:
        workspace = state.require_workspace()
        record = workspace.load_draft_record()
        return {"bundle": record["bundle"], "saved_at": record["saved_at"], "base_commit": record["base_commit"], "workspace": workspace.status()}

    @app.put("/api/draft")
    def save_draft(request: BundleRequest) -> dict[str, Any]:
        workspace = state.require_workspace()
        clean = _sanitize_bundle(request.bundle)
        return workspace.save_draft(clean, snapshot=request.snapshot)

    @app.post("/api/preview")
    def preview(request: BundleRequest) -> dict[str, Any]:
        workspace = state.require_workspace()
        clean = _sanitize_bundle(request.bundle)
        return workspace.build_preview(clean)

    @app.get("/api/drafts/history")
    def draft_history() -> list[dict[str, str]]:
        return state.require_workspace().draft_history()

    @app.post("/api/drafts/restore")
    def restore_draft(request: RestoreRequest) -> dict[str, Any]:
        return {"bundle": state.require_workspace().restore_draft_snapshot(request.identifier)}

    @app.get("/api/history")
    def published_history() -> list[dict[str, str]]:
        return state.require_workspace().list_published_history()

    @app.post("/api/history/restore")
    def restore_published(request: RestoreRequest) -> dict[str, Any]:
        return {"bundle": state.require_workspace().restore_published(request.identifier)}

    @app.get("/api/git/status")
    def git_status() -> dict[str, Any]:
        return state.require_workspace().status()

    @app.post("/api/git/sync")
    def git_sync() -> dict[str, Any]:
        github_token = state.credentials.get()
        return state.require_workspace().sync(github_token)

    @app.post("/api/publish")
    def publish(request: PublishRequest) -> dict[str, Any]:
        workspace = state.require_workspace()
        clean = _sanitize_bundle(request.bundle)
        workspace.save_draft(clean, snapshot=True)
        return workspace.publish(clean, state.credentials.get(), request.message)

    @app.get("/api/media")
    def media() -> list[dict[str, Any]]:
        return state.require_workspace().media_items()

    @app.post("/api/media")
    async def upload_media(kind: str, file: UploadFile = File(...)) -> dict[str, Any]:
        limit = 25 * 1024 * 1024 if kind == "image" else 50 * 1024 * 1024
        payload = await file.read(limit + 1)
        if len(payload) > limit:
            raise EditorError("El archivo supera el tamano maximo permitido.")
        return state.require_workspace().add_pending_upload(file.filename or "file", payload, kind)

    @app.delete("/api/media/{relative_path:path}")
    def delete_media(relative_path: str) -> dict[str, bool]:
        workspace = state.require_workspace()
        bundle = workspace.load_draft_record()["bundle"]
        workspace.remove_media(relative_path, bundle)
        return {"deleted": True}

    @app.post("/api/media/restore")
    def restore_media(request: RestoreRequest) -> dict[str, bool]:
        state.require_workspace().restore_media(request.identifier)
        return {"restored": True}

    @app.get("/preview/{preview_path:path}")
    def preview_file(preview_path: str):
        workspace = state.require_workspace()
        relative = Path(preview_path or "index.html")
        if preview_path.endswith("/") or not relative.suffix:
            relative = relative / "index.html"
        candidates = [workspace.preview_root / relative, workspace.pending_root / relative, workspace.root / relative]
        for candidate in candidates:
            resolved = candidate.resolve()
            allowed_roots = [workspace.preview_root.resolve(), workspace.pending_root.resolve(), workspace.root.resolve()]
            if not any(resolved == root or root in resolved.parents for root in allowed_roots):
                continue
            if resolved.exists() and resolved.is_file():
                media_type = mimetypes.guess_type(resolved.name)[0]
                return FileResponse(resolved, media_type=media_type)
        raise HTTPException(status_code=404, detail="Preview file not found")

    @app.get("/", response_class=HTMLResponse)
    def editor_index():
        index = static_root / "index.html"
        if index.exists():
            return FileResponse(index)
        return HTMLResponse(
            "<main style='font-family:system-ui;max-width:720px;margin:10vh auto'>"
            "<h1>ISH Editor</h1><p>La interfaz aun no esta compilada. Ejecuta <code>npm run build</code> dentro de <code>editor/ui</code>.</p></main>",
            status_code=503,
        )

    @app.get("/{asset_path:path}")
    def editor_asset(asset_path: str):
        candidate = (static_root / asset_path).resolve()
        if static_root.resolve() not in candidate.parents or not candidate.exists() or not candidate.is_file():
            candidate = static_root / "index.html"
        if candidate.exists():
            return FileResponse(candidate)
        raise HTTPException(status_code=404)

    return app
