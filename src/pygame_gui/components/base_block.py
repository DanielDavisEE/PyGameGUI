from typing import Self

import pygame
from pygame_gui.components import Window


class Block(Window):
    coordinates: tuple[int, int]
    alignments: tuple[str, str]
    margins: tuple[int, int]

    def __init__(self, parent: Self | None = None, *_,

                 coordinates: tuple[int, int] | None = None,
                 coord_x: int | None = None,
                 coord_y: int | None = None,

                 alignment: str | tuple[str, str] | None = None,
                 align_x: str | None = None,
                 align_y: str | None = None,

                 margin: int | tuple[int, int] | None = None,
                 margin_x: int | None = None,
                 margin_y: int | None = None,

                 priority: int = 0,
                 polygon=None,

                 **kwargs):
        super().__init__(**kwargs)

        self.translate_positional_requirements(
            coordinates, coord_x, coord_y,
            alignment, align_x, align_y,
            margin, margin_x, margin_y
        )

        self.parent = parent
        self.priority = priority
        self.polygon = polygon

        self.parent.add_child(self)

    def translate_positional_requirements(self,
                                          coordinates, coord_x, coord_y,
                                          alignment, align_x, align_y,
                                          margin, margin_x, margin_y
                                          ):
        # Check for overdefined coordinates. Exactly one constraint should be present for x and y coordinates each.
        # These can be provided by the following keywords: coordinates, coord_x, coord_y, alignment, align_x, align_y.
        # Alignment options are left, centre, right for x and top, center, bottom for y.
        assert len([x for x in [coordinates[0], coord_x, align_x] if x is not None]) == 1, "X coordinates are over- or underdefined"
        assert len([x for x in [coordinates[1], coord_y, align_y] if x is not None]) == 1, "Y coordinates are over- or underdefined"

        if coordinates is not None:
            self.coordinates = tuple(coordinates)
        else:
            self.coordinates = coord_x, coord_y

        if alignment is not None:
            if isinstance(alignment, str):
                self.alignments = alignment, alignment
            elif isinstance(alignment, list):
                self.alignments = tuple(alignment)
        else:
            self.alignments = align_x, align_y

        # Define the margins of the block relative to its parents.
        # Only used in the case of calculating coordinates from alignment.
        assert len([x for x in [margin[0], margin_x] if x is not None]) == 1, "X margin is over- or underdefined"
        assert len([x for x in [margin[1], margin_y] if x is not None]) == 1, "Y margin is over- or underdefined"

        if margin is not None:
            if isinstance(margin, int):
                self.margins = margin, margin
            elif isinstance(margin, list):
                self.margins = tuple(margin)
            else:
                raise TypeError(f"'margin' should be one of NoneType, int, list or tuple. {type(margin)} was provided.")
        else:
            self.margins = margin_x, margin_y

        align_x, align_y = self.alignments
        margin_x, margin_y = self.margins
        if align_x:
            if align_x == 'left':
                self.coordinates[0] = margin_x
            elif align_x == 'centre':
                self.coordinates[0] = (self.parent.dimensions[0] - self.dimensions[0]) // 2
            elif align_x == 'right':
                self.coordinates[0] = self.parent.dimensions[0] - self.dimensions[0] - margin_x
            elif align_x is not None:
                raise ValueError(f'{align_x} is not a valid alignment.')

        if align_y:
            if align_y == 'top':
                self.coordinates[1] = margin_y
            elif align_y == 'centre':
                self.coordinates[1] = (self.parent.dimensions[1] - self.dimensions[1]) // 2
            elif align_y == 'bottom':
                self.coordinates[1] = self.parent.dimensions[1] - self.dimensions[1] - margin_y
            elif align_y is not None:
                raise ValueError(f'{align_y} is not a valid alignment.')

    def _create_surface(self):
        self.surface = pygame.Surface(self.dimensions).convert()
        self.surface.fill(self.colour)

    def draw_block(self):
        super().draw_block()

        self.blit_text()
        if self.polygon:
            pygame.draw.polygon(self.surface, *self.polygon)

        self.parent.surface.blit(self.surface, self.coordinates)

    def __delitem__(self):
        for child in self.children.copy():
            child.__delitem__()

        self.parent.children.remove(self)

        self = None

    def add_child(self, block: Self):
        self.children.add(block)

    def move(self,
             del_x: int = 0,
             del_y: int = 0,

             x: int = None,
             y: int = None):
        # Update coordinates
        self.coordinates = x, y


if __name__ == '__main__':
    pass
