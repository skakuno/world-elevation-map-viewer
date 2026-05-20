from PIL import Image
import numpy as np
import os

# 大きな画像を扱えるように設定
Image.MAX_IMAGE_PIXELS = None

def get_vegetation_color(value):
    """植生値（0-100, 254）をRGB色に変換"""
    if value == 254:
        # 海
        return (50, 100, 150)
    elif value == 0:
        # データなし（グレー）
        return (180, 180, 180)
    else:
        # 植生 1-100: 茶色→黄緑→濃い緑のグラデーション
        # 100を超える値は100として扱う
        value = min(value, 100)
        
        # 1-50: 茶色(160,120,80)から黄緑(180,200,80)
        # 51-100: 黄緑から濃い緑(0,100,0)
        if value <= 50:
            # 低植生: 茶色→黄緑
            t = value / 50.0
            r = int(160 + (180 - 160) * t)
            g = int(120 + (200 - 120) * t)
            b = int(80)
        else:
            # 高植生: 黄緑→濃い緑
            t = (value - 50) / 50.0
            r = int(180 - 180 * t)
            g = int(200 - 100 * t)
            b = int(80 - 80 * t)
        
        # 0-255の範囲に制限
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        return (r, g, b)

# ルックアップテーブルを事前に作成（高速化）
COLOR_LUT = np.zeros((256, 3), dtype=np.uint8)
for i in range(256):
    r, g, b = get_vegetation_color(i)
    COLOR_LUT[i] = [r, g, b]

def generate_vegetation_tiles(image_path, output_dir, max_zoom=9, tile_size=256):
    """植生TIFFファイルからタイルを生成"""
    
    print("=" * 60)
    print("植生タイル生成開始")
    print("=" * 60)
    
    # 出力ディレクトリを作成
    os.makedirs(output_dir, exist_ok=True)
    
    # TIFFファイルを開く
    print(f"\n[ステップ1] TIFFファイルを読み込み中: {image_path}")
    img = Image.open(image_path)
    base_width, base_height = img.size
    print(f"画像サイズ: {base_width} x {base_height}")
    print(f"画像モード: {img.mode}")
    
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
                    
                    # パレットモードのままリサイズ（NEAREST: 値を保持）
                    tile = region.resize((tile_size, tile_size), Image.NEAREST)
                    region.close()
                    
                    # リサイズ後の小さいタイルをRGBに変換
                    if is_palette_mode:
                        tile_data = np.array(tile, dtype=np.uint8)
                        # ルックアップテーブルで高速変換
                        rgb_tile = COLOR_LUT[tile_data]
                        
                        tile.close()
                        tile = Image.fromarray(rgb_tile, mode='RGB')
                else:
                    # 空のタイル（海の色）
                    tile = Image.new('RGB', (tile_size, tile_size), get_vegetation_color(254))
                
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
    input_file = "gm_ve_v2植生ver2.tif"
    output_directory = "gm_ve"
    
    generate_vegetation_tiles(input_file, output_directory, max_zoom=9)
