"""元のTIFファイルのデータを直接調査"""
from PIL import Image
import numpy as np

# 大きな画像を扱えるようにする
Image.MAX_IMAGE_PIXELS = None

# 1つのTIFファイルを読み込む
print("=== 元データの調査 ===\n")

tif_file = "gm_el_v2_1_1.tif"
print(f"ファイル: {tif_file}")

img = Image.open(tif_file)
print(f"モード: {img.mode}")
print(f"サイズ: {img.size}")

# NumPy配列に変換（符号付き整数として）
data = np.array(img, dtype=np.int32)

print(f"\n=== 統計情報 ===")
print(f"最小値: {data.min()}")
print(f"最大値: {data.max()}")
print(f"平均値: {data.mean():.2f}")

# ユニークな値の範囲を確認
unique_values = np.unique(data)
print(f"\nユニークな値の数: {len(unique_values)}")
print(f"最小の10個の値: {unique_values[:10]}")
print(f"最大の10個の値: {unique_values[-10:]}")

# 特定の値の出現回数
print(f"\n=== 特定の値の出現頻度 ===")
print(f"値 -9999 のピクセル数: {np.sum(data == -9999)} ({np.sum(data == -9999) / data.size * 100:.2f}%)")
print(f"値 -999999 のピクセル数: {np.sum(data == -999999)} ({np.sum(data == -999999) / data.size * 100:.2f}%)")
print(f"値 8888 のピクセル数: {np.sum(data == 8888)} ({np.sum(data == 8888) / data.size * 100:.2f}%)")
print(f"値 0 のピクセル数: {np.sum(data == 0)} ({np.sum(data == 0) / data.size * 100:.2f}%)")

# 負の値の範囲
negative_data = data[data < 0]
if len(negative_data) > 0:
    print(f"\n=== 負の値の分布 ===")
    print(f"負の値のピクセル数: {len(negative_data)} ({len(negative_data) / data.size * 100:.2f}%)")
    
    # -9999以外の負の値
    negative_not_9999 = negative_data[negative_data != -9999]
    if len(negative_not_9999) > 0:
        print(f"-9999以外の負の値: {len(negative_not_9999)} ピクセル")
        print(f"  最小値: {negative_not_9999.min()}")
        print(f"  最大値: {negative_not_9999.max()}")
        print(f"  ユニークな値: {len(np.unique(negative_not_9999))} 種類")

# 0以上の値の分布
positive_data = data[data >= 0]
print(f"\n=== 0以上の値の分布 ===")
print(f"0以上のピクセル数: {len(positive_data)} ({len(positive_data) / data.size * 100:.2f}%)")

# サンプル領域を見る（海岸線付近）
print(f"\n=== サンプル領域（10x10ピクセル、中心付近）===")
sample = data[10800:10810, 10800:10810]
print(sample)

# 画像の端のサンプル
print(f"\n=== 画像左上隅（10x10ピクセル）===")
corner = data[0:10, 0:10]
print(corner)
