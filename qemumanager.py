import sys
from time import sleep, time

import macro

from typing import List


class QEMUManager:
    def __init__(self,
                 positions: List[(int, int)],
                 qemu: str,
                 options: str = None,
                 redirect: str = None
                 ) -> None:
        assert len(positions) >= 2

        self.runner_pos = positions[0]
        self.monitor_pos = positions[1]
        self.qemu_binary = qemu

        if redirect:
            options += f" &>{redirect}"

        self.logfile = open(redirect, "r")
        self.log_buffer = ""
        self.qemu_options = options

        self.boot_qemu()
        self.print_out()

    def boot_qemu(self):
        macro.grab_window(self.runner_pos)
        script = f"{self.qemu_binary} {self.qemu_options}"
        macro.run_command(script)

    @staticmethod
    def login(id, pw=None):
        macro.run_command(id)

        if pw:
            sleep(1)
            macro.run_command(pw)

    @staticmethod
    def logout():
        macro.run_command("exit")
        sleep(4)

    def print_out(self, timeout=0):
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

            if previous_tell == current_tell:
                break

    def flush_log_buffer(self):
        self.log_buffer = ""


if __name__ == '__main__':
    pos1_x = sys.argv[1]
    pos1_y = sys.argv[2]
    pos2_x = sys.argv[3]
    pos2_y = sys.argv[4]
    positions = [(pos1_x, pos1_y), (pos2_x, pos2_y)]

    manager = QEMUManager(positions=positions,
                          qemu="qemu-system-riscv64",
                          options="-machine virt -cpu rv64 -m 1G -device virtio-blk-device,drive=hd "
                                  "-drive file=overlay.qcow2,if=none,id=hd -device virtio-net-device,netdev=net "
                                  "-netdev user,id=net,hostfwd=tcp::2222-:22 "
                                  "-bios /usr/lib/riscv64-linux-gnu/opensbi/generic/fw_jump.elf "
                                  "-kernel /usr/lib/u-boot/qemu-riscv64_smode/uboot.elf "
                                  "-object rng-random,filename=/dev/urandom,id=rng "
                                  "-device virtio-rng-device,rng=rng -append \"root=LABEL=rootfs console=ttyS0\" "
                                  "-nographic -monitor telnet:127.0.0.1:55555,server,nowait"
                          )