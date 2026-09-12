"""ANSI color helpers for pis CLI output.

Auto-detects terminal color support. Disabled with --no-color flag or
when stdout is not a TTY. Uses standard ANSI escape codes — no deps.

On Windows, enables virtual terminal processing so ANSI codes render
in the console (disabled by default on older Windows terminals).
"""

from __future__ import annotations

import os
import sys


# --- State ------------------------------------------------------------------

_enabled: bool | None = None


def _enable_windows_ansi() -> None:
    """Enable ANSI escape code processing on Windows.

    On Windows 10+, the console needs ENABLE_VIRTUAL_TERMINAL_PROCESSING
    turned on. Without it, ANSI codes show as raw text or are stripped.
    """
    if sys.platform != "win32":
        return
    try:
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.windll.kernel32

        # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        STD_OUTPUT_HANDLE = -11
        handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        if handle == 0 or handle == -1:
            return

        mode = wintypes.DWORD()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return

        new_mode = mode.value | 0x0004
        kernel32.SetConsoleMode(handle, new_mode)
    except Exception:
        # if anything fails, colors just won't render — not fatal
        pass


def init(no_color: bool = False) -> None:
    """Initialize color support. Call once at CLI startup."""
    global _enabled
    if no_color:
        _enabled = False
        return
    # disable if NO_COLOR env var is set (https://no-color.org/)
    if os.environ.get("NO_COLOR"):
        _enabled = False
        return
    # disable if not a TTY (piped output, redirected)
    if not sys.stdout.isatty():
        _enabled = False
        return
    # on Windows, enable ANSI processing in the console
    _enable_windows_ansi()
    _enabled = True


def _enabled_or_false() -> bool:
    if _enabled is None:
        # lazy init: assume disabled if not explicitly set
        return False
    return _enabled


# --- Color codes ------------------------------------------------------------

_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"

_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_BLUE = "\033[34m"
_MAGENTA = "\033[35m"
_CYAN = "\033[36m"


# --- Helpers ----------------------------------------------------------------

def _wrap(code: str, text: str) -> str:
    if not _enabled_or_false():
        return text
    return f"{code}{text}{_RESET}"


def bold(text: str) -> str:
    return _wrap(_BOLD, text)


def dim(text: str) -> str:
    return _wrap(_DIM, text)


def red(text: str) -> str:
    return _wrap(_RED, text)


def green(text: str) -> str:
    return _wrap(_GREEN, text)


def yellow(text: str) -> str:
    return _wrap(_YELLOW, text)


def blue(text: str) -> str:
    return _wrap(_BLUE, text)


def magenta(text: str) -> str:
    return _wrap(_MAGENTA, text)


def cyan(text: str) -> str:
    return _wrap(_CYAN, text)


# --- Semantic helpers -------------------------------------------------------

def success(text: str) -> str:
    return green(text)


def error(text: str) -> str:
    return red(text)


def warning(text: str) -> str:
    return yellow(text)


def info(text: str) -> str:
    return cyan(text)


def header(text: str) -> str:
    return bold(text)
