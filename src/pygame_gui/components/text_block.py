import pygame

from pygame_gui.components import Block


class Text(Block):

    def __init__(self, **kwargs):
        self.text_alignment = kwargs.get('text_alignment', 'centre')
        text_value = kwargs.get('text_value', '')
        self.font_colour = kwargs.get('text_colour', 'black')
        self.font = kwargs.get('text_size', 20)

        alignments = ['left', 'centre', 'right']
        assert self.text_alignment in alignments

        self.primary_text = {
            'value': str(text_value),
            'text': None,
            'pos': None
        }

        super().__init__(**kwargs)

    def _create_surface(self):
        super()._create_surface()

        try:
            self.font = pygame.font.Font(None, self.font)
        except pygame.error:
            pygame.init()
            self.font = pygame.font.Font(None, self.font)

        self.font_colour = self.colour_palette[self.font_colour]

    def update_text(self):
        centre_coords = [int(n // 2) for n in self.dimensions]

        self.primary_text['text'] = self.font.render(self.primary_text['value'], 1, self.font_colour)
        if self.text_alignment == 'left':
            self.primary_text['pos'] = (self.primary_text['text'].get_rect(
                left=self._MARGIN,
                centery=centre_coords[1]))
        elif self.text_alignment == 'centre':
            self.primary_text['pos'] = (self.primary_text['text'].get_rect(
                center=centre_coords))
        elif self.text_alignment == 'right':
            self.primary_text['pos'] = (self.primary_text['text'].get_rect(
                right=(self.dimensions[0] - self._MARGIN),
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
        self.surface.blit(self.primary_text['text'], self.primary_text['pos'])
