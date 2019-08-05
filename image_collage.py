import argparse
import sys
from glob import glob
from math import ceil, floor
from os.path import isfile
import natsort

from PIL import Image


def hex_to_color(hex_str):
    hex_str = hex_str.strip('#')
    if len(hex_str) == 3:
        r, g, b = hex_str
        r = int(r, 16) * 17
        g = int(g, 16) * 17
        b = int(b, 16) * 17
    elif len(hex_str) == 6:
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
    else:
        raise ValueError(hex_str)
    return r, g, b


def centered_crop(im, target_size):
    tw, th = target_size
    w, h = im.size
    dw = (w - tw) / 2
    dh = (h - th) / 2
    return im.crop((floor(dw),
                    floor(dh),
                    floor(w - dw),
                    floor(h - dh)))


def fit(im, target_size, bg=None):
    tw, th = target_size
    w, h = im.size
    dw = floor((w - tw) / 2)
    dh = floor((h - th) / 2)
    if bg and (dw < 0 or dh < 0):
        canvas = Image.new('RGB',
                           (max(w, tw), max(h, th)),
                           hex_to_color(bg))
        canvas.paste(im, (max(0, -dw), max(0, -dh)))
        del im
        return centered_crop(canvas, target_size)

    return centered_crop(im, target_size)


def make_collage(f_names, args):
    images = [Image.open(f) for f in f_names]
    size = images[0].size

    w, h = size
    bg = "fff"
    if args.fit:
        fit_arg = args.fit.split(":")
        if len(fit_arg) == 2:
            w, h = fit_arg
        else:
            bg, w, h = fit_arg
        w = int(w)
        h = int(h)

    else:
        for im in images:
            assert im.size == size, "sizes are not equal"

    m = args.cols
    n = ceil(len(f_names) / m)
    new_im = Image.new('RGB', (m * w + (m - 1) * args.border, n * h + (n - 1) * args.border))
    for k, im in enumerate(images):
        i = (k % m)
        j = (k // m)
        x = i * (w + args.border)
        y = j * (h + args.border)
        if args.fit:
            im = fit(im, (w, h), bg)
            new_im.paste(im, (x, y))
        else:
            new_im.paste(im, (x, y))

    new_im.save(args.output, quality=args.quality)


def main(args):
    files = set()
    for p in args.f_patterns:
        files.update(filter(isfile, glob(p)))

    if not files:
        print("no files provided")
        return

    print("got files:")
    for f in files:
        print("\t", f)
    print("")

    if len(files) < 2:
        print("only one file provided, nothing to do")
        return
    make_collage(natsort.natsorted(files), args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser("image collage maker")
    parser.add_argument("-c", "--cols", default=0, type=int)
    parser.add_argument("--fit", help="the option is useful when images are not exact same size. So you use"
                                      "`--fit 800:600` or `--fit fff:800:600` to crop/pad the images to the same size",
                        default="", type=str)
    parser.add_argument("-b", "--border", default=0, type=int)
    parser.add_argument("-o", "--output", default="collage.jpg", type=str)
    parser.add_argument("-q", "--quality", help="jpeg quality", default=100, type=int)
    parser.add_argument('f_patterns', metavar='N', type=str, nargs='+',
                        help='files or file patterns')
    args = parser.parse_args(sys.argv[1:])
    main(args)
