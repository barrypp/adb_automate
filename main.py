
import io
import re
import time
from subprocess import check_output

import easyocr
import numpy
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
    return check_output(var.adb_path + ' ' + para, shell=True)

def get_screen_size():
    out = run(wm_size)
    match = re.search('([0-9]+).([0-9]+)',out.decode())
    return list(map(int,match.groups()))

def get_current_activity():
    out = run(dumpsys_activity)
    match = re.search(r".+mResumedActivity.+", out.decode())
    if (match):
        return match[0]


def check_current_activity(regstr):
    out = get_current_activity()
    print(out)
    return bool(re.search(regstr, out))


def wait_and_return_from_ads():
    time.sleep(10)
    while (not check_current_activity(var.game)):
        time.sleep(2)
        run(input_keyevent+' 4')
    time.sleep(1)

def get_screen(box=None):
    image = Image.open(io.BytesIO(run(screencap + ' -p')))
    return image.crop(box)

def get_ocr(image):
    reader = easyocr.Reader(['ch_sim','en']) # this needs to run only once to load the model into memory
    return reader.readtext(numpy.asarray(image))

def plot_ocr(image,text):
    draw = ImageDraw.Draw(image)
    fnt = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 40)
    for t in text:
        draw.polygon(list(numpy.asarray(t[0]).flat),outline ="red")
        draw.text(t[0][3],f'{t[1]}|{t[2]:0.2f}',font=fnt,fill='red')
    image.show()

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


while (True):
    out = run('devices')
    match = re.search(var.ip, out.decode())
    if (match):
        break
    run(f'connect {var.ip}:{var.port}')
    time.sleep(1)

out = run(am_start + ' ' + var.game)
run(pointer_location + ' 1')

#do_ads_1(6)
#do_ads_2(6)

im = get_screen()
plot_ocr(im,get_ocr(im))


run(pointer_location + ' 0')
print('ok')
