# BD2 Mod Comparison Tool

BrownDust 2 本地 Mod 比較與管理工具。透過視覺化介面瀏覽、比較不同作者的 Mod 版本，並將選定的版本一鍵整合到輸出資料夾。

## 功能特色

- **自動掃描** — 遞迴掃描 `MODS/` 資料夾，自動辨識 Spine 動畫 Mod 與圖片替換 Mod
- **多版本比較** — 同一角色若有多位作者的 Mod，可即時切換預覽
- **Spine 動畫播放** — 內建 Spine Player，支援動畫選擇、播放/暫停、同步鏡頭
- **選用管理** — 勾選想使用的 Mod 版本，支援搜尋、作者篩選、僅顯示已選
- **一鍵套用** — 將選定的 Mod 版本自動複製到 `MODS_MERGED/` 整合資料夾

## 資料夾結構

```
BD2_ModComparisonTool/
├── start_tool.bat            # 啟動工具（雙擊執行）
├── ModComparisonTools/       # 工具程式碼
│   ├── mod_index_server.py   #   Python 後端伺服器
│   ├── mod_viewer.html       #   前端介面（單一 HTML）
│   └── vendor/               #   第三方函式庫（Spine Player）
├── MODS/                     # Mod 來源（使用者自行放置）
│   ├── 作者A/
│   │   └── <mod 資料夾>/
│   └── 作者B/
│       └── <mod 資料夾>/
└── MODS_MERGED/              # 整合輸出（工具自動產生）
```

## 環境需求

- **Python 3.10+**（標準函式庫即可，無需額外套件）
- 現代瀏覽器（Chrome / Edge / Firefox）

## 使用方式

### 1. 放置 Mod

將 Mod 檔案依**作者名稱**分資料夾放入 `MODS/`：

```
MODS/
├── AuthorA/
│   └── SomeCharacter_Skin/
│       ├── char000123.atlas
│       ├── char000123.skel (或 .json)
│       └── char000123.png
└── AuthorB/
    └── SomeCharacter_AltSkin/
        ├── char000123.atlas
        └── char000123.json
```

**支援的 Mod 格式：**
- **Spine Mod**：`.atlas` + `.skel` 或 `.json`
- **圖片替換 Mod**：`.modfile` + `textures/*.png`

### 2. 啟動工具

雙擊根目錄的 `start_tool.bat`，瀏覽器會自動開啟介面。

也可以手動啟動：

```bash
python ModComparisonTools/mod_index_server.py
# 然後瀏覽 http://localhost:8000/ModComparisonTools/mod_viewer.html
```

### 3. 操作介面

| 功能 | 說明 |
|------|------|
| 搜尋 | 輸入 Mod ID 或角色關鍵字 |
| 作者篩選 | 下拉選單篩選特定作者 |
| 只顯示已選 | 僅列出已選用的 Mod |
| 版本切換 | 點擊作者按鈕即時切換預覽 |
| 動畫播放 | 選擇動作並播放 / 暫停 |
| 選用 / 取消 | 決定是否使用此版本 |

### 4. 儲存與套用

- **「儲存選擇」** — 將目前的選擇記錄到本機
- **「套用選擇」** — 將選定版本的檔案複製到 `MODS_MERGED/` 資料夾，可直接供遊戲使用

## 注意事項

- `MODS/` 和 `MODS_MERGED/` 不包含在本倉庫中，需自行放置 Mod 檔案
- `MODS_MERGED/` 會在套用時自動建立
- 同名 Mod 資料夾會被覆蓋更新

## 授權

本工具僅供個人使用，Mod 素材版權歸原作者所有。
