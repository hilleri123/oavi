#!/usr/bin/python3

import random
import sys
from PIL import Image, ImageDraw


def pixel_gen(img):
    pix = img.load()
    for row in range(img.size[1]):
        for col in range(img.size[0]):
            yield ((col, row), pix[col, row])



def hystogram(img):
    res = None
    for _, (_, p) in enumerate(pixel_gen(img)):
        if res is None:
            res = [{} for _ in p]
        for i, val in enumerate(p):
            if val in res[i].keys():
                res[i][val] += 1
            else:
                res[i][val] = 1
    return res

def main():
    if len(sys.argv) < 2:
        print("no file given")
        return
    image = Image.open(sys.argv[-1])
    draw = ImageDraw.Draw(image)
    for _, (pos, p) in enumerate(pixel_gen(image)):
        s = sum(p[:3]) // 3
        draw.point(pos, (s,s,s))
    image.save("res_0.jpg", "JPEG")

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
    image.save("res_1.jpg", "JPEG")



if __name__ == "__main__":
    main()
