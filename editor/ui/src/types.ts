export type JsonPrimitive = string | number | boolean | null;
export type JsonValue = JsonPrimitive | JsonValue[] | { [key: string]: JsonValue };
export type JsonRecord = { [key: string]: JsonValue };

export interface ActionItem {
  label: string;
  style?: string;
  page_id?: string;
  site_link?: string;
  url?: string;
  [key: string]: JsonValue | undefined;
}

export interface Section {
  id: string;
  type: string;
  visible: boolean;
  locked?: boolean;
  variant?: string;
  data: JsonRecord;
}

export interface SitePage {
  id: string;
  route: string;
  core_route?: boolean;
  title: string;
  description: string;
  social_image: string;
  hero_image: string;
  conference_page: boolean;
  show_in_navigation?: boolean;
  sections: Section[];
}

export interface NavigationItem extends JsonRecord {
  page_id: string;
  label: string;
}

export interface NavigationGroup extends JsonRecord {
  id: string;
  label: string;
  items: NavigationItem[];
}

export interface SiteSettings extends JsonRecord {
  name: string;
  language: string;
  public_url: string;
  navigation: {
    [key: string]: JsonValue;
    groups: NavigationGroup[];
    conference_subnav: string[];
  };
  links: Record<string, string>;
  conference: Record<string, string>;
}

export interface ContentBundle {
  schema_version: number;
  site: SiteSettings;
  collections: Record<string, JsonRecord[]>;
  pages: SitePage[];
}

export interface WorkspaceStatus {
  root: string;
  branch: string;
  head: string;
  dirty_paths: string[];
  draft: boolean;
  pending_uploads: number;
  pending_deletions: number;
  publish_remote?: string | null;
}

export interface SectionTemplate {
  type: string;
  label: string;
  description: string;
  variant?: string;
  data: JsonRecord;
}

export interface PageTemplateSection {
  type: string;
  variant?: string;
  data: JsonRecord;
}

export interface PageTemplate {
  id: string;
  label: string;
  description: string;
  sections: PageTemplateSection[];
}

export interface EditorEdition {
  id: "basic" | "advanced" | "unified";
  label: string;
  price_label: string;
  show_distinction: boolean;
  advanced_features: boolean;
}

export interface EditorEditionOption {
  id: "basic" | "advanced";
  label: string;
  price_label: string;
  features: string[];
}

export interface BootstrapData {
  repository: string;
  branch: string;
  suggested_workspace: string;
  workspace: WorkspaceStatus | null;
  credentials: { configured: boolean; persistent: boolean; method: "token" | "ssh" | "none" };
  edition: EditorEdition;
  edition_catalog: EditorEditionOption[];
  features: { custom_site: boolean };
  section_catalog: SectionTemplate[];
  page_catalog: PageTemplate[];
}

export interface LocalAuthStatus {
  configured: boolean;
  authenticated: boolean;
  can_setup: boolean;
}

export interface MediaItem {
  path: string;
  asset: string;
  kind: "image" | "document";
  name: string;
  pending: boolean;
  pending_delete?: boolean;
  width?: number;
  height?: number;
}

export interface DraftHistoryItem {
  id: string;
  saved_at: string;
  base_commit: string;
}

export interface PublishedHistoryItem {
  commit: string;
  date: string;
  message: string;
}

export type EditorMode = "pages" | "shared" | "media" | "history";
export type PreviewSize = "desktop" | "tablet" | "mobile";
