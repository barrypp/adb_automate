
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

keycode_back = 4
t_start = time.perf_counter()

ignore_warning = [b'Warning: Activity not started, intent has been delivered to currently running top-most instance.\r\n',
                  b'Warning: Activity not started, its current task has been brought to the front\r\n']


def run(para):
    out = subprocess.run(var.adb_path + ' ' + para,
                         shell=True, capture_output=True)
    if (out.stderr):
        if (out.stderr not in ignore_warning):
            print(out.args, f'| returncode: {out.returncode}', f' | stdout len: {len(out.stdout)} |', out.stderr)
    return out.stdout


def get_logt():
    return f'{time.perf_counter()-t_start:0.3f}s'

def in_game():
    return get_current_activity() == var.game 


def tap(x, y, delay=0.5):
    #print(f'tap {x},{y} {delay}s')
    run(input_tap+f' {x} {y}')
    time.sleep(delay)


def keyevent(code, delay=0.5):
    run(input_keyevent + f' {code}')
    time.sleep(delay)


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
    while(count):
        count -= 1
        print(get_logt()+f' do_ads_1 count: {count}')
        tap(840, 2900)
        tap(770, 2500)
        wait_ads_and_back()
        try_switch_to_main_screen()


def do_ads_2(count):
    while(count):
        count -= 1
        print(get_logt()+f' do_ads_2 count: {count}')
        tap(1300, 700)
        tap(1000, 1700)
        if (in_game()):
            tap(1000, 1900)
        wait_ads_and_back()
        try_switch_to_main_screen()


def do_ads_3(count):
    im_temp = cv2.imread('template/ads_vip.png')
    dy0, dx0, _ = im_temp.shape
    x1, y1, x2, y2 = (1178, 573, 1440, 1347)
    while(count):
        count -= 1
        print(get_logt()+f' do_ads_2 count: {count}')
        _, m, _, (dx, dy) = search_icon(get_screen((x1, y1, x2, y2)), im_temp)
        if (m >= 0.9):
            print(get_logt()+' do_ads_2 detected')
            tap(x1+dx+dx0/2, y1+dy+dy0/2)
            tap(1000, 1900)
            wait_ads_and_back()
            try_switch_to_main_screen()
        time.sleep(30)


def wait_ads_and_back():
    time.sleep(2)
    if (in_game()):
        return
    time.sleep(40)
    keyevent(keycode_back)
    if (not in_game()):
        tap(1384, 61)
    if (not in_game()):
        run(am_start + ' ' + var.game)


def try_switch_to_main_screen():
    run(am_start + ' ' + var.game)
    im_temp = cv2.imread('template/main_screen_setting.png')
    while(not match_icon(get_screen((1280, 2685, 1370, 2770)), im_temp)):
        keyevent(keycode_back)
        if (not in_game()):
            run(am_start + ' ' + var.game)
            time.sleep(5)


if __name__ == "__main__":

    while (True):
        out = run('devices').decode()
        if (re.search('offline', out)):
            run('kill-server')
            continue
        if (re.search(f'{var.ip}:{var.port}', out)):
            break
        print(run(f'connect {var.ip}:{var.port}').decode())
        time.sleep(1)

    run(pointer_location + ' 1')
    try_switch_to_main_screen()

    #do_ads_1(4)
    # do_ads_2(30)
    do_ads_3(100)

    #im = get_screen()
    #cv2.imwrite('template/icon.png', im)
    #plt.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
    # plt.show()

    #im = get_screen()
    #plot_ocr(im, get_ocr(im))

    run(pointer_location + ' 0')
    print('ok')
