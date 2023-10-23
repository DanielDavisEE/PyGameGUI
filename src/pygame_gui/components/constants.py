from enum import Enum, IntFlag, auto
from typing import Self

import pygame
from pygame.locals import *

MARGIN = 10
KMOD_BASE = 4096


class KeyboardModifiers(IntFlag):
    # Single bit flags
    LSHIFT = KMOD_LSHIFT
    RSHIFT = KMOD_RSHIFT

    LCTRL = KMOD_LCTRL
    RCTRL = KMOD_RCTRL

    LALT = KMOD_LALT
    RALT = KMOD_RALT

    LMETA = KMOD_LMETA
    RMETA = KMOD_RMETA

    NUM = KMOD_NUM
    CAPS = KMOD_CAPS
    MODE = KMOD_MODE

    # Pygame builtin combinations
    SHIFT = KMOD_SHIFT
    CTRL = KMOD_CTRL
    ALT = KMOD_ALT
    META = KMOD_META

    # Custom combinations
    CTRL_SHIFT = CTRL | SHIFT
    CTRL_ALT = CTRL | ALT
    SHIFT_ALT = SHIFT | ALT
    CTRL_SHIFT_ALT = CTRL | SHIFT | ALT

    # Some bits inbetween flags were not used by pygame
    _UNUSED = 4 | 8 | 16 | 32


# typing_response = {
#     KeyboardEvents.CTRL: {'fallback': lambda *_: None},
#     KeyboardEvents.SHIFT: {'fallback': lambda *_: None},
#     KeyboardEvents.ALT: {'fallback': lambda *_: None},
#     KeyboardEvents.CTRL_SHIFT: {'fallback': lambda *_: None},
#     KeyboardEvents.CTRL_ALT: {'fallback': lambda *_: None},
#     KeyboardEvents.SHIFT_ALT: {'fallback': lambda *_: None},
#     KeyboardEvents.CTRL_SHIFT_ALT: {'fallback': lambda *_: None},
#     KMOD_SHIFT | KMOD_CAPS: {'fallback': lambda *_: None},
# }


class MouseEvents(Enum):
    # Mouse events
    LEFT_MOUSE_UP = MOUSEBUTTONUP, BUTTON_LEFT
    MIDDLE_MOUSE_UP = MOUSEBUTTONUP, BUTTON_MIDDLE
    RIGHT_MOUSE_UP = MOUSEBUTTONUP, BUTTON_RIGHT
    SCROLL_MOUSE_UP = MOUSEBUTTONUP, BUTTON_WHEELDOWN
    _SCROLL_MOUSE_UP = MOUSEBUTTONUP, BUTTON_WHEELUP  # Duplicate

    LEFT_MOUSE_DOWN = MOUSEBUTTONDOWN, BUTTON_LEFT
    MIDDLE_MOUSE_DOWN = MOUSEBUTTONDOWN, BUTTON_MIDDLE
    RIGHT_MOUSE_DOWN = MOUSEBUTTONDOWN, BUTTON_RIGHT
    _SCROLL_MOUSE_DOWN = MOUSEBUTTONDOWN, BUTTON_WHEELDOWN  # Duplicate
    SCROLL_MOUSE_DOWN = MOUSEBUTTONDOWN, BUTTON_WHEELUP

    MOVE_MOUSE = (MOUSEMOTION,)


class Alignment(IntFlag):
    # x alignments
    LEFT = auto()
    CENTRE = auto()
    RIGHT = auto()

    # y alignments
    TOP = auto()
    # CENTRE = auto()
    BOTTOM = auto()
