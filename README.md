# CAD 類似形状検索アプリ

CADデータ（STL/OBJ）をアップロードし、データベースに登録済みの3Dモデルの中から**形状が似ているものを自動で検索・ランキング表示**するWebアプリケーションです。

## 主な機能

- **類似形状検索** — CADファイルをアップロードするだけで、類似度スコア付きで類似モデルを一覧表示
- **3Dプレビュー** — ブラウザ上でCADデータを3D表示（回転・ズーム・ワイヤーフレーム切替）
- **データ登録・管理** — CADファイルの登録・一覧・削除・ダウンロード

## アーキテクチャ

```
[Next.js フロントエンド]  ←  ローカル実行 (localhost:3000)
        │
        │  REST API (HTTP)
        ▼
[Python FastAPI バックエンド]  ←  Docker コンテナ (localhost:8000)
        │
        ▼
[PostgreSQL + pgvector]  ←  Docker コンテナ (localhost:5432)
```

### 技術スタック

| レイヤー | 技術 |
|---------|------|
| フロントエンド | Next.js 16 (App Router) / TypeScript / Tailwind CSS / Three.js (@react-three/fiber) |
| バックエンド | Python 3.11 / FastAPI / trimesh / PyTorch (PointNet) |
| データベース | PostgreSQL 16 + pgvector（ベクトル類似検索） |
| インフラ | Docker Compose |

### 特徴抽出パイプライン

```
CADファイル (STL/OBJ)
  → メッシュ読み込み (trimesh)
  → 正規化 (原点中心 + 単位球スケーリング)
  → 点群サンプリング (2,048点)
  → PointNet (256次元 特徴ベクトル)
  → pgvector コサイン距離検索
```

## 必要環境

- **Docker** & **Docker Compose**
- **Node.js** 18+
- ディスク容量: 約5GB（Docker イメージ含む）

## セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/<your-username>/shape-based-retrieval.git
cd shape-based-retrieval
```

### 2. 環境変数の設定

```bash
cp .env.example .env
```

> ポートが競合する場合は `.env` 内の `BACKEND_PORT` / `DB_PORT` をコメント解除して変更してください。

### 3. Docker コンテナ起動（バックエンド + DB）

```bash
docker compose up -d
```

初回はイメージのビルドに時間がかかります（PyTorch のインストールのため約5〜10分）。

起動確認:

```bash
curl http://localhost:8000/api/health
# => {"status":"ok","database":"connected"}
```

### 4. サンプルデータ投入

```bash
docker compose exec backend python scripts/seed_data.py
```

32個のサンプル形状（立方体・球・円柱・円錐・トーラス・複合形状）が自動生成・登録されます。

### 5. フロントエンド起動

```bash
cd frontend
npm install
npm run dev
```

### 6. ブラウザでアクセス

http://localhost:3000 を開きます。

## 使い方

### 類似検索

1. 「類似検索」タブを選択
2. STL / OBJ ファイルをドラッグ＆ドロップ（またはクリックして選択）
3. 3Dプレビューで確認
4. 「類似検索」ボタンをクリック
5. 類似度スコア付きの結果が表示されます

### データ登録

1. 「データ登録」タブを選択
2. CADファイルをアップロード
3. プレビューで確認後、「登録する」ボタンをクリック

## API エンドポイント

| メソッド | パス | 説明 |
|---------|------|------|
| `POST` | `/api/upload` | CADファイルをアップロード・登録 |
| `POST` | `/api/search` | CADファイルで類似検索 |
| `GET` | `/api/models` | 登録済みモデル一覧 |
| `GET` | `/api/models/{id}` | モデル詳細取得 |
| `DELETE` | `/api/models/{id}` | モデル削除 |
| `GET` | `/api/models/{id}/file` | CADファイルダウンロード |
| `GET` | `/api/health` | ヘルスチェック |

## ディレクトリ構成

```
shape-based-retrieval/
├── frontend/                  # Next.js フロントエンド
│   └── src/
│       ├── app/               # App Router ページ
│       └── components/        # React コンポーネント
│           ├── CadUploader.tsx     # D&D ファイルアップロード
│           ├── CadViewer.tsx       # Three.js 3Dビューワー
│           ├── SearchResults.tsx   # 検索結果一覧
│           └── CadCard.tsx         # モデルカード
├── backend/                   # Python FastAPI バックエンド
│   ├── app/
│   │   ├── main.py                # FastAPI エントリポイント
│   │   ├── config.py              # 設定管理
│   │   ├── routers/               # API ルーター (upload, search)
│   │   ├── services/              # ビジネスロジック
│   │   │   ├── cad_processor.py       # CAD → 点群変換
│   │   │   ├── feature_extractor.py   # PointNet 特徴抽出
│   │   │   └── similarity.py         # pgvector 類似検索
│   │   ├── models/                # DB・Pydantic スキーマ
│   │   └── ml/
│   │       └── pointnet.py        # 簡易版 PointNet
│   ├── scripts/               # サンプルデータ生成・投入
│   └── db/init.sql            # DB 初期化 SQL
├── docker-compose.yml
├── .env.example
└── README.md
```

## 対応ファイル形式

- STL（バイナリ / ASCII）
- OBJ
- STEP / IGES — 将来対応予定

## 停止・クリーンアップ

```bash
# コンテナ停止
docker compose down

# データも含めて完全に削除
docker compose down -v
```

## ライセンス

[MIT License](./LICENSE)
