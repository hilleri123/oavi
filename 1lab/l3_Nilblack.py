#!/usr/bin/python3

import random
import sys
from PIL import Image, ImageDraw
from main import *

from statistics import mean, stdev

K = -0.2


def new_apply_func(pix_img, mask, point:Point_type):
    mid_mask = (len(mask)//2, len(mask[0])//2)
    pixs = []
    for imask, mask_row in enumerate(mask):
        for jmask, mask_val in enumerate(mask_row):
            try:
                tmp = mask_val * pix_img[point[0]+jmask-mid_mask[0], point[1]+imask-mid_mask[1]]
            except IndexError:
                tmp = [0]*len(pix_img[point])
            pixs.append(tmp[0])
    T = mean(pixs) + K * stdev(pixs)

    if ((np.array(pix_img[point]) > T).all()):
        return (0,0,0)
    return (254, 254, 254)


@print_durations
def nilblack(image, draw):
    integral_img = integral_copy(image)
    integral_img.save("integral.jpg", "JPEG")
    mask = [[1]*15]*15

    for pos, p in pixel_gen(integral_img, mask=mask, apply_func=new_apply_func):
        draw.point(pos, p)



    image.save("res_"+name+"_3.jpg", "JPEG")



if __name__ == "__main__":
    main(nilblack)
