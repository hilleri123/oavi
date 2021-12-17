#!/usr/bin/python3

from main import *

lab_num = 56

@print_durations
def l56_grad(image):
    G_x =  [[ 3, 0, -3],
            [10, 0,-10],
            [ 3, 0, -3]]
    G_y =  [[ 3, 10, 3],
            [ 0,  0, 0],
            [-3,-10,-3]]
    o = (255,255,255)
    x = (0,0,0)

    rang = 230
    for var, g_func in zip([5,6],gradient_functions):
        res = image.copy()
        draw = ImageDraw.Draw(res)
        for pos, g in gradient(image, G_x, G_y, g_func=g_func):
            if g > rang:
                draw.point(pos, x)
            else:
                draw.point(pos, o)
        res.save(f"res_{name}_rang{rang}_{var}.jpg", "JPEG")

    return image


if __name__ == "__main__":
    main(l56_grad, lab_num)


