"""
土地被覆データ（land cover）からマップタイルを生成
カテゴリカルデータなので、NEAREST補間のみ使用
"""
from PIL import Image
import os
from pathlib import Path
import numpy as np

Image.MAX_IMAGE_PIXELS = None

# 土地被覆カテゴリのカラーマップ（値1-20）
# 標準的なGlobal Mapの分類に基づく
LANDCOVER_COLORS = {
    1: (0, 100, 0),      # 常緑針葉樹林 - Broadleaf Evergreen Forest
    2: (0, 150, 0),      # 常緑広葉樹林 - Broadleaf Deciduous Forest
    3: (50, 200, 50),    # 針葉樹林 - Needleleaf Evergreen Forest
    4: (100, 200, 100),  # 針葉落葉樹林 - Needleleaf Deciduous Forest
    5: (150, 200, 150),  # 混交林 - Mixed Forest
    6: (200, 200, 0),    # 樹木開放地 - Tree Open
    7: (255, 255, 100),  # 低木地 - Shrub
    8: (255, 200, 100),  # 草本 - Herbaceous
    9: (200, 150, 100),  # 草本/低木混合 - Herbaceous with Sparse Tree/Shrub
    10: (255, 255, 0),   # 疎植生 - Sparse Vegetation
    11: (255, 100, 100), # 農地 - Cropland
    12: (220, 220, 100), # 水田 - Paddy field
    13: (200, 100, 50),  # 農地/その他混合 - Cropland / Other Vegetation Mosaic
    14: (150, 150, 150), # マングローブ - Mangrove
    15: (200, 200, 200), # 湿地 - Wetland
    16: (180, 180, 180), # 裸地 - Bare area
    17: (255, 255, 255), # 都市 - Urban
    18: (200, 255, 255), # 雪氷 - Snow / Ice
    19: (100, 150, 200), # 水域 - Water bodies
    20: (50, 100, 150),  # 海 - Sea
}


def generate_landcover_tiles(image_path, output_dir, max_zoom=9, tile_size=256):
    """
    土地被覆データからマップタイルを生成
    
    Args:
        image_path: 入力TIFFファイル
        output_dir: 出力ディレクトリ
        max_zoom: 最大ズームレベル
        tile_size: タイルサイズ
    """
    print("=" * 60)
    print("土地被覆タイル生成開始")
    print("=" * 60)
    
    print(f"\n[ステップ1] TIFFファイルを読み込み中: {image_path}")
    img = Image.open(image_path)
    
    base_width, base_height = img.size
    print(f"画像サイズ: {base_width} x {base_height}")
    print(f"画像モード: {img.mode}")
    
    # パレットモードの場合、RGBに変換
    # パレットモードの場合、タイルごとに変換するのでそのまま保持
    is_palette_mode = (img.mode == 'P')
    if is_palette_mode:
        print("パレットモード検出 - タイルごとにRGB変換します")
    
    print(f"\n[ステップ2] マップタイルを生成中...")
    
    # 各ズームレベルを生成
    for zoom in range(max_zoom + 1):
        print(f"\nズームレベル {zoom} を生成中...")
        
        # このズームレベルでのタイル数を計算
        num_tiles_x = 2 ** zoom
        num_tiles_y = 2 ** (zoom - 1) if zoom > 0 else 1
        
        # このズームレベルでの画像サイズ
        zoom_width = num_tiles_x * tile_size
        zoom_height = num_tiles_y * tile_size
        
        print(f"  論理サイズ: {zoom_width} x {zoom_height}")
        print(f"  タイル数: {num_tiles_x} x {num_tiles_y} = {num_tiles_x * num_tiles_y}")
        
        # 拡大率を計算
        scale_x = zoom_width / base_width
        scale_y = zoom_height / base_height
        
        # ズームディレクトリを作成
        zoom_dir = os.path.join(output_dir, str(zoom))
        os.makedirs(zoom_dir, exist_ok=True)
        
        # タイルを生成
        tile_count = 0
        for tile_x in range(num_tiles_x):
            # Xディレクトリを作成
            x_dir = os.path.join(zoom_dir, str(tile_x))
            os.makedirs(x_dir, exist_ok=True)
            
            for tile_y in range(num_tiles_y):
                # このタイルの地理座標範囲を計算
                # タイル座標から経度緯度への変換
                lon_min = (tile_x / num_tiles_x) * 360 - 180
                lon_max = ((tile_x + 1) / num_tiles_x) * 360 - 180
                lat_max = 90 - (tile_y / num_tiles_y) * 180
                lat_min = 90 - ((tile_y + 1) / num_tiles_y) * 180
                
                # 地理座標から元画像のピクセル座標へ変換
                src_left = ((lon_min + 180) / 360) * base_width
                src_right = ((lon_max + 180) / 360) * base_width
                src_top = ((90 - lat_max) / 180) * base_height
                src_bottom = ((90 - lat_min) / 180) * base_height
                
                # 整数座標に変換（四捨五入）
                src_left = round(src_left)
                src_top = round(src_top)
                src_right = round(src_right)
                src_bottom = round(src_bottom)
                
                # 元画像の境界を超えないように制限
                src_left = max(0, min(src_left, base_width))
                src_top = max(0, min(src_top, base_height))
                src_right = max(0, min(src_right, base_width))
                src_bottom = max(0, min(src_bottom, base_height))
                
                # 元画像から領域を切り出し
                if src_right > src_left and src_bottom > src_top:
                    region = img.crop((src_left, src_top, src_right, src_bottom))
                    
                    # パレットモードのままリサイズ（NEAREST: カテゴリを保持）
                    tile = region.resize((tile_size, tile_size), Image.NEAREST)
                    region.close()
                    
                    # リサイズ後の小さいタイルをRGBに変換
                    if is_palette_mode:
                        tile_data = np.array(tile, dtype=np.uint8)
                        rgb_tile = np.zeros((tile_size, tile_size, 3), dtype=np.uint8)
                        
                        # カテゴリごとに色を割り当て（256x256の小さい配列なので高速）
                        for category, color in LANDCOVER_COLORS.items():
                            rgb_tile[tile_data == category] = color
                        
                        tile.close()
                        tile = Image.fromarray(rgb_tile, mode='RGB')
                else:
                    # 空のタイル（海の色）
                    tile = Image.new('RGB', (tile_size, tile_size), LANDCOVER_COLORS[20])
                
                # PNGとして保存
                tile_path = os.path.join(x_dir, f"{tile_y}.png")
                tile.save(tile_path, 'PNG', optimize=True)
                tile.close()
                
                tile_count += 1
                
                if tile_count % 1000 == 0:
                    print(f"  {tile_count} タイル生成済み...")
        
        print(f"  ズームレベル {zoom}: {tile_count} タイル生成完了")
    
    img.close()
    
    print("\n" + "=" * 60)
    print("完了！")
    print("=" * 60)


if __name__ == "__main__":
    input_file = "gm_lc_v3被覆ver3.tif"
    output_directory = "gm_lc"
    
    generate_landcover_tiles(input_file, output_directory, max_zoom=9)
