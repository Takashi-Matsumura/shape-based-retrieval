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
2. STL / OBJ ファイルをドラッグ＆ドロップ（またはクリックして選択）、
   または **「デモ用サンプルから選択」** でプリセットのクエリファイルをワンクリック選択
3. 3Dプレビューで確認
4. 「類似検索」ボタンをクリック
5. 類似度スコア付きの結果が表示されます

> デモ用サンプルは `backend/data/demo_queries/` に STL 6 点・OBJ 4 点の計 10 ファイルが格納されています。
> `docker exec cad-search-backend python -m scripts.generate_demo_queries` で再生成できます。

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
| `GET` | `/api/demo-queries` | デモ用クエリファイル一覧 |
| `GET` | `/api/demo-queries/{filename}` | デモ用クエリファイルダウンロード |
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
│   │   ├── generate_samples.py      # 登録用サンプル生成 (32個)
│   │   ├── seed_data.py             # サンプルを API 経由で登録
│   │   └── generate_demo_queries.py # 検索デモ用クエリ生成 (STL+OBJ)
│   ├── data/demo_queries/     # デモ用クエリファイル (STL 6 + OBJ 4)
│   └── db/init.sql            # DB 初期化 SQL
├── demo/                     # Windows スタンドアロン デモアプリ
│   ├── app.py                    # Gradio エントリポイント
│   ├── core/                     # ONNX推論・SQLite・類似検索
│   ├── hooks/                    # PyInstaller ランタイムフック
│   ├── scripts/                  # ONNX変換・データ生成・ビルド
│   ├── data/                     # ONNXモデル・SQLite DB・サンプルSTL
│   ├── demo.spec                 # PyInstaller 設定
│   ├── requirements.txt          # 実行時依存
│   └── requirements-dev.txt      # 開発用依存
├── docker-compose.yml
├── .env.example
└── README.md
```

## Windows デモ版（スタンドアロン）

Docker や開発環境を使わず、Windows PC 上で手軽にCAD類似形状検索を試せるデモアプリです。

### exe 版（Python 不要）

[Releases](../../releases) ページから最新の **CADSearchDemo.zip** をダウンロードしてください。

1. `CADSearchDemo.zip` をダウンロード
2. 任意のフォルダに展開
3. `CADSearchDemo.exe` をダブルクリック
4. ブラウザが自動で開く（`http://127.0.0.1:7860`）
5. STL / OBJ ファイルをドラッグ＆ドロップして「Search」
6. 手元にファイルがなければ `_internal/data/samples/` 内のSTLで動作確認可能

> exe は GitHub Actions で自動ビルドされます。Python のインストールは不要です。

### Python から実行する場合

Python 3.10 以上がインストールされている環境では、ソースから直接実行できます。

```bash
cd demo
pip install -r requirements.txt
python app.py
```

ブラウザが自動で開き、`http://127.0.0.1:7860` でアプリにアクセスできます。

### デモの使い方

1. 画面左側でSTL / OBJ ファイルをアップロード
2. 右側にアップロードした3Dモデルのプレビューが表示される
3. top-k スライダーで返す結果数を調整（1〜10）
4. 「Search」ボタンをクリック
5. 下段に類似度スコア付きの3Dプレビューが表示される

### デモの技術構成

| 項目 | 技術 |
|------|------|
| UI | Gradio（ブラウザベース） |
| 推論 | ONNX Runtime（PyTorch 不要、約50MB） |
| DB | SQLite + numpy cosine similarity |
| 3D表示 | Plotly Mesh3d |
| サンプルデータ | 32個の基本形状（box / sphere / cylinder / cone / torus / composite） |

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
