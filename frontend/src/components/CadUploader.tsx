"use client";

import { useCallback, useRef, useState } from "react";

interface CadUploaderProps {
  onFileSelect: (file: File) => void;
}

const ALLOWED_EXTENSIONS = [".stl", ".obj"];

export default function CadUploader({ onFileSelect }: CadUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const isValidFile = (file: File): boolean => {
    const ext = file.name.toLowerCase().slice(file.name.lastIndexOf("."));
    return ALLOWED_EXTENSIONS.includes(ext);
  };

  const handleFile = useCallback(
    (file: File) => {
      if (isValidFile(file)) {
        onFileSelect(file);
      } else {
        alert("対応していないファイル形式です。STL または OBJ ファイルを選択してください。");
      }
    },
    [onFileSelect]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFile(file);
      // Reset input so same file can be re-selected
      if (inputRef.current) inputRef.current.value = "";
    },
    [handleFile]
  );

  return (
    <div
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onClick={() => inputRef.current?.click()}
      className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
        isDragging
          ? "border-[var(--primary)] bg-blue-50 dark:bg-blue-900/20"
          : "border-[var(--border)] hover:border-[var(--primary)] hover:bg-[var(--accent)]"
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".stl,.obj"
        onChange={handleInputChange}
        className="hidden"
      />
      <div className="space-y-2">
        <div className="text-4xl opacity-40">&#9651;</div>
        <p className="font-medium">CADファイルをドラッグ＆ドロップ</p>
        <p className="text-sm opacity-60">
          またはクリックしてファイルを選択（STL / OBJ）
        </p>
        <p className="text-xs opacity-40">最大 50MB</p>
      </div>
    </div>
  );
}
