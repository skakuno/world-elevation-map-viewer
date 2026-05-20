"""
負の値の詳細を調査
"""
from PIL import Image
import numpy as np

Image.MAX_IMAGE_PIXELS = None

# カスピ海、死海、五大湖などを含む領域をサンプリング
tif_files = [
    ('gm_el_v2_1_3.tif', '中東・カスピ海'),
    ('gm_el_v2_2_1.tif', '北米五大湖'),
]

for tif_file, description in tif_files:
    print(f"\n{'='*60}")
    print(f"{description}: {tif_file}")
    print('='*60)
    
    img = Image.open(tif_file)
    width, height = img.size
    
    # 中央付近をサンプリング
    regions = [
        (width//4, height//4, width//4 + 2000, height//4 + 2000),
        (width//2, height//2, width//2 + 2000, height//2 + 2000),
        (3*width//4, 3*height//4, 3*width//4 + 2000, 3*height//4 + 2000),
    ]
    
    all_data = []
    for i, box in enumerate(regions):
        try:
            region = img.crop(box)
            data = np.array(region, dtype=np.int32)
            all_data.append(data)
        except:
            pass
    
    if all_data:
        combined = np.concatenate([d.flatten() for d in all_data])
        
        # 負の値の統計
        negative_mask = combined < 0
        negative_values = combined[negative_mask]
        
        print(f"\n負の値の統計:")
        print(f"  負の値の数: {len(negative_values):,} ({len(negative_values)/len(combined)*100:.2f}%)")
        
        if len(negative_values) > 0:
            # -9999を除く
            non_sea_negative = negative_values[negative_values != -9999]
            if len(non_sea_negative) > 0:
                print(f"\n-9999以外の負の値:")
                print(f"  個数: {len(non_sea_negative):,}")
                print(f"  最小値: {np.min(non_sea_negative)}")
                print(f"  最大値: {np.max(non_sea_negative)}")
                print(f"  ユニークな値: {len(np.unique(non_sea_negative))}")
                
                # 頻度の高い値
                unique, counts = np.unique(non_sea_negative, return_counts=True)
                top_10 = sorted(zip(unique, counts), key=lambda x: x[1], reverse=True)[:10]
                print(f"\n  頻度の高い負の値 Top 10:")
                for val, count in top_10:
                    print(f"    {val}: {count}回 ({count/len(combined)*100:.4f}%)")
        
        # ゼロと正の値
        zero_count = np.sum(combined == 0)
        positive_count = np.sum(combined > 0)
        print(f"\nその他の値:")
        print(f"  ゼロ: {zero_count:,} ({zero_count/len(combined)*100:.2f}%)")
        print(f"  正の値: {positive_count:,} ({positive_count/len(combined)*100:.2f}%)")
    
    img.close()

print("\n" + "="*60)
print("結論:")
print("-9999以外の負の値がある場合、それらは内陸の低地や湖を示します")
print("これらを海面として扱うと、カスピ海や死海が海になってしまいます")
print("="*60)
