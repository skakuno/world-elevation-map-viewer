from PIL import Image
import numpy as np

# 大きな画像を扱えるように設定
Image.MAX_IMAGE_PIXELS = None

# TIFFファイルを開く
file_path = "gm_ve_v2植生ver2.tif"
print(f"ファイル: {file_path}")
print("=" * 60)

with Image.open(file_path) as img:
    print(f"モード: {img.mode}")
    print(f"サイズ: {img.size}")
    
    # サンプリング（メモリ節約のため1/100のピクセルを調査）
    width, height = img.size
    print(f"\nサンプリング中 (1/100ピクセル)...")
    
    sampled_data = []
    step = 10  # 10ピクセルごとにサンプリング
    
    for y in range(0, height, step):
        for x in range(0, width, step):
            try:
                pixel = img.getpixel((x, y))
                sampled_data.append(pixel)
            except:
                pass
    
    sampled_array = np.array(sampled_data)
    
    print(f"\n統計情報:")
    print(f"最小値: {sampled_array.min()}")
    print(f"最大値: {sampled_array.max()}")
    
    # ユニークな値を確認
    unique_values = np.unique(sampled_array)
    print(f"\n検出された値: {unique_values}")
    print(f"値の種類: {len(unique_values)}種類")
    
    # 各値の頻度
    print(f"\n値の分布（上位10個）:")
    unique, counts = np.unique(sampled_array, return_counts=True)
    total_samples = len(sampled_array)
    
    # 頻度順にソート
    sorted_indices = np.argsort(-counts)
    for i in sorted_indices[:10]:
        value = unique[i]
        count = counts[i]
        percentage = (count / total_samples) * 100
        print(f"値 {value:3d}: {count:8d} ピクセル ({percentage:5.2f}%)")

print("\n" + "=" * 60)
print("分析完了")
