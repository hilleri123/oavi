#!/usr/bin/python3

import random
import sys
import typing
from PIL import Image, ImageDraw


def pixel_gen(img, mask=[[1]], default=0):
    pix = img.load()
    mid_mask = (len(mask)//2, len(mask[0])//2)
    for row in range(img.size[1]):
        for col in range(img.size[0]):
            res = [0]*len(pix[0,0])
            for imask, mask_row in enumerate(mask):
                for jmask, mask_val in enumerate(mask_row):
                    tmp = mask_val * pix[col+jmask-mid_mask[0], row+imask-mid_mask[1]]
                    for tmp_i, tmp_val in enumerate(tmp):
                        res[tmp_i] += tmp_val
            yield ((col, row), res)

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
