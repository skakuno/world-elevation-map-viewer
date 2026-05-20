"""
元データの座標系を確認
TIFFファイルのジオリファレンス情報を読み取る
"""
try:
    from osgeo import gdal
    gdal.UseExceptions()
    
    print("=" * 80)
    print("GDAL で TIFFファイルのジオリファレンス情報を確認")
    print("=" * 80)
    
    # 最初のTIFFファイルを開く
    tif_file = 'gm_el_v2_1_1.tif'
    ds = gdal.Open(tif_file)
    
    if ds is None:
        print(f"ファイルが開けません: {tif_file}")
    else:
        print(f"\nファイル: {tif_file}")
        print(f"サイズ: {ds.RasterXSize} x {ds.RasterYSize}")
        
        # ジオトランスフォーム情報
        geotransform = ds.GetGeoTransform()
        if geotransform:
            print(f"\nジオトランスフォーム:")
            print(f"  左上X (経度): {geotransform[0]}")
            print(f"  ピクセル幅: {geotransform[1]}")
            print(f"  回転X: {geotransform[2]}")
            print(f"  左上Y (緯度): {geotransform[3]}")
            print(f"  回転Y: {geotransform[4]}")
            print(f"  ピクセル高さ: {geotransform[5]}")
            
            # 右下の座標を計算
            right_lon = geotransform[0] + ds.RasterXSize * geotransform[1]
            bottom_lat = geotransform[3] + ds.RasterYSize * geotransform[5]
            
            print(f"\nカバー範囲:")
            print(f"  経度: {geotransform[0]}° to {right_lon}°")
            print(f"  緯度: {geotransform[3]}° to {bottom_lat}°")
        
        # 投影情報
        projection = ds.GetProjection()
        if projection:
            print(f"\n投影: {projection[:100]}...")
        
        ds = None

except ImportError:
    print("GDAL がインストールされていません")
    print("代替方法：PIL で画像サイズを確認")
    print()
    
    from PIL import Image
    import os
    
    Image.MAX_IMAGE_PIXELS = None
    
    print("=" * 80)
    print("TIFFファイルのサイズとファイル名から推測")
    print("=" * 80)
    
    tif_files = [
        ['gm_el_v2_1_1.tif', 'gm_el_v2_1_2.tif', 'gm_el_v2_1_3.tif', 'gm_el_v2_1_4.tif'],
        ['gm_el_v2_2_1.tif', 'gm_el_v2_2_2.tif', 'gm_el_v2_2_3.tif', 'gm_el_v2_2_4.tif'],
    ]
    
    print("\nファイル配置（generate_tiles.py の配置）:")
    print("  1行目（row 1）: 1_1, 1_2, 1_3, 1_4")
    print("  2行目（row 2）: 2_1, 2_2, 2_3, 2_4")
    print()
    
    # 最初のファイルのサイズを確認
    first_file = 'gm_el_v2_1_1.tif'
    if os.path.exists(first_file):
        img = Image.open(first_file)
        w, h = img.size
        img.close()
        
        print(f"各TIFFのサイズ: {w} x {h}")
        print(f"結合後のサイズ: {w*4} x {h*2}")
        print()
        
        # 15秒角解像度から計算
        arc_seconds = 15
        degrees_per_pixel = arc_seconds / 3600
        
        lon_coverage = w * degrees_per_pixel
        lat_coverage = h * degrees_per_pixel
        
        print(f"解像度: {arc_seconds}秒角 = {degrees_per_pixel}度/ピクセル")
        print(f"各ファイルのカバー範囲: {lon_coverage}° x {lat_coverage}°")
        print()
        
        # 推測される配置
        print("推測される配置パターン:")
        print("\nパターン1: 標準（西から東、北から南）")
        print("  1_1: -180° to -90°E, 90° to 0°N")
        print("  1_2: -90° to 0°E, 90° to 0°N  ← ロンドンはここ")
        print("  1_3: 0° to 90°E, 90° to 0°N")
        print("  1_4: 90° to 180°E, 90° to 0°N")
        print()
        print("パターン2: 日付変更線中心")
        print("  1_1: 0° to 90°E, 90° to 0°N  ← ロンドンはここ")
        print("  1_2: 90° to 180°E, 90° to 0°N")
        print("  1_3: -180° to -90°E, 90° to 0°N")
        print("  1_4: -90° to 0°E, 90° to 0°N")
        print()
        print("どちらのパターンか確認するには、既知の地形を視覚的に確認する必要があります")
