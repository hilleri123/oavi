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
        res = np.zeros(WHITE[0]+1)
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
    res = np.zeros((WHITE[0]+1, WHITE[0]+1))
    hist = np.zeros(WHITE[0]+1)
    func = create_apply_func(d=d, phi=phi)
    max_max = 0
    for pos, (val, row) in progress.bar(pixel_gen(mono_img, func), expected_size=mono_img.size[0]*mono_img.size[1]):
        res[val] += row
        max_max = max(max_max, max(row))
        hist[val] += 1
    res_img = Image.fromarray(np.uint8(res*255/max_max))
    res_img.save(f"{name}_matrix.jpg", "JPEG")
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
    for (i, j), p in progress.bar(pixel_gen(h_img), expected_size=h_img.size[0]*h_img.size[1]):
        res_s["asm"] += p**2
        res_s["con"] += (i-j)**2 * p
        if i == max_i[0] and j == max_j[0]:
            res_s["mpr"] = p 
        res_s["lun"] += p / (1+(i-j)**2)
        if p != 0:
            res_s["ent"] -= p * np.log2(p)
        if i == j:
            res_s["tr"] += p

    return res_s 


def pow_transform(img:Image, _:np.array, c=1.5, f0=0, y=0.3):
    res_img = img.copy()
    d = ImageDraw.Draw(res_img)
    for pos, pixel in pixel_gen(img):
        p = int(WHITE[0] * c * (pixel[0]/WHITE[0] + f0)**y)
        if p > WHITE[0]:
            p = WHITE[0]
        d.point(pos, (p,p,p))
    return res_img

def log_transform(img:Image, hist:np.array, L=8):
    res_img = img.copy()
    d = ImageDraw.Draw(res_img)
    s = np.sum(hist)
    hist /= s
    mean = np.mean(hist)
    pos_range = max(2, np.max(hist)-mean)
    neg_range = max(2, mean-np.min(hist))
    pos_alpha = 2**(L-1) / np.log(pos_range)
    neg_alpha = 2**(L-1) / np.log(neg_range)
    for pos, pixel in pixel_gen(img):
        p = pixel[0] - mean
        if p >= 1:
            p = mean + pos_alpha*np.log(p)
        elif p <= -1:
            p = mean - neg_alpha*np.log(np.abs(p))
        else:
            p = mean
        p = int(p)
        if p > WHITE[0]:
            p = WHITE[0]
        d.point(pos, (p,p,p))
    return res_img

methods = (
        ("pow", pow_transform),
        ("log", log_transform),
        )


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
        directory = f"pics_{idx}"
        if not os.path.exists(directory):
            os.makedirs(directory)

        new_name = f"{directory}/{name}_{idx}"
        tmp_img, hist = Haralic_matrix(new_name, mono_img, d, phi)

        f = plt.figure()
        plt.bar(np.arange(hist.size), hist)
        plt.savefig(f"{new_name}_bar.png")
        plt.close(f)

        calc_params(tmp_img, hist).to_csv(f"{new_name}.csv", header=True)

        for m_idx, (m_name, method) in enumerate(methods):
            new_new_name = f"{new_name}_{m_idx}_{m_name}"
            new_img = method(mono_img, hist)

            new_img.save(f"{new_new_name}.jpg", "JPEG")
            new_tmp_img, new_hist = Haralic_matrix(new_new_name, new_img, d, phi)

            f = plt.figure()
            plt.bar(np.arange(new_hist.size), new_hist)
            plt.savefig(f"{new_new_name}_bar.png")
            plt.close(f)

            calc_params(new_tmp_img, new_hist).to_csv(f"{new_new_name}.csv", header=True)
    


if __name__ == "__main__":
    main()



