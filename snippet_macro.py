import pyautogui as gui
import sys
import time

def get_pos():
    x, y = gui.position()
    print(x, y)
    return x, y


def type_enter(cmd):
    gui.typewrite(cmd)
    gui.press('enter')


def run_script(script):
    with open(script, "r") as fd:
        for line in fd:
            cmd = line.replace('\n', '')

            if cmd.isnumeric():
                time.sleep(int(cmd))
                continue

            type_enter(cmd)


def log_on(pos):
    gui.moveTo(pos)
    gui.click()
    type_enter("log out_asm")


def view_disass(pos):
    gui.moveTo(pos)
    gui.click()
    type_enter("disass $pc, $pc+1")


def gdb_ni_ready(pos):
    gui.moveTo(pos)
    gui.click()
    gui.typewrite("ni")


def gdb_ni_enter(pos):
    gui.moveTo(pos)
    gui.click()
    gui.press('enter')


def log_off(pos):
    gui.moveTo(pos)
    gui.click()
    type_enter("log none")


def pre_flush(shell1, shell2):
    log_on(shell2)
    gdb_ni_enter(shell1)
    log_off(shell2)

    gui.moveTo(shell1)
    gui.click()
    type_enter("r")
    time.sleep(1)
    type_enter("y")
    time.sleep(3)



if __name__=="__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    script = sys.argv[2] if len(sys.argv) > 2 else None

    shell1_pos = 211, 1026
    shell2_pos = 1090, 783

    if script:
        gui.moveTo(shell1_pos)
        gui.click()
        run_script(script)
        gui.moveTo(shell2_pos)
        gui.click()
        type_enter("netcat 127.0.0.1 55555")

    pre_flush(shell1_pos, shell2_pos)
    for i in range(0, count):
        view_disass(shell1_pos)
        gdb_ni_ready(shell1_pos)
        log_on(shell2_pos)
        gdb_ni_enter(shell1_pos)
        log_off(shell2_pos)

