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

        self.primary_text = {
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

        self.primary_text['surface'] = self.font.render(self.primary_text['value'], True, self.font_colour)
        if self.text_alignment == Alignment.LEFT:
            self.primary_text['rect'] = (self.primary_text['surface'].get_rect(
                left=MARGIN,
                centery=centre_coords[1]))
        elif self.text_alignment == Alignment.CENTRE:
            self.primary_text['rect'] = (self.primary_text['surface'].get_rect(
                center=centre_coords))
        elif self.text_alignment == Alignment.RIGHT:
            self.primary_text['rect'] = (self.primary_text['surface'].get_rect(
                right=(self.dimensions[0] - MARGIN),
                centery=centre_coords[1]))

    def set_text(self, text):
        self.primary_text['value'] = text

    def get_text(self):
        return self.primary_text['value']

    def append_text(self, text):
        self.primary_text['value'] += text

    def remove_text(self, amount=1):
        assert amount > 0
        self.primary_text['value'] = self.primary_text['value'][:-amount]

    def blit_text(self):
        self.update_text()
        self.surface.blit(self.primary_text['surface'], self.primary_text['rect'])
