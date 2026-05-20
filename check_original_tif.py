"""
元のTIFFファイルの値を確認
"""
from PIL import Image
import numpy as np
import os

# 大きな画像を扱えるようにする
Image.MAX_IMAGE_PIXELS = None

def check_tif(filepath):
    """TIFFファイルの内容を詳しく調査"""
    if not os.path.exists(filepath):
        print(f"ファイルが見つかりません: {filepath}")
        return
    
    print(f"\n{'='*60}")
    print(f"ファイル: {filepath}")
    print('='*60)
    
    img = Image.open(filepath)
    print(f"サイズ: {img.size}")
    print(f"モード: {img.mode}")
    
    # 小さなサンプル領域だけをロード（メモリ節約）
    # 複数の領域をサンプリング
    width, height = img.size
    
    sample_regions = [
        (0, 0, 1000, 1000),  # 左上
        (width//2, height//2, width//2 + 1000, height//2 + 1000),  # 中央
        (width - 1000, height - 1000, width, height),  # 右下
    ]
    
    all_samples = []
    
    for i, box in enumerate(sample_regions):
        try:
            region = img.crop(box)
            data = np.array(region)
            all_samples.append(data)
            print(f"\nサンプル領域 {i+1} {box}:")
            print(f"  最小値: {np.min(data)}")
            print(f"  最大値: {np.max(data)}")
            print(f"  平均値: {np.mean(data):.2f}")
            
            # 特殊な値
            total = data.size
            negative = np.sum(data < 0)
            zero = np.sum(data == 0)
            minus9999 = np.sum(data == -9999)
            near8888 = np.sum((data >= 8880) & (data <= 8900))
            
            print(f"  負の値: {negative} ({negative/total*100:.2f}%)")
            print(f"  -9999: {minus9999} ({minus9999/total*100:.2f}%)")
            print(f"  ゼロ: {zero} ({zero/total*100:.2f}%)")
            print(f"  8880-8900: {near8888} ({near8888/total*100:.2f}%)")
            
            region.close()
        except Exception as e:
            print(f"  エラー: {e}")
    
    # 全サンプルからユニークな値を調査
    if all_samples:
        combined = np.concatenate([s.flatten() for s in all_samples])
        unique = np.unique(combined)
        print(f"\n全サンプルのユニークな値の数: {len(unique):,}")
        print(f"  最小20値: {sorted(unique)[:20]}")
        print(f"  最大20値: {sorted(unique)[-20:]}")
    
    img.close()

def main():
    print("元のTIFFファイルの調査")
    print("="*60)
    
    # 8つのTIFFファイルをチェック
    tif_files = [
        'gm_el_v2_1_1.tif',
        'gm_el_v2_1_2.tif',
        'gm_el_v2_1_3.tif',
        'gm_el_v2_1_4.tif',
        'gm_el_v2_2_1.tif',
        'gm_el_v2_2_2.tif',
        'gm_el_v2_2_3.tif',
        'gm_el_v2_2_4.tif',
    ]
    
    for tif_file in tif_files[:2]:  # まず最初の2つをチェック
        check_tif(tif_file)

if __name__ == '__main__':
    main()
