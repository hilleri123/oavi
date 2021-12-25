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
from collections.abc import Iterable 



alphabet = sys.argv[1]

BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (0,0,255)
RED = (255,0,0)
GREY = (100,100,100)
Point_type = typing.Tuple[int, int]

def pixel_gen(img:Image, start=None, end=None, white_black=True):
    pix = img.load()
    if start is None:
        start = (0,0)
    if end is None:
        end = (img.size)
    for row in range(start[1], end[1]):
        for col in range(start[0], end[0]):
            pos = (col, row)
            if white_black:
                yield (pos, 0 if pix[pos][0] > WHITE[0]/2 else 1)
            else:
                yield (pos, pix[pos])


def get_profile(img:Image):
    res = [np.zeros(i) for i in img.size]
    for pos, pix in pixel_gen(img, white_black=False):
        res[0][pos[0]] += pix[0]/255
        res[1][pos[1]] += 1-pix[0]/255
    return res


def out_size(fnt:ImageFont):
    return sum(fnt.getsize(c)[0] for c in alphabet)


def move_point(p0:Point_type, p1:Point_type):
    return tuple(i+j for i, j in zip(p0, p1))

def get_moment(img:Image, p:int, q:int, x_c:int, y_c:int):
    m = 0
    for (x, y), pix in pixel_gen(img):
        m += (x-x_c)**p * (y-y_c)**q * pix
    return m


def calc_weight(img:Image, _:pd.Series):
    w = 0
    for (x, y), pix in pixel_gen(img):
        w += pix
    return w

def calc_norm_weight(img:Image, acc:pd.Series):
    return acc[header_names[0][0]] / img.size[0] / img.size[1]

def calc_center_of_gravity(img:Image, acc:pd.Series):
    res = [0,0]
    for idx, (p, q) in enumerate([(1, 0), (0, 1)]):
        for (x, y), pix in pixel_gen(img):
            res[idx] += x**p * y**q * pix
    return tuple(i/acc[header_names[0][0]] for i in res)

def calc_norm_center_of_gravity(img:Image, acc:pd.Series):
    return tuple((pos-1)/(img.size[idx]-1) for idx, pos in enumerate(acc[header_names[2][0]]))

def calc_axial_moments(img:Image, acc:pd.Series):
    res = [0,0]
    x_c, y_c = acc[header_names[2][0]]
    for idx, (p, q) in enumerate([(2, 0), (0, 2)]):
        res[idx] = get_moment(img, p=p, q=q, x_c=x_c, y_c=y_c)
    return tuple(res)

def calc_norm_axial_moments(img:Image, acc:pd.Series):
    sub = sum(i**2 for i in img.size)
    return tuple(i/sub for i in acc[header_names[4][0]])

#def calc_profiles(img:Image, acc:pd.Series):
    #return (0,0)

header_names = (
        ("weight",calc_weight), #0
        ("norm weight",calc_norm_weight), #1
        ("center of gravity",calc_center_of_gravity), #2
        ("norm CenterOfGravity",calc_norm_center_of_gravity), #3
        ("axial moments (h, v)",calc_axial_moments), #4
        ("norm axial moments",calc_norm_axial_moments), #5
        #("profiles",calc_profiles), #6
        )

def main():
    height = [12, 15, 30]
    fonts = ["dejavy/DejaVuSansCondensed.ttf", "freefont/FreeMono.ttf", "croscore/Arimo-Italic.ttf"]

    space = 4

    base_directory = "pics"
    if not os.path.exists(base_directory):
        os.makedirs(base_directory)
    for h, f in zip(height, fonts):
        directory = f"{base_directory}/alpabet{h}"
        if not os.path.exists(directory):
            os.makedirs(directory)
        fnt = ImageFont.truetype(f"/usr/share/fonts/truetype/{f}", h)
        base_fnt = ImageFont.truetype(f"/usr/share/fonts/truetype/{fonts[0]}", h)

        data = pd.DataFrame({cl_name:[] for cl_name, _ in header_names})

        max_size_width = np.zeros(1+len(header_names))
        for idx, char in enumerate(progress.bar(alphabet)):
            char_size = fnt.getsize(char)
            if max_size_width[-1] < char_size[0]:
                max_size_width[-1] = char_size[0]
            img = Image.new('RGB', char_size, color = WHITE)
            d = ImageDraw.Draw(img)
            d.text((0,0), char, font=fnt, fill=BLACK)
            img.save(f'{directory}/{idx}_{char}.png')

            row = pd.Series(name=char)
            for col, (col_name, func) in enumerate(header_names):
                val = pd.Series({col_name:func(img, row)})
                row = row.append(val)
                text = str(np.round(val[col_name], 2))
                text_size = max(base_fnt.getsize(col_name)[0], base_fnt.getsize(text)[0])
                if max_size_width[col] < text_size:
                    max_size_width[col] = text_size
            row.name = char
            data = data.append(row)

            prof_img = img.copy()
            prof_d = ImageDraw.Draw(prof_img)
            prof_d.text((0,0), char, font=fnt, fill=BLACK)
            x_prof, y_prof = get_profile(prof_img)
            plt.gca().invert_yaxis()
            plt.imshow(np.asarray(prof_img))
            plt.plot(x_prof, label="x profile", color="red")
            plt.plot(y_prof, range(y_prof.size), label="y profile", color="green")
            plt.legend()
            plt.savefig(f'{directory}/{idx}_{char}_profile.png')


            #
        data.to_csv(f'{directory}/data_{h}.csv')
        print(data)

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
                val = np.round(data[col_name][char], 2)
                text = str(val.tolist())
                d_res.text(move_point(xy, (offset, 0)), text, fill=BLACK)
                offset += max_size_width[col]+space

        res_img.save(f'{directory}/all.png')


if __name__ == "__main__":
    print(alphabet)
    main()



