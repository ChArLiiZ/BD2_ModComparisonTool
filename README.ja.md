# BD2 Mod 比較ツール

**Language / 語言：** [English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

**BrownDust 2** 用のローカルMod比較・管理ツールです。ビジュアルインターフェースで異なる作者のModバージョンを閲覧・比較し、選択したバージョンをワンクリックで出力フォルダに統合できます。

## 機能

- **自動スキャン** — `MODS/` フォルダを再帰的にスキャンし、SpineアニメーションModと画像置換Modを自動検出
- **マルチバージョン比較** — 同じキャラクターに複数の作者のModがある場合、即座にプレビューを切り替え
- **Spineアニメーション再生** — 内蔵Spine Playerでアニメーション選択、再生/一時停止、カメラ同期をサポート
- **選択管理** — 検索、作者フィルター、選択済みのみ表示で、使いたいModバージョンを選択
- **ワンクリック統合** — 選択したModバージョンを `MODS_MERGED/` 出力フォルダに自動コピー
- **多言語UI** — 英語、日本語、繁体字中国語に対応

## フォルダ構成

```
BD2_ModComparisonTool/
├── start_tool.bat            # ツール起動（ダブルクリック）
├── ModComparisonTools/       # ツールソースコード
│   ├── mod_index_server.py   #   Pythonバックエンドサーバー
│   ├── mod_viewer.html       #   フロントエンドUI（単一HTML）
│   └── vendor/               #   サードパーティライブラリ（Spine Player）
├── MODS/                     # Modソース（ユーザーが配置）
│   ├── 作者A/
│   │   └── <modフォルダ>/
│   └── 作者B/
│       └── <modフォルダ>/
└── MODS_MERGED/              # 統合出力（自動生成）
```

## 必要環境

- **Python 3.10+**（標準ライブラリのみ、追加パッケージ不要）
- モダンブラウザ（Chrome / Edge / Firefox）

## 使い方

### 1. Modを配置

Modファイルを**作者名**ごとにフォルダ分けして `MODS/` に配置します：

```
MODS/
├── AuthorA/
│   └── SomeCharacter_Skin/
│       ├── char000123.atlas
│       ├── char000123.skel（または .json）
│       └── char000123.png
└── AuthorB/
    └── SomeCharacter_AltSkin/
        ├── char000123.atlas
        └── char000123.json
```

**対応Modフォーマット：**
- **Spine Mod**：`.atlas` + `.skel` または `.json`
- **画像置換Mod**：`.modfile` + `textures/*.png`

### 2. ツールを起動

ルートディレクトリの `start_tool.bat` をダブルクリックすると、ブラウザが自動で開きます。

手動で起動することもできます：

```bash
python ModComparisonTools/mod_index_server.py
# その後 http://localhost:8000/ModComparisonTools/mod_viewer.html を開く
```

### 3. インターフェースガイド

| 機能 | 説明 |
|------|------|
| 検索 | Mod IDまたはキャラクターキーワードを入力 |
| 作者フィルター | ドロップダウンから特定の作者でフィルタリング |
| 選択済みのみ | 選択済みのModのみを表示 |
| バージョン切り替え | 作者ボタンをクリックしてプレビューを切り替え |
| アニメーション | アニメーションを選択して再生/一時停止 |
| 選択/解除 | このバージョンを使用するかどうかを決定 |

### 4. 保存と適用

- **「選択を保存」** — 現在の選択記録をローカルに保存
- **「選択を適用」** — 選択したバージョンのファイルを `MODS_MERGED/` フォルダにコピー、ゲームですぐに使用可能

## 注意事項

- `MODS/` と `MODS_MERGED/` はこのリポジトリに含まれていません。自分でModファイルを配置してください
- `MODS_MERGED/` は適用時に自動的に作成されます
- 同名のModフォルダは上書きされます

## ライセンス

MIT License — 詳細は [LICENSE](LICENSE) をご覧ください。

Mod素材の著作権は各作者に帰属します。
