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


if __name__=="__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    script = sys.argv[2] if len(sys.argv) > 2 else None

    shell1_pos = 211, 1026
    shell2_pos = 1090, 783

    if script:
        grab_window(shell1_pos)
        run_script(script)
        grab_window(shell2_pos)
        run_command("netcat 127.0.0.1 55555")

    pre_flush(shell1_pos, shell2_pos)
    for i in range(0, count):
        view_disass(shell1_pos)
        gdb_ni_ready(shell1_pos)
        log_on(shell2_pos)
        gdb_ni_enter(shell1_pos)
        log_off(shell2_pos)

