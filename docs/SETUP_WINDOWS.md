# Windows + Docker Desktop 環境セットアップ手順

本書は、Windows PC（Docker Desktop インストール済み）で本プロジェクト（Next.js フロントエンド + Python FastAPI バックエンド + PostgreSQL/pgvector）を起動し、**自社 CAD データを登録して類似検索の精度を評価する**までの手順をまとめたものです。

> Windows スタンドアロンのデモ版（`demo/` 配下）とは別構成です。デモ版は検索専用でデータ登録ができないため、精度評価用途では本構成（フルスタック）を使用します。

---

## 0. 前提条件

相手 PC に以下がインストールされていること。

| 必要ソフト | 推奨バージョン | 確認コマンド（PowerShell） |
|-----------|---------------|--------------------------|
| Docker Desktop for Windows | 最新（WSL2 バックエンド有効） | `docker --version` / `docker compose version` |
| Node.js | 18 以上（LTS 推奨、20 系がベター） | `node --version` / `npm --version` |
| Git | 任意のバージョン | `git --version` |

> **未インストールの場合**: これら 3 つのソフトのダウンロードから Windows へのインストール手順は、[`INSTALL_PREREQUISITES_WINDOWS.md`](./INSTALL_PREREQUISITES_WINDOWS.md) にまとめています。まずそちらを完了してから本書の手順 1 以降に進んでください。

**ディスク容量の目安**: 約 5GB（Docker イメージ + PyTorch を含む）。

**メモリの目安**: 8GB 以上推奨。Docker Desktop に 4GB 以上を割り当てること（`Settings > Resources`）。

### ポート使用状況の事前確認

本プロジェクトは **デフォルトで以下 3 ポートを使用**します。以下のコマンドを実行し、すべて**何も表示されない（=空いている）**ことを確認してください。

| ポート | 用途 |
|-------|------|
| 3000 | フロントエンド (Next.js) |
| 8000 | バックエンド (FastAPI) |
| 5432 | PostgreSQL |

```powershell
netstat -ano | findstr :3000
netstat -ano | findstr :8000
netstat -ano | findstr :5432
```

**いずれかのポートが使用中だった場合に限り**、手順 2 で `.env` によるポート変更を行います。すべて空いていればポート変更は不要です。

---

## 1. ソースコード取得

任意の作業ディレクトリで clone します。

```powershell
cd C:\work
git clone <リポジトリURL> shape-based-retrieval
cd shape-based-retrieval
```

---

## 2. 環境変数ファイルの作成

```powershell
copy .env.example .env
```

> **通常はこのまま `.env` を編集する必要はありません。** デフォルトで フロントエンド `3000` / バックエンド `8000` / DB `5432` を使用します。以下の「ポート変更」セクションは、**手順 0 のポート事前確認で競合が見つかった場合のみ**実施してください。

### ポート変更（競合時のみ）

**上記の事前確認でポート競合がなかった場合、このセクションはスキップしてください。**

競合していた場合に限り、`.env` をエディタで開いて、競合しているポートのみを変更します。例：`8000` が他プロセスに使われていた場合：

```
BACKEND_PORT=8001
DB_PORT=5433
```

**重要**: `BACKEND_PORT` を変更した場合は、**フロントエンド側にも必ず同じ値を設定**します。`frontend/.env.local` を新規作成：

```
BACKEND_PORT=8001
```

> `frontend/.env.local` を作らないと、フロントエンドの API プロキシがデフォルトの `8000` を参照してしまい、接続できません。
>
> 以降の手順で出てくる `http://localhost:8000/...` は、ポート変更した場合は読み替えてください（例: `http://localhost:8001/...`）。

---

## 3. Docker コンテナ起動（バックエンド + DB）

Docker Desktop を起動した状態で、プロジェクトルートで実行：

```powershell
docker compose up -d --build
```

初回は PyTorch 等のインストールで **5〜10 分**かかります（回線状況により変動）。

### 起動確認

```powershell
docker compose ps
```

`cad-search-db` が `healthy`、`cad-search-backend` が `Up` であれば OK。

```powershell
curl http://localhost:8000/api/health
# => {"status":"ok","database":"connected"}
```

> `BACKEND_PORT` を変更した場合は、URL のポート部分を合わせてください（以降の例も同様）。

---

## 4. 初期サンプルデータの扱い

**検索精度評価が目的の場合は、付属のサンプル投入はスキップしてください。** 本プロジェクトに付属する 32 個の基本形状（立方体・球・円柱など）は動作確認用のダミーデータで、評価対象の社内 CAD と混ざるとノイズになります。

デモ目的で投入したい場合のみ：

```powershell
docker compose exec backend python scripts/seed_data.py
```

---

## 5. 自社 CAD データの登録

### 方法 A: ブラウザ UI から 1 件ずつ登録（少量向け）

後述のフロントエンド起動後、ブラウザの「データ登録」タブから STL / OBJ ファイルをアップロードします。

### 方法 B: PowerShell で一括登録（大量向け・推奨）

登録したい CAD ファイルを 1 つのディレクトリに集約し、以下のように一括 POST します。

```powershell
# 例: C:\cad_samples\ 配下の全 STL / OBJ を登録
Get-ChildItem -Path C:\cad_samples -Include *.stl,*.obj -Recurse | ForEach-Object {
    Write-Host "Uploading: $($_.Name)"
    curl.exe -X POST `
        -F "file=@$($_.FullName)" `
        http://localhost:8000/api/upload
}
```

### 登録結果の確認

```powershell
curl http://localhost:8000/api/models
```

登録件数が期待通りであることを確認します。

### 対応ファイル形式

- STL（バイナリ / ASCII）
- OBJ

> STEP / IGES は未対応です。CAD ソフト（Fusion360 / SolidWorks / FreeCAD 等）で STL にエクスポートしてから登録してください。

---

## 6. フロントエンド起動

**新しい PowerShell ウィンドウ**を開いて実行：

```powershell
cd C:\work\shape-based-retrieval\frontend
npm install
npm run dev
```

- `npm install` は初回のみ（3〜5 分）。
- `Ready in XXXms` が表示されたら起動完了。

---

## 7. ブラウザでアクセス

http://localhost:3000 を開きます。

- **類似検索タブ** — クエリにする CAD ファイルをアップロードし、「類似検索」ボタンで類似度スコア付きランキングを表示。
- **データ登録タブ** — 個別ファイルの追加登録。
- **3D プレビュー** — 回転・ズーム・ワイヤーフレーム切替で形状を目視確認。

精度評価では、「想定通りの類似品が上位に来るか」「別カテゴリのものが誤ってヒットしていないか」を確認します。

---

## 8. 停止・再起動

### 停止（登録データは保持）

```powershell
docker compose down
```

フロントエンドは起動中のコンソールで `Ctrl+C`。

### 次回起動（ビルド不要）

```powershell
docker compose up -d
cd frontend
npm run dev
```

### データごと完全リセット（登録した CAD も消える）

```powershell
docker compose down -v
```

> `-v` はボリューム削除オプションです。PostgreSQL のデータと登録ファイルが失われるため、本番評価中は使用しないこと。

---

## 9. よくあるトラブルと対処

| 症状 | 原因 | 対処 |
|------|------|------|
| `docker compose up` が途中で止まる / OOM で終了 | Docker Desktop のメモリ不足 | `Settings > Resources` でメモリを 4GB 以上に増やす |
| `port is already allocated` | ポート競合 | `.env` で `BACKEND_PORT` / `DB_PORT` を変更し、`frontend/.env.local` も合わせる |
| フロントは開くが検索で 502/500 エラー | バックエンド未起動またはポート不一致 | `docker compose logs backend` でログ確認、`frontend/.env.local` の値を確認 |
| STL 登録で `mesh parse error` | ファイル破損、または対応外形式（STEP / IGES） | STL / OBJ に変換してから登録 |
| `npm install` が失敗 | Node.js バージョンが古い | Node.js 18 以上にアップデート |
| Docker ビルドで pip が極端に遅い | プロキシ環境 | Docker Desktop の `Settings > Resources > Proxies` を設定 |
| `docker compose exec` でバックエンドに入れない | コンテナ未起動 | `docker compose ps` で `Up` になっているか確認、再起動 |

---

## 10. ログ確認

問題切り分け用のログ取得コマンド。

```powershell
# バックエンドのログ（直近 100 行）
docker compose logs --tail 100 backend

# DB のログ
docker compose logs --tail 100 db

# リアルタイムで追尾
docker compose logs -f backend
```

---

## 11. 成果物チェックリスト（配布側）

相手先に渡す前に以下を確認：

- [ ] リポジトリ URL（または zip 一式）を共有
- [ ] 本手順書（`docs/SETUP_WINDOWS.md`）が含まれていること
- [ ] 評価用の社内 CAD データ（STL / OBJ に変換済み）
- [ ] 対応拡張子が **STL / OBJ のみ**であることを明記済み
- [ ] 相手環境のスペック確認（メモリ 8GB 以上、空きディスク 5GB 以上）

---

## 参考: アーキテクチャ概要

```
[Next.js フロントエンド]  ← npm run dev （localhost:3000）
        │
        │  REST API (HTTP、Next.js rewrite で /api/* をバックエンドへプロキシ)
        ▼
[Python FastAPI バックエンド]  ← Docker コンテナ (localhost:8000)
        │
        ▼
[PostgreSQL + pgvector]  ← Docker コンテナ (localhost:5432)
```

特徴抽出: CAD → trimesh で読み込み → 正規化 → 2,048 点サンプリング → PointNet で 256 次元ベクトル → pgvector でコサイン距離検索。
