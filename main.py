
import io
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

main_screen_setting_box = (1280, 2685, 1370, 2770)


def run(para):
    return subprocess.check_output(var.adb_path + ' ' + para, shell=True)


def get_screen_size():
    out = run(wm_size)
    match = re.search('([0-9]+).([0-9]+)', out.decode())
    return list(map(int, match.groups()))


def check_current_activity(regstr=None):
    out = run(dumpsys_activity)
    match = re.search(r".+mResumedActivity.+", out.decode())
    if (match):
        if regstr is not None:
            return (bool(re.search(regstr, match[0])), match[0])
        else:
            return (None, match[0])
    else:
        return (None, None)


def wait_and_return_from_ads():
    time.sleep(10)
    while (not check_current_activity(var.game)[0]):
        time.sleep(2)
        run(input_keyevent+' 4')
    time.sleep(1)


def check_screen(box=None,im_template=None, p=0.9):
    im = np.frombuffer(run(screencap + ' -p'), dtype=np.uint8)
    im = cv2.imdecode(im, cv2.IMREAD_COLOR)
    if (box):
        im = im[box[1]:box[3], box[0]:box[2]]
    if (im_template is not None):
        out = cv2.matchTemplate(im, im_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(out)
        return (max_val >= p, (min_val, max_val, min_loc, max_loc),im)
    else:
        return (None,None,im)


def check_ocr(im, str=None, p=0.9):
    # this needs to run only once to load the model into memory
    reader = easyocr.Reader(['ch_sim', 'en'])
    ocr = reader.readtext(im)
    if (str is not None):
        for o in ocr:
            if (o[1] == str and o[2] >= p):
                return (True, o, ocr)
        return (False, None, ocr)
    else:
        return (None, None, ocr)


def wait_and_check_ocr(str, p=0.9, box=None):
    while(True):
        im = check_screen(box)[2]
        if (check_ocr(im, str, p)[0]):
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
        if (check_current_activity(var.game)):
            run(input_keyevent+' 4')
            time.sleep(1)
        else:
            wait_and_return_from_ads()

def try_switch_to_main_screen():
    im_temp = cv2.imread('template/main_screen_setting.png')
    time.sleep(5)
    while(not check_screen(main_screen_setting_box,im_temp)[0]):
        run(input_keyevent+' 4')
        time.sleep(2)


while (True):
    out = run('devices')
    match = re.search(var.ip, out.decode())
    if (match):
        break
    run(f'connect {var.ip}:{var.port}')
    time.sleep(1)

out = run(am_start + ' ' + var.game)
run(pointer_location + ' 1')


try_switch_to_main_screen()

# do_ads_1(10)
# do_ads_2(6)

#im = get_screen((1280, 2685, 1370, 2770))
#cv2.imwrite('template/icon.png', im)
#plt.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
#plt.show()

im = check_screen()[2]
plot_ocr(im, check_ocr(im)[2])

#img = cv2.imread


run(pointer_location + ' 0')
print('ok')
