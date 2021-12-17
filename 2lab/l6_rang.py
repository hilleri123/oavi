#!/usr/bin/python3

from main import *

lab = 4

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

    if np.sum(pixs) >= 6*255*len(pix_img[point]):
        return (255, 255, 255)
    elif np.sum(pixs) <= 2*255*len(pix_img[point]):
        return (0,0,0)
    else:
        return pix_img[point]


@print_durations
def median_x(image, noise_img):
    masks = {'hollow':
            [[0,0,1,0,0],
             [0,1,1,1,0],
             [1,1,1,1,1],
             [0,1,1,1,0],
             [0,0,1,0,0]],
            'hill':
            [[1,1,1,1,1],
             [1,0,0,0,1],
             [1,0,1,0,1],
             [1,0,0,0,1],
             [1,1,1,1,1]],
            }

    mask_name = ''
    res = image.copy()
    draw = ImageDraw.Draw(res)
    for curr_mask_name, mask in masks.items():
        mask_name += curr_mask_name
        tmp_res = res.copy()
        for pos, p in pixel_gen(tmp_res, mask=mask, apply_func=new_apply_func):
            draw.point(pos, p)
    
    
        res.save(f"res_{name}_{mask_name}_{lab}.jpg", "JPEG")
    
        diff_img = difference(noise_img, res)
        diff_img.save(f"res_{name}_diff_{mask_name}_{lab}.jpg", "JPEG")
    return res


if __name__ == "__main__":
    main(median_x, lab)


