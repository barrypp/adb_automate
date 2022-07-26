import os
import re
import time
from subprocess import check_output

import var

am_start = ['shell','am','start','-n']
pointer_location = ['shell','settings','put','system','pointer_location']
input_tap = ['shell','input','tap']
input_keyevent = ['shell','input','keyevent']
dumpsys_activity = ['shell','dumpsys','activity','a']

def run(para):
    check_output(var.adb_path + para)

def get_current_activity():
    out = run(dumpsys_activity)
    match = re.search(r".+mResumedActivity.+",out.decode())
    if (match):
        return match[0]

def check_current_activity(regstr):
    return bool(re.search(regstr,get_current_activity()))

def wait_and_return_from_ads():
    time.sleep(1)
    while (not check_current_activity(var.game)):
        time.sleep(1)
        run(input_keyevent+['4'])


def do_ads_1(count):
    while(count):
        count -= 1
        run(input_tap+['770','2500'])
        wait_and_return_from_ads()


while (True):
    out = run(['devices'])
    match = re.search(var.ip,out.decode())
    if (match): break
    run(['connect',f'{var.ip}:{var.port}'])
    time.sleep(1)

out = run(am_start + [var.game])
run(pointer_location+['1'])

do_ads_1(6)

run(pointer_location+['0'])
print('ok')