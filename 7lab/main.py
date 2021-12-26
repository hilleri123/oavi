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



BLACK = (0,0,0)
WHITE = (255,255,255)
GREY = (100,100,100)
Point_type = typing.Tuple[int, int]




def create_apply_func(d=1, phi=(0,)):
    def apply_func(img:Image, pix, pos:Point_type):
        res = np.zeros(WHITE[0])
        pixs = img.load()
        base_x, base_y = pos
        for angle in phi:
            x = base_x + np.around(np.cos(angle/180*np.pi))*d
            y = base_y + np.around(np.sin(angle/180*np.pi))*d
            if 0 <= x < img.size[0] and 0 <= y < img.size[1]:
                val = pix[x, y][0]
                res[val] += 1
        return (pix[base_x, base_y][0], res)
    return apply_func



def pixel_gen(img:Image, apply_func=lambda img, pix, x: pix[x]):
    pix = img.load()
    for row in range(img.size[1]):
        for col in range(img.size[0]):
            pos = (col, row)
            yield (pos, apply_func(img, pix, pos))


def Haralic_matrix(name:str, mono_img:Image, d:int, phi:tuple):
    res = np.zeros((WHITE[0], WHITE[0]))
    hist = np.zeros(WHITE[0])
    func = create_apply_func(d=d, phi=phi)
    for pos, (val, row) in progress.bar(pixel_gen(mono_img, func), expected_size=mono_img.size[0]*mono_img.size[1]):
        res[val] += row
        hist[val] += 1
    res_img = Image.fromarray(np.uint8(res))
    res_img.save(f"matrix_{name}.jpg", "JPEG")
    return (res_img, hist)



def calc_params(h_img:Image, hist:np.array):
    res_s = pd.Series({"asm":0, "con":0, "mpr":0, "lun":0, "ent":0, "tr":0, "av":0, "d":0})
    max_i, max_j = [0,0], [0,0]
    for idx, p in enumerate(hist):
        if p > max_j[1]:
            max_i = max_j.copy()
            max_j = [idx, p]
        elif p > max_i[1]:
            max_i = [idx, p]
    print(max_i, max_j)
    for (i, j), p in progress.bar(pixel_gen(h_img), expected_size=h_img.size[0]*h_img.size[1]):
        res_s["asm"] += p**2
        res_s["con"] += (i-j)**2 * p
        if i == max_i[0] and j == max_j[0]:
            res_s["mpr"] = p / WHITE[0]
        res_s["lun"] += p / (1+(i-j)**2)
        if p != 0:
            res_s["ent"] -= p * np.log2(p)
        if i == j:
            res_s["tr"] += p

    return res_s 

file_name = sys.argv[-1]

def main():
    name = file_name.split('.')[0]
    mono_img = Image.open(file_name)
    draw = ImageDraw.Draw(mono_img)
    for pos, p in pixel_gen(mono_img):
        s = sum(p[:3]) // 3
        draw.point(pos, (s,s,s))
    mono_img.save(f"mono_{name}.jpg", "JPEG")
    
    haralic_param = (
            (1, (0, 90, 180, 270)),
            (2, (0, 90, 180, 270)),
            (1, (45, 135, 225, 315)),
            (2, (45, 135, 225, 315)),
            )
    for idx, (d, phi) in enumerate(haralic_param):
        tmp_img, hist = Haralic_matrix(f"{name}_{idx}", mono_img, d, phi)
        print(calc_params(tmp_img, hist))
    


if __name__ == "__main__":
    main()



