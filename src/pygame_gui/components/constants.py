from enum import Enum, IntFlag, auto
from typing import Self

import pygame
from pygame.locals import *

MARGIN = 10
KMOD_BASE = 4096


class KeyboardEvents(Enum):
    CTRL = (KMOD_CTRL,)
    SHIFT = (KMOD_SHIFT,)
    ALT = (KMOD_ALT,)

    CTRL_SHIFT = KMOD_CTRL, KMOD_SHIFT
    CTRL_ALT = KMOD_CTRL, KMOD_ALT
    SHIFT_ALT = KMOD_SHIFT, KMOD_ALT

    CTRL_SHIFT_ALT = KMOD_CTRL, KMOD_SHIFT, KMOD_ALT


typing_response = {
    KeyboardEvents.CTRL: {'fallback': lambda *_: None},
    KeyboardEvents.SHIFT: {'fallback': lambda *_: None},
    KeyboardEvents.ALT: {'fallback': lambda *_: None},
    KeyboardEvents.CTRL_SHIFT: {'fallback': lambda *_: None},
    KeyboardEvents.CTRL_ALT: {'fallback': lambda *_: None},
    KeyboardEvents.SHIFT_ALT: {'fallback': lambda *_: None},
    KeyboardEvents.CTRL_SHIFT_ALT: {'fallback': lambda *_: None},
    KMOD_SHIFT | KMOD_CAPS: {'fallback': lambda *_: None},
}


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
