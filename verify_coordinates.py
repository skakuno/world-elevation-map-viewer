"""
座標とタイル位置の検証スクリプト
"""
import math

def lat_lon_to_tile(longitude, latitude, zoom):
    """経度緯度からタイル座標を計算"""
    tile_size = 256
    tiles_x = 2 ** zoom
    tiles_y = 2 ** (zoom - 1) if zoom > 0 else 1
    map_width = tiles_x * tile_size
    map_height = tiles_y * tile_size
    
    # ピクセル座標に変換
    pixel_x = ((longitude + 180) / 360) * map_width
    pixel_y = ((90 - latitude) / 180) * map_height
    
    # タイル座標に変換
    tile_x = int(pixel_x // tile_size)
    tile_y = int(pixel_y // tile_size)
    
    # タイル内での相対位置
    in_tile_x = pixel_x % tile_size
    in_tile_y = pixel_y % tile_size
    
    return {
        'tile_x': tile_x,
        'tile_y': tile_y,
        'pixel_x': pixel_x,
        'pixel_y': pixel_y,
        'in_tile_x': in_tile_x,
        'in_tile_y': in_tile_y,
        'tile_path': f'{zoom}/{tile_x}/{tile_y}.png'
    }

# テスト都市の座標
cities = {
    'ロンドン': (-0.1276, 51.5074),
    'ドーバー海峡': (1.4, 51.0),
    '東京': (139.6917, 35.6895),
}

print("=" * 80)
print("座標検証 - ズームレベル5")
print("=" * 80)

zoom = 5
for city_name, (lon, lat) in cities.items():
    result = lat_lon_to_tile(lon, lat, zoom)
    print(f"\n{city_name}: {lon}°E, {lat}°N")
    print(f"  タイル: {result['tile_path']}")
    print(f"  ピクセル座標: ({result['pixel_x']:.2f}, {result['pixel_y']:.2f})")
    print(f"  タイル内位置: ({result['in_tile_x']:.2f}, {result['in_tile_y']:.2f})")

print("\n" + "=" * 80)
print("タイルファイルの存在確認")
print("=" * 80)

import os
for city_name, (lon, lat) in cities.items():
    result = lat_lon_to_tile(lon, lat, zoom)
    tile_path = f"tiles_8bit/{result['tile_path']}"
    exists = os.path.exists(tile_path)
    print(f"{city_name}: {tile_path} {'✓存在' if exists else '✗不在'}")
