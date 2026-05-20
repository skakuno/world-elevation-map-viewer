"""
海岸線付近のタイルを分析して、陸地に標高0が混ざっているか調査
"""
from PIL import Image
import numpy as np
import os

def analyze_tile(tile_path):
    """タイル内の標高分布を分析"""
    img = Image.open(tile_path)
    data = np.array(img)
    
    total_pixels = data.size
    zero_pixels = np.sum(data == 0)
    land_pixels = np.sum(data > 0)
    
    # 標高値の統計
    if land_pixels > 0:
        land_data = data[data > 0]
        min_land = np.min(land_data)
        max_land = np.max(land_data)
        mean_land = np.mean(land_data)
    else:
        min_land = max_land = mean_land = 0
    
    # 0と非0の境界ピクセル数（海岸線の推定）
    # 縦横に隣接するピクセルで値が変わる場所をカウント
    boundaries = 0
    for i in range(data.shape[0] - 1):
        for j in range(data.shape[1] - 1):
            if (data[i, j] == 0 and data[i+1, j] > 0) or \
               (data[i, j] > 0 and data[i+1, j] == 0) or \
               (data[i, j] == 0 and data[i, j+1] > 0) or \
               (data[i, j] > 0 and data[i, j+1] == 0):
                boundaries += 1
    
    img.close()
    
    return {
        'total': total_pixels,
        'zero': zero_pixels,
        'land': land_pixels,
        'zero_percent': (zero_pixels / total_pixels) * 100,
        'land_percent': (land_pixels / total_pixels) * 100,
        'min_land': min_land,
        'max_land': max_land,
        'mean_land': mean_land,
        'boundaries': boundaries
    }

def main():
    print("=" * 60)
    print("海岸線タイル分析")
    print("=" * 60)
    
    # 複数のズームレベルとタイルを分析
    test_tiles = [
        # ズームレベル4: 大陸規模
        ('tiles/4/13/6.png', 'ヨーロッパ (4/13/6)'),
        ('tiles/4/14/7.png', 'アジア西部 (4/14/7)'),
        # ズームレベル5: 地域規模
        ('tiles/5/26/12.png', '中国・日本 (5/26/12)'),
        ('tiles/5/27/13.png', '日本南部 (5/27/13)'),
        ('tiles/5/17/10.png', 'ヨーロッパ中部 (5/17/10)'),
        ('tiles/5/28/14.png', '東南アジア (5/28/14)'),
        # ズームレベル6: より詳細
        ('tiles/6/52/24.png', '中国東部 (6/52/24)'),
        ('tiles/6/56/28.png', '東南アジア詳細 (6/56/28)'),
        ('tiles/6/33/21.png', 'アフリカ北部 (6/33/21)'),
        # ズームレベル7
        ('tiles/7/104/48.png', '中国沿岸 (7/104/48)'),
        ('tiles/7/112/56.png', 'インドシナ半島 (7/112/56)'),
    ]
    
    for tile_path, description in test_tiles:
        if not os.path.exists(tile_path):
            print(f"\n【{description}】")
            print(f"  ファイルが見つかりません: {tile_path}")
            continue
        
        print(f"\n【{description}】")
        result = analyze_tile(tile_path)
        
        print(f"  総ピクセル数: {result['total']:,}")
        print(f"  標高0 (海): {result['zero']:,} ({result['zero_percent']:.1f}%)")
        print(f"  標高>0 (陸): {result['land']:,} ({result['land_percent']:.1f}%)")
        
        if result['land'] > 0:
            print(f"  陸地の標高範囲: {result['min_land']}m ～ {result['max_land']:,}m")
            print(f"  陸地の平均標高: {result['mean_land']:.1f}m")
        
        print(f"  海陸境界ピクセル数: {result['boundaries']:,}")
        
        # 海岸線の複雑さを推定
        if result['zero'] > 0 and result['land'] > 0:
            complexity = result['boundaries'] / min(result['zero'], result['land'])
            if complexity > 0.1:
                print(f"  → 複雑な海岸線（境界が多い）")
            elif result['boundaries'] > 100:
                print(f"  → 海岸線を含む")
            else:
                print(f"  → 海と陸が混在しているが境界は少ない")
        elif result['zero'] == result['total']:
            print(f"  → 完全に海")
        elif result['land'] == result['total']:
            print(f"  → 完全に陸地")

if __name__ == '__main__':
    main()
