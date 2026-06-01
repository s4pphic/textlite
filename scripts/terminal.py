# "Platform agnostic" terminal magic to avoid
# having per-OS code muddling about across the
# entire codebase, so it's all contained right
# here. It's gonna be pretty messy...

# Some example code of how this *should* be used!
#
# Terminal.print_f("Saved!", bold=True, colour="green")
# Terminal.clear()
# Terminal.print_at(10, 5, "x", colour="red")
# Terminal.print_at(1, 1, "Header", bold=True, restore=True)
# 
# with Terminal.cursor_hidden():
#     for i in range(Terminal.size()[0]):
#         Terminal.print_ch(i + 1, 3, "─")

import sys
import shutil
from contextlib import contextmanager

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
    __ITALIC = "\033[3m]"

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
    def bold(cls, text: str) -> str:
        """Takes `text` input, returns bold version"""
        return cls._esc(cls.__BOLD, text)
 
    @classmethod
    def dim(cls, text: str) -> str:
        """Renders `text` input as dim."""
        return cls._esc(cls.__DIM, text)
 
    @classmethod
    def colour(cls, text: str, code: str) -> str:
        """Takes a `text` input and an ANSI colour `code`, returns them together."""
        return cls._esc(code, text)
 
    @classmethod
    def italic(cls, text: str) -> str:
        """Takes in a string of `text` and returns the italicised version."""
        return cls._esc(cls.__ITALIC, text)
    
    # ---------------- Colour lookup ----------------
 
    @classmethod
    def _colour_code(cls, name: str) -> str:
        table = {
            "red": cls.__RED,   "green": cls.__GREEN, "yellow": cls.__YELLOW,
            "blue": cls.__BLUE, "cyan":  cls.__CYAN,
        }
        return table.get(name.lower(), "")
 
    @classmethod
    def _style(cls, text: str, *, bold=False, dim=False, italic=False, colour: str | None = None) -> str:
        """Wrap `text` in the requested style codes (noop when not a TTY)"""
        codes = ""
        if bold: codes += cls.__BOLD
        if dim: codes += cls.__DIM
        if italic: codes += cls.__ITALIC
        if colour: codes += cls._colour_code(colour)
        return cls._esc(codes, text) if codes else text
    
    # ---------------- Formatted print (very cool) ----------------
 
    @classmethod
    def print_f(cls, text: str, *, end: str = "\n", flush: bool = False, **style) -> None:
        """Print `text` with optional bold/dim/italic/colour=... styles applied"""
        print(cls._style(text, **style), end=end, flush=flush)
 
    # ---------------- Positioned output ----------------

    # NOTE: public API is (col, row), 1-based; matches size() returning (cols, lines).
    # ANSI itself wants row;col, so the swap is handled internally
 
    @classmethod
    def move_to(cls, col: int, row: int) -> None:
        """Move the cursor to (col, row). Noop when not a TTY"""
        if not cls.is_tty():
            return
        sys.stdout.write(f"\033[{row};{col}H")
        sys.stdout.flush()
 
    @classmethod
    def move(cls, cols: int = 0, rows: int = 0) -> None:
        """
        Relative move: +cols -> right, +rows -> down (negatives go left/up)
        """
        if not cls.is_tty(): return

        out = ""
        if cols > 0: 
            out += f"\033[{cols}C"
        elif cols < 0: 
            out += f"\033[{-cols}D"

        if rows > 0: 
            out += f"\033[{rows}B"
        elif rows < 0: 
            out += f"\033[{-rows}A"

        if out:
            sys.stdout.write(out)
            sys.stdout.flush()
 
    @classmethod
    def print_at(cls, col: int, row: int, text: str, *, restore: bool = False, **style) -> None:
        """
        Write `text` at (col, row). `restore=True` returns the cursor afterward. 
        Accepts the same style kwargs as print_f.
        """
        body = cls._style(text, **style)
        if not cls.is_tty():
            print(body, end="")
            return
        out = "\033[s" if restore else ""
        out += f"\033[{row};{col}H{body}"
        if restore:
            out += "\033[u"
        sys.stdout.write(out)
        sys.stdout.flush()
 
    @classmethod
    def print_ch(cls, col: int, row: int, ch: str, **style) -> None:
        """Put a single character at (col, row)"""
        cls.print_at(col, row, ch[:1], **style)
 
    # ---------------- Screen / cursor control ----------------
 
    @classmethod
    def clear(cls) -> None:
        """Clear the screen and home the cursor."""
        if not cls.is_tty():
            return
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()
 
    @classmethod
    def clear_line(cls) -> None:
        """Erase the current line and return to its start."""
        if not cls.is_tty():
            return
        sys.stdout.write("\r\033[2K")
        sys.stdout.flush()
 
    @classmethod
    def hide_cursor(cls) -> None:
        if cls.is_tty():
            sys.stdout.write("\033[?25l")
            sys.stdout.flush()
 
    @classmethod
    def show_cursor(cls) -> None:
        if cls.is_tty():
            sys.stdout.write("\033[?25h")
            sys.stdout.flush()
 
    @classmethod
    @contextmanager
    def cursor_hidden(cls):
        """`with Terminal.cursor_hidden():` guarantees the cursor comes back even if the block raises."""
        cls.hide_cursor()
        try:
            yield
        finally:
            cls.show_cursor()

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