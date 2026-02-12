"use client";

import { useCallback, useEffect, useState } from "react";
import CadUploader from "@/components/CadUploader";
import CadViewer from "@/components/CadViewer";
import SearchResults from "@/components/SearchResults";
import CadCard from "@/components/CadCard";

type Mode = "register" | "search";

interface CadModel {
  id: number;
  filename: string;
  vertex_count: number | null;
  face_count: number | null;
  created_at: string | null;
}

interface SearchResult extends CadModel {
  similarity: number;
}

export default function Home() {
  const [mode, setMode] = useState<Mode>("search");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileBuffer, setFileBuffer] = useState<ArrayBuffer | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [messageType, setMessageType] = useState<"success" | "error">("success");
  const [searchResults, setSearchResults] = useState<SearchResult[] | null>(null);
  const [registeredModels, setRegisteredModels] = useState<CadModel[]>([]);

  const fetchModels = useCallback(async () => {
    try {
      const res = await fetch("/api/models");
      if (res.ok) {
        const data = await res.json();
        setRegisteredModels(data);
      }
    } catch {
      // Silently fail
    }
  }, []);

  useEffect(() => {
    fetchModels();
  }, [fetchModels]);

  const handleFileSelect = useCallback((file: File) => {
    setSelectedFile(file);
    setSearchResults(null);
    setMessage(null);
    const reader = new FileReader();
    reader.onload = () => {
      setFileBuffer(reader.result as ArrayBuffer);
    };
    reader.readAsArrayBuffer(file);
  }, []);

  const handleRegister = useCallback(async () => {
    if (!selectedFile) return;
    setIsLoading(true);
    setMessage(null);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const res = await fetch("/api/upload", { method: "POST", body: formData });
      const data = await res.json();
      if (res.ok) {
        setMessage(`登録完了: ${data.filename} (ID: ${data.id})`);
        setMessageType("success");
        setSelectedFile(null);
        setFileBuffer(null);
        fetchModels();
      } else {
        setMessage(`エラー: ${data.detail}`);
        setMessageType("error");
      }
    } catch (err) {
      setMessage(`通信エラー: ${err instanceof Error ? err.message : "Unknown error"}`);
      setMessageType("error");
    } finally {
      setIsLoading(false);
    }
  }, [selectedFile, fetchModels]);

  const handleSearch = useCallback(async () => {
    if (!selectedFile) return;
    setIsLoading(true);
    setMessage(null);
    setSearchResults(null);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const res = await fetch("/api/search", { method: "POST", body: formData });
      const data = await res.json();
      if (res.ok) {
        setSearchResults(data.results);
        if (data.results.length === 0) {
          setMessage("類似モデルが見つかりませんでした");
          setMessageType("success");
        }
      } else {
        setMessage(`エラー: ${data.detail}`);
        setMessageType("error");
      }
    } catch (err) {
      setMessage(`通信エラー: ${err instanceof Error ? err.message : "Unknown error"}`);
      setMessageType("error");
    } finally {
      setIsLoading(false);
    }
  }, [selectedFile]);

  const handleDelete = useCallback(
    async (id: number) => {
      try {
        const res = await fetch(`/api/models/${id}`, { method: "DELETE" });
        if (res.ok) {
          fetchModels();
          setMessage("モデルを削除しました");
          setMessageType("success");
        }
      } catch {
        setMessage("削除に失敗しました");
        setMessageType("error");
      }
    },
    [fetchModels]
  );

  return (
    <main className="min-h-screen p-6 max-w-7xl mx-auto">
      <header className="mb-8">
        <h1 className="text-3xl font-bold mb-2">CAD 類似形状検索</h1>
        <p className="text-[var(--foreground)] opacity-60">
          CADデータ（STL/OBJ）をアップロードして、類似形状を検索します
        </p>
      </header>

      {/* Mode Tabs */}
      <div className="flex gap-1 mb-6 bg-[var(--accent)] rounded-lg p-1 w-fit">
        <button
          onClick={() => {
            setMode("search");
            setMessage(null);
          }}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            mode === "search"
              ? "bg-[var(--primary)] text-white"
              : "hover:bg-[var(--border)]"
          }`}
        >
          類似検索
        </button>
        <button
          onClick={() => {
            setMode("register");
            setMessage(null);
          }}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            mode === "register"
              ? "bg-[var(--primary)] text-white"
              : "hover:bg-[var(--border)]"
          }`}
        >
          データ登録
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Upload + Preview */}
        <div className="space-y-4">
          <CadUploader onFileSelect={handleFileSelect} />

          {fileBuffer && selectedFile && (
            <div className="bg-[var(--card-bg)] border border-[var(--border)] rounded-xl p-4">
              <h3 className="text-sm font-medium mb-2 opacity-70">
                プレビュー: {selectedFile.name}
              </h3>
              <div className="h-80 rounded-lg overflow-hidden border border-[var(--border)]">
                <CadViewer
                  fileBuffer={fileBuffer}
                  fileName={selectedFile.name}
                />
              </div>
              <div className="mt-4 flex gap-3">
                {mode === "register" ? (
                  <button
                    onClick={handleRegister}
                    disabled={isLoading}
                    className="px-6 py-2.5 bg-[var(--primary)] text-white rounded-lg font-medium hover:bg-[var(--primary-hover)] disabled:opacity-50 transition-colors"
                  >
                    {isLoading ? "処理中..." : "登録する"}
                  </button>
                ) : (
                  <button
                    onClick={handleSearch}
                    disabled={isLoading}
                    className="px-6 py-2.5 bg-[var(--primary)] text-white rounded-lg font-medium hover:bg-[var(--primary-hover)] disabled:opacity-50 transition-colors"
                  >
                    {isLoading ? "検索中..." : "類似検索"}
                  </button>
                )}
              </div>
            </div>
          )}

          {message && (
            <div
              className={`p-4 rounded-lg text-sm ${
                messageType === "success"
                  ? "bg-green-50 text-green-800 border border-green-200 dark:bg-green-900/20 dark:text-green-300 dark:border-green-800"
                  : "bg-red-50 text-red-800 border border-red-200 dark:bg-red-900/20 dark:text-red-300 dark:border-red-800"
              }`}
            >
              {message}
            </div>
          )}
        </div>

        {/* Right: Results or Model List */}
        <div>
          {mode === "search" && searchResults ? (
            <SearchResults results={searchResults} />
          ) : (
            <div className="bg-[var(--card-bg)] border border-[var(--border)] rounded-xl p-4">
              <h3 className="text-lg font-semibold mb-4">
                登録済みモデル ({registeredModels.length})
              </h3>
              {registeredModels.length === 0 ? (
                <p className="text-sm opacity-60 py-8 text-center">
                  モデルが登録されていません
                </p>
              ) : (
                <div className="space-y-3 max-h-[600px] overflow-y-auto">
                  {registeredModels.map((model) => (
                    <CadCard
                      key={model.id}
                      model={model}
                      onDelete={handleDelete}
                    />
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
