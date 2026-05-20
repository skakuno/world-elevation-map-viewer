# World Elevation Map Viewer

世界標高・土地被覆・植生データを、256x256タイルとして表示するためのHTMLビューアと生成スクリプトです。

## 含まれるもの

- ローカルタイル表示用ビューア
  - `integrated_viewer.html`
  - `simple_viewer.html`
  - `simple_viewer_color.html`
  - `LC_hifuku_viewer.html`
  - `VE_shokusei_viewer.html`
- 国土地理院の地理院タイルを直接読むビューア
  - `gsi_direct_viewer.html`
- タイル生成・検証用Pythonスクリプト
  - `generate_tiles.py`
  - `generate_landcover_tiles.py`
  - `generate_vegetation_tiles.py`
  - `verify_coordinates.py`
  - ほか
- ライセンス・出典説明
  - `about_license.html`
  - `ライセンス説明.txt`

## 含まれないもの

このリポジトリには、巨大な実データは含めていません。

除外している主なデータ:

- `tiles/`
- `tiles_8bit/`
- `tiles_color/`
- `gm_lc/`
- `gm_ve/`
- `*.tif`
- `*.tiff`
- `*.zip`
- `*.pdf`
- `*.odt`

これらはファイル数や容量が大きいため、GitHubリポジトリでは管理しません。

## 使い方

ローカルタイル版を使う場合は、対応するタイルフォルダを同じ階層に配置してから、HTMLファイルをブラウザで開きます。

例:

```text
integrated_viewer.html
tiles_8bit/
tiles_color/
gm_lc/
gm_ve/
```

GSI直読版を使う場合は、インターネット接続がある状態で次のファイルを開きます。

```text
gsi_direct_viewer.html
```

## データ出典

本プロジェクトでは、国土地理院の地球地図全球版データおよび地理院タイルを参照しています。利用時は各データの利用条件を確認し、必要な出典表示を行ってください。

- 地球地図全球版: https://www.gsi.go.jp/kankyochiri/gm_global.html
- 地理院タイル一覧: https://maps.gsi.go.jp/development/ichiran.html
- 測量成果の利用手続: https://www.gsi.go.jp/LAW/2930-index.html

## 注意

GSIタイルや他国の地図当局タイルを自分のサーバーへ保存・再配信する場合は、単なる背景表示とは扱いが変わります。公式URLから直接読む場合、保存して配る場合、加工して配る場合を分けて、各ライセンスと利用条件を確認してください。
