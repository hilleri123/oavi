#!/usr/bin/python3

import random
import sys
import typing
import numpy as np
from PIL import Image, ImageDraw




def pixel_gen(img, mask=[[1]], default=0):
    pix = img.load()
    mid_mask = (len(mask)//2, len(mask[0])//2)
    for row in range(img.size[1]):
        for col in range(img.size[0]):
            res = np.zeros(len(pix[0,0]), dtype=int)
            for imask, mask_row in enumerate(mask):
                for jmask, mask_val in enumerate(mask_row):
                    try:
                        tmp = mask_val * pix[col+jmask-mid_mask[0], row+imask-mid_mask[1]]
                    except IndexError:
                        tmp = [0]*len(res)
                    res += tmp
            yield ((col, row), tuple(res))


def integral_copy(img):
    res = img.copy()
    res_pix = img.load()
    draw = ImageDraw.Draw(res)
    for (x, y), pix in pixel_gen(res):
        new_pix = np.array(pix)
        if x > 0:
            new_pix += res_pix[x-1, y]
        if y > 0:
            new_pix += res_pix[x, y-1]
        if x > 0 and y > 0:
            new_pix -= res_pix[x-1, y-1]
        draw.point((x, y), tuple(new_pix))
    return res

Point_type = typing.Tuple[int, int]

class Rect:
    def __init__(self, top, bottom, left, right):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

    def move(self, point:Point_type):
        self.left += point[0]
        self.right += point[0]
        self.top += point[1]
        self.bottom += point[1]

    def inside(self, point:Point_type):
        return left <= point[0] and point[0] <= right and bottom <= point[1] and point[1] <= top


def hystogram(img, rect:Rect = None):
    res = None
    for _, (point, pix) in enumerate(pixel_gen(img)):
        if res is None:
            res = [{} for _ in pix]
        if rect == None or rect.inside(point):
            for i, val in enumerate(pix):
                if val in res[i].keys():
                    res[i][val] += 1
                else:
                    res[i][val] = 1
    return res



def main(func=None):
    if len(sys.argv) < 2:
        print("no file given")
        return
    image = Image.open(sys.argv[-1])
    draw = ImageDraw.Draw(image)
    for _, (pos, p) in enumerate(pixel_gen(image)):
        s = sum(p[:3]) // 3
        draw.point(pos, (s,s,s))
    image.save("res_0.jpg", "JPEG")

    if func:
        func(image, draw)



if __name__ == "__main__":
    main()