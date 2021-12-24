#!/usr/bin/python3

from PIL import Image, ImageDraw, ImageFont
import sys
from clint.textui import progress
import typing
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd

alphabet = sys.argv[1]

BLACK = (0,0,0)
WHITE = (255,255,255)
GREY = (100,100,100)
Point_type = typing.Tuple[int, int]

def pixel_gen(img:Image, start=None, end=None):
    pix = img.load()
    if start is None:
        start = (0,0)
    if end is None:
        end = (img.size)
    for row in range(start[1], end[1]):
        for col in range(start[0], end[1]):
            pos = (col, row)
            yield (pos, tuple(apply_func(pix, mask, pos)))



def out_size(fnt:ImageFont):
    return sum(fnt.getsize(c)[0] for c in alphabet)


def move_point(p0:Point_type, p1:Point_type):
    return tuple(i+j for i, j in zip(p0, p1))


def main():
    height = [12, 15, 30]
    fonts = ["dejavy/DejaVuSansCondensed.ttf", "freefont/FreeMono.ttf", "croscore/Arimo-Italic.ttf"]

    space = 4
    header_names = (
            ("weight",None), 
            ("specific weight",None),
            ("center of gravity",None),
            ("norm CenterOfGravity",None),
            ("axial moments (h, v)",None),
            ("norm axial moments",None),
            ("profiles",None),
            )

    base_directory = "pics"
    if not os.path.exists(base_directory):
        os.makedirs(base_directory)
    for h, f in zip(height, fonts):
        directory = f"{base_directory}/alpabet{h}"
        if not os.path.exists(directory):
            os.makedirs(directory)
        fnt = ImageFont.truetype(f"/usr/share/fonts/truetype/{f}", h)
        base_fnt = ImageFont.truetype(f"/usr/share/fonts/truetype/{fonts[0]}", h)

        max_size_width = np.zeros(1+len(header_names))
        for idx, char in enumerate(alphabet):
            char_size = fnt.getsize(char)
            if max_size_width[-1] < char_size[0]:
                max_size_width[-1] = char_size[0]
            img = Image.new('RGB', char_size, color = WHITE)
            d = ImageDraw.Draw(img)
            d.text((0,0), char, font=fnt, fill=BLACK)
            img.save(f'{directory}/{idx}_{char}.png')

            for col, (col_name, func) in enumerate(header_names):
                text_size = base_fnt.getsize(col_name)
                if max_size_width[col] < text_size[0]:
                    max_size_width[col] = text_size[0]
            #calc

            #

        img_width = int(np.sum(max_size_width))+space*(max_size_width.size+1)
        res_img = Image.new('RGB', (img_width, (h+space)*(len(alphabet)+1)+space), color = WHITE)
        d_res = ImageDraw.Draw(res_img)

        #draw header
        offset = max_size_width[-1]+space+space
        for col, (col_name, _) in enumerate(header_names):
            d_res.text(move_point((space, space), (offset, 0)), col_name, fill=BLACK)
            offset += max_size_width[col]+space

        for idx, char in enumerate(alphabet):
            xy = (space, space+(idx+1)*(h+space)) 
            char_size = base_fnt.getsize(char)
            d_res.rectangle([xy, move_point(xy, char_size)], fill=GREY)
            d_res.text(xy, char, font=fnt, fill=BLACK)
            offset = max_size_width[-1]+space+space
            for col, (col_name, _) in enumerate(header_names):
                d_res.text(move_point(xy, (offset, 0)), col_name, fill=BLACK)
                offset += max_size_width[col]+space

        res_img.save(f'{directory}/all.png')


if __name__ == "__main__":
    print(alphabet)
    main()



