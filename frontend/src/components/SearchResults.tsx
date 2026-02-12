"use client";

import CadViewer from "./CadViewer";

interface SearchResult {
  id: number;
  filename: string;
  vertex_count: number | null;
  face_count: number | null;
  similarity: number;
  created_at: string | null;
}

interface SearchResultsProps {
  results: SearchResult[];
}

export default function SearchResults({ results }: SearchResultsProps) {
  if (results.length === 0) {
    return (
      <div className="bg-[var(--card-bg)] border border-[var(--border)] rounded-xl p-8 text-center">
        <p className="text-sm opacity-60">類似モデルが見つかりませんでした</p>
      </div>
    );
  }

  return (
    <div className="bg-[var(--card-bg)] border border-[var(--border)] rounded-xl p-4">
      <h3 className="text-lg font-semibold mb-4">
        検索結果 ({results.length}件)
      </h3>
      <div className="space-y-4 max-h-[700px] overflow-y-auto">
        {results.map((result, index) => (
          <div
            key={result.id}
            className="border border-[var(--border)] rounded-lg overflow-hidden"
          >
            <div className="h-48">
              <CadViewer
                fileUrl={`/api/models/${result.id}/file`}
                fileName={result.filename}
              />
            </div>
            <div className="p-3 space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-medium text-sm truncate">
                  #{index + 1} {result.filename}
                </span>
                <span
                  className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                    result.similarity >= 0.8
                      ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300"
                      : result.similarity >= 0.5
                        ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300"
                        : "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300"
                  }`}
                >
                  {(result.similarity * 100).toFixed(1)}%
                </span>
              </div>
              <div className="text-xs opacity-50">
                頂点数: {result.vertex_count?.toLocaleString() ?? "-"} / 面数:{" "}
                {result.face_count?.toLocaleString() ?? "-"}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
