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
    res = np.zeros(len(pix_img[0,0]), dtype=int)
    for imask, mask_row in enumerate(mask):
        for jmask, mask_val in enumerate(mask_row):
            try:
                tmp = mask_val * pix_img[point[0]+jmask-mid_mask[0], point[1]+imask-mid_mask[1]]
            except IndexError:
                tmp = [0]*len(res)
            res += tmp
    return res



def pixel_gen(img:Image, mask=[[1]], default=0, apply_func=default_mask_apply):
    pix = img.load()
    for row in range(img.size[1]):
        for col in range(img.size[0]):
            pos = (col, row)
            yield (pos, tuple(apply_func(pix, mask, pos)))


def integral_copy(img:Image):
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


def add_noise(img:Image):
    res = img.copy()
    res_pix = img.load()
    draw = ImageDraw.Draw(res)
    for (x, y), pix in pixel_gen(res):
        if np.random.rand(1) > 0.7:
            new_pix = np.empty(np.array(pix).size, dtype=int)
            new_pix.fill(int(np.random.randint(2)*255))
            draw.point((x, y), tuple(new_pix))
    return res

def difference(first:Image, last:Image):
    res = first.copy()
    res_pix = first.load()
    last_pix = last.load()
    draw = ImageDraw.Draw(res)
    for (x, y), pix in pixel_gen(res):
        new_pix = np.array(pix)
        new_pix -= np.array(last_pix[x, y])
        draw.point((x, y), tuple(np.absolute(new_pix)))
    return res



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
    noise_image = add_noise(image)
    noise_image.save(f"res_{name}_noise_{lab}.jpg", "JPEG")

    if func:
        res_img = func(image, noise_image)
        #if res_img:
            #diff_img = difference(noise_image, res_img)
            #diff_img.save("res_" + name + "_diff.jpg", "JPEG")



if __name__ == "__main__":
    main()
