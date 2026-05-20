"""
16ビットタイルを8ビットグレースケールに変換
元の16ビット版は保持し、8ビット版を別ディレクトリに生成
"""
from PIL import Image
import os
import numpy as np
from pathlib import Path
import glob

def convert_tile_to_8bit(input_path, output_path, global_min=0, global_max=9000):
    """
    16ビットタイルを8ビットグレースケールに変換
    配色: 海面=薄い灰色、陸地は標高が高いほど黒くなる
    
    タイル値のマッピング：
      0 = 海面（元の-9999）
      9500～9999 = 海面下-500m～-1m（内陸の湖や低地）
      10000 = 標高0m
      10001以上 = 標高1m以上
    
    Args:
        input_path: 入力ファイルパス（16ビット）
        output_path: 出力ファイルパス（8ビット）
        global_min: 全体の最小標高値（実質的な最小値、-500m想定）
        global_max: 全体の最大標高値
    """
    try:
        img = Image.open(input_path)
        data = np.array(img)
        
        # 配色設定
        SEA_COLOR = 200        # 海面（値0） = 薄い灰色
        LAND_START = 120       # 標高0m（値10000） = 濃い灰色（海岸線を明確にするため）
        LAND_END = 0           # 最高標高 = 真っ黒
        BELOW_SEA_START = 190  # 海面下-500m = 海の色に近い
        BELOW_SEA_END = 160    # 海面下-1m = 陸地より明るい
        
        # 結果用の配列を作成
        normalized = np.zeros_like(data, dtype=np.uint8)
        
        # 海（値0）を薄い灰色に
        sea_mask = (data == 0)
        normalized[sea_mask] = SEA_COLOR
        
        # 海面下の陸地（値9500～9999）= カスピ海、死海など
        # 海の色に近づけて、視覚的に識別できるようにする
        below_sea_mask = (data >= 9500) & (data < 10000)
        if np.any(below_sea_mask):
            below_sea_values = data[below_sea_mask]
            # 9500→BELOW_SEA_START(190)、9999→BELOW_SEA_END(160)への線形補間
            normalized_below = (below_sea_values - 9500) / 499.0  # 0～1
            colors_below = (BELOW_SEA_START + (BELOW_SEA_END - BELOW_SEA_START) * normalized_below).astype(np.uint8)
            normalized[below_sea_mask] = colors_below
        
        # 陸地（値>=10000）を標高に応じて黒くする
        # 値10000 = 標高0m、値10001 = 標高1m、...
        land_mask = (data >= 10000)
        if np.any(land_mask) and global_max > global_min:
            # 実際の標高に変換（値-10000）
            land_elevations = data[land_mask] - 10000
            # 標高を0～1に正規化
            land_normalized = np.clip(land_elevations / global_max, 0, 1)
            # 標高が高いほど黒く（120→0）
            land_colors = (LAND_START * (1 - land_normalized)).astype(np.uint8)
            normalized[land_mask] = land_colors
        
        # 8ビットグレースケール画像として保存
        output_img = Image.fromarray(normalized, mode='L')
        output_img.save(output_path, 'PNG', optimize=True)
        
        img.close()
        output_img.close()
        
        return True
    except Exception as e:
        print(f"  エラー: {input_path} - {e}")
        return False


def scan_max_value(tiles_dir):
    """全タイルをスキャンして最大値を見つける"""
    print("全タイルの最大標高値を検索中...")
    
    max_value = 0
    sample_count = 0
    
    # 各ズームレベルから代表的なタイルをサンプリング
    for zoom in range(10):  # 0-9
        zoom_dir = os.path.join(tiles_dir, str(zoom))
        if not os.path.exists(zoom_dir):
            continue
        
        # 各ズームレベルから複数のタイルをサンプリング
        tiles = glob.glob(os.path.join(zoom_dir, "*", "*.png"))
        
        # サンプル数を制限（大量のタイルがある場合）
        sample_size = min(len(tiles), max(10, len(tiles) // 100))
        import random
        sampled_tiles = random.sample(tiles, sample_size) if len(tiles) > sample_size else tiles
        
        for tile_path in sampled_tiles:
            try:
                img = Image.open(tile_path)
                data = np.array(img)
                tile_max = data.max()
                if tile_max > max_value:
                    max_value = tile_max
                img.close()
                sample_count += 1
            except:
                pass
    
    print(f"  サンプル数: {sample_count}")
    print(f"  検出された最大値: {max_value}")
    
    return max_value


def convert_all_tiles(input_dir="tiles", output_dir="tiles_8bit"):
    """すべてのタイルを16ビットから8ビットに変換"""
    
    print("="*60)
    print("タイル変換: 16ビット → 8ビットグレースケール")
    print("="*60)
    
    # 全体の最大値をスキャン（より正確な正規化のため）
    global_max = scan_max_value(input_dir)
    
    # 最大値に余裕を持たせる（最高峰を考慮）
    if global_max < 6000:
        global_max = 6000  # エベレスト級まで考慮
    elif global_max < 9000:
        global_max = 9000  # 最大9000mまで
    
    global_min = 0
    
    print(f"\n正規化範囲: {global_min} ～ {global_max}m")
    print(f"出力先: {output_dir}/")
    
    # すべてのタイルファイルを検索
    tile_files = glob.glob(os.path.join(input_dir, "*", "*", "*.png"))
    total_files = len(tile_files)
    
    print(f"\n変換対象: {total_files} ファイル")
    print("\n変換開始...")
    
    converted = 0
    failed = 0
    
    for i, input_path in enumerate(tile_files, 1):
        # 相対パスを取得（tiles/zoom/x/y.png）
        rel_path = os.path.relpath(input_path, input_dir)
        output_path = os.path.join(output_dir, rel_path)
        
        # 出力ディレクトリを作成
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 変換
        if convert_tile_to_8bit(input_path, output_path, global_min, global_max):
            converted += 1
        else:
            failed += 1
        
        # 進捗表示
        if i % 1000 == 0 or i == total_files:
            print(f"  進捗: {i}/{total_files} ({100*i/total_files:.1f}%) - 成功: {converted}, 失敗: {failed}")
    
    print("\n" + "="*60)
    print("変換完了")
    print(f"  成功: {converted}")
    print(f"  失敗: {failed}")
    print(f"  出力先: {output_dir}/")
    print("="*60)


def main():
    input_dir = "tiles"          # 16ビット版
    output_dir = "tiles_8bit"    # 8ビット版
    
    if not os.path.exists(input_dir):
        print(f"エラー: {input_dir} ディレクトリが見つかりません")
        return
    
    convert_all_tiles(input_dir, output_dir)


if __name__ == "__main__":
    main()
