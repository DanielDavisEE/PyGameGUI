from enum import IntFlag, auto

MARGIN = 10
KMOD_BASE = 4096


class Alignment(IntFlag):
    # x alignments
    LEFT = auto()
    CENTRE = auto()
    RIGHT = auto()

    # y alignments
    TOP = auto()
    # CENTRE = auto()
    BOTTOM = auto()
