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


def get_moment(img:Image, p:int, q:int, x_c:int, y_c:int, r:Rect=None):
    m = 0
    for (x, y), pix in pixel_gen(img, r=r):
        if not r is None:
            x -= r.start[0]
            y -= r.start[1]
        m += (x-x_c)**p * (y-y_c)**q * pix
    return m 


def calc_weight(img:Image, _:pd.Series, r:Rect=None):
    w = 0
    for (x, y), pix in pixel_gen(img, r=r):
        w += pix
    return w

def calc_norm_weight(img:Image, acc:pd.Series, r:Rect=None):
    sub = img.size[0]*img.size[1]
    if not r is None:
        sub = r.size[0]*r.size[1]
    return acc[header_names[0][0]] / sub

def calc_center_of_gravity(img:Image, acc:pd.Series, r:Rect=None):
    res = [0,0]
    for idx, (p, q) in enumerate([(1, 0), (0, 1)]):
        for (x, y), pix in pixel_gen(img, r=r):
            if not r is None:
                x -= r.start[0]
                y -= r.start[1]
            res[idx] += x**p * y**q * pix
    return tuple(i/acc[header_names[0][0]] for i in res)

def calc_norm_center_of_gravity(img:Image, acc:pd.Series, r:Rect=None):
    size = img.size
    if not r is None:
        size = r.size
    return tuple((pos-1)/(size[idx]-1) for idx, pos in enumerate(acc[header_names[2][0]]))

def calc_axial_moments(img:Image, acc:pd.Series, r:Rect=None):
    res = [0,0]
    x_c, y_c = acc[header_names[2][0]]
    for idx, (p, q) in enumerate([(0, 2), (2, 0)]):
        res[idx] = get_moment(img, p=p, q=q, x_c=x_c, y_c=y_c, r=r)
    return tuple(res)

def calc_norm_axial_moments(img:Image, acc:pd.Series, r:Rect=None):
    sub = sum(acc[header_names[4][0]])
    return tuple(i/sub for i in acc[header_names[4][0]])

#def calc_profiles(img:Image, acc:pd.Series):
    #return (0,0)

header_names = (
        ("weight",calc_weight), #0
        ("norm weight",calc_norm_weight), #1
        ("center of gravity",calc_center_of_gravity), #2
        ("norm CenterOfGravity",calc_norm_center_of_gravity), #3
        ("axial moments (h, v)",calc_axial_moments), #4
        ("norm axial moments",calc_norm_axial_moments), #5
        #("profiles",calc_profiles), #6
        )

norm_attr = tuple(header_names[i][0] for i in [1,3,5])
print(norm_attr)

def distance(s0:pd.Series, s1:pd.Series):
    d = 0
    for attr in norm_attr:
        if isinstance(s0[attr], Iterable):
            tmp_d = 0
            for i, j in zip(s0[attr], s1[attr]):
                tmp_d += (i-j)**2
            d += tmp_d
        else:
            d += (s0[attr]-s1[attr])**2
    return 1-np.sqrt(d)


def main():
    height = [12, 15, 30]
    fonts = ["dejavy/DejaVuSansCondensed.ttf", "freefont/FreeMono.ttf", "croscore/Arimo-Italic.ttf"]

    threshould = [0.95, 0.6]
    space = 4

    base_directory = "pics"
    if not os.path.exists(base_directory):
        os.makedirs(base_directory)

    char_directory = f"{base_directory}/chars"
    if not os.path.exists(char_directory):
        os.makedirs(char_directory)


    base_h = 12
    base_fnt = ImageFont.truetype(f"/usr/share/fonts/truetype/{fonts[0]}", base_h)
    base_data = pd.DataFrame({cl_name:[] for cl_name, _ in header_names})
    for idx, char in enumerate(progress.bar(alphabet)):
        char_size = base_fnt.getsize(char)
        img = Image.new('RGB', char_size, color = WHITE)
        d = ImageDraw.Draw(img)
        d.text((0,0), char, font=base_fnt, fill=BLACK)
        
        pixs = img.load()
        top_y = 0
        end_loop = False
        for y in range(img.size[1]):
            top_y = y
            for x in range(img.size[0]):
                if pixs[x, y][0] < WHITE[0]/2:
                    end_loop = True
                    break
            if end_loop:
                break

        img = img.crop((0, top_y, img.size[0], img.size[1]))
        img.save(f"{char_directory}/{idx}.png")

        row = pd.Series(name=char)
        for col, (col_name, func) in enumerate(header_names):
            row = row.append(pd.Series({col_name:func(img, row)}))
        row.name = char
        base_data = base_data.append(row)

    base_data.to_csv(f'{base_directory}/base_data_{base_h}.csv')
    print(base_data)

    for h in height:
        directory = f"{base_directory}/alpabet{h}"
        if not os.path.exists(directory):
            os.makedirs(directory)

        fnt = ImageFont.truetype(f"/usr/share/fonts/truetype/{fonts[0]}", h)

        img = Image.new('RGB', (space+fnt.getsize(alphabet)[0]+space, space+h+space), color = WHITE)
        d = ImageDraw.Draw(img)
        d.text((space, space), alphabet, font=fnt, fill=BLACK)
        img.save(f'{directory}/base.png')


        seg_img = img.copy()
        f = plt.figure()
        ax = f.add_subplot(111)
        ax.imshow(np.asarray(seg_img))

        x_prof, y_prof = get_profile(img)

        rects = []
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
                res_r = Rect(start=(left_x-1, top_y-1,), end=(x, bottom_y,))
                rects.append(res_r)
                rect = Rectangle(res_r.start, res_r.size[0], res_r.size[1], linewidth=1, edgecolor='green', facecolor='none')
                ax.add_patch(rect)
            prev_y = y
        f.savefig(f'{directory}/{h}_seg.png')
        plt.close(f)


        
        print('rects')
        data = pd.DataFrame({char_name:[] for char_name in base_data.index})
        for idx_r, rect in enumerate(progress.bar(rects)):
            tmp_data = pd.Series(name=idx)
            for col, (col_name, func) in enumerate(header_names):
                tmp_data = tmp_data.append(pd.Series({col_name:func(img, tmp_data, r=rect)}))

            row = pd.Series()
            for idx, base_row in base_data.iterrows():
                row = row.append(pd.Series({idx:distance(base_row, tmp_data)}))
            row.name = idx_r
            data = data.append(row)

        data.to_csv(f'{directory}/data_{h}.csv')
        print(data)









if __name__ == "__main__":
    print(alphabet)
    main()



