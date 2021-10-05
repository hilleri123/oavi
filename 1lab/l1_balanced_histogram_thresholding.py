#!/usr/bin/python3

import random
import sys
from PIL import Image, ImageDraw

from main import *




@print_durations
def hysto(image, draw):
    h = hystogram(image)[0]
    begin = min(h.keys())
    end = max(h.keys())
    mid = (begin+end)//2
    left = 0
    right = 0
    for key, val in h.items():
        if key <= mid:
            left += val
        else:
            right += val

    while (begin <= end):
        if right > left:
            right -= h.get(end, 0)
            end -= 1
            if (begin + end) // 2 < mid:
                right += h.get(mid, 0)
                left -= h.get(mid, 0)
                mid -= 1
        else:
            left -= h.get(begin, 0)
            begin += 1
            if (begin + end) // 2 < mid:
                left += h.get(mid+1, 0)
                right -= h.get(mid+1, 0)
                mid += 1
    threshold_pix = h.get(mid, 0)

    print(threshold_pix)

    for _, (pos, p) in enumerate(pixel_gen(image)):
        s = 0
        if p[0] < threshold_pix:
            s = 254
        draw.point(pos, (s,s,s))
    image.save("res_"+name+"_1.jpg", "JPEG")



if __name__ == "__main__":
    main(hysto)
