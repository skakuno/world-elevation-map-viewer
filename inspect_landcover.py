"""
被覆データ（land cover）TIFファイルを調査
"""
from PIL import Image
import numpy as np

Image.MAX_IMAGE_PIXELS = None

tif_file = "gm_lc_v3被覆ver3.tif"
print(f"=== {tif_file} の調査 ===\n")

img = Image.open(tif_file)
print(f"モード: {img.mode}")
print(f"サイズ: {img.size}")

data = np.array(img, dtype=np.int32)

print(f"\n=== 統計情報 ===")
print(f"最小値: {data.min()}")
print(f"最大値: {data.max()}")

# サンプリングしてユニークな値を調査（全体だとメモリ不足）
print("\nサンプリング（1/100）でユニーク値を調査...")
sample_data = data[::10, ::10]  # 10ピクセルごとにサンプリング
unique_values = np.unique(sample_data)
print(f"検出された値: {unique_values}")

# 各値の出現頻度（サンプルデータで）
print(f"\n=== 各カテゴリの出現頻度（サンプル）===")
for value in unique_values:
    count = np.sum(sample_data == value)
    percentage = count / sample_data.size * 100
    print(f"値 {value:3d}: {count:12d} ピクセル ({percentage:6.2f}%)")

# サンプル領域
print(f"\n=== サンプル領域（10x10ピクセル、中央付近）===")
h, w = data.shape
sample = data[h//2:h//2+10, w//2:w//2+10]
print(sample)

img.close()
print("\n調査完了")
