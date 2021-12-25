#!/usr/bin/python3

from PIL import Image, ImageDraw, ImageFont
import sys
from clint.textui import progress
import typing
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd
from collections.abc import Iterable 



alphabet = sys.argv[1]

BLACK = (0,0,0)
WHITE = (255,255,255)
GREY = (100,100,100)
Point_type = typing.Tuple[int, int]

class Rect:
    def __init__(self,start:Point_type, end:Point_type=None, size:Point_type=None):
        self.start = start
        if size is None:
            self.size = tuple(j-i for i, j in zip(start, end))
        else:
            self.size = size
        if end is None:
            self.end = tuple(j+i for i, j in zip(start, size))
        else:
            self.end = end



def pixel_gen(img:Image, r:Rect=None, white_black=True):
    pix = img.load()
    if r is None:
        start = (0,0)
        end = (img.size)
    else:
        start = r.start
        end = r.end
    for row in range(start[1], end[1]):
        for col in range(start[0], end[0]):
            pos = (col, row)
            if white_black:
                yield (pos, 0 if pix[pos][0] > WHITE[0]/2 else 1)
            else:
                yield (pos, pix[pos])


def get_profile(img:Image, r:Rect=None):
    res = [np.zeros(i) for i in img.size]
    for pos, pix in pixel_gen(img, r=r, white_black=False):
        res[0][pos[0]] += pix[0]/255
        res[1][pos[1]] += 1-pix[0]/255
    return res



def move_point(p0:Point_type, p1:Point_type):
    return tuple(i+j for i, j in zip(p0, p1))



def main():
    height = [12, 15, 30]
    fonts = ["dejavy/DejaVuSansCondensed.ttf", "freefont/FreeMono.ttf", "croscore/Arimo-Italic.ttf"]

    threshould = [0.95, 0.6]
    space = 4

    base_directory = "pics"
    if not os.path.exists(base_directory):
        os.makedirs(base_directory)
    for h, f in zip(height, fonts):
        directory = f"{base_directory}/alpabet{h}"
        if not os.path.exists(directory):
            os.makedirs(directory)
        fnt = ImageFont.truetype(f"/usr/share/fonts/truetype/{f}", h)

        img = Image.new('RGB', (space+fnt.getsize(alphabet)[0]+space, space+h+space), color = WHITE)
        d = ImageDraw.Draw(img)
        d.text((space, space), alphabet, font=fnt, fill=BLACK)
        img.save(f'{directory}/base.png')

        x_prof, y_prof = get_profile(img)
        prof_img = img.copy()
        f = plt.figure()
        ax = f.add_subplot(111)
        ax.imshow(np.asarray(prof_img))
        ax.plot(x_prof, label="x profile", color="red")
        ax.plot(y_prof, range(y_prof.size), label="y profile", color="green")
        f.savefig(f'{directory}/{h}_profile.png')
        plt.close(f)


        seg_img = img.copy()
        f = plt.figure()
        ax = f.add_subplot(111)
        ax.imshow(np.asarray(seg_img))

        left_x = 0
        prev_y = None
        for x, y in enumerate(progress.bar(x_prof)):
            y = img.size[1] - y
            #print(x, y)
            if prev_y is None:
                prev_y = y
                continue
            if y > threshould[0] and prev_y <= threshould[0]:
                left_x = x
            elif y <= threshould[0] and prev_y > threshould[0]:
                tmp_r = Rect(start=(left_x, 0,), end=(x, img.size[1],))

                _, curr_y_prof = get_profile(img, r=tmp_r)
                top_y = 0
                bottom_y = img.size[1]
                prev_x = None
                for curr_y, curr_x in enumerate(curr_y_prof):
                    if prev_x is None:
                        prev_x = curr_x
                        continue
                    if curr_x > threshould[1] and prev_x <= threshould[1]:
                        top_y = curr_y
                    elif curr_x <= threshould[1] and prev_x > threshould[1]:
                        bottom_y = curr_y
                    prev_x = curr_x
                res_r = Rect(start=(left_x, top_y,), end=(x, bottom_y,))
                rect = Rectangle(res_r.start, res_r.size[0], res_r.size[1], linewidth=1, edgecolor='green', facecolor='none')
                ax.add_patch(rect)
            prev_y = y
        f.savefig(f'{directory}/{h}_seg.png')
        plt.close(f)








if __name__ == "__main__":
    print(alphabet)
    main()



