import pygame


class Window:
    base_colours = {
        'bg_colour': (230, 220, 205),
        'title_colour': (238, 201, 0),
        'board_colour': (105, 95, 80),
        'tile_colour': (134, 122, 102),
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'offwhite': (240, 240, 240),
    }

    def __init__(self, *,
                 dimensions: tuple[int, int] | None,

                 caption: str = '',
                 colour: str | tuple[int, int, int] = 'white',
                 colour_palette: dict[str, tuple[int, int, int]] = None,
                 **kwargs):
        self.dimensions = dimensions
        self.colour = self.translate_colour_input(colour)
        self.colour_palette = colour_palette or self.base_colours
        self.caption = caption

        self.active = False
        self.surface = None
        self.children = set()

    def _create_surface(self):
        pygame.display.set_caption(self.caption)
        self.surface = pygame.display.set_mode(self.dimensions)
        self.surface.fill(self.colour)

    def draw_block(self):
        if not self.surface:
            self._create_surface()

        for child in sorted(self.children, key=lambda x: x.priority):
            child.draw_block()

    def translate_colour_input(self, colour):
        if isinstance(colour, str):
            colour = self.colour_palette[colour]
        elif isinstance(colour, tuple):
            colour = colour
        elif isinstance(colour, list):
            colour = tuple(colour)
        else:
            raise TypeError(f'Invalid type {type(colour)} for block colour')
        return colour

    def mouse_event_handler(self, event):
        for child in list(self.children):
            child.mouse_event_handler(event)

    def keyboard_event_handler(self, event):
        pass

    def blit_text(self):
        pass

    def clock(self):
        pass
