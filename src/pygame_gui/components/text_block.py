import pygame

from pygame_gui.components.constants import MARGIN, Alignment
from pygame_gui.components.base_block import Block


class Text(Block):

    def __init__(self, parent, *,
                 text_value='',
                 font_colour: str | tuple[int, int, int] = 'black',
                 font_size: int = 20,
                 text_alignment: Alignment | str = Alignment.CENTRE,
                 **kwargs
                 ):
        super().__init__(parent, **kwargs)

        self.text_info = {
            'value': str(text_value),
            # 'surface': Surface,
            # 'rect': tuple[int, int]
        }

        self.font_colour = font_colour
        if isinstance(font_colour, str):
            self.font_colour = self.colour_palette[self.font_colour]

        self.font_size = font_size

        try:
            self.font = pygame.font.Font(None, self.font_size)
        except pygame.error:
            pygame.init()
            self.font = pygame.font.Font(None, self.font_size)

        self.text_alignment = text_alignment
        if isinstance(self.text_alignment, str):
            self.text_alignment = self.alignment_mapping[self.text_alignment]
        assert self.text_alignment in (Alignment.LEFT | Alignment.CENTRE | Alignment.RIGHT)

    def update_text(self):
        centre_coords = [int(n // 2) for n in self.dimensions]

        self.text_info['surface'] = self.font.render(self.text_info['value'], True, self.font_colour)
        if self.text_alignment == Alignment.LEFT:
            self.text_info['rect'] = (self.text_info['surface'].get_rect(
                left=MARGIN,
                centery=centre_coords[1]))
        elif self.text_alignment == Alignment.CENTRE:
            self.text_info['rect'] = (self.text_info['surface'].get_rect(
                center=centre_coords))
        elif self.text_alignment == Alignment.RIGHT:
            self.text_info['rect'] = (self.text_info['surface'].get_rect(
                right=(self.dimensions[0] - MARGIN),
                centery=centre_coords[1]))

    def set_text(self, text: str):
        self.text_info['value'] = text

    def get_text(self) -> str:
        return self.text_info['value']

    def blit_text(self):
        self.update_text()
        self.surface.blit(self.text_info['surface'], self.text_info['rect'])
