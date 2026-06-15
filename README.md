# Yukkuri TTS Bot

## Installation

### 1. 前提環境の構築
以下のコマンドが使用できるようにしておいてください。
- `make`: コマンドの実行用
- `poetry`: 環境の構築用

### 2. 開発環境の構築

0. SSH接続

任意の方法でSSH接続できるようにしておくこと。ホスト名を`manju`で設定しておく。

1. リポジトリのClone

RaspberryPiのHOMEディレクトリの直下で以下を実行する

```sh
# ディレクトリの作成
mkdir bot && cd bot

# クローン
git clone git@github.com:Futaba-Kosuke/fastapi_template.git

# poetry install -v
# cp .env.template .env
# git config --local core.hooksPath .githooks
PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring make

# Results
# .venv: 仮想環境
# .env: 環境変数の書き込み用
# .githooks: Gitコミット時の処理を定義

```

2. aquestalkの導入

```
# scpコマンドで手元のOSから送信する
scp -r {PATH} manju:~/bot/
```

3. systemedの定義

以下のように設定

```sh
vim /etc/systemd/system/manju-run.service
```

```
[Unit]
Description=Run make run in myproject folder
After=network.target

[Service]
Environment="PATH=/home/{{USER_NAME}}/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Type=simple
WorkingDirectory=/home/{{USER_NAME}}/bot/yukkuri_tts_bot_discord
ExecStart=/usr/bin/make run
User={{USER_NAME}}
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```sh
sudo systemctl enable manju-run.service
sudo systemctl start manju-run.service
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
