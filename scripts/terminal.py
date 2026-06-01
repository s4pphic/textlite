# "Platform agnostic" terminal magic to avoid
# having per-OS code muddling about across the
# entire codebase, so it's all contained right
# here. It's gonna be pretty messy...

import sys
import shutil

class Terminal:
    # ---------------- TTY Detection && Size helpers ----------------

    @staticmethod
    def is_tty() -> bool:
        return sys.stdout.isatty()
    
    @staticmethod
    def size() -> tuple[int, int]:
        sz = shutil.get_terminal_size(fallback=(80,24))
        return (sz.columns, sz.lines)
    
    # ---------------- ANSI Escape codes ----------------

    __RESET  = "\033[0m"
    __BOLD   = "\033[1m"
    __DIM    = "\033[2m"

    __RED    = "\033[31m"
    __GREEN  = "\033[32m"
    __YELLOW = "\033[33m"
    __BLUE   = "\033[34m"
    __CYAN   = "\033[36m"

    @classmethod
    def _esc(cls, code: str, text: str) -> str:
        if not cls.is_tty():
            return text
        return f"{code}{text}{cls.__RESET}"

    # ---------------- Pretty print methods ----------------

    @classmethod
    def bold(cls, text: str) -> str: ...

    @classmethod
    def colour(cls, text: str, code: str) -> str: ...

    @classmethod
    def italic(cls, text: str) -> str: ...

    # ---------------- Raw input ----------------

    @staticmethod
    def getch() -> str:
        if sys.platform == "win32":
            import msvcrt
            return msvcrt.getch().decode("utf-8", errors="replace")
        else:
            import tty, termios
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                return sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)