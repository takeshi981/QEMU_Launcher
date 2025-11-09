import os
import json

CONFIG_FILE = "qemu_paths.json"

DEFAULT_PATHS = {
    "x86_64": "qemu-system-x86_64",
    "x86_64w": "qemu-system-x86_64w",
    "aarch64": "qemu-system-aarch64",
    "aarch64w": "qemu-system-aarch64w",
    "alpha": "qemu-system-alpha",
    "alphaw": "qemu-system-alphaw",
    "arm": "qemu-system-arm",
    "armw": "qemu-system-armw",
    "avr": "qemu-system-avr",
    "avrw": "qemu-system-avrw",
    "hppa": "qemu-system-hppa",
    "hppaw": "qemu-system-hppaw",
    "i386": "qemu-system-i386",
    "i386w": "qemu-system-i386w",
    "loongarch64": "qemu-system-loongarch64",
    "loongarch64w": "qemu-system-loongarch64w",
    "microblaze": "qemu-system-microblaze",
    "microblazeel": "qemu-system-microblazeel",
    "microblazeelw": "qemu-system-microblazeelw",
    "mips": "qemu-system-mips",
    "mips64": "qemu-system-mips64",
    "mips64el": "qemu-system-mips64el",
    "mips64elw": "qemu-system-mips64elw",
    "mips64w": "qemu-system-mips64w",
    "mipsel": "qemu-system-mipsel",
    "mipselw": "qemu-system-mipselw",
    "mipsw": "qemu-system-mipsw",
    "or1k": "qemu-system-or1k",
    "or1kw": "qemu-system-or1kw",
    "ppc": "qemu-system-ppc",
    "ppc64": "qemu-system-ppc64",
    "ppc64w": "qemu-system-ppc64w",
    "riscv32": "qemu-system-riscv32",
    "riscv32w": "qemu-system-riscv32w",
    "riscv64": "qemu-system-riscv64",
    "riscv64w": "qemu-system-riscv64w",
    "rx": "qemu-system-rx",
    "rxw": "qemu-system-rxw",
    "s390x": "qemu-system-s390x",
    "s390xw": "qemu-system-s390xw",
    "sh4": "qemu-system-sh4",
    "sh4eb": "qemu-system-sh4eb",
    "sh4ebw": "qemu-system-sh4ebw",
    "sparc": "qemu-system-sparc",
    "sparc64": "qemu-system-sparc64",
    "sparc64w": "qemu-system-sparc64w",
    "sparcw": "qemu-system-sparcw",
    "tricore": "qemu-system-tricore",
    "tricorew": "qemu-system-tricorew",
    "xtensa": "qemu-system-xtensa",
    "xtensaeb": "qemu-system-xtensaeb",
    "ztensaebw": "qemu-system-xtensaebw",
    "xtensaw": "qemu-system-xtensaw"
    
}

def load_paths():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return DEFAULT_PATHS.copy()

def save_paths(paths):
    with open(CONFIG_FILE, "w") as f:
        json.dump(paths, f, indent=4)
       

