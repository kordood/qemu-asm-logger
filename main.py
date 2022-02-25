from qemumanager import QEMUManager

if __name__ == '__main__':
    positions = [(530, 1038), (917, 807)]
    manager = QEMUManager(positions,
                          qemu="qemu-system-riscv64",
                          options="-machine virt -cpu rv64 -m 1G -device virtio-blk-device,drive=hd "
                                  "-drive file=overlay.qcow2,if=none,id=hd -device virtio-net-device,netdev=net "
                                  "-netdev user,id=net,hostfwd=tcp::2222-:22 "
                                  "-bios /usr/lib/riscv64-linux-gnu/opensbi/generic/fw_jump.elf "
                                  "-kernel /usr/lib/u-boot/qemu-riscv64_smode/uboot.elf "
                                  "-object rng-random,filename=/dev/urandom,id=rng "
                                  "-device virtio-rng-device,rng=rng -append \"root=LABEL=rootfs console=ttyS0\" "
                                  "-nographic -monitor telnet:127.0.0.1:55555,server,nowait",
                          redirect="/home/docker/debian-rv64/artifacts/qemu.log",
                          id="root",
                          pw="root"
                          )
    manager.extract_log("/home/debian/out/addi_regs", "main", 30)
