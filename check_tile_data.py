"""
生成されたタイルのデータを確認するスクリプト
"""
from PIL import Image
import os
import numpy as np

def check_tile(tile_path):
    """タイルのデータを確認"""
    if not os.path.exists(tile_path):
        print(f"ファイルが見つかりません: {tile_path}")
        return
    
    img = Image.open(tile_path)
    
    print(f"\n{'='*60}")
    print(f"ファイル: {tile_path}")
    print(f"{'='*60}")
    print(f"サイズ: {img.size}")
    print(f"モード: {img.mode}")
    
    # ピクセルデータを配列に変換
    data = np.array(img)
    
    print(f"\nデータ統計:")
    print(f"  最小値: {data.min()}")
    print(f"  最大値: {data.max()}")
    print(f"  平均値: {data.mean():.2f}")
    print(f"  中央値: {np.median(data):.2f}")
    print(f"  標準偏差: {data.std():.2f}")
    
    # 値の分布を確認
    unique_values = np.unique(data)
    print(f"\n  ユニークな値の数: {len(unique_values)}")
    if len(unique_values) <= 10:
        print(f"  すべての値: {unique_values}")
    else:
        print(f"  最初の10値: {unique_values[:10]}")
        print(f"  最後の10値: {unique_values[-10:]}")
    
    # ゼロでないピクセルの数
    non_zero = np.count_nonzero(data)
    total = data.size
    print(f"\n  総ピクセル数: {total}")
    print(f"  非ゼロピクセル: {non_zero} ({100*non_zero/total:.1f}%)")
    print(f"  ゼロピクセル: {total-non_zero} ({100*(total-non_zero)/total:.1f}%)")
    
    img.close()
    
    return data


def create_preview(tile_path, output_path):
    """タイルを視認可能なグレースケール画像に変換"""
    img = Image.open(tile_path)
    data = np.array(img)
    
    # データの範囲を確認
    min_val = data.min()
    max_val = data.max()
    
    if max_val > min_val:
        # 0-255の範囲に正規化
        normalized = ((data - min_val) / (max_val - min_val) * 255).astype(np.uint8)
        preview = Image.fromarray(normalized, mode='L')
        preview.save(output_path)
        print(f"\nプレビュー画像を保存しました: {output_path}")
        print(f"  元の範囲: {min_val} ～ {max_val}")
    else:
        print(f"\nデータの範囲がありません（すべて {min_val}）")
    
    img.close()


def main():
    print("タイルデータ確認ツール")
    print("="*60)
    
    # いくつかのタイルを確認
    test_tiles = [
        "tiles/0/0/0.png",        # ズームレベル0
        "tiles/5/16/8.png",       # ズームレベル5 中央付近
        "tiles/9/256/128.png",    # ズームレベル9 中央
    ]
    
    for tile_path in test_tiles:
        if os.path.exists(tile_path):
            data = check_tile(tile_path)
            
            # プレビュー画像を作成
            base_name = tile_path.replace('.png', '_preview.png')
            create_preview(tile_path, base_name)
        else:
            print(f"\nタイルが見つかりません: {tile_path}")
    
    print("\n" + "="*60)
    print("確認完了")


if __name__ == "__main__":
    main()
