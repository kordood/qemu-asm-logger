import datetime
import sys
from time import sleep, time

import macro

from typing import List


class QEMUMonitor:
    def __init__(self,
                 position: (int, int),
                 address: str,
                 port: str or int
                 ):
        self.position = position
        self.address = address
        self.port = port

    # Todo: use decorator to grab window
    def attach(self):
        macro.grab_window(self.position)
        cmd = f"netcat {self.address} {self.port}"
        macro.run_command(cmd)

    def log_on(self):
        macro.grab_window(self.position)
        macro.run_command("log out_asm")

    def log_off(self):
        macro.grab_window(self.position)
        macro.run_command("log none")


class QEMURunner:
    def __init__(self,
                 position: (int, int),
                 qemu: str,
                 options: str = '',
                 redirect: str = "/dev/null"
                 ):
        self.position = position
        self.qemu_binary = qemu

        if redirect:
            options += f" &>{redirect}"

        self.qemu_options = options
        self.boot_finish = False
        self.boot_qemu()
        sleep(80)
        self.logfile = open(redirect, "r")
        self.log_buffer = ""
        self.print_out()
        self.boot_finish = True

    def boot_qemu(self):
        macro.grab_window(self.position)
        script = f"{self.qemu_binary} {self.qemu_options}"
        macro.run_command(script)

    def login(self, id, pw=None):
        macro.grab_window(self.position)
        macro.run_command(id)

        if pw:
            sleep(1)
            macro.run_command(pw)

        sleep(3)

    def logout(self):
        macro.grab_window(self.position)
        macro.run_command("exit")
        sleep(4)

    def view_disass(self):
        macro.grab_window(self.position)
        macro.run_command("disass $pc, $pc+1")

    def standby_gdb_ni(self):
        macro.grab_window(self.position)
        macro.type_command("ni")

    def enter_gdb_ni(self):
        macro.grab_window(self.position)
        macro.press_key('enter')

    def rerun_gdb(self):
        macro.grab_window(self.position)
        macro.run_command("r")
        sleep(1)
        macro.run_command("y")
        sleep(3)

    def print_out(self, timeout: int = 0):
        self.flush_log_buffer()
        previous_tell = self.logfile.tell()
        current_time = time()

        while True:
            log_line = self.logfile.readline()
            self.log_buffer += log_line
            print(log_line)
            current_tell = self.logfile.tell()

            if timeout > 0:
                time_gap = time() - current_time
                if timeout <= time_gap:
                    break

            if previous_tell == current_tell or log_line == '':
                break

    def flush_log_buffer(self):
        self.log_buffer = ""


class QEMUManager:
    def __init__(self,
                 positions: List,
                 qemu: str,
                 options: str = '',
                 redirect: str = "/dev/null",
                 monitor_addr: str = "127.0.0.1",
                 monitor_port: str or int = "55555",
                 id="root",
                 pw=None
                 ):
        assert len(positions) >= 2

        if isinstance(monitor_port, int):
            monitor_port = str(monitor_port)

        if "-monitor" in options:
            monitor_addr, monitor_port = self.parse_monitor_option(options)
        else:
            monitor_option = f" -monitor telnet:{monitor_addr}:{monitor_port},server,nowait"
            options += monitor_option

        self.positions = positions
        self.runner = QEMURunner(positions[0], qemu=qemu, options=options, redirect=redirect)
        self.runner.login(id=id, pw=pw)
        sleep(1)
        self.monitor = QEMUMonitor(positions[1], address=monitor_addr, port=monitor_port)
        self.monitor.attach()

    @staticmethod
    def parse_monitor_option(option: str) -> (str, str):
        monitor_option = option.split("-monitor ")[-1]
        if ' ' in monitor_option:
            monitor_option = monitor_option.split(' ', 1)[0]

        if ',' in monitor_option:
            monitor_option = monitor_option.split(',', 1)[0]

        network_info = monitor_option.split(':')
        address = network_info[1]
        port = network_info[2]
        return address, port

    def pre_flush(self):
        self.runner.standby_gdb_ni()
        self.monitor.log_on()
        self.runner.enter_gdb_ni()
        self.monitor.log_off()
        self.runner.rerun_gdb()


if __name__ == '__main__':
    pos1_x = sys.argv[1]
    pos1_y = sys.argv[2]
    pos2_x = sys.argv[3]
    pos2_y = sys.argv[4]
    positions = [(pos1_x, pos1_y), (pos2_x, pos2_y)]
    now = datetime.datetime.now().strftime("%d-%m-%Y-%H:%M:%S")
    logfile = f"log_{now}.txt"

    manager = QEMUManager(positions=positions,
                          qemu="qemu-system-riscv64",
                          options="-machine virt -cpu rv64 -m 1G -device virtio-blk-device,drive=hd "
                                  "-drive file=overlay.qcow2,if=none,id=hd -device virtio-net-device,netdev=net "
                                  "-netdev user,id=net,hostfwd=tcp::2222-:22 "
                                  "-bios /usr/lib/riscv64-linux-gnu/opensbi/generic/fw_jump.elf "
                                  "-kernel /usr/lib/u-boot/qemu-riscv64_smode/uboot.elf "
                                  "-object rng-random,filename=/dev/urandom,id=rng "
                                  "-device virtio-rng-device,rng=rng -append \"root=LABEL=rootfs console=ttyS0\" "
                                  "-nographic -monitor telnet:127.0.0.1:55555,server,nowait",
                          redirect=logfile,
                          id="root",
                          pw="root"
                          )