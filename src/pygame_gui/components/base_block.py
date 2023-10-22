from typing import Self

import pygame
from pygame_gui.components.constants import Alignment
from pygame_gui.components.window import Window


class Block(Window):
    alignment_mapping = {
        'left': Alignment.LEFT,
        'centre': Alignment.CENTRE,
        'right': Alignment.RIGHT,
        'top': Alignment.TOP,
        'bottom': Alignment.BOTTOM,
    }

    def __init__(self, parent: Self | None = None, *,

                 coordinates: tuple[int, int] | None = None,
                 coord_x: int | None = None,
                 coord_y: int | None = None,

                 alignment: Alignment | tuple[Alignment, Alignment] | None = None,
                 align_x: Alignment | None = None,
                 align_y: Alignment | None = None,

                 margin: int | tuple[int, int] | None = None,
                 margin_x: int | None = None,
                 margin_y: int | None = None,

                 priority: int = 0,
                 polygon=None,

                 **kwargs):
        """
        Defining object positioning:
        For a particular axis (of x or y) there should only be one constraint. A coordinate
        (from coordinates - which defines both x and y, coord_x or coord_y) is a complete constraint
        and shouldn't be used in conjunction with alignment or margin for that axis. alignment and
        margin can be used together, although margin is optional and will default to 0 for each axis.
        While coordinates must be a tuple of both x and y positions, alignment and margin can either
        be a single value which defines both x and y or a tuple for both.
        All three can input x and y separately with the x/y specific arguments, which should be
        individual values for that axis.

        Args:
            parent:

            coordinates:
            coord_x:
            coord_y:

            alignment:
            align_x:
            align_y:

            margin:
            margin_x:
            margin_y:

            priority:
            polygon:
            **kwargs:
        """
        super().__init__(**kwargs)

        # The various inputs which constrain the position
        coordinates, alignments, margins = self.simplify_positional_requirements(
            coordinates, coord_x, coord_y,
            alignment, align_x, align_y,
            margin, margin_x, margin_y)

        # The true position as a result of the above constraints
        self.coordinates = self.translate_positional_requirements(coordinates, alignments, margins)

        self.parent = parent
        self.priority = priority
        self.polygon = polygon

        self.parent.add_child(self)

    def translate_positional_requirements(self,
                                          coordinates: tuple[int | None, int | None],
                                          alignments: tuple[Alignment | None, Alignment | None],
                                          margins: tuple[int | None, int | None]
                                          ) -> tuple[int, int]:
        coord_x, coord_y = coordinates
        align_x, align_y = alignments
        margin_x, margin_y = margins
        if isinstance(align_x, Alignment):
            if align_x == Alignment.LEFT:
                coord_x = margin_x
            elif align_x == Alignment.CENTRE:
                coord_x = (self.parent.dimensions[0] - self.dimensions[0]) // 2
            elif align_x == Alignment.RIGHT:
                coord_x = self.parent.dimensions[0] - self.dimensions[0] - margin_x

        if isinstance(align_y, Alignment):
            if align_y == Alignment.TOP:
                coord_y = margin_y
            elif align_y == Alignment.CENTRE:
                coord_y = (self.parent.dimensions[1] - self.dimensions[1]) // 2
            elif align_y == Alignment.BOTTOM:
                coord_y = self.parent.dimensions[1] - self.dimensions[1] - margin_y

        return coord_x, coord_y

    def _simplify_single_positional_requirement(self, constraint_name, combined_value, x_value, y_value):
        # Check that combined parameters and individual parameters are not being used together
        if combined_value is not None and (x_value is not None or y_value is not None):
            raise ValueError(f"Too many {constraint_name} constraints were input: {combined_value=}, {x_value=}, {y_value=}")

        # Convert combined parameters to pair if they were input as single values
        if combined_value is None or isinstance(combined_value, int) or isinstance(combined_value, Alignment):
            combined_value = combined_value, combined_value

        # For each parameter type and each axis, extract whichever value was provided
        x_value = x_value or combined_value[0]
        y_value = y_value or combined_value[1]

        return x_value, y_value

    def simplify_positional_requirements(self,
                                         coordinates, coord_x, coord_y,
                                         alignments, align_x, align_y,
                                         margins, margin_x, margin_y
                                         ) -> tuple[tuple, tuple, tuple]:
        # For each parameter type and each axis, extract whichever value was provided
        coord_x, coord_y = self._simplify_single_positional_requirement('coordinate', coordinates, coord_x, coord_y)
        align_x, align_y = self._simplify_single_positional_requirement('alignment', alignments, align_x, align_y)
        margin_x, margin_y = self._simplify_single_positional_requirement('margin', margins, margin_x, margin_y)

        # Check that the axes have been correctly constrained
        if coord_x and align_x:
            raise ValueError("The x position has been over-constrained")
        if coord_x is None and align_x is None:
            raise ValueError("The x position has been under-constrained")
        if coord_y and align_y:
            raise ValueError("The y position has been over-constrained")
        if coord_y is None and align_y is None:
            raise ValueError("The y position has been under-constrained")

        if coord_x and margin_x or coord_y and margin_y:
            raise ValueError("Coordinates and margins should not be used together")

        coordinates = coord_x, coord_y
        alignments = align_x, align_y
        margins = margin_x or 0, margin_y or 0  # Default to 0 from None for margins

        return coordinates, alignments, margins

    def _create_surface(self):
        self.surface = pygame.Surface(self.dimensions).convert()

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

    def move(self,
             del_x: int = 0,
             del_y: int = 0,

             x: int = None,
             y: int = None):
        # Update coordinates
        self.coordinates = x, y


if __name__ == '__main__':
    pass
