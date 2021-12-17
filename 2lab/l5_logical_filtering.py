#!/usr/bin/python3

from main import *

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
def logical_filtering(image, noise_img):
    res = image.copy()
    draw = ImageDraw.Draw(res)
    mask = [[1,1,1],
            [1,0,1],
            [1,1,1]]

    for pos, p in pixel_gen(res, mask=mask, apply_func=new_apply_func):
        draw.point(pos, p)


    res.save(f"res_{name}_5.jpg", "JPEG")

    diff_img = difference(noise_img, res)
    diff_img.save(f"res_{name}_diff_5.jpg", "JPEG")
    return res


if __name__ == "__main__":
    main(logical_filtering, 5)


