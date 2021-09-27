#!/usr/bin/python3

import random
import sys
from PIL import Image, ImageDraw

from main import *

def M_h(hystogram, t):
    M = [0,0]
    for key, val in hystogram.items():
        M[int(key > t)] += val
    return M


def D_h(hystogram, M, t):
    D = [0,0]
    M = M_h(hystogram, t)
    for key, val in hystogram.items():
        D[int(key > t)] += val / sum(hystogram.values()) * (key - M[int(key > t)])**2
    return D


def ekvila(image, draw):
    h = hystogram(image)[0]
    R = Rect(top = 15, bottom = 0, left = 0, right = 15)
    r = Rect(top = 3,  bottom = 0, left = 0, right = 3)
    right_top = image.size
    
    integral_img = integral_copy(image)
    integral_img.save("integral.jpg", "JPEG")
#!!!!!!!!!!!!!!!!!!

    begin = min(h.keys())
    end = max(h.keys())
    max_val = None
    threshold_pix = h[begin]
    pix_count = sum(h.values())
    for t in range(begin, end+1):
        M = M_h(h, t)
        D = D_h(h, M, t)
        D_all = sum([i*j for i, j in zip(M, D)]) / pix_count
        D_cls = M[0] * M[1] * (M[0] - M[1])**2 / pix_count**2
        if max_val == None or max_val < D_cls/D_all:
            threshold_pix = h[t]

    print(threshold_pix)

    for _, (pos, p) in enumerate(pixel_gen(image)):
        s = 0
        if p[0] < threshold_pix:
            s = 254
        draw.point(pos, (s,s,s))
    image.save("res_2.jpg", "JPEG")



if __name__ == "__main__":
    main(ekvila)
