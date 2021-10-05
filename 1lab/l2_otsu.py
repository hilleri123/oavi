#!/usr/bin/python3

import random
import sys
from PIL import Image, ImageDraw

from main import *

def M_h(h:Hystogram_type, t):
    M = [0,0]
    for key, val in h.items():
        M[int(key > t)] += val
    return M


def D_h(h:Hystogram_type, M, t):
    D = [0,0]
    M = M_h(h, t)
    for key, val in h.items():
        D[int(key > t)] += val / sum(h.values()) * (key - M[int(key > t)])**2
    return D


@print_durations
def otsu_calc(h:Hystogram_type):
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
            try:
                threshold_pix = h[t]
            except KeyError:
                tmp = t
                while not tmp in h.keys():
                    tmp -= 1
                threshold_pix = h[tmp]

    return threshold_pix


@print_durations
def otsu(image, draw):
    h = hystogram(image)[0]
    threshold_pix = otsu_calc(h)

    print(threshold_pix)

    for _, (pos, p) in enumerate(pixel_gen(image)):
        s = 0
        if p[0] < threshold_pix:
            s = 254
        draw.point(pos, (s,s,s))
    image.save("res_"+name+"_2.jpg", "JPEG")



if __name__ == "__main__":
    main(otsu)
