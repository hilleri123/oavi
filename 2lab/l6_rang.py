#!/usr/bin/python3

from main import *

lab = 6

def new_apply_func(pix_img, mask, point:Point_type):
    mid_mask = (len(mask)//2, len(mask[0])//2)
    pixs = np.empty((len(mask), len(mask[0]), len(pix_img[point])))
    for imask, mask_row in enumerate(mask):
        for jmask, mask_val in enumerate(mask_row):
            try:
                tmp = np.array(pix_img[point[0]+jmask-mid_mask[0], point[1]+imask-mid_mask[1]]) * np.array(mask_val)
                #print(tmp)
            except IndexError:
                tmp = np.zeros(len(pix_img[point]))
            pixs[imask, jmask] = tmp

    if np.sum(pixs) >= 255*len(pix_img[point]):
        return (255, 255, 255)
    elif np.sum(pixs) <= 255*len(pix_img[point]):
        return (0,0,0)
    else:
        return pix_img[point]


@print_durations
def rang(image, noise_img):
    r3 = 1/3
    r4 = 1/4
    r5 = 1/5
    r6 = 1/6
    masks = {'rang3':
            [[r3,r3,r3],
             [r3,r3,r3],
             [r3,r3,r3]],
            'rang4':
            [[r4,r4,r4],
             [r4,r4,r4],
             [r4,r4,r4]],
            'rang5':
            [[r5,r5,r5],
             [r5,r5,r5],
             [r5,r5,r5]],
            'rang6':
            [[r6,r6,r6],
             [r6,r6,r6],
             [r6,r6,r6]],
            }

    res = image.copy()
    for mask_name, mask in masks.items():
        tmp_res = res.copy()
        draw = ImageDraw.Draw(tmp_res)
        for pos, p in pixel_gen(res, mask=mask, apply_func=new_apply_func):
            draw.point(pos, p)
    
    
        tmp_res.save(f"res_{name}_{mask_name}_{lab}.jpg", "JPEG")
    
        diff_img = difference(noise_img, tmp_res)
        diff_img.save(f"res_{name}_diff_{mask_name}_{lab}.jpg", "JPEG")
    return res


if __name__ == "__main__":
    main(rang, lab)


