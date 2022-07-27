
import re
import subprocess
import time

import cv2
import easyocr
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import var

am_start = 'shell am start -n'
pointer_location = 'shell settings put system pointer_location'
input_tap = 'shell input tap'
input_keyevent = 'shell input keyevent'
dumpsys_activity = 'shell dumpsys activity a'
screencap = 'exec-out screencap'
wm_size = 'shell wm size'


def run(para):
    return subprocess.check_output(var.adb_path + ' ' + para, shell=True)


def get_screen_size():
    out = run(wm_size)
    match = re.search('([0-9]+).([0-9]+)', out.decode())
    return list(map(int, match.groups()))


def get_current_activity():
    out = run(dumpsys_activity)
    match = re.search(r".+mResumedActivity.+ (com.+) ", out.decode())
    if (match):
        return match.group(1)


def get_screen(box=None):
    im = np.frombuffer(run(screencap + ' -p'), dtype=np.uint8)
    im = cv2.imdecode(im, cv2.IMREAD_COLOR)
    if (box is not None):
        return im[box[1]:box[3], box[0]:box[2]]
    else:
        return im


def match_icon(im, im_temp, p=0.9):
    out = cv2.matchTemplate(im, im_temp, cv2.TM_CCOEFF_NORMED)
    return cv2.minMaxLoc(out)[1] >= p


def search_icon(im, im_temp):
    out = cv2.matchTemplate(im, im_temp, cv2.TM_CCOEFF_NORMED)
    return cv2.minMaxLoc(out)


def get_ocr(im):
    reader = easyocr.Reader(['ch_sim', 'en'])
    return reader.readtext(im)


def match_ocr(ocr, str, p=0.9):
    for o in ocr:
        if (o[1] == str and o[2] >= p):
            return True


def search_ocr(ocr, str, p=0.9):
    for o in ocr:
        if (o[1] == str and o[2] >= p):
            return o


def wait_and_match_ocr(str, p=0.9, box=None):
    while(True):
        im = get_screen(box)
        if (match_ocr(get_ocr(im), str, p)):
            return
        time.sleep(1)


def plot_ocr(im, text):
    image = Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image)
    fnt = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 40)
    for t in text:
        draw.polygon(list(np.asarray(t[0]).flat), outline="red")
        draw.text(t[0][3], f'{t[1]}|{t[2]:0.2f}', font=fnt, fill='red')
    plt.imshow(image)
    plt.show()

# -----------------------------


def do_ads_1(count):
    run(input_tap+' 840 2900')
    while(count):
        count -= 1
        run(input_tap+' 770 2500')
        wait_and_return_from_ads()


def do_ads_2(count):
    while(count):
        count -= 1
        run(input_tap+' 1300 700')
        time.sleep(0.5)
        run(input_tap+' 1000 1700')
        run(input_tap+' 1000 1900')
        time.sleep(0.5)
        if (get_current_activity() == var.game):
            try_switch_to_main_screen()
        else:
            wait_and_return_from_ads()


def wait_and_return_from_ads():
    time.sleep(10)
    while (get_current_activity() != var.game):
        time.sleep(5)
        run(input_keyevent+' 4')
    time.sleep(1)


def try_switch_to_main_screen():
    im_temp = cv2.imread('template/main_screen_setting.png')
    time.sleep(2)
    while(not match_icon(get_screen((1280, 2685, 1370, 2770)), im_temp)):
        run(input_keyevent+' 4')
        time.sleep(2)


if __name__ == "__main__":

    while (True):
        out = run('devices')
        match = re.search(var.ip, out.decode())
        if (match):
            break
        out = run(f'connect {var.ip}:{var.port}')
        print(out.decode())
        time.sleep(1)

    out = run(am_start + ' ' + var.game)
    run(pointer_location + ' 1')

    try_switch_to_main_screen()

    do_ads_1(2)
    #do_ads_2(30)

    #im = get_screen((1280, 2685, 1370, 2770))
    #cv2.imwrite('template/icon.png', im)
    #plt.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
    #plt.show()

    #im = get_screen()
    #plot_ocr(im, get_ocr(im))

    run(pointer_location + ' 0')
    print('ok')
