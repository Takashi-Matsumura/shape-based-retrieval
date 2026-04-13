# 前提ソフトウェアのインストール手順（Windows）

本書は、[`SETUP_WINDOWS.md`](./SETUP_WINDOWS.md) の「手順 0: 前提条件」で要求される 3 つの必須ソフトウェアを、Windows PC にインストールする手順をまとめたものです。

| 順序 | ソフトウェア | 役割 | 推奨バージョン |
|------|-------------|------|---------------|
| 1 | Git for Windows | ソースコードの取得 | 最新安定版 |
| 2 | Node.js (LTS) | フロントエンド (Next.js) 実行 | 18 以上（20 LTS 推奨） |
| 3 | Docker Desktop for Windows | バックエンド + DB 実行 | 最新 |

> **推奨インストール順**: Git → Node.js → Docker Desktop の順を推奨します（Docker Desktop は WSL2 の有効化や PC 再起動が発生するため、最後が無難）。
>
> **管理者権限**: 3 つとも管理者権限が必要です。インストーラ起動時に UAC（ユーザーアカウント制御）ダイアログが表示されます。

---

## 1. Git for Windows

### 1.1 ダウンロード

公式サイト: https://git-scm.com/download/win

アクセスすると 64-bit Windows 用インストーラが自動でダウンロードされます（`Git-X.XX.X-64-bit.exe`）。ダウンロードされない場合は「Click here to download」リンクをクリック。

### 1.2 インストール

ダウンロードした `.exe` を**ダブルクリック**で実行します。UAC が出たら「はい」。

インストーラの選択肢は**基本的にすべてデフォルトのまま「Next」で進めて問題ありません**。迷いそうな画面のみ補足：

| 画面 | 推奨選択 |
|------|---------|
| Select Components | デフォルトのまま |
| Choosing the default editor | 使い慣れたエディタ（不明なら「Use Visual Studio Code as Git's default editor」か「Use Notepad」） |
| Adjusting your PATH environment | **"Git from the command line and also from 3rd-party software"（デフォルト・推奨）** |
| Choosing HTTPS transport backend | "Use the OpenSSL library"（デフォルト） |
| Configuring the line ending conversions | "Checkout Windows-style, commit Unix-style line endings"（デフォルト） |
| Configuring the terminal emulator | "Use MinTTY"（デフォルト） |

最後の画面で「Install」をクリック → 完了後「Finish」。

### 1.3 動作確認

**PowerShell** を新規に開いて（既に開いているウィンドウは PATH が反映されないので必ず新規）：

```powershell
git --version
```

`git version 2.XX.X.windows.X` のような表示が出れば成功。

---

## 2. Node.js (LTS)

### 2.1 ダウンロード

公式サイト: https://nodejs.org/ja

トップページに **「LTS（推奨版）」** のボタンがあるのでそれをクリック。`node-vXX.XX.X-x64.msi` がダウンロードされます。

> バージョンは必ず **18 以上**。2026 年現在の LTS は 20 系または 22 系のどちらかです。どちらでも本プロジェクトは動作します。

### 2.2 インストール

ダウンロードした `.msi` を**ダブルクリック**で実行。UAC が出たら「はい」。

インストーラの選択肢は**すべてデフォルトのまま「Next」で進めて問題ありません**。補足：

| 画面 | 推奨選択 |
|------|---------|
| License Agreement | チェックを入れて Next |
| Destination Folder | デフォルト (`C:\Program Files\nodejs\`) |
| Custom Setup | デフォルト（すべての機能を「Will be installed on local hard drive」） |
| Tools for Native Modules | **チェックは不要**（本プロジェクトではネイティブビルド不要）。迷ったらデフォルトの**チェックなし**でOK |

「Install」→ 完了後「Finish」。

### 2.3 動作確認

**新規**の PowerShell で：

```powershell
node --version
npm --version
```

それぞれ `vXX.XX.X` / `XX.XX.X` が表示されれば成功。Node のメジャーバージョンが **18 以上**であることを必ず確認してください。

---

## 3. Docker Desktop for Windows

Docker Desktop は他 2 つより手順が多めです。PC の再起動も発生するので時間に余裕を持って作業してください。

### 3.1 事前確認: ハードウェア要件

- Windows 10 64-bit (22H2 以降) もしくは Windows 11 64-bit
- **CPU の仮想化機能 (VT-x / AMD-V) が有効**
- メモリ 8GB 以上推奨
- WSL2 が利用可能であること

#### 仮想化が有効かの確認

`Ctrl + Shift + Esc` でタスクマネージャー → 「パフォーマンス」タブ → 「CPU」 → 右下の **「仮想化: 有効」** と表示されていれば OK。

「無効」の場合は BIOS/UEFI 設定で **Intel VT-x** または **AMD-V** を有効化してください（手順は PC メーカー依存。Dell/HP/Lenovo 等の公式サイトを参照）。

### 3.2 ダウンロード

公式サイト: https://www.docker.com/products/docker-desktop/

「Download for Windows - AMD64」をクリック（ARM 版の Surface などを除く通常の PC は AMD64 でOK）。`Docker Desktop Installer.exe` がダウンロードされます。

### 3.3 インストール

ダウンロードした `Docker Desktop Installer.exe` を**ダブルクリック**で実行。UAC が出たら「はい」。

インストールウィザードの選択肢：

| 画面 | 推奨選択 |
|------|---------|
| Configuration | **"Use WSL 2 instead of Hyper-V (recommended)"** に**チェック**（デフォルト・推奨） |
|  | "Add shortcut to desktop" はお好みで |

「Ok」をクリックしてインストール開始。完了に数分かかります。

### 3.4 PC 再起動

インストール完了後、**「Close and restart」** をクリックして PC を再起動します（必須）。

### 3.5 初回起動とセットアップ

再起動後、Docker Desktop が自動起動します（しない場合はスタートメニューから「Docker Desktop」を起動）。

1. **Service Agreement**: 「Accept」をクリック
2. **サインイン / サインアップ画面**: **「Continue without signing in」を選択してスキップ OK**（業務用で課金プラン契約している場合のみログイン）
3. **アンケート**: スキップして OK
4. 初回起動時、WSL2 のカーネル更新が必要な場合があります。ダイアログの指示に従ってリンク先から `wsl_update_x64.msi` をインストール、Docker Desktop を再起動。
5. 起動完了後、画面右下のタスクトレイに **クジラのアイコン**が表示され、アイコンが緑の状態で静止していれば起動完了。

### 3.6 リソース設定（推奨）

Docker Desktop の **Settings → Resources → Advanced** で以下を推奨値に調整：

| 項目 | 推奨値 |
|------|-------|
| CPUs | 4 以上 |
| Memory | **4GB 以上**（本プロジェクトの PyTorch イメージで最低 4GB 必要） |
| Swap | 1GB |
| Disk image size | 64GB 以上 |

設定後「Apply & Restart」。

### 3.7 プロキシ設定（社内ネットワーク環境の場合のみ）

社内プロキシ経由でインターネット接続している環境では、**Settings → Resources → Proxies** で HTTP/HTTPS プロキシの設定が必要です。

- `Manual proxy configuration` を選択
- `Web Server (HTTP)` と `Secure Web Server (HTTPS)` にプロキシ URL を入力（例: `http://proxy.company.local:8080`）
- 「Apply & Restart」

プロキシが正しく設定されていないと、手順 3（Docker ビルド）で pip インストールが失敗します。

### 3.8 動作確認

**新規**の PowerShell で：

```powershell
docker --version
docker compose version
docker run --rm hello-world
```

- `docker --version` → `Docker version XX.X.X, build xxxxxxx`
- `docker compose version` → `Docker Compose version vX.X.X`
- `docker run hello-world` → `Hello from Docker!` の英文メッセージが表示される

すべて表示されれば Docker Desktop のセットアップ完了です。

---

## 4. インストール完了後のチェックリスト

以下のコマンドをすべて新規 PowerShell で実行し、全てバージョンが表示されれば前提条件クリアです。

```powershell
git --version
node --version
npm --version
docker --version
docker compose version
```

- [ ] Git 2.x が表示される
- [ ] Node.js **18 以上**が表示される
- [ ] npm が表示される
- [ ] Docker が表示される
- [ ] Docker Compose v2 系が表示される
- [ ] タスクトレイの Docker クジラアイコンが**緑**で静止している

問題なければ [`SETUP_WINDOWS.md`](./SETUP_WINDOWS.md) の「手順 1: ソースコード取得」に進んでください。

---

## 5. よくあるトラブル

| 症状 | 原因 | 対処 |
|------|------|------|
| Docker Desktop 起動時に `WSL 2 installation is incomplete` | WSL2 カーネル未更新 | エラーダイアログのリンクから `wsl_update_x64.msi` をインストール、Docker を再起動 |
| Docker 起動時に `Hardware assisted virtualization...` エラー | BIOS で仮想化無効 | 3.1 参照、BIOS で VT-x / AMD-V を有効化 |
| `docker run hello-world` でイメージ pull が失敗 | プロキシ未設定 / ネットワーク制限 | 3.7 のプロキシ設定を確認 |
| `node --version` が古いバージョンを返す | 旧版が残存 | コントロールパネルから旧 Node.js をアンインストール → 新規インストーラ再実行 |
| `git` / `node` / `docker` が「コマンドが見つかりません」 | PATH が反映されていない | 既存の PowerShell を閉じて**新規**で開き直す |
| 企業 PC でインストーラ実行がブロックされる | 管理者権限なし / グループポリシー制限 | 情報システム部門に依頼 |
