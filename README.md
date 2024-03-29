# Yukkuri TTS Bot

## Installation

### 1. 前提環境の構築
以下のコマンドが使用できるようにしておいてください。
- `make`: コマンドの実行用
- `poetry`: 環境の構築用

### 2. 開発環境の構築
```sh
# クローン
git clone git@github.com:Futaba-Kosuke/fastapi_template.git

# poetry install -v
# cp .env.template .env
# git config --local core.hooksPath .githooks
make

# Results
# .venv: 仮想環境
# .env: 環境変数の書き込み用
# .githooks: Gitコミット時の処理を定義
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
