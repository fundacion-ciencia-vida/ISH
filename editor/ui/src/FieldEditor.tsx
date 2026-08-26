import { lazy, Suspense, useState, type ReactNode } from "react";
import { ChevronDown, ChevronUp, FileText, Image, Plus, Trash2 } from "lucide-react";
import { createId } from "./id";
import type { JsonRecord, JsonValue } from "./types";

const RichTextEditor = lazy(() => import("./RichTextEditor").then((module) => ({ default: module.RichTextEditor })));

interface Props {
  label: string;
  fieldKey: string;
  value: JsonValue;
  onChange: (value: JsonValue) => void;
  onChooseMedia?: (kind: "image" | "document", current: string, apply: (value: string) => void) => void;
  depth?: number;
  allowArrayStructure?: boolean;
}

const multilineKeys = new Set(["description", "lede", "heading", "introduction", "note", "caption", "affiliation", "historical_note", "questions", "agenda_note", "organizer"]);

const fieldLabels: Record<string, string> = {
  abstract_deadline: "Fecha limite de abstracts",
  abstract_label: "Texto del abstract",
  abstract_url: "Enlace del abstract",
  award: "Premio",
  award_nominations: "Formulario de nominaciones",
  award_nominations_deadline: "Cierre de nominaciones",
  award_archive: "Historial de premios",
  award_profiles: "Descripcion de premios",
  awards: "Premios",
  actions: "Botones y enlaces",
  address: "Direccion",
  address_label: "Etiqueta de direccion",
  affiliation: "Afiliacion",
  alt: "Texto alternativo",
  aria_label: "Etiqueta accesible",
  articles: "Articulos",
  board: "Consejo asesor",
  body_html: "Contenido",
  brand: "Marca",
  breadcrumbs: "Migas de navegacion",
  caption: "Pie de foto",
  category: "Categoria",
  category_detail: "Detalle de categoria",
  clp: "Pesos chilenos",
  clp_rate: "Tarifa en pesos chilenos",
  collection: "Coleccion",
  columns: "Columnas",
  committees: "Comites",
  communications: "Comunicaciones",
  conference: "Congreso",
  conference_field: "Dato del congreso",
  conference_page: "Pagina del congreso",
  contact_heading: "Titulo de contacto",
  contacts: "Contactos",
  conditions: "Condiciones",
  countdown_date: "Fecha de cuenta regresiva",
  country: "Pais",
  date: "Fecha",
  dates_label: "Texto de fechas",
  default_social_image: "Imagen predeterminada para redes",
  description: "Descripcion",
  detail: "Detalle",
  details: "Detalles",
  deadline: "Fecha limite",
  deadline_label: "Etiqueta de fecha limite",
  early_bird_deadline: "Fecha limite early bird",
  email: "Correo electronico",
  end_date: "Fecha de termino",
  eyebrow: "Antetitulo",
  event: "Datos del evento",
  event_date: "Fecha del evento",
  date_iso: "Fecha interna (AAAA-MM-DD)",
  date_label: "Fecha visible",
  duration: "Duracion",
  focal_x: "Encuadre horizontal (%)",
  focal_y: "Encuadre vertical (%)",
  featured: "Destacada",
  fellowship_application: "Formulario de fellowships",
  fellowship_deadline: "Cierre de fellowships",
  former_meetings: "Reuniones anteriores",
  footer: "Pie de pagina",
  group: "Grupo",
  groups: "Grupos",
  heading: "Titulo de seccion",
  hotels: "Hoteles y alojamiento",
  highlight: "Destacado",
  historical_note: "Nota historica",
  honorary: "Honorario",
  icon: "Icono",
  hero_image: "Imagen principal",
  image: "Imagen",
  image_alt: "Texto alternativo de imagen",
  items: "Elementos",
  introduction: "Introduccion",
  includes: "Incluye",
  label: "Etiqueta",
  language: "Idioma",
  lede: "Introduccion",
  line_1: "Linea 1",
  line_2: "Linea 2",
  link_label: "Texto del enlace",
  links: "Enlaces",
  location: "Ubicacion",
  location_carousel: "Carrusel de destino",
  logo: "Logo",
  map_url: "Enlace al mapa",
  name: "Nombre",
  navigation: "Navegacion",
  note: "Nota",
  number: "Numero",
  officer: "Cargo directivo",
  opportunity_grid: "Oportunidades",
  operator: "Operador",
  page_id: "Pagina de destino",
  paragraphs: "Parrafos",
  password: "Contrasena de acceso",
  platform: "Plataforma",
  presentation: "Presentacion",
  price: "Precio",
  price_basis: "Base de la tarifa",
  practical_tips: "Consejos practicos",
  public_url: "URL publica",
  published: "Publicada",
  registration: "Registro",
  rates: "Tarifas",
  rate_note: "Nota de tarifa",
  recipient: "Persona premiada",
  report_url: "Enlace del informe",
  role: "Cargo",
  route: "Ruta",
  routes: "Rutas",
  room: "Habitacion",
  rows: "Filas",
  questions: "Participacion y preguntas",
  social_image: "Imagen para redes sociales",
  speakers: "Conferencistas",
  sponsors: "Socios y auspiciadores",
  secondary_price: "Precio secundario",
  service_type: "Tipo de servicio",
  short_name: "Nombre corto",
  shortcuts: "Accesos directos",
  show_teasers: "Mostrar adelantos",
  site_heading: "Titulo del sitio",
  site_link: "Enlace compartido",
  start_date: "Fecha de inicio",
  steps: "Pasos",
  style: "Estilo",
  tag: "Etiqueta breve",
  title: "Titulo",
  time: "Horario",
  tracks: "Bloques de programa",
  tours: "Tours opcionales",
  transfers: "Traslados",
  travel_links: "Enlaces para el viaje",
  upcoming: "Proximo",
  url: "URL",
  usd: "Dolares indicados en la cotizacion",
  usd_rate: "Tarifa en dolares indicada en la cotizacion",
  value: "Valor",
  values: "Valores",
  venue: "Lugar",
  visible: "Visible",
  agenda_note: "Nota sobre la agenda",
  organizer: "Organiza",
  format: "Modalidad",
  workshop_date: "Fecha del workshop",
  workshop_name: "Nombre del workshop",
  year: "Ano",
  basis: "Base",
  booking_email: "Correo de reserva",
  booking_phone: "Telefono de reserva",
  booking_via: "Reserva mediante",
  distance: "Distancia",
  occupancy: "Ocupacion",
  phone: "Telefono",
  primary: "Opcion principal",
};

function CollapsibleRecord({
  title,
  initiallyOpen,
  controls,
  value,
  onChange,
  onChooseMedia,
  depth,
  allowArrayStructure,
}: {
  title: string;
  initiallyOpen: boolean;
  controls: ReactNode;
  value: JsonRecord;
  onChange: (value: JsonRecord) => void;
  onChooseMedia?: Props["onChooseMedia"];
  depth: number;
  allowArrayStructure: boolean;
}) {
  const [open, setOpen] = useState(initiallyOpen);
  return (
    <details className="array-object" open={open} onToggle={(event) => setOpen(event.currentTarget.open)}>
      <summary><span>{title}</span>{controls}</summary>
      {open && <RecordEditor value={value} onChange={onChange} onChooseMedia={onChooseMedia} depth={depth} allowArrayStructure={allowArrayStructure} />}
    </details>
  );
}

export function humanize(value: string) {
  if (fieldLabels[value]) return fieldLabels[value];
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
    .replace("Url", "URL")
    .replace("Id", "ID");
}

function blankValue(value: JsonValue): JsonValue {
  if (Array.isArray(value)) return [];
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value).map(([key, item]) => [
        key,
        key === "id" ? createId() : blankValue(item),
      ]),
    ) as JsonRecord;
  }
  if (typeof value === "boolean") return false;
  if (typeof value === "number") return 0;
  return "";
}

function defaultArrayItem(fieldKey: string): JsonValue {
  if (fieldKey === "actions") return { label: "New action", style: "primary", url: "" };
  if (fieldKey === "rows") return { category: "New row", category_detail: "", values: [""] };
  if (fieldKey === "columns") return { label: "New column", detail: "" };
  if (fieldKey === "items") {
    return { id: createId(), title: "New item", description: "", image: "", alt: "", caption: "" };
  }
  return "";
}

function mediaKind(key: string, current: string): "image" | "document" | null {
  const normalized = key.toLowerCase();
  if (normalized.includes("alt") || normalized.includes("caption") || normalized.endsWith("site_link")) return null;
  if (normalized === "image" || normalized === "images" || normalized.endsWith("_image") || normalized.includes("logo") || /\.(png|jpe?g|webp|avif)(\?.*)?$/i.test(current)) return "image";
  if (key.includes("document") || key.includes("pdf") || /\.pdf$/i.test(current)) return "document";
  return null;
}

export function FieldEditor({ label, fieldKey, value, onChange, onChooseMedia, depth = 0, allowArrayStructure = true }: Props) {
  if (fieldKey === "id" && depth > 0) {
    return <input type="hidden" value={String(value ?? "")} readOnly />;
  }

  if (typeof value === "boolean") {
    return (
      <label className="toggle-field">
        <span>{label}</span>
        <input type="checkbox" checked={value} onChange={(event) => onChange(event.target.checked)} />
        <span className="toggle-track" aria-hidden="true" />
      </label>
    );
  }

  if (typeof value === "number") {
    const percentage = fieldKey === "focal_x" || fieldKey === "focal_y";
    return (
      <label className="field">
        <span>{label}</span>
        <input type="number" min={percentage ? 0 : undefined} max={percentage ? 100 : undefined} value={value} onChange={(event) => onChange(Number(event.target.value))} />
      </label>
    );
  }

  if (typeof value === "string") {
    if (fieldKey.endsWith("_html")) {
      return (
        <div className="field rich-field">
          <span>{label}</span>
          <Suspense fallback={<div className="rich-editor-loading">Cargando editor...</div>}>
            <RichTextEditor value={value} onChange={onChange} />
          </Suspense>
        </div>
      );
    }
    const kind = mediaKind(fieldKey, value);
    const isLong = multilineKeys.has(fieldKey) || value.length > 110;
    return (
      <label className="field">
        <span>{label}</span>
        <div className={kind ? "input-with-action" : undefined}>
          {isLong ? (
            <textarea rows={Math.min(8, Math.max(3, Math.ceil(value.length / 65)))} value={value} onChange={(event) => onChange(event.target.value)} />
          ) : (
            <input value={value} onChange={(event) => onChange(event.target.value)} />
          )}
          {kind && onChooseMedia && (
            <button
              type="button"
              className="icon-button inset-action"
              title={kind === "image" ? "Elegir imagen" : "Elegir documento"}
              aria-label={kind === "image" ? "Elegir imagen" : "Elegir documento"}
              onClick={() => onChooseMedia(kind, value, (next) => onChange(next))}
            >
              {kind === "image" ? <Image /> : <FileText />}
            </button>
          )}
        </div>
      </label>
    );
  }

  if (Array.isArray(value)) {
    const template: JsonValue = value[0] ?? defaultArrayItem(fieldKey);
    return (
      <div className="array-field">
        <div className="array-heading">
          <span>{label}</span>
          {allowArrayStructure && <button
            type="button"
            className="icon-button"
            aria-label={`Agregar a ${label}`}
            title={`Agregar a ${label}`}
            onClick={(event) => {
              const field = event.currentTarget.closest(".array-field");
              onChange([...value, blankValue(template)]);
              window.requestAnimationFrame(() => {
                const items = field?.querySelector(":scope > .array-items");
                const target = items?.lastElementChild;
                if (target instanceof HTMLDetailsElement) target.open = true;
                target?.scrollIntoView({ block: "nearest" });
                target?.querySelector<HTMLElement>("input:not([type='hidden']), textarea, select")?.focus({ preventScroll: true });
              });
            }}
          >
            <Plus />
          </button>}
        </div>
        <div className="array-items">
          {value.map((item, index) => {
            const update = (next: JsonValue) => onChange(value.map((candidate, candidateIndex) => (candidateIndex === index ? next : candidate)));
            const controls = allowArrayStructure ? (
              <div className="row-controls">
                <button type="button" className="icon-button" disabled={index === 0} title="Subir" aria-label="Subir" onClick={() => {
                  const next = [...value];
                  [next[index - 1], next[index]] = [next[index], next[index - 1]];
                  onChange(next);
                }}><ChevronUp /></button>
                <button type="button" className="icon-button" disabled={index === value.length - 1} title="Bajar" aria-label="Bajar" onClick={() => {
                  const next = [...value];
                  [next[index + 1], next[index]] = [next[index], next[index + 1]];
                  onChange(next);
                }}><ChevronDown /></button>
                <button type="button" className="icon-button danger" title="Eliminar" aria-label="Eliminar" onClick={() => onChange(value.filter((_, candidateIndex) => candidateIndex !== index))}><Trash2 /></button>
              </div>
            ) : null;
            if (item && typeof item === "object" && !Array.isArray(item)) {
              const title = String((item as JsonRecord).title ?? (item as JsonRecord).name ?? (item as JsonRecord).label ?? `${label} ${index + 1}`);
              return (
                <CollapsibleRecord
                  key={`${title}-${index}`}
                  title={title || `${label} ${index + 1}`}
                  initiallyOpen={value.length <= 2}
                  controls={controls}
                  value={item as JsonRecord}
                  onChange={update}
                  onChooseMedia={onChooseMedia}
                  depth={depth + 1}
                  allowArrayStructure={allowArrayStructure}
                />
              );
            }
            return (
              <div className="array-row" key={index}>
                <FieldEditor label={`${label} ${index + 1}`} fieldKey={fieldKey} value={item} onChange={update} onChooseMedia={onChooseMedia} depth={depth + 1} allowArrayStructure={allowArrayStructure} />
                {controls}
              </div>
            );
          })}
          {!value.length && <p className="empty-inline">Sin elementos.</p>}
        </div>
      </div>
    );
  }

  if (value && typeof value === "object") {
    return (
      <fieldset className="record-fieldset">
        <legend>{label}</legend>
        <RecordEditor value={value as JsonRecord} onChange={onChange} onChooseMedia={onChooseMedia} depth={depth + 1} allowArrayStructure={allowArrayStructure} />
      </fieldset>
    );
  }

  return null;
}

interface RecordProps {
  value: JsonRecord;
  onChange: (value: JsonRecord) => void;
  onChooseMedia?: Props["onChooseMedia"];
  depth?: number;
  allowArrayStructure?: boolean;
}

export function RecordEditor({ value, onChange, onChooseMedia, depth = 0, allowArrayStructure = true }: RecordProps) {
  return (
    <div className="record-editor">
      {Object.entries(value).map(([key, item]) => (
        <FieldEditor
          key={key}
          label={humanize(key)}
          fieldKey={key}
          value={item}
          onChange={(next) => onChange({ ...value, [key]: next })}
          onChooseMedia={onChooseMedia}
          depth={depth}
          allowArrayStructure={allowArrayStructure}
        />
      ))}
    </div>
  );
}
