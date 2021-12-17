#!/usr/bin/python3

import random
import sys
import typing
import numpy as np
from PIL import Image, ImageDraw
from funcy import print_durations

Point_type = typing.Tuple[int, int]
Hystogram_type = typing.Dict[int, int]

def default_mask_apply(pix_img, mask, point:Point_type):
    mid_mask = (len(mask)//2, len(mask[0])//2)
    res = np.zeros(len(pix_img[0,0]), dtype=float)
    for imask, mask_row in enumerate(mask):
        for jmask, mask_val in enumerate(mask_row):
            try:
                tmp = np.array(mask_val) * pix_img[point[0]+jmask-mid_mask[0], point[1]+imask-mid_mask[1]]
            except IndexError:
                tmp = [0.]*len(res)
            res += tmp
    return res.astype(int)



def pixel_gen(img:Image, mask=[[1]], default=0, apply_func=default_mask_apply):
    pix = img.load()
    for row in range(img.size[1]):
        for col in range(img.size[0]):
            pos = (col, row)
            yield (pos, tuple(apply_func(pix, mask, pos)))



def xy_gradient(img:Image, G_x, G_y, apply_func=default_mask_apply):
    pix = img.load()
    for row in range(img.size[1]):
        for col in range(img.size[0]):
            pos = (col, row)
            x = np.average(apply_func(pix, G_x, pos))
            y = np.average(apply_func(pix, G_y, pos))
            yield (pos, (x, y))

def G_sqrt(x, y):
    return np.sqrt(x**2+y**2)
def G_abs(x, y):
    return np.abs(x)+np.abs(y)

gradient_functions = [G_sqrt, G_abs]

def gradient(img:Image, G_x, G_y, g_func=gradient_functions[0], apply_func=default_mask_apply):
    for pos, (x, y) in xy_gradient(img, G_x, G_y, apply_func):
        yield (pos, g_func(x, y))


name = sys.argv[-1].split('.')[0]

@print_durations
def main(func=None, lab=0):
    if len(sys.argv) < 2:
        print("no file given")
        return
    image = Image.open(sys.argv[-1])
    draw = ImageDraw.Draw(image)
    for pos, p in pixel_gen(image):
        s = sum(p[:3]) // 3
        draw.point(pos, (s,s,s))
    image.save(f"res_{name}_0.jpg", "JPEG")

    if func:
        res_img = func(image)
        #if res_img:
            #diff_img = difference(noise_image, res_img)
            #diff_img.save("res_" + name + "_diff.jpg", "JPEG")



if __name__ == "__main__":
    main()
