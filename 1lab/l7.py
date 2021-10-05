#!/usr/bin/python3

import random
import sys
from PIL import Image, ImageDraw
from main import *


from l2_otsu import otsu_calc

#15 - это типа много
e = 15


@print_durations
def ekvila(image, draw):
    R = Rect(top = 15, bottom = 0, left = 0, right = 15)
    R.move((-6,-6))
    r = Rect(top = 3,  bottom = 0, left = 0, right = 3)
    right_top = image.size
    
    integral_img = integral_copy(image)
    integral_img.save("integral.jpg", "JPEG")
    pix_img = image.load()
    #pix_img = integral_img.load()

    right_point = (3,0)
    top_point = (0,3)
    R_left = (-6,0)
    while r.top <= right_top[1]:
        print(r.top, r.right)
        small_h = hystogram(integral_img, r)[0]
        big_h = hystogram(integral_img, r)[0]
        M = sum(big_h.values())/255
        if abs(M-sum(small_h.values())/9) >= e:
            T = otsu_calc(big_h)
            for (x, y) in r:
                s = 0
                if pix_img[x,y][0] < T:
                    s = 254
                draw.point((x, y), (s,s,s))
        else:
            for (x, y) in r:
                p = int(M>254/2)
                draw.point((x, y), (p,p,p))

        r.move(right_point)
        R.move(right_point)
        if r.left >= right_top[0]:
            r.move_to_left()
            R.move_to_left()
            R.move(R_left)
            r.move(top_point)
            R.move(top_point)


#!!!!!!!!!!!!!!!!!!


    image.save("res_"+name+"_6.jpg", "JPEG")



if __name__ == "__main__":
    main(ekvila)
