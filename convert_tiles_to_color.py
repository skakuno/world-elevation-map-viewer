from PIL import Image
import numpy as np
import os

def hex_to_rgb(hex_color):
    """16進数カラーコードをRGBに変換"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# 段彩図カラーマップ（標高別）
COLOR_MAP = [
    # (標高上限, RGB色)
    # 海
    (-10000, hex_to_rgb('#2D8CDB')),  # 海面 -9999
    
    # 海面以下の陸地（カスピ海、死海など）
    (-100, hex_to_rgb('#8FD3FF')),    # -146～-100m: 水色
    (0, hex_to_rgb('#A8D8FF')),       # -100～0m: 明るい水色
    
    # 陸地
    (100, hex_to_rgb('#D7F0C0')),     # 0～100m: 淡い緑
    (300, hex_to_rgb('#B8E186')),     # 100～300m: 薄緑
    (700, hex_to_rgb('#7FBC41')),     # 300～700m: 緑
    (1500, hex_to_rgb('#C8C26E')),    # 700～1500m: 黄緑～黄土
    (2500, hex_to_rgb('#B89C5A')),    # 1500～2500m: 黄土色
    (3500, hex_to_rgb('#9B6D3E')),    # 2500～3500m: 茶色
    (4500, hex_to_rgb('#7A5230')),    # 3500～4500m: 濃い茶
    (5500, hex_to_rgb('#A8A8A8')),    # 4500～5500m: 灰色
    (10000, hex_to_rgb('#FFFFFF')),   # 5500m以上: 白
]

def convert_tile_to_color(input_path, output_path):
    """16bitタイルをカラー段彩図に変換（高速化版）"""
    try:
        # 16bit PNG を読み込み
        img = Image.open(input_path)
        data = np.array(img, dtype=np.int32)
        
        # カラー画像を作成
        height, width = data.shape
        color_image = np.zeros((height, width, 3), dtype=np.uint8)
        
        # 海面マスク
        sea_mask = (data == 0)
        color_image[sea_mask] = hex_to_rgb('#2D8CDB')
        
        # データなしマスク
        nodata_mask = (data == 8888)
        color_image[nodata_mask] = (200, 200, 200)
        
        # 陸地マスク（海とデータなし以外）
        land_mask = ~sea_mask & ~nodata_mask
        
        # 標高に変換
        elevation = data.copy()
        elevation[land_mask] = data[land_mask] - 10000
        
        # 各標高帯に色を適用
        for i, (max_elev, color) in enumerate(COLOR_MAP):
            if i == 0:
                # 最初のエントリ（海）はスキップ（既に処理済み）
                continue
            
            if i == 1:
                # 最低標高帯
                mask = land_mask & (elevation <= max_elev)
            else:
                # 前の閾値からこの閾値まで
                prev_max = COLOR_MAP[i-1][0]
                mask = land_mask & (elevation > prev_max) & (elevation <= max_elev)
            
            color_image[mask] = color
        
        # カラーPNGとして保存
        output_img = Image.fromarray(color_image, mode='RGB')
        output_img.save(output_path, 'PNG', optimize=True)
        output_img.close()
        
        return True
    except Exception as e:
        print(f"エラー: {input_path} - {e}")
        return False

def convert_all_tiles(input_dir='tiles', output_dir='tiles_color'):
    """全てのタイルをカラー変換"""
    print("=" * 60)
    print("カラー段彩図変換開始")
    print("=" * 60)
    
    # 出力ディレクトリを作成
    os.makedirs(output_dir, exist_ok=True)
    
    total_tiles = 0
    converted_tiles = 0
    
    # 各ズームレベルを処理
    for zoom in range(10):  # 0-9
        zoom_input_dir = os.path.join(input_dir, str(zoom))
        zoom_output_dir = os.path.join(output_dir, str(zoom))
        
        if not os.path.exists(zoom_input_dir):
            continue
        
        print(f"\nズームレベル {zoom} を変換中...")
        os.makedirs(zoom_output_dir, exist_ok=True)
        
        # X座標のディレクトリを処理
        x_dirs = [d for d in os.listdir(zoom_input_dir) 
                  if os.path.isdir(os.path.join(zoom_input_dir, d))]
        
        for x in x_dirs:
            x_input_dir = os.path.join(zoom_input_dir, x)
            x_output_dir = os.path.join(zoom_output_dir, x)
            os.makedirs(x_output_dir, exist_ok=True)
            
            # Y座標のタイルを処理
            tiles = [f for f in os.listdir(x_input_dir) if f.endswith('.png')]
            
            for tile in tiles:
                input_path = os.path.join(x_input_dir, tile)
                output_path = os.path.join(x_output_dir, tile)
                
                if convert_tile_to_color(input_path, output_path):
                    converted_tiles += 1
                
                total_tiles += 1
                
                if total_tiles % 1000 == 0:
                    print(f"  {total_tiles} タイル変換済み...")
        
        print(f"  ズームレベル {zoom}: 完了")
    
    print("\n" + "=" * 60)
    print(f"完了！ {converted_tiles}/{total_tiles} タイル変換")
    print("=" * 60)

if __name__ == "__main__":
    convert_all_tiles()
