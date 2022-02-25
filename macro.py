import pyautogui as gui
import sys
import time


def get_pos():
    x, y = gui.position()
    print(x, y)
    return x, y


def grab_window(pos):
    gui.moveTo(pos)
    gui.click()


def type_command(cmd):
    gui.typewrite(cmd)


def press_key(key):
    gui.press(key)


def run_command(cmd):
    gui.typewrite(cmd)
    gui.press('enter')


def run_script(script):
    with open(script, "r") as fd:
        for line in fd:
            cmd = line.replace('\n', '')

            if cmd.isnumeric():
                time.sleep(int(cmd))
                continue

            run_command(cmd)


if __name__ == "__main__":
    print(get_pos())
