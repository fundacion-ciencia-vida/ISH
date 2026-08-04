import { useCallback, useEffect, useMemo, useRef, useState, type RefObject } from "react";
import {
  closestCenter,
  DndContext,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import {
  ArchiveRestore,
  Check,
  ChevronDown,
  ChevronRight,
  CircleAlert,
  CloudUpload,
  Copy,
  Database,
  Eye,
  EyeOff,
  FileText,
  GripVertical,
  History,
  Image,
  KeyRound,
  Laptop,
  Layers3,
  LoaderCircle,
  LockKeyhole,
  LogIn,
  LogOut,
  Menu,
  Monitor,
  PanelRightClose,
  PanelRightOpen,
  Plus,
  Redo2,
  RefreshCw,
  Save,
  Settings2,
  Smartphone,
  Tablet,
  Trash2,
  Undo2,
  Upload,
  X,
} from "lucide-react";
import { api } from "./api";
import { FieldEditor, humanize, RecordEditor } from "./FieldEditor";
import { createId } from "./id";
import { Modal } from "./Modal";
import type {
  BootstrapData,
  ContentBundle,
  DraftHistoryItem,
  EditorEdition,
  EditorEditionOption,
  EditorMode,
  JsonRecord,
  JsonValue,
  LocalAuthStatus,
  MediaItem,
  PageTemplate,
  PreviewSize,
  PublishedHistoryItem,
  Section,
  SectionTemplate,
  SitePage,
} from "./types";
import { useHistoryState } from "./useHistoryState";

type SaveState = "saved" | "saving" | "error";

function clone<T>(value: T): T {
  return structuredClone(value);
}

function orderedPages(bundle: ContentBundle): SitePage[] {
  const ids = [
    "home",
    ...bundle.site.navigation.groups.flatMap((group) => group.items.map((item) => item.page_id)),
    ...bundle.site.navigation.conference_subnav,
  ];
  const positions = new Map(ids.map((id, index) => [id, index]));
  return [...bundle.pages].sort((left, right) => {
    const leftPosition = positions.get(left.id) ?? Number.MAX_SAFE_INTEGER;
    const rightPosition = positions.get(right.id) ?? Number.MAX_SAFE_INTEGER;
    return leftPosition - rightPosition;
  });
}

function sharedContentTarget(bundle: ContentBundle, collection: string): { pageId: string; sectionId: string } | null {
  const pages = orderedPages(bundle);
  if (collection === "site") {
    const home = pages.find((page) => page.id === "home");
    const hero = home?.sections.find((section) => section.type === "home_hero") ?? home?.sections[0];
    return home && hero ? { pageId: home.id, sectionId: hero.id } : null;
  }
  for (const page of pages) {
    const section = page.sections.find((candidate) => candidate.data.collection === collection);
    if (section) return { pageId: page.id, sectionId: section.id };
  }
  return null;
}

function SortableSectionRow({
  section,
  selected,
  onSelect,
  onToggle,
  onDuplicate,
  onDelete,
  structuralEditing,
}: {
  section: Section;
  selected: boolean;
  onSelect: () => void;
  onToggle: () => void;
  onDuplicate: () => void;
  onDelete: () => void;
  structuralEditing: boolean;
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: section.id });
  return (
    <div
      ref={setNodeRef}
      className={`section-row${selected ? " is-selected" : ""}${isDragging ? " is-dragging" : ""}`}
      style={{ transform: CSS.Transform.toString(transform), transition }}
    >
      {structuralEditing ? <button type="button" className="drag-handle" aria-label="Reordenar seccion" title="Reordenar seccion" {...attributes} {...listeners}>
        <GripVertical />
      </button> : <span className="drag-handle is-static" aria-hidden="true"><FileText /></span>}
      <button type="button" className="section-row-main" onClick={onSelect}>
        <span>{humanize(section.type)}</span>
        <small>{section.id}</small>
      </button>
      {structuralEditing && <div className="section-row-actions">
        <button type="button" className="icon-button" onClick={onToggle} aria-label={section.visible ? "Ocultar seccion" : "Mostrar seccion"} title={section.visible ? "Ocultar seccion" : "Mostrar seccion"}>
          {section.visible ? <Eye /> : <EyeOff />}
        </button>
        <button type="button" className="icon-button" onClick={onDuplicate} aria-label="Duplicar seccion" title="Duplicar seccion"><Copy /></button>
        {!section.locked && <button type="button" className="icon-button danger" onClick={onDelete} aria-label="Eliminar seccion" title="Eliminar seccion"><Trash2 /></button>}
      </div>}
    </div>
  );
}

function LocalAuthScreen({ status, onAuthenticated }: { status: LocalAuthStatus; onAuthenticated: () => Promise<void> }) {
  const setup = !status.configured;
  const [username, setUsername] = useState(setup ? "admin" : "");
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const ready = username.trim().length >= 3 && password.length >= (setup ? 10 : 1) && (!setup || password === confirmation);

  const submit = async () => {
    if (!ready || (setup && !status.can_setup)) return;
    setBusy(true);
    setMessage("");
    try {
      if (setup) await api.setupLocalAuth(username.trim(), password);
      else await api.loginLocal(username.trim(), password);
      await onAuthenticated();
    } catch (authError) {
      setMessage(authError instanceof Error ? authError.message : "No fue posible iniciar la sesion local.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="setup-screen">
      <form className="setup-panel auth-panel" onSubmit={(event) => { event.preventDefault(); void submit(); }}>
        <div className="setup-brand"><span>ISH</span><div><strong>Editor del sitio</strong><small>Acceso local</small></div></div>
        <LockKeyhole className="auth-mark" aria-hidden="true" />
        <h1>{setup ? "Crear acceso local" : "Iniciar sesion"}</h1>
        <p>{setup ? "Estas credenciales se guardan solamente en este equipo." : "Ingresa las credenciales configuradas para este editor."}</p>
        {setup && !status.can_setup && <div className="auth-warning"><CircleAlert /><span>Abre el enlace de configuracion mostrado al iniciar la aplicacion.</span></div>}
        <label className="field"><span>Usuario</span><input autoFocus value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" /></label>
        <label className="field"><span>Contrasena</span><input type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete={setup ? "new-password" : "current-password"} /></label>
        {setup && <label className="field"><span>Repetir contrasena</span><input type="password" value={confirmation} onChange={(event) => setConfirmation(event.target.value)} autoComplete="new-password" /></label>}
        {message && <div className="auth-warning"><CircleAlert /><span>{message}</span></div>}
        <button type="submit" className="primary-command auth-submit" disabled={!ready || busy || (setup && !status.can_setup)}>
          {busy ? <LoaderCircle className="spin" /> : <LogIn />}<span>{busy ? "Abriendo..." : setup ? "Crear y entrar" : "Entrar"}</span>
        </button>
      </form>
    </main>
  );
}

function Setup({ bootstrap, onReady, onError }: { bootstrap: BootstrapData; onReady: () => void; onError: (message: string) => void }) {
  const [token, setToken] = useState("");
  const [destination, setDestination] = useState(bootstrap.suggested_workspace);
  const [busy, setBusy] = useState(false);
  const submit = async () => {
    setBusy(true);
    try {
      await api.saveToken(token);
      await api.clone(destination);
      onReady();
    } catch (error) {
      onError(error instanceof Error ? error.message : "No fue posible preparar el editor.");
    } finally {
      setBusy(false);
    }
  };
  return (
    <main className="setup-screen">
      <section className="setup-panel">
        <div className="setup-brand"><span>ISH</span><div><strong>Editor del sitio</strong><small>Configuracion inicial</small></div></div>
        <h1>Conectar la copia local</h1>
        <p>El editor clonara la rama <strong>{bootstrap.branch}</strong> y guardara el acceso a GitHub en el llavero de este equipo.</p>
        <label className="field"><span>Token personal de GitHub</span><input type="password" value={token} onChange={(event) => setToken(event.target.value)} autoComplete="off" /></label>
        <label className="field"><span>Carpeta para el sitio</span><input value={destination} onChange={(event) => setDestination(event.target.value)} /></label>
        <button type="button" className="primary-command" disabled={busy || token.length < 8 || !destination.trim()} onClick={submit}>
          {busy ? <LoaderCircle className="spin" /> : <CloudUpload />}<span>{busy ? "Preparando..." : "Clonar y abrir"}</span>
        </button>
        <small className="setup-repository">{bootstrap.repository}</small>
      </section>
    </main>
  );
}

function MediaLibrary({
  items,
  selecting,
  kind,
  onChoose,
  onUpload,
  onDelete,
  onRestore,
}: {
  items: MediaItem[];
  selecting?: boolean;
  kind?: "image" | "document";
  onChoose?: (item: MediaItem) => void;
  onUpload: (file: File, kind: "image" | "document") => void;
  onDelete: (item: MediaItem) => void;
  onRestore: (item: MediaItem) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const visible = kind ? items.filter((item) => item.kind === kind) : items;
  return (
    <div className="media-library">
      <div className="media-toolbar">
        <div><strong>Biblioteca</strong><span>{visible.length} recursos</span></div>
        <button type="button" className="secondary-command" onClick={() => inputRef.current?.click()}><Upload /><span>Subir</span></button>
        <input
          ref={inputRef}
          type="file"
          hidden
          accept={kind === "document" ? "application/pdf" : kind === "image" ? "image/*" : "image/*,application/pdf"}
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) onUpload(file, file.type === "application/pdf" ? "document" : "image");
            event.currentTarget.value = "";
          }}
        />
      </div>
      <div className="media-grid">
        {visible.map((item) => (
          <article className={`media-item${item.pending_delete ? " is-deleted" : ""}`} key={`${item.pending}-${item.path}`}>
            <button type="button" className="media-preview" onClick={() => selecting && !item.pending_delete && onChoose?.(item)} disabled={!selecting || item.pending_delete}>
              {item.kind === "image" ? <img src={`/preview/${item.path}`} alt="" loading="lazy" /> : <FileText />}
              {(item.pending || item.pending_delete) && <span>{item.pending_delete ? "Se eliminara" : "Pendiente"}</span>}
            </button>
            <div><strong title={item.name}>{item.name}</strong><small>{item.pending_delete ? "Eliminacion pendiente" : item.kind === "image" ? "Imagen" : "PDF"}</small></div>
            {item.pending_delete ? <button type="button" className="icon-button" onClick={() => onRestore(item)} aria-label="Restaurar recurso" title="Conservar recurso"><ArchiveRestore /></button> : <button type="button" className="icon-button danger" onClick={() => onDelete(item)} aria-label="Eliminar recurso" title={item.pending ? "Eliminar carga" : "Eliminar al publicar"}><Trash2 /></button>}
          </article>
        ))}
        {!visible.length && <div className="empty-state"><Image /><p>No hay recursos de este tipo.</p></div>}
      </div>
    </div>
  );
}

function HistoryPanel({
  drafts,
  published,
  onRestoreDraft,
  onRestorePublished,
}: {
  drafts: DraftHistoryItem[];
  published: PublishedHistoryItem[];
  onRestoreDraft: (id: string) => void;
  onRestorePublished: (commit: string) => void;
}) {
  return (
    <div className="history-panel">
      <section><h3>Borradores locales</h3>{drafts.map((item) => <button type="button" className="history-row" key={item.id} onClick={() => onRestoreDraft(item.id)}><History /><span><strong>{new Date(item.saved_at).toLocaleString("es-CL")}</strong><small>{item.base_commit.slice(0, 8)}</small></span><ArchiveRestore /></button>)}{!drafts.length && <p className="empty-inline">Aun no hay revisiones locales.</p>}</section>
      <section><h3>Publicaciones</h3>{published.map((item) => <button type="button" className="history-row" key={item.commit} onClick={() => onRestorePublished(item.commit)}><CloudUpload /><span><strong>{item.message}</strong><small>{new Date(item.date).toLocaleString("es-CL")} · {item.commit.slice(0, 8)}</small></span><ArchiveRestore /></button>)}{!published.length && <p className="empty-inline">El historial administrable aparecera despues de la primera publicacion.</p>}</section>
    </div>
  );
}

function EditionControl({
  edition,
  catalog,
  open,
  onToggle,
  onClose,
  controlRef,
}: {
  edition: EditorEdition;
  catalog: EditorEditionOption[];
  open: boolean;
  onToggle: () => void;
  onClose: () => void;
  controlRef: RefObject<HTMLDivElement | null>;
}) {
  return (
    <div className="edition-control" ref={controlRef}>
      <button className={`edition-chip is-${edition.id}`} type="button" aria-expanded={open} aria-haspopup="dialog" onClick={onToggle}>
        <Layers3 aria-hidden="true" />
        <span><strong><span className="edition-prefix">Edicion </span>{edition.label}</strong><small>{edition.price_label}</small></span>
        <ChevronDown className={open ? "is-open" : ""} aria-hidden="true" />
      </button>
      {open && <section className="edition-popover" role="dialog" aria-label="Ediciones del editor">
        <header><div><span>Alcance de esta entrega</span><strong>Ediciones del editor</strong></div><button type="button" className="icon-button" onClick={onClose} title="Cerrar" aria-label="Cerrar"><X /></button></header>
        <div className="edition-options">
          {catalog.map((option) => <section className={option.id === edition.id ? "edition-option is-current" : "edition-option"} key={option.id}>
            <div><span>Edicion {option.label}</span><strong>{option.price_label}</strong>{option.id === edition.id && <em>Activa</em>}</div>
            <ul>{option.features.map((feature) => <li key={feature}><Check />{feature}</li>)}</ul>
          </section>)}
        </div>
        <p>{edition.id === "basic" ? "Las herramientas para crear y reorganizar la estructura no estan habilitadas en esta entrega." : "Las herramientas de contenido y estructura estan habilitadas en esta entrega."}</p>
      </section>}
    </div>
  );
}

export default function App() {
  const [localAuth, setLocalAuth] = useState<LocalAuthStatus | null>(null);
  const [bootstrap, setBootstrap] = useState<BootstrapData | null>(null);
  const [loading, setLoading] = useState(true);
  const bundleHistory = useHistoryState<ContentBundle | null>(null);
  const bundle = bundleHistory.value;
  const [baseline, setBaseline] = useState<ContentBundle | null>(null);
  const [mode, setMode] = useState<EditorMode>("pages");
  const [selectedPageId, setSelectedPageId] = useState("");
  const [selectedSectionId, setSelectedSectionId] = useState<string | null>(null);
  const [selectedCollection, setSelectedCollection] = useState("site");
  const [previewSize, setPreviewSize] = useState<PreviewSize>("desktop");
  const [previewVersion, setPreviewVersion] = useState(0);
  const [previewRoutes, setPreviewRoutes] = useState<Record<string, string>>({});
  const [saveState, setSaveState] = useState<SaveState>("saved");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [inspectorOpen, setInspectorOpen] = useState(() => !window.matchMedia("(max-width: 760px)").matches);
  const [sectionModal, setSectionModal] = useState(false);
  const [pageModal, setPageModal] = useState(false);
  const [publishModal, setPublishModal] = useState(false);
  const [tokenModal, setTokenModal] = useState(false);
  const [passwordModal, setPasswordModal] = useState(false);
  const [editionPanelOpen, setEditionPanelOpen] = useState(false);
  const [mediaPicker, setMediaPicker] = useState<{ kind: "image" | "document"; apply: (value: string) => void } | null>(null);
  const [media, setMedia] = useState<MediaItem[]>([]);
  const [drafts, setDrafts] = useState<DraftHistoryItem[]>([]);
  const [published, setPublished] = useState<PublishedHistoryItem[]>([]);
  const [busyAction, setBusyAction] = useState("");
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const editionControlRef = useRef<HTMLDivElement>(null);
  const autosaveReady = useRef(false);

  const loadWorkspace = useCallback(async () => {
    setLoading(true);
    try {
      const [bootstrapData, contentData] = await Promise.all([api.bootstrap(), api.content()]);
      setBootstrap(bootstrapData);
      bundleHistory.reset(contentData.bundle);
      setBaseline(clone(contentData.bundle));
      const first = orderedPages(contentData.bundle)[0];
      setSelectedPageId((current) => current || first?.id || "");
      setSaveState("saved");
      autosaveReady.current = true;
      const preview = await api.preview(contentData.bundle);
      setPreviewRoutes(preview.pages);
      setPreviewVersion((current) => current + 1);
    } catch (loadError) {
      try {
        const bootstrapData = await api.bootstrap();
        setBootstrap(bootstrapData);
      } catch {
        setError(loadError instanceof Error ? loadError.message : "No fue posible iniciar el editor.");
      }
    } finally {
      setLoading(false);
    }
  }, [bundleHistory]);

  useEffect(() => {
    const initialize = async () => {
      try {
        const status = await api.authStatus();
        setLocalAuth(status);
        if (status.authenticated) await loadWorkspace();
        else setLoading(false);
      } catch (authError) {
        setError(authError instanceof Error ? authError.message : "No fue posible comprobar el acceso local.");
        setLoading(false);
      }
    };
    void initialize();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const expire = () => {
      autosaveReady.current = false;
      setLocalAuth((current) => ({ configured: current?.configured ?? true, authenticated: false, can_setup: false }));
      setLoading(false);
    };
    window.addEventListener("ish-auth-expired", expire);
    return () => window.removeEventListener("ish-auth-expired", expire);
  }, []);

  useEffect(() => {
    if (!bundle || !autosaveReady.current) return;
    setSaveState("saving");
    const timer = window.setTimeout(async () => {
      try {
        await api.saveDraft(bundle);
        const preview = await api.preview(bundle);
        setPreviewRoutes(preview.pages);
        setPreviewVersion((current) => current + 1);
        setSaveState("saved");
      } catch (saveError) {
        setSaveState("error");
        setError(saveError instanceof Error ? saveError.message : "No fue posible guardar el borrador.");
      }
    }, 850);
    return () => window.clearTimeout(timer);
  }, [bundle]);

  useEffect(() => {
    const listener = (event: MessageEvent) => {
      if (event.data?.type === "ish-select-section" && typeof event.data.sectionId === "string") {
        setSelectedSectionId(event.data.sectionId);
        setMode("pages");
      }
      if (event.data?.type === "ish-preview-ready") {
        iframeRef.current?.contentWindow?.postMessage({ type: "ish-highlight-section", sectionId: selectedSectionId }, "*");
      }
    };
    window.addEventListener("message", listener);
    return () => window.removeEventListener("message", listener);
  }, [selectedSectionId]);

  useEffect(() => {
    iframeRef.current?.contentWindow?.postMessage({ type: "ish-highlight-section", sectionId: selectedSectionId }, "*");
  }, [selectedSectionId, previewVersion]);

  useEffect(() => {
    if (!notice) return;
    const timer = window.setTimeout(() => setNotice(""), 3500);
    return () => window.clearTimeout(timer);
  }, [notice]);

  useEffect(() => {
    if (!editionPanelOpen) return;
    const closeOutside = (event: PointerEvent) => {
      if (!editionControlRef.current?.contains(event.target as Node)) setEditionPanelOpen(false);
    };
    const closeWithKeyboard = (event: KeyboardEvent) => {
      if (event.key === "Escape") setEditionPanelOpen(false);
    };
    document.addEventListener("pointerdown", closeOutside);
    document.addEventListener("keydown", closeWithKeyboard);
    return () => {
      document.removeEventListener("pointerdown", closeOutside);
      document.removeEventListener("keydown", closeWithKeyboard);
    };
  }, [editionPanelOpen]);

  const selectedPage = bundle?.pages.find((page) => page.id === selectedPageId) ?? null;
  const selectedSection = selectedPage?.sections.find((section) => section.id === selectedSectionId) ?? null;
  const pages = useMemo(() => bundle ? orderedPages(bundle) : [], [bundle]);
  const dirty = Boolean(bundle && baseline && JSON.stringify(bundle) !== JSON.stringify(baseline));
  const customSite = bootstrap?.features?.custom_site ?? false;
  const showEditionDistinction = bootstrap?.edition?.show_distinction ?? false;
  const sharedSiteValue = bundle
    ? customSite
      ? bundle.site
      : Object.fromEntries(Object.entries(bundle.site).filter(([key]) => key !== "navigation")) as JsonRecord
    : null;

  const compactLayout = () => window.matchMedia("(max-width: 760px)").matches;
  const openInspector = () => setInspectorOpen(true);

  const showSharedCollection = (collection: string, openEditor = true) => {
    setSelectedCollection(collection);
    if (bundle) {
      const target = sharedContentTarget(bundle, collection);
      if (target) {
        setSelectedPageId(target.pageId);
        setSelectedSectionId(target.sectionId);
      }
    }
    if (openEditor) openInspector();
  };

  const updateBundle = (transform: (draft: ContentBundle) => void) => {
    if (!bundle) return;
    const next = clone(bundle);
    transform(next);
    bundleHistory.set(next);
  };

  const updatePage = (pageId: string, transform: (page: SitePage) => void) => updateBundle((next) => {
    const page = next.pages.find((candidate) => candidate.id === pageId);
    if (page) transform(page);
  });

  const chooseMedia = (_kind: "image" | "document", _current: string, apply: (value: string) => void) => {
    setMediaPicker({ kind: _kind, apply });
    void api.media().then(setMedia).catch((mediaError) => setError(mediaError.message));
  };

  const uploadMedia = async (file: File, kind: "image" | "document") => {
    setBusyAction("upload");
    try {
      const item = await api.uploadMedia(file, kind);
      setMedia((current) => [item, ...current]);
      setNotice("Recurso cargado en el borrador.");
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "No fue posible cargar el archivo.");
    } finally {
      setBusyAction("");
    }
  };

  const deleteMediaItem = async (item: MediaItem) => {
    if (!window.confirm(item.pending ? "Eliminar esta carga del borrador?" : "Eliminar este recurso en la proxima publicacion?")) return;
    try {
      await api.deleteMedia(item.path);
      setMedia((current) => item.pending
        ? current.filter((candidate) => candidate.path !== item.path)
        : current.map((candidate) => candidate.path === item.path ? { ...candidate, pending_delete: true } : candidate));
      setNotice(item.pending ? "Carga eliminada." : "El recurso se eliminara al publicar.");
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "No fue posible eliminar el recurso.");
    }
  };

  const restoreMediaItem = async (item: MediaItem) => {
    try {
      await api.restoreMedia(item.path);
      setMedia((current) => current.map((candidate) => candidate.path === item.path ? { ...candidate, pending_delete: false } : candidate));
      setNotice("El recurso se conservara.");
    } catch (restoreError) {
      setError(restoreError instanceof Error ? restoreError.message : "No fue posible restaurar el recurso.");
    }
  };

  const loadSideData = async (nextMode: EditorMode) => {
    setMode(nextMode);
    if (nextMode === "shared") {
      showSharedCollection(selectedCollection, false);
      setInspectorOpen(!compactLayout());
    }
    else if (nextMode === "media" || nextMode === "history" || compactLayout()) setInspectorOpen(false);
    try {
      if (nextMode === "media") setMedia(await api.media());
      if (nextMode === "history") {
        const [localHistory, publicationHistory] = await Promise.all([api.draftHistory(), api.publishedHistory()]);
        setDrafts(localHistory);
        setPublished(publicationHistory);
      }
    } catch (sideError) {
      setError(sideError instanceof Error ? sideError.message : "No fue posible cargar esta seccion.");
    }
  };

  const handleDragEnd = ({ active, over }: DragEndEvent) => {
    if (!customSite || !selectedPage || !over || active.id === over.id) return;
    const oldIndex = selectedPage.sections.findIndex((section) => section.id === active.id);
    const newIndex = selectedPage.sections.findIndex((section) => section.id === over.id);
    updatePage(selectedPage.id, (page) => { page.sections = arrayMove(page.sections, oldIndex, newIndex); });
  };

  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } }), useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }));

  const previewPath = previewRoutes[selectedPageId] ?? (selectedPage?.route ? `${selectedPage.route}/` : "");
  const iframeSrc = `/preview/${previewPath}?v=${previewVersion}`;

  const openAuthenticatedWorkspace = async () => {
    const status = await api.authStatus();
    setLocalAuth(status);
    if (!status.authenticated) throw new Error("No fue posible abrir la sesion local.");
    await loadWorkspace();
  };

  if (loading) {
    return <main className="loading-screen"><LoaderCircle className="spin" /><span>Abriendo el editor...</span></main>;
  }
  if (localAuth && !localAuth.authenticated) {
    return <LocalAuthScreen status={localAuth} onAuthenticated={openAuthenticatedWorkspace} />;
  }
  if (!localAuth) {
    return <main className="loading-screen error-screen"><CircleAlert /><strong>No se pudo comprobar el acceso local</strong><span>{error}</span></main>;
  }
  if (!bootstrap) {
    return <main className="loading-screen error-screen"><CircleAlert /><strong>No se pudo abrir el editor</strong><span>{error || "No fue posible cargar la copia local del sitio."}</span></main>;
  }
  if (!bootstrap.workspace || !bundle) {
    return <><Setup bootstrap={bootstrap} onReady={() => void loadWorkspace()} onError={setError} />{error && <div className="toast is-error"><CircleAlert />{error}<button onClick={() => setError("")}><X /></button></div>}</>;
  }

  const pageChanges = bundle.pages.filter((page) => {
    const original = baseline?.pages.find((candidate) => candidate.id === page.id);
    return JSON.stringify(original) !== JSON.stringify(page);
  });
  const collectionChanges = Object.keys(bundle.collections).filter((key) => JSON.stringify(bundle.collections[key]) !== JSON.stringify(baseline?.collections[key]));

  return (
    <div className={`editor-app${inspectorOpen ? "" : " inspector-closed"}`}>
      <header className={`editor-topbar${showEditionDistinction ? " has-edition" : ""}`}>
        <div className="editor-brand"><span>ISH</span><div><strong>Editor</strong><small>{bootstrap.workspace.branch}</small></div></div>
        {showEditionDistinction && <EditionControl edition={bootstrap.edition} catalog={bootstrap.edition_catalog} open={editionPanelOpen} onToggle={() => setEditionPanelOpen((current) => !current)} onClose={() => setEditionPanelOpen(false)} controlRef={editionControlRef} />}
        <div className="save-status" data-state={saveState}>{saveState === "saving" ? <LoaderCircle className="spin" /> : saveState === "error" ? <CircleAlert /> : <Check />}<span>{saveState === "saving" ? "Guardando" : saveState === "error" ? "Error al guardar" : dirty ? "Borrador guardado" : "Sin cambios"}</span></div>
        <div className="topbar-actions">
          <button className="icon-command" type="button" disabled={!bundleHistory.canUndo} onClick={bundleHistory.undo} title="Deshacer" aria-label="Deshacer"><Undo2 /></button>
          <button className="icon-command" type="button" disabled={!bundleHistory.canRedo} onClick={bundleHistory.redo} title="Rehacer" aria-label="Rehacer"><Redo2 /></button>
          <span className="topbar-divider" />
          <button className="secondary-command" type="button" title="Sincronizar" aria-label="Sincronizar" onClick={async () => { try { setBusyAction("sync"); const result = await api.sync(); setNotice(result.updated ? "Sitio sincronizado." : "Ya estaba actualizado."); } catch (syncError) { if (!bootstrap.credentials.configured) setTokenModal(true); else setError(syncError instanceof Error ? syncError.message : "No fue posible sincronizar."); } finally { setBusyAction(""); } }}><RefreshCw className={busyAction === "sync" ? "spin" : ""} /><span>Sincronizar</span></button>
          <button className="primary-command" type="button" onClick={() => bootstrap.credentials.configured ? setPublishModal(true) : setTokenModal(true)}><CloudUpload /><span>Publicar</span></button>
          <span className="topbar-divider" />
          <button className="icon-command" type="button" title="Cambiar contrasena" aria-label="Cambiar contrasena" onClick={() => setPasswordModal(true)}><KeyRound /></button>
          <button className="icon-command" type="button" title="Cerrar sesion local" aria-label="Cerrar sesion local" onClick={async () => { await api.logoutLocal(); autosaveReady.current = false; bundleHistory.reset(null); setBootstrap(null); setBaseline(null); setLocalAuth({ configured: true, authenticated: false, can_setup: false }); }}><LogOut /></button>
        </div>
      </header>

      <nav className="editor-rail" aria-label="Areas del editor">
        <button className={mode === "pages" ? "is-active" : ""} onClick={() => void loadSideData("pages")} title="Paginas" aria-label="Paginas"><FileText /></button>
        <button className={mode === "shared" ? "is-active" : ""} onClick={() => void loadSideData("shared")} title="Contenido compartido" aria-label="Contenido compartido"><Database /></button>
        <button className={mode === "media" ? "is-active" : ""} onClick={() => void loadSideData("media")} title="Medios" aria-label="Medios"><Image /></button>
        <button className={mode === "history" ? "is-active" : ""} onClick={() => void loadSideData("history")} title="Historial" aria-label="Historial"><History /></button>
      </nav>

      <aside className="editor-sidebar">
        {mode === "pages" && <>
          <div className="panel-heading"><div><span>Paginas</span><small>{bundle.pages.length} publicadas</small></div>{customSite && <button className="icon-button" type="button" onClick={() => setPageModal(true)} title="Nueva pagina" aria-label="Nueva pagina"><Plus /></button>}</div>
          {showEditionDistinction && !customSite && <button type="button" className="edition-boundary" onClick={() => setEditionPanelOpen(true)}><LockKeyhole /><span><strong>Nuevas paginas y secciones</strong><small>Edicion Avanzada · $1.200.000 liquido</small></span><ChevronRight /></button>}
          <div className="page-list">{pages.map((page) => <button type="button" key={page.id} className={page.id === selectedPageId ? "page-row is-active" : "page-row"} onClick={() => { setSelectedPageId(page.id); setSelectedSectionId(null); }}><span>{page.title.split(" | ")[0]}</span><small>/{page.route}</small><ChevronRight /></button>)}</div>
          {selectedPage && <div className="section-outline">
            <div className="outline-heading"><span>Contenido</span>{customSite && <button type="button" className="icon-button" onClick={() => setSectionModal(true)} title="Agregar seccion" aria-label="Agregar seccion"><Plus /></button>}</div>
            <button type="button" className={!selectedSectionId ? "settings-row is-selected" : "settings-row"} onClick={() => { setSelectedSectionId(null); openInspector(); }}><Settings2 /><span>Configuracion de pagina</span></button>
            <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}><SortableContext items={selectedPage.sections.map((section) => section.id)} strategy={verticalListSortingStrategy}><div className="section-list">{selectedPage.sections.map((section) => <SortableSectionRow key={section.id} section={section} selected={selectedSectionId === section.id} structuralEditing={customSite} onSelect={() => { setSelectedSectionId(section.id); openInspector(); }} onToggle={() => updatePage(selectedPage.id, (page) => { const target = page.sections.find((candidate) => candidate.id === section.id); if (target) target.visible = !target.visible; })} onDuplicate={() => updatePage(selectedPage.id, (page) => { const index = page.sections.findIndex((candidate) => candidate.id === section.id); const duplicate = clone(section); duplicate.id = `${section.type}-${createId().slice(0, 8)}`; duplicate.locked = false; page.sections.splice(index + 1, 0, duplicate); setSelectedSectionId(duplicate.id); })} onDelete={() => { if (window.confirm("Eliminar esta seccion del borrador?")) updatePage(selectedPage.id, (page) => { page.sections = page.sections.filter((candidate) => candidate.id !== section.id); setSelectedSectionId(null); }); }} />)}</div></SortableContext></DndContext>
          </div>}
        </>}
        {mode === "shared" && <><div className="panel-heading"><div><span>Contenido compartido</span><small>Una edicion para todo el sitio</small></div></div><button type="button" className={selectedCollection === "site" ? "shared-row is-active" : "shared-row"} onClick={() => showSharedCollection("site")}><Settings2 /><span>Datos generales</span><ChevronRight /></button>{Object.entries(bundle.collections).map(([key, items]) => <button type="button" className={selectedCollection === key ? "shared-row is-active" : "shared-row"} key={key} onClick={() => showSharedCollection(key)}><Database /><span>{humanize(key)}</span><small>{items.length}</small><ChevronRight /></button>)}</>}
        {mode === "media" && <MediaLibrary items={media} onUpload={uploadMedia} onDelete={deleteMediaItem} onRestore={restoreMediaItem} />}
        {mode === "history" && <HistoryPanel drafts={drafts} published={published} onRestoreDraft={async (id) => { const response = await api.restoreDraft(id); bundleHistory.reset(response.bundle); setNotice("Revision local restaurada como borrador."); }} onRestorePublished={async (commit) => { const response = await api.restorePublished(commit); bundleHistory.reset(response.bundle); setNotice("Publicacion restaurada como borrador."); }} />}
      </aside>

      <main className="preview-workspace">
        <div className="preview-toolbar"><div className="preview-address"><span className="status-dot" />/{selectedPage?.route}</div><div className="preview-sizes" aria-label="Tamano de vista"><button className={previewSize === "desktop" ? "is-active" : ""} onClick={() => setPreviewSize("desktop")} title="Escritorio" aria-label="Escritorio"><Monitor /></button><button className={previewSize === "tablet" ? "is-active" : ""} onClick={() => setPreviewSize("tablet")} title="Tablet" aria-label="Tablet"><Tablet /></button><button className={previewSize === "mobile" ? "is-active" : ""} onClick={() => setPreviewSize("mobile")} title="Movil" aria-label="Movil"><Smartphone /></button></div><button className="icon-button" type="button" onClick={() => setInspectorOpen((current) => !current)} title={inspectorOpen ? "Cerrar inspector" : "Abrir inspector"} aria-label={inspectorOpen ? "Cerrar inspector" : "Abrir inspector"}>{inspectorOpen ? <PanelRightClose /> : <PanelRightOpen />}</button></div>
        <div className={`preview-frame size-${previewSize}`}><iframe ref={iframeRef} src={iframeSrc} title={`Vista previa de ${selectedPage?.title ?? "pagina"}`} /></div>
      </main>

      {inspectorOpen && <aside className="editor-inspector">
        <div className="inspector-heading"><div><span>{mode === "shared" ? humanize(selectedCollection) : selectedSection ? humanize(selectedSection.type) : "Pagina"}</span><small>{mode === "shared" ? "Contenido compartido" : selectedSection?.id ?? selectedPage?.id}</small></div><button type="button" className="icon-button inspector-close" onClick={() => setInspectorOpen(false)} title="Cerrar inspector" aria-label="Cerrar inspector"><PanelRightClose /></button></div>
        <div className="inspector-content">
          {mode === "pages" && selectedPage && !selectedSection && <>
            <RecordEditor value={{ title: selectedPage.title, description: selectedPage.description, social_image: selectedPage.social_image, hero_image: selectedPage.hero_image, ...(customSite ? { ...(!selectedPage.core_route ? { route: selectedPage.route } : {}), conference_page: selectedPage.conference_page } : {}) } as JsonRecord} onChange={(value) => updatePage(selectedPage.id, (page) => { page.title = String(value.title); page.description = String(value.description); page.social_image = String(value.social_image); page.hero_image = String(value.hero_image); if (customSite) { if (!page.core_route) page.route = String(value.route); page.conference_page = Boolean(value.conference_page); } })} onChooseMedia={chooseMedia} allowArrayStructure={customSite} />
            {customSite && !selectedPage.core_route && <button type="button" className="danger-command" onClick={() => { if (!window.confirm("Eliminar esta pagina y quitarla de la navegacion?")) return; updateBundle((next) => { next.pages = next.pages.filter((page) => page.id !== selectedPage.id); next.site.navigation.groups.forEach((group) => { group.items = group.items.filter((item) => item.page_id !== selectedPage.id); }); next.site.navigation.conference_subnav = next.site.navigation.conference_subnav.filter((id) => id !== selectedPage.id); }); setSelectedPageId(bundle.pages.find((page) => page.id !== selectedPage.id)?.id ?? ""); }}><Trash2 /><span>Eliminar pagina</span></button>}
          </>}
          {mode === "pages" && selectedPage && selectedSection && <>{customSite && <div className="section-meta"><label className="toggle-field"><span>Visible</span><input type="checkbox" checked={selectedSection.visible} onChange={(event) => updatePage(selectedPage.id, (page) => { const target = page.sections.find((section) => section.id === selectedSection.id); if (target) target.visible = event.target.checked; })} /><span className="toggle-track" /></label>{selectedSection.variant !== undefined && <label className="field"><span>Variante</span><input value={selectedSection.variant} onChange={(event) => updatePage(selectedPage.id, (page) => { const target = page.sections.find((section) => section.id === selectedSection.id); if (target) target.variant = event.target.value; })} /></label>}</div>}<RecordEditor value={selectedSection.data} onChange={(value) => updatePage(selectedPage.id, (page) => { const target = page.sections.find((section) => section.id === selectedSection.id); if (target) target.data = value; })} onChooseMedia={chooseMedia} allowArrayStructure={customSite} /></>}
          {mode === "shared" && selectedCollection === "site" && sharedSiteValue && <RecordEditor value={sharedSiteValue} onChange={(value) => updateBundle((next) => { next.site = customSite ? value as ContentBundle["site"] : { ...next.site, ...value, navigation: next.site.navigation } as ContentBundle["site"]; })} onChooseMedia={chooseMedia} allowArrayStructure={customSite} />}
          {mode === "shared" && selectedCollection !== "site" && <FieldEditor label={humanize(selectedCollection)} fieldKey={selectedCollection} value={bundle.collections[selectedCollection] as JsonValue} onChange={(value) => updateBundle((next) => { next.collections[selectedCollection] = value as JsonRecord[]; })} onChooseMedia={chooseMedia} allowArrayStructure={customSite || selectedCollection === "communications"} />}
          {(mode === "media" || mode === "history") && <div className="inspector-empty"><Menu /><p>Selecciona una pagina o contenido compartido para editar sus campos.</p></div>}
        </div>
      </aside>}

      {customSite && sectionModal && <Modal title="Agregar seccion" onClose={() => setSectionModal(false)}><div className="template-list">{bootstrap.section_catalog.map((template: SectionTemplate) => <button type="button" key={template.type} onClick={() => { if (!selectedPage) return; const section: Section = { id: `${template.type}-${createId().slice(0, 8)}`, type: template.type, visible: true, data: clone(template.data), ...(template.variant ? { variant: template.variant } : {}) }; updatePage(selectedPage.id, (page) => page.sections.push(section)); setSelectedSectionId(section.id); setSectionModal(false); }}><span>{template.label}</span><small>{template.description}</small><Plus /></button>)}</div></Modal>}
      {customSite && pageModal && <NewPageModal templates={bootstrap.page_catalog} existingRoutes={bundle.pages.map((page) => page.route)} onClose={() => setPageModal(false)} onCreate={(title, route, group, template) => { const id = `page-${route.replace(/\//g, "-")}-${createId().slice(0, 6)}`; const conference = group === "conference"; const sections: Section[] = [{ id: "hero", type: "page_hero", visible: true, locked: true, data: { eyebrow: conference ? "ICH2026" : "ISH", title, lede: "", image: "ui/social-preview.jpg", breadcrumbs: true, actions: [] } }, ...template.sections.map((section) => ({ id: `${section.type}-${createId().slice(0, 8)}`, type: section.type, visible: true, data: clone(section.data), ...(section.variant ? { variant: section.variant } : {}) }))]; const page: SitePage = { id, route, title, description: title, social_image: "ui/social-preview.jpg", hero_image: "ui/social-preview.jpg", conference_page: conference, core_route: false, sections }; updateBundle((next) => { next.pages.push(page); if (group !== "hidden") { const target = next.site.navigation.groups.find((candidate) => candidate.id === group); target?.items.push({ page_id: id, label: title }); } if (conference) next.site.navigation.conference_subnav.push(id); }); setSelectedPageId(id); setSelectedSectionId(null); setPageModal(false); }} />}
      {mediaPicker && <Modal title={mediaPicker.kind === "image" ? "Elegir imagen" : "Elegir documento"} onClose={() => setMediaPicker(null)} wide><MediaLibrary items={media} selecting kind={mediaPicker.kind} onChoose={(item) => { mediaPicker.apply(item.asset); setMediaPicker(null); }} onUpload={uploadMedia} onDelete={deleteMediaItem} onRestore={restoreMediaItem} /></Modal>}
      {tokenModal && <TokenModal onClose={() => setTokenModal(false)} onSaved={async () => { const next = await api.bootstrap(); setBootstrap(next); setTokenModal(false); setNotice("Token guardado en este equipo."); }} />}
      {passwordModal && <PasswordModal onClose={() => setPasswordModal(false)} onSaved={() => { setPasswordModal(false); setNotice("Contrasena local actualizada."); }} />}
      {publishModal && <PublishModal pages={pageChanges.map((page) => page.title)} collections={collectionChanges.map(humanize)} busy={busyAction === "publish"} onClose={() => setPublishModal(false)} onPublish={async (message) => { setBusyAction("publish"); try { const result = await api.publish(bundle, message); setBaseline(clone(bundle)); const nextBootstrap = await api.bootstrap(); setBootstrap(nextBootstrap); setPublishModal(false); setNotice(`${result.message} ${result.commit.slice(0, 8)}`); } catch (publishError) { setError(publishError instanceof Error ? publishError.message : "No fue posible publicar."); } finally { setBusyAction(""); } }} />}
      {error && <div className="toast is-error"><CircleAlert />{error}<button onClick={() => setError("")} aria-label="Cerrar"><X /></button></div>}
      {notice && <div className="toast is-success"><Check />{notice}</div>}
    </div>
  );
}

function NewPageModal({ templates, existingRoutes, onClose, onCreate }: { templates: PageTemplate[]; existingRoutes: string[]; onClose: () => void; onCreate: (title: string, route: string, group: string, template: PageTemplate) => void }) {
  const [title, setTitle] = useState("");
  const [route, setRoute] = useState("");
  const [group, setGroup] = useState("society");
  const [templateId, setTemplateId] = useState(templates[0]?.id ?? "");
  const updateTitle = (value: string) => { setTitle(value); setRoute(value.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "")); };
  const selectedTemplate = templates.find((template) => template.id === templateId) ?? templates[0];
  const normalizedRoute = route.replace(/^\/+|\/+$/g, "");
  const routeTaken = Boolean(normalizedRoute) && existingRoutes.map((value) => value.replace(/^\/+|\/+$/g, "")).includes(normalizedRoute);
  return <Modal title="Nueva pagina" onClose={onClose}><div className="modal-form"><label className="field"><span>Titulo</span><input autoFocus value={title} onChange={(event) => updateTitle(event.target.value)} /></label><label className="field"><span>Ruta</span><div className="route-input"><span>/</span><input value={route} aria-invalid={routeTaken} onChange={(event) => setRoute(event.target.value.toLowerCase().replace(/[^a-z0-9/-]/g, "-"))} /></div>{routeTaken && <small className="field-error">Esta ruta ya esta en uso.</small>}</label><div className="field"><span>Plantilla</span><div className="page-template-options">{templates.map((template) => <button type="button" key={template.id} className={template.id === templateId ? "is-selected" : ""} aria-pressed={template.id === templateId} onClick={() => setTemplateId(template.id)}><span>{template.label}</span><small>{template.description}</small></button>)}</div></div><label className="field"><span>Navegacion</span><select value={group} onChange={(event) => setGroup(event.target.value)}><option value="society">Society</option><option value="conference">Conference</option><option value="hidden">Fuera del menu</option></select></label><div className="modal-actions"><button type="button" className="secondary-command" onClick={onClose}>Cancelar</button><button type="button" className="primary-command" disabled={!title.trim() || !route.trim() || routeTaken || !selectedTemplate} onClick={() => selectedTemplate && onCreate(title.trim(), route.trim(), group, selectedTemplate)}><Plus /><span>Crear pagina</span></button></div></div></Modal>;
}

function TokenModal({ onClose, onSaved }: { onClose: () => void; onSaved: () => void }) {
  const [token, setToken] = useState("");
  const [busy, setBusy] = useState(false);
  return <Modal title="Acceso a GitHub" onClose={onClose}><div className="modal-form"><p className="modal-copy">Usa un token limitado al repositorio ISH con permiso de lectura y escritura de contenidos.</p><label className="field"><span>Token personal</span><input type="password" autoFocus autoComplete="off" value={token} onChange={(event) => setToken(event.target.value)} /></label><div className="modal-actions"><button className="secondary-command" onClick={onClose}>Cancelar</button><button className="primary-command" disabled={busy || token.length < 8} onClick={async () => { setBusy(true); try { await api.saveToken(token); onSaved(); } finally { setBusy(false); } }}><Save /><span>{busy ? "Guardando" : "Guardar"}</span></button></div></div></Modal>;
}

function PasswordModal({ onClose, onSaved }: { onClose: () => void; onSaved: () => void }) {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const ready = currentPassword.length > 0 && newPassword.length >= 10 && newPassword === confirmation;
  return <Modal title="Cambiar contrasena local" onClose={onClose}><form className="modal-form" onSubmit={async (event) => { event.preventDefault(); if (!ready) return; setBusy(true); setMessage(""); try { await api.changeLocalPassword(currentPassword, newPassword); onSaved(); } catch (passwordError) { setMessage(passwordError instanceof Error ? passwordError.message : "No fue posible cambiar la contrasena."); } finally { setBusy(false); } }}><p className="modal-copy">El cambio se guarda solo en este equipo y cierra las otras sesiones del editor.</p><label className="field"><span>Contrasena actual</span><input type="password" autoFocus autoComplete="current-password" value={currentPassword} onChange={(event) => setCurrentPassword(event.target.value)} /></label><label className="field"><span>Nueva contrasena</span><input type="password" autoComplete="new-password" value={newPassword} onChange={(event) => setNewPassword(event.target.value)} /></label><label className="field"><span>Repetir nueva contrasena</span><input type="password" autoComplete="new-password" value={confirmation} onChange={(event) => setConfirmation(event.target.value)} /></label>{message && <div className="auth-warning"><CircleAlert /><span>{message}</span></div>}<div className="modal-actions"><button type="button" className="secondary-command" onClick={onClose}>Cancelar</button><button type="submit" className="primary-command" disabled={!ready || busy}>{busy ? <LoaderCircle className="spin" /> : <KeyRound />}<span>{busy ? "Guardando" : "Actualizar"}</span></button></div></form></Modal>;
}

function PublishModal({ pages, collections, busy, onClose, onPublish }: { pages: string[]; collections: string[]; busy: boolean; onClose: () => void; onPublish: (message: string) => void }) {
  const [message, setMessage] = useState("Update site content via ISH Editor");
  return <Modal title="Publicar en GitHub Pages" onClose={onClose}><div className="publish-summary"><p>Se compilara y validara una copia temporal antes de enviar los cambios a <strong>gh-pages</strong>.</p><div><span>Paginas modificadas</span>{pages.length ? pages.map((page) => <strong key={page}>{page}</strong>) : <small>Sin cambios de pagina</small>}</div><div><span>Contenido compartido</span>{collections.length ? collections.map((collection) => <strong key={collection}>{collection}</strong>) : <small>Sin cambios compartidos</small>}</div><label className="field"><span>Mensaje de publicacion</span><input value={message} onChange={(event) => setMessage(event.target.value)} /></label><div className="modal-actions"><button className="secondary-command" disabled={busy} onClick={onClose}>Cancelar</button><button className="primary-command" disabled={busy} onClick={() => onPublish(message)}>{busy ? <LoaderCircle className="spin" /> : <CloudUpload />}<span>{busy ? "Publicando" : "Confirmar publicacion"}</span></button></div></div></Modal>;
}
