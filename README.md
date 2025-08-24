# FastAPI Template

## Installation

### 1. 前提環境の構築

1. 使用するコマンド

以下のコマンドが使用できるようにしておいてください。
- `make`: コマンドの実行用
- `poetry`: 環境の構築用

2. `opus`, `ffmpeg`のインストール

```sh
sudo apt update
sudo apt install -y libopus0 libopus-dev ffmpeg

# Tips: opusはraspberry pi osの場合、/usr/lib/aarch64-linux-gnu/libopus.soに配置されている
```

3. `aquestalkpi`のインストール

```sh
# 作業ディレクトリに移動
mkdir ~/bot

# 必要ファイルのダウンロード
wget https://www.a-quest.com/archive/package/aquestalkpi-20220207.tgz -O aquestalkpi.tgz
zcat aquestalkpi.tgz | tar xv

# 64bit版を適用
cd aquestalkpi
mv AquesTalkPi AquesTalkPi32
cp bin64/AquesTalkPi AquesTalkPi
```

### 2. 開発環境の構築
```sh
cd ~/bot

# クローン
git clone git@github.com:Futaba-Kosuke/fastapi_template.git

# パッケージのインストール
# pyproject.tomlに従って.venv/を生成
make

# GitHooksの設定
# 自動でリンター／フォーマッターを動かせるようにする
git config --local core.hooksPath .githooks

# 仮想環境に入る
make env
```

### 3. 開発時の補足
開発時には仮想環境に入った状態で開発することを強く推奨します。
```sh
# 仮想環境に入る
make env

# スクリプトの実行
make run

# フォーマッター、リンターの実行
make lint
```

コミット時には以下のモジュールが自動で動作します。
| Module | Description |
| -- | -- |
| isort | モジュールのインポート順調整 |
| black | フォーマット調整 |
| flake8 | PEP8スタイル、論理エラー、複雑度のチェック |
| mypy | 型チェック |

### 4. ディレクトリ構成
> 参考: https://docs.python-guide.org/writing/structure/
