"use client";

interface CadModel {
  id: number;
  filename: string;
  vertex_count: number | null;
  face_count: number | null;
  created_at: string | null;
}

interface CadCardProps {
  model: CadModel;
  onDelete?: (id: number) => void;
}

export default function CadCard({ model, onDelete }: CadCardProps) {
  return (
    <div className="flex items-center justify-between p-3 border border-[var(--border)] rounded-lg hover:bg-[var(--accent)] transition-colors">
      <div className="flex-1 min-w-0">
        <p className="font-medium text-sm truncate">{model.filename}</p>
        <div className="flex gap-3 text-xs opacity-50 mt-1">
          <span>ID: {model.id}</span>
          <span>頂点: {model.vertex_count?.toLocaleString() ?? "-"}</span>
          <span>面: {model.face_count?.toLocaleString() ?? "-"}</span>
          {model.created_at && (
            <span>{new Date(model.created_at).toLocaleDateString("ja-JP")}</span>
          )}
        </div>
      </div>
      <div className="flex gap-2 ml-3">
        <a
          href={`/api/models/${model.id}/file`}
          download={model.filename}
          className="px-3 py-1 text-xs border border-[var(--border)] rounded-md hover:bg-[var(--accent)] transition-colors"
        >
          DL
        </a>
        {onDelete && (
          <button
            onClick={() => {
              if (confirm(`「${model.filename}」を削除しますか？`)) {
                onDelete(model.id);
              }
            }}
            className="px-3 py-1 text-xs text-red-600 border border-red-200 rounded-md hover:bg-red-50 dark:text-red-400 dark:border-red-800 dark:hover:bg-red-900/20 transition-colors"
          >
            削除
          </button>
        )}
      </div>
    </div>
  );
}
