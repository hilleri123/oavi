#!/usr/bin/python3

from main import *

lab_num = 12

@print_durations
def l12_grad(image):
    G_x =  [[0, 0, 0],
            [0,-1, 0],
            [0, 0, 1]]
    G_y =  [[ 0, 0, 0],
            [ 0, 0,-1],
            [ 0, 1, 0]]
    o = (255,255,255)
    x = (0,0,0)

    rang = 60
    for var, g_func in zip([1,2],gradient_functions):
        res = image.copy()
        res_tmp = image.copy()
        draw = ImageDraw.Draw(res)
        draw_tmp = ImageDraw.Draw(res_tmp)
        for pos, g in gradient(image, G_x, G_y, g_func=g_func):
            if g > rang:
                draw.point(pos, x)
            else:
                draw.point(pos, o)        
            draw_tmp.point(pos, (int(g),)*3)
        res.save(f"res_{name}_rang{rang}_{var}.jpg", "JPEG")
        res_tmp.save(f"res_{name}_gradient{rang}_{var}.jpg", "JPEG")
    return image


if __name__ == "__main__":
    main(l12_grad, lab_num)


