from PIL import Image
from pathlib import Path
import argparse
import math

Image.MAX_IMAGE_PIXELS = None


def scan_min_max(files, nodata)
    values_min = []
    values_max = []

    for f in files
        img = Image.open(f)

        # mode I の場合、画素値を読む
        extrema = img.getextrema()
        print(f)
        print(  size, img.size)
        print(  mode, img.mode)
        print(  extrema, extrema)

        # ここでは簡易版として、NoData=-9999を除外する前提で、
        # 最小値は0に固定する。標高図ならこれが安全。
        # 海底や負値も使いたい場合は後で変更可能。
        values_min.append(0)
        values_max.append(extrema[1])

        img.close()

    global_min = min(values_min)
    global_max = max(values_max)

    print(使用する表示範囲, global_min, ～, global_max)
    return global_min, global_max


def dem_to_8bit(img, global_min, global_max, nodata)
    
    mode I の標高画像を、表示用8bitグレーに変換する。
    NoData は 0 黒にする。
    

    if global_max = global_min
        return img.convert(L)

    # point() は mode I では巨大テーブルが扱いづらいので、
    # pixel access で安全に処理する。
    w, h = img.size
    src = img.load()

    out = Image.new(L, (w, h), 0)
    dst = out.load()

    scale = 255.0  (global_max - global_min)

    for y in range(h)
        if y % 1000 == 0
            print(  row, y, , h)

        for x in range(w)
            v = src[x, y]

            if v == nodata
                g = 0
            else
                g = int((v - global_min)  scale)
                if g  0
                    g = 0
                elif g  255
                    g = 255

            dst[x, y] = g

    return out


def combine(files, output, cols, nodata)
    rows = math.ceil(len(files)  cols)

    # 全体の表示範囲を決める
    global_min, global_max = scan_min_max(files, nodata)

    # サイズ確認
    first = Image.open(files[0])
    tile_w, tile_h = first.size
    first.close()

    total_w = tile_w  cols
    total_h = tile_h  rows

    print(出力サイズ, total_w, x, total_h)

    result = Image.new(L, (total_w, total_h), 0)

    for i, f in enumerate(files)
        print(処理中, f)

        img = Image.open(f)
        gray = dem_to_8bit(img, global_min, global_max, nodata)

        col = i % cols
        row = i  cols

        x = col  tile_w
        y = row  tile_h

        print(貼り付け位置, x, y)
        result.paste(gray, (x, y))

        img.close()
        gray.close()

    result.save(output, compression=tiff_lzw)
    print(完了, output)


def main()
    parser = argparse.ArgumentParser(description=標高DEM系TIFFを見える8bitグレー画像として結合します。)
    parser.add_argument(--cols, type=int, required=True)
    parser.add_argument(-o, --output, required=True)
    parser.add_argument(--nodata, type=int, default=-9999)
    parser.add_argument(inputs, nargs=+)

    args = parser.parse_args()

    files = [Path(x) for x in args.inputs]

    combine(files, Path(args.output), args.cols, args.nodata)


if __name__ == __main__
    main()