from __future__ import annotations

import argparse
import os
import socket
import threading
import webbrowser
from pathlib import Path

import uvicorn

from .app import create_app
from .auth import LocalCredentialStore
from .config import set_editor_edition


def available_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def generate_site(source: Path, output: Path, bundle: Path) -> None:
    os.environ["ISH_SOURCE_ROOT"] = str(source.resolve())
    os.environ["ISH_OUTPUT_ROOT"] = str(output.resolve())
    os.environ["ISH_CONTENT_BUNDLE"] = str(bundle.resolve())

    from scripts.content_store import load_content_bundle, validate_publishable_content
    from scripts.build_site import main as build_site
    from scripts.validate_site import validate

    draft_preview = output.name == "preview" and bundle.name == "preview-bundle.json"
    if not draft_preview:
        validate_publishable_content(load_content_bundle(override_path=bundle))
    build_site()
    if draft_preview:
        return
    errors = validate()
    if errors:
        raise RuntimeError("\n".join(errors))


def main() -> None:
    parser = argparse.ArgumentParser(description="ISH local website editor")
    parser.add_argument("--workspace", type=Path, help="Existing ISH repository clone")
    parser.add_argument("--host", default=os.environ.get("ISH_EDITOR_HOST", "0.0.0.0"), choices=("127.0.0.1", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--edition", choices=("basic", "advanced", "unified"), help="Editor feature edition")
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--reset-auth", action="store_true", help="Remove local editor credentials and exit")
    parser.add_argument("--internal-generate", nargs=3, metavar=("SOURCE", "OUTPUT", "BUNDLE"), help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.internal_generate:
        try:
            generate_site(*(Path(value) for value in args.internal_generate))
        except (RuntimeError, ValueError) as error:
            parser.exit(2, f"Error: {error}\n")
        return

    if args.reset_auth:
        removed = LocalCredentialStore().reset()
        print("Credenciales locales eliminadas." if removed else "No habia credenciales locales configuradas.")
        return

    if args.edition:
        os.environ["ISH_EDITOR_EDITION"] = set_editor_edition(args.edition)

    port = args.port or available_port()
    app = create_app(workspace_path=args.workspace)
    setup_token = app.state.session_token
    browser_host = "127.0.0.1" if args.host == "0.0.0.0" else args.host
    base_url = f"http://{browser_host}:{port}/"
    url = base_url if app.state.editor.local_auth.configured else f"{base_url}?setup={setup_token}"
    if not args.no_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    print(f"ISH Editor: {url}")
    uvicorn.run(app, host=args.host, port=port, log_level="warning")


if __name__ == "__main__":
    main()
