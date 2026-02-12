"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Grid } from "@react-three/drei";
import * as THREE from "three";
import { STLLoader } from "three/examples/jsm/loaders/STLLoader.js";
import { OBJLoader } from "three/examples/jsm/loaders/OBJLoader.js";

interface CadViewerProps {
  fileBuffer?: ArrayBuffer;
  fileUrl?: string;
  fileName: string;
}

function MeshObject({
  geometry,
  wireframe,
}: {
  geometry: THREE.BufferGeometry;
  wireframe: boolean;
}) {
  const meshRef = useRef<THREE.Mesh>(null);

  // Center and normalize the geometry
  const normalizedGeometry = useMemo(() => {
    const geo = geometry.clone();
    geo.computeBoundingBox();
    const box = geo.boundingBox!;
    const center = new THREE.Vector3();
    box.getCenter(center);
    geo.translate(-center.x, -center.y, -center.z);

    const size = new THREE.Vector3();
    box.getSize(size);
    const maxDim = Math.max(size.x, size.y, size.z);
    if (maxDim > 0) {
      const scale = 2 / maxDim;
      geo.scale(scale, scale, scale);
    }

    geo.computeVertexNormals();
    return geo;
  }, [geometry]);

  return (
    <mesh ref={meshRef} geometry={normalizedGeometry}>
      <meshStandardMaterial
        color="#6b9eff"
        wireframe={wireframe}
        side={THREE.DoubleSide}
        flatShading
      />
    </mesh>
  );
}

function SceneContent({
  geometry,
  wireframe,
}: {
  geometry: THREE.BufferGeometry;
  wireframe: boolean;
}) {
  return (
    <>
      <ambientLight intensity={0.4} />
      <directionalLight position={[5, 5, 5]} intensity={0.8} />
      <directionalLight position={[-5, -3, -5]} intensity={0.3} />
      <MeshObject geometry={geometry} wireframe={wireframe} />
      <Grid
        args={[10, 10]}
        position={[0, -1.5, 0]}
        cellSize={0.5}
        cellColor="#888888"
        sectionSize={2}
        sectionColor="#666666"
        fadeDistance={10}
        fadeStrength={1}
      />
      <OrbitControls makeDefault enableDamping dampingFactor={0.1} />
    </>
  );
}

export default function CadViewer({ fileBuffer, fileUrl, fileName }: CadViewerProps) {
  const [geometry, setGeometry] = useState<THREE.BufferGeometry | null>(null);
  const [wireframe, setWireframe] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadGeometry = async () => {
      try {
        setError(null);
        let buffer = fileBuffer;

        if (!buffer && fileUrl) {
          const res = await fetch(fileUrl);
          buffer = await res.arrayBuffer();
        }

        if (!buffer) return;

        const ext = fileName.toLowerCase().split(".").pop();

        if (ext === "stl") {
          const loader = new STLLoader();
          const geo = loader.parse(buffer);
          setGeometry(geo);
        } else if (ext === "obj") {
          const loader = new OBJLoader();
          const text = new TextDecoder().decode(buffer);
          const group = loader.parse(text);
          // Merge all geometries from the OBJ
          const geometries: THREE.BufferGeometry[] = [];
          group.traverse((child) => {
            if (child instanceof THREE.Mesh && child.geometry) {
              geometries.push(child.geometry);
            }
          });
          if (geometries.length > 0) {
            const merged =
              geometries.length === 1
                ? geometries[0]
                : mergeBufferGeometries(geometries);
            if (merged) setGeometry(merged);
            else setError("メッシュの読み込みに失敗しました");
          } else {
            setError("有効なメッシュが含まれていません");
          }
        } else {
          setError(`未対応のファイル形式: .${ext}`);
        }
      } catch (err) {
        setError(
          `ファイル読み込みエラー: ${err instanceof Error ? err.message : "Unknown"}`
        );
      }
    };

    loadGeometry();
  }, [fileBuffer, fileUrl, fileName]);

  if (error) {
    return (
      <div className="flex items-center justify-center h-full bg-[var(--accent)] text-sm opacity-60">
        {error}
      </div>
    );
  }

  if (!geometry) {
    return (
      <div className="flex items-center justify-center h-full bg-[var(--accent)] text-sm opacity-60">
        読み込み中...
      </div>
    );
  }

  return (
    <div className="relative w-full h-full">
      <Canvas camera={{ position: [3, 2, 3], fov: 45 }}>
        <SceneContent geometry={geometry} wireframe={wireframe} />
      </Canvas>
      <button
        onClick={() => setWireframe((prev) => !prev)}
        className="absolute top-2 right-2 px-3 py-1 text-xs bg-[var(--card-bg)] border border-[var(--border)] rounded-md opacity-80 hover:opacity-100 transition-opacity"
      >
        {wireframe ? "ソリッド" : "ワイヤーフレーム"}
      </button>
    </div>
  );
}

function mergeBufferGeometries(
  geometries: THREE.BufferGeometry[]
): THREE.BufferGeometry | null {
  if (geometries.length === 0) return null;
  if (geometries.length === 1) return geometries[0];

  // Simple merge: combine all positions and indices
  const positions: number[] = [];
  const normals: number[] = [];
  let indexOffset = 0;
  const indices: number[] = [];

  for (const geo of geometries) {
    const pos = geo.getAttribute("position");
    if (!pos) continue;

    for (let i = 0; i < pos.count; i++) {
      positions.push(pos.getX(i), pos.getY(i), pos.getZ(i));
    }

    const norm = geo.getAttribute("normal");
    if (norm) {
      for (let i = 0; i < norm.count; i++) {
        normals.push(norm.getX(i), norm.getY(i), norm.getZ(i));
      }
    }

    const idx = geo.getIndex();
    if (idx) {
      for (let i = 0; i < idx.count; i++) {
        indices.push((idx.array as unknown as number[])[i] + indexOffset);
      }
    }

    indexOffset += pos.count;
  }

  const merged = new THREE.BufferGeometry();
  merged.setAttribute(
    "position",
    new THREE.Float32BufferAttribute(positions, 3)
  );
  if (normals.length > 0) {
    merged.setAttribute(
      "normal",
      new THREE.Float32BufferAttribute(normals, 3)
    );
  }
  if (indices.length > 0) {
    merged.setIndex(indices);
  }

  return merged;
}
