#!/usr/bin/python3

import random
import sys
from PIL import Image, ImageDraw
from main import *

from statistics import mean, stdev

k = 0.5


def new_apply_func(pix_img, mask, point:Point_type, res_func):
    mid_mask = (len(mask)//2, len(mask[0])//2)
    pixs = []
    for imask, mask_row in enumerate(mask):
        for jmask, mask_val in enumerate(mask_row):
            try:
                tmp = mask_val * pix_img[point[0]+jmask-mid_mask[0], point[1]+imask-mid_mask[1]]
            except IndexError:
                tmp = [0]*len(pix_img[point])
            pixs.append(tmp[0])

    return res_func(pixs, pix_img[point])


def kristian_res_func(pixs, pix, R, M):
    T = (1-k)*mean(pixs) + k*M + k*stdev(pixs)/R*(mean(pixs)-M)

    if ((np.array(pix) > T).all()):
        return (0,0,0)
    return (254, 254, 254)


@print_durations
def kristian(image, draw):
    h = hystogram(image)[0]
    integral_img = integral_copy(image)
    integral_img.save("integral.jpg", "JPEG")
    mask = [[1]*15]*15

    R = 0
    R_func = lambda pix_img, mask, point:new_apply_func(pix_img, mask, point, lambda pixs, _: [stdev(pixs)]*3)
    for pos, p in pixel_gen(integral_img, mask=mask, apply_func=R_func):
        R = max(R, p[0])
    M = min(h.values())
    print(R, M)

    in_func = lambda pixs, pix: kristian_res_func(pixs, pix, R, M)
    ultra_new_apply_func = lambda pix_img, mask, point:new_apply_func(pix_img, mask, point, in_func)

    for pos, p in pixel_gen(integral_img, mask=mask, apply_func=ultra_new_apply_func):
        draw.point(pos, p)



    image.save("res_"+name+"_4.jpg", "JPEG")



if __name__ == "__main__":
    main(kristian)
