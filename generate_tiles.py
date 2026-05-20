"""
DEM TIFFファイルを結合し、マップタイル（zoom/x/y.png）を生成します。
元データの値をマッピング：
  -9999（海面） → 0
  それ以外の値 → value + 10000
つまり：
  0 = 海面
  9854 = 標高-146m（海面下の陸地）
  9973 = 標高-27m（カスピ海など）
  10000 = 標高0m
  18692 = 標高8692m
"""
from PIL import Image
import os
import math
from pathlib import Path
import numpy as np

Image.MAX_IMAGE_PIXELS = None


def combine_tiffs(files, cols=4):
    """TIFFファイルを横4縦2で結合（負の値を処理）"""
    rows = math.ceil(len(files) / cols)

    # サイズ確認
    first = Image.open(files[0])
    tile_w, tile_h = first.size
    mode = first.mode
    print(f"TIFFファイルサイズ: {tile_w} x {tile_h}, モード: {mode}")
    first.close()

    total_w = tile_w * cols
    total_h = tile_h * rows

    print(f"結合画像サイズ: {total_w} x {total_h}")
    
    # NumPy配列として結合（負の値を処理するため）
    result_array = np.zeros((total_h, total_w), dtype=np.int32)

    for i, f in enumerate(files):
        print(f"結合中: {f}")

        img = Image.open(f)
        data = np.array(img, dtype=np.int32)
        
        # 統計情報
        print(f"  最小値: {np.min(data)}, 最大値: {np.max(data)}")
        print(f"  -9999（海面）: {np.sum(data == -9999)} ピクセル ({np.sum(data == -9999)/data.size*100:.1f}%)")
        
        # 値をマッピング：-9999→0、それ以外→value+10000
        mapped_data = np.where(data == -9999, 0, data + 10000).astype(np.int32)
        
        col = i % cols
        row = i // cols

        x = col * tile_w
        y = row * tile_h

        print(f"  貼り付け位置: ({x}, {y})")
        result_array[y:y+tile_h, x:x+tile_w] = mapped_data

        img.close()
    
    # NumPy配列からPIL Imageに変換（16ビット符号なし）
    # 値の範囲を確認
    print(f"\n結合後の統計:")
    print(f"  最小値: {np.min(result_array)}")
    print(f"  最大値: {np.max(result_array)}")
    print(f"  値0（海面）: {np.sum(result_array == 0)} ピクセル ({np.sum(result_array == 0)/result_array.size*100:.1f}%)")
    print(f"  値9500-9999（海面下）: {np.sum((result_array >= 9500) & (result_array < 10000))} ピクセル ({np.sum((result_array >= 9500) & (result_array < 10000))/result_array.size*100:.4f}%)")
    print(f"  値10000（標高0m）: {np.sum(result_array == 10000)} ピクセル ({np.sum(result_array == 10000)/result_array.size*100:.4f}%)")
    print(f"  値>10000（陸地）: {np.sum(result_array > 10000)} ピクセル ({np.sum(result_array > 10000)/result_array.size*100:.1f}%)")
    
    # 16ビット符号なし整数に変換（0-65535）
    result_array_uint16 = np.clip(result_array, 0, 65535).astype(np.uint16)
    result = Image.fromarray(result_array_uint16, mode='I;16')

    return result


def generate_tiles(image, output_dir, max_zoom=9, tile_size=256):
    """
    画像からマップタイルを生成（メモリ効率的な方法）
    各タイルを元画像から直接切り出してリサイズすることで、
    巨大な中間画像を作らずにタイルを生成します。
    
    Args:
        image: PIL Image object
        output_dir: 出力ディレクトリ
        max_zoom: 最大ズームレベル
        tile_size: タイルサイズ (デフォルト256x256)
    """
    base_width, base_height = image.size
    print(f"\n元画像サイズ: {base_width} x {base_height}")
    print(f"元画像モード: {image.mode}")

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

        # タイルを生成（メモリ効率的な方法）
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
                # 元画像は -180° to +180°（横）、+90° to -90°（縦）をカバー
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
                    region = image.crop((src_left, src_top, src_right, src_bottom))
                    
                    # タイルサイズにリサイズ（NEAREST: 補間なし、海岸線を保持）
                    tile = region.resize((tile_size, tile_size), Image.NEAREST)
                    region.close()
                else:
                    # 空のタイル
                    tile = Image.new(image.mode, (tile_size, tile_size), 0)

                # PNGとして保存
                tile_path = os.path.join(x_dir, f"{tile_y}.png")
                tile.save(tile_path, 'PNG')
                tile.close()

                tile_count += 1

                if tile_count % 1000 == 0:
                    print(f"  {tile_count} タイル生成済み...")

        print(f"  ズームレベル {zoom}: {tile_count} タイル生成完了")


def main():
    # 8つのTIFFファイルを指定
    tiff_files = [
        "gm_el_v2_1_1.tif",
        "gm_el_v2_1_2.tif",
        "gm_el_v2_1_3.tif",
        "gm_el_v2_1_4.tif",
        "gm_el_v2_2_1.tif",
        "gm_el_v2_2_2.tif",
        "gm_el_v2_2_3.tif",
        "gm_el_v2_2_4.tif",
    ]

    print("=" * 60)
    print("DEM タイル生成開始（グレースケール変換なし）")
    print("=" * 60)

    # TIFFファイルを結合（元のデータ形式を保持）
    print("\n[ステップ1] TIFFファイルを結合中...")
    combined_image = combine_tiffs(tiff_files, cols=4)

    # タイルを生成
    print("\n[ステップ2] マップタイルを生成中...")
    output_dir = "tiles"
    generate_tiles(combined_image, output_dir, max_zoom=9, tile_size=256)

    combined_image.close()

    print("\n" + "=" * 60)
    print("完了！")
    print("=" * 60)


if __name__ == "__main__":
    main()
