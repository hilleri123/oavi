#!/usr/bin/python3

import random
import sys
from PIL import Image, ImageDraw
from main import *



#15 - это типа много
t = 0.15


def new_apply_func(pix_img, mask, point:Point_type):
    pix = np.array(default_mask_apply(pix_img, mask, point), dtype=int) / len(mask) / len(mask[0])
    if ((1 - pix_img[point] / pix < t).all()):
        return (0,0,0)
    return (254, 254, 254)


@print_durations
def bernstein(image, draw):
    integral_img = integral_copy(image)
    integral_img.save("integral.jpg", "JPEG")
    mask = [[1,1,1,1,1],
            [1,1,1,1,1],
            [1,1,1,1,1],
            [1,1,1,1,1],
            [1,1,1,1,1],]

    for pos, p in pixel_gen(integral_img, mask=mask, apply_func=new_apply_func):
        draw.point(pos, p)



    image.save("res_"+name+"_5.jpg", "JPEG")



if __name__ == "__main__":
    main(bernstein)
