import { useEffect, useState } from "react";
import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Link from "@tiptap/extension-link";
import { Table } from "@tiptap/extension-table";
import TableRow from "@tiptap/extension-table-row";
import TableHeader from "@tiptap/extension-table-header";
import TableCell from "@tiptap/extension-table-cell";
import {
  Bold,
  Heading2,
  Heading3,
  Italic,
  Link2,
  List,
  ListOrdered,
  Minus,
  MoreHorizontal,
  Quote,
  Table2,
} from "lucide-react";

interface Props {
  value: string;
  onChange: (value: string) => void;
}

export function RichTextEditor({ value, onChange }: Props) {
  const [advanced, setAdvanced] = useState(false);
  const editor = useEditor({
    extensions: [
      StarterKit.configure({ link: false } as never),
      Link.configure({ openOnClick: false, autolink: true }),
      Table.configure({ resizable: false }),
      TableRow,
      TableHeader,
      TableCell,
    ],
    content: value,
    editorProps: {
      attributes: { class: "rich-editor-content" },
    },
    onUpdate: ({ editor: activeEditor }) => onChange(activeEditor.getHTML()),
    immediatelyRender: false,
  });

  useEffect(() => {
    if (editor?.isInitialized && !editor.isDestroyed && editor.getHTML() !== value) {
      editor.commands.setContent(value, { emitUpdate: false });
    }
  }, [editor, value]);

  if (!editor) return null;

  const setLink = () => {
    const current = editor.getAttributes("link").href as string | undefined;
    const href = window.prompt("URL del enlace", current ?? "https://");
    if (href === null) return;
    if (!href.trim()) editor.chain().focus().unsetLink().run();
    else editor.chain().focus().extendMarkRange("link").setLink({ href: href.trim() }).run();
  };

  const tool = (label: string, active: boolean, action: () => void, icon: React.ReactNode) => (
    <button
      type="button"
      className={active ? "rich-tool is-active" : "rich-tool"}
      aria-label={label}
      title={label}
      onClick={action}
    >
      {icon}
    </button>
  );

  return (
    <div className="rich-editor">
      <div className="rich-toolbar" aria-label="Formato de texto">
        {tool("Negrita", editor.isActive("bold"), () => editor.chain().focus().toggleBold().run(), <Bold />)}
        {tool("Cursiva", editor.isActive("italic"), () => editor.chain().focus().toggleItalic().run(), <Italic />)}
        {tool("Enlace", editor.isActive("link"), setLink, <Link2 />)}
        {tool("Lista", editor.isActive("bulletList"), () => editor.chain().focus().toggleBulletList().run(), <List />)}
        {tool(
          "Lista numerada",
          editor.isActive("orderedList"),
          () => editor.chain().focus().toggleOrderedList().run(),
          <ListOrdered />,
        )}
        <span className="toolbar-divider" />
        <button
          type="button"
          className={advanced ? "rich-tool is-active" : "rich-tool"}
          aria-label="Mas opciones de formato"
          title="Mas opciones de formato"
          onClick={() => setAdvanced((current) => !current)}
        >
          <MoreHorizontal />
        </button>
        {advanced && (
          <>
            {tool("Encabezado 2", editor.isActive("heading", { level: 2 }), () => editor.chain().focus().toggleHeading({ level: 2 }).run(), <Heading2 />)}
            {tool("Encabezado 3", editor.isActive("heading", { level: 3 }), () => editor.chain().focus().toggleHeading({ level: 3 }).run(), <Heading3 />)}
            {tool("Cita", editor.isActive("blockquote"), () => editor.chain().focus().toggleBlockquote().run(), <Quote />)}
            {tool("Insertar tabla", editor.isActive("table"), () => editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run(), <Table2 />)}
            {tool("Separador", false, () => editor.chain().focus().setHorizontalRule().run(), <Minus />)}
          </>
        )}
      </div>
      <EditorContent editor={editor} />
    </div>
  );
}
