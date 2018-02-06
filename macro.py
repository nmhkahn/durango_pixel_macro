import argparse
import collections
import keyboard
import pyautogui
import numpy as np
import scipy.misc as misc

num_board = 32
bx, by, bw, bh = 0, 0, 0, 0
is_pressed = False
pyautogui.FAILSAFE = False

def create_palette(path, num_color=40):
    palette = list()
    num_row, num_column = 5, int(num_color/5)

    picker = misc.imread(path, mode="RGB")
    h, w = picker.shape[:2]
    pick_h, pick_w = int((h-num_column*2)/num_column), int(w/num_row)

    for j in range(num_row):
        row = list()
        for i in range(num_column):
            if (j % 2) == 1:
                row.append(picker[i*pick_h+pick_h, j*pick_w+int(pick_w/2)])
            else:
                row.append(picker[i*pick_h+int(pick_h/2), j*pick_w+int(pick_w/2)])
        palette.append(row)

    return palette


def create_draws(im, palette):
    size = im.shape[0]
    draws = collections.OrderedDict()
    for j in range(len(palette)):
        for i in range(len(palette[0])):
            draws["{}{}".format(j,i)] = list()

    def get_palette_index(pixel):
        for j, row in enumerate(palette):
            for i, pick in enumerate(row):
                if np.all(pixel==pick):
                    return j, i
    
    for i in range(size):
        for j in range(size):
            pj, pi = get_palette_index(im[i,j])
            draws["{}{}".format(pj,pi)].append((j, i))

    return draws


def get_board_size():
    def set_xy():
        global bx, by
        bx, by = pyautogui.position()

    def set_wh():
        global bx, by, bw, bh
        tx, ty = pyautogui.position()
        bw, bh = tx-bx, ty-by
    
    print("Aim the position and press w or e. q to quit")
    keyboard.add_hotkey("w", set_xy)
    keyboard.add_hotkey("e", set_wh)
    keyboard.wait("q")

    pixel_w, pixel_h = bw/num_board, bh/num_board
    return pixel_w, pixel_h, bx, by


def draw(draws, pixel_size, start_cord, interval):
    global is_pressed
    pw, ph = pixel_size
    sx, sy = start_cord
    
    for draw in draws:
        x = sx + pw*draw[0]+pw/2
        y = sy + ph*draw[1]+ph/2
        pyautogui.click(x=x, y=y, button="left")
        if keyboard.is_pressed("q"): break

    is_pressed = True


def main():
    global is_pressed
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str)
    parser.add_argument("--interval", default=0.01, type=float)
    args = parser.parse_args()

    im = misc.imread(args.path, mode="RGB")
    palette = create_palette("picker.png", 40)

    draws = create_draws(im, palette)
    pixel_w, pixel_h, start_w, start_h = get_board_size()
    
    for k, v in draws.items():
        if len(v) == 0: continue

        print("Select ({}, {}) picker and press s".format(k[0], k[1:]))
        hk = keyboard.add_hotkey("s", draw, (v, (pixel_w, pixel_h), (start_w, start_h), args.interval))
        while True:
            if is_pressed:
                keyboard.remove_hotkey(hk)
                is_pressed = False
                break

if __name__ == "__main__":
    main()
