"""
Suggestions list:
 - scroll on dropdown list with arrow keys
 - select from dropdown list with enter key
 - move mouse cursor by clicking on text
 - select portions of text
 - scroll by clicking anywhere on scroll bar
 - allow buttons to be selected and pressed with enter
 - navigate with tab key
 - ctrl-z and ctrl-y
 - something with ctrl-s
"""
from typing import Self

import pygame
import pygame.locals as py_locals
import pyperclip

UNIT = 10
KMOD_BASE = 4096
MARGIN = 10


class RootBlock:
    colours = {
        'bg_colour': (230, 220, 205),
        'title_colour': (238, 201, 0),
        'board_colour': (105, 95, 80),
        'tile_colour': (134, 122, 102),
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'offwhite': (240, 240, 240),
    }

    def __init__(self, gui, *_, dimensions, colour, caption='', colour_palette=None, **kwargs):
        self.gui = gui
        self.dimensions = dimensions
        self.colour = None
        self.caption = caption
        if colour_palette:
            self.colours = colour_palette

        self.children = set()
        self.surface = None

        self.set_colour(colour)
        self.create_object()

    def create_object(self):
        pygame.display.set_caption(self.caption)
        self.surface = pygame.display.set_mode(self.dimensions)

    def set_colour(self, colour):
        if isinstance(colour, str):
            self.colour = self.colours[colour]
        elif isinstance(colour, tuple):
            self.colour = colour
        elif isinstance(colour, list):
            self.colour = tuple(colour)
        else:
            raise TypeError(f'Invalid type {type(colour)} for block colour')

    def mouse_event_handler(self, event):
        for child in list(self.children):
            child.mouse_event_handler(event)

    def keyboard_event_handler(self, event):
        pass

    def blit_text(self):
        pass

    def draw_block(self):
        self.surface.fill(self.colour)

        for child in sorted(self.children, key=lambda x: x.priority):
            child.draw_block()


class Block(RootBlock):
    coordinates: tuple[int, int]
    alignments: tuple[str, str]
    margins: tuple[int, int]

    def __init__(self, gui, parent, *_,
                 dimensions: tuple[int, int],
                 colour: str | tuple,

                 coordinates: tuple[int, int] | None = None,
                 coord_x: int | None = None,
                 coord_y: int | None = None,

                 alignment: str | tuple[str, str] | None,
                 align_x: str | None = None,
                 align_y: str | None = None,

                 margin: int | tuple[int, int] | None = None,
                 margin_x: int | None = None,
                 margin_y: int | None = None,

                 priority: int = 0,
                 polygon=None,

                 **kwargs):
        self.translate_positional_requirements(
            coordinates, coord_x, coord_y,
            alignment, align_x, align_y,
            margin, margin_x, margin_y
        )

        super().__init__(gui,
            dimensions=dimensions,
            coordinates=coordinates,
            colour=colour)

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

    def __delitem__(self):
        for child in self.children.copy():
            child.__delitem__()

        self.parent.children.remove(self)

        self = None

    def add_child(self, block: Self):
        self.children.add(block)

    def create_surface(self):
        block = pygame.Surface(self.dimensions)
        block = block.convert()
        block.fill(self.colour)
        self.surface = block

    def move(self, del_x=0, del_y=0, x=None, y=None):
        # Update coordinates
        self.coordinates = tuple([x, y])

    def draw_block(self):
        self.create_surface()
        self.blit_text()

        for child in sorted(self.children, key=lambda x: x.priority):
            child.draw_block()

        if self.polygon:
            pygame.draw.polygon(self.surface, *self.polygon)

        self.parent.surface.blit(self.surface, self.coordinates)


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

    def create_object(self):
        super().create_object()

        try:
            self.font = pygame.font.Font(None, self.font)
        except pygame.error:
            pygame.init()
            self.font = pygame.font.Font(None, self.font)

        self.font_colour = self.colours[self.font_colour]

    def update_text(self):
        centre_coords = [int(n // 2) for n in self.dimensions]

        self.primary_text['text'] = self.font.render(self.primary_text['value'], 1, self.font_colour)
        if self.text_alignment == 'left':
            self.primary_text['pos'] = (self.primary_text['text'].get_rect(
                left=MARGIN,
                centery=centre_coords[1]))
        elif self.text_alignment == 'centre':
            self.primary_text['pos'] = (self.primary_text['text'].get_rect(
                center=centre_coords))
        elif self.text_alignment == 'right':
            self.primary_text['pos'] = (self.primary_text['text'].get_rect(
                right=(self.dimensions[0] - MARGIN),
                centery=centre_coords[1]))

    def set_text(self, text):
        self.primary_text['value'] = text

    def get_text(self):
        return self.primary_text['value']

    def append_text(self, text):
        self.primary_text['value'] += text

    def remove_text(self, amount=-1):
        assert amount < 0
        self.primary_text['value'] = self.primary_text['value'][:amount]

    def blit_text(self):
        self.update_text()
        self.surface.blit(self.primary_text['text'], self.primary_text['pos'])


class Button(Text):

    def __init__(self, **kwargs):
        self.held = False
        self.event_function_dict = {
            'left_mouse_down': lambda *_: None,
            'right_mouse_down': lambda *_: None,
            'middle_mouse_down': lambda *_: None,
            'left_mouse_up': lambda *_: None,
            'right_mouse_up': lambda *_: None,
            'middle_mouse_up': lambda *_: None,
            'scroll_mouse': lambda *_: None,
            'move_mouse': lambda *_: None,
        }

        super().__init__(**kwargs)

        def hold_down(event):
            if self.check_collision(event):
                self.held = True

        def release(event):
            self.held = False

        self.default_mouse_handlers = {'left_mouse_down': hold_down,
                                       'left_mouse_up': release}
        self.set_mouse_handlers(self.event_function_dict)

    def create_object(self):
        super().create_object()

        # Coordinates need to be reference from window, not parent surface
        parent_tmp = self.parent
        self.overall_coords = list(self.coordinates)
        while parent_tmp != self.gui.window:
            self.overall_coords[0] += parent_tmp.coordinates[0]
            self.overall_coords[1] += parent_tmp.coordinates[1]
            parent_tmp = parent_tmp.parent

        self.create_rect()

    def create_rect(self):
        # Create rect object for simplicity of collision detection
        self.button_rect = py_locals.Rect(self.overall_coords, self.dimensions)

    def set_mouse_handlers(self, function_dict):
        for func_name, func in function_dict.items():
            def modify_default(default_func, new_func):
                def inner(*arg):
                    new_func(*arg)
                    default_func(*arg)

                return inner

            self.event_function_dict[func_name] = modify_default(self.default_mouse_handlers.get(func_name, lambda *_: None), func)

    def mouse_event_handler(self, event):

        super().mouse_event_handler(event)

        if event.type == pygame.MOUSEMOTION:
            self.event_function_dict['move_mouse'](event)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button < 4:
            if event.button == 1:  # Left mouse
                self.event_function_dict['left_mouse_down'](event)
            elif event.button == 2:  # Middle mouse
                self.event_function_dict['middle_mouse_down'](event)
            elif event.button == 3:  # Right mouse
                self.event_function_dict['right_mouse_down'](event)
        elif event.type == pygame.MOUSEBUTTONUP and event.button < 4:
            if event.button == 1:  # Left mouse
                self.event_function_dict['left_mouse_up'](event)
            elif event.button == 2:  # Middle mouse
                self.event_function_dict['middle_mouse_up'](event)
            elif event.button == 3:  # Right mouse
                self.event_function_dict['right_mouse_up'](event)
        else:
            assert (event.type == pygame.MOUSEBUTTONDOWN or
                    event.type == pygame.MOUSEBUTTONUP)
            scroll = event.button
            scroll -= 3
            if scroll % 2 == 1:
                scroll += 1
                scroll *= -1
            scroll //= 2

            self.event_function_dict['scroll_mouse'](event, scroll)

    def check_collision(self, event):
        mouse_pos = event.pos
        return self.button_rect.collidepoint(mouse_pos)

    def keyboard_event_handler(self, event):
        if event.key == py_locals.RETURN:
            self.event_function_dict['left_mouse_up'](event)

    def move(self, del_x=0, del_y=0, x=None, y=None):
        if x is None:
            x = self.coordinates[0] + del_x
        else:
            del_x = x - self.coordinates[0]
        if y is None:
            y = self.coordinates[1] + del_y
        else:
            del_y = y - self.coordinates[1]

        super().move(del_x, del_y, x, y)

        # Update rect
        self.overall_coords[0] += del_x
        self.overall_coords[1] += del_y

        self.create_rect()


class TextBox(Button):

    def __init__(self, **kwargs):

        self.active = False
        self.tb_colours = {
            True: 'white',
            False: 'offwhite'
        }

        self.cursor_info = {
            'on': False,
            'text': None,
            'pos': None
        }
        self.second_text = {
            'value': '',
            'text': None,
            'pos': None
        }

        kwargs['colour'] = self.tb_colours[self.active]
        kwargs['text_alignment'] = 'left'

        super().__init__(**kwargs)

        self.set_mouse_handlers({'left_mouse_down': self.toggle_select})

        self.cursor_info['colour'] = self.colour

    def update_cursor(self):

        text_rect = self.primary_text['pos']

        cursor_colour = self.font_colour if self.cursor_info['on'] else self.colour

        self.cursor_info['text'] = self.font.render('|', 1, cursor_colour)
        self.cursor_info['pos'] = self.cursor_info['text'].get_rect(
            left=text_rect.right,
            centery=text_rect.centery)

    def toggle_select(self, event):
        isCollision = self.check_collision(event)
        if isCollision:
            self.active = True
            self.gui.active_object = self
        if not isCollision:
            self.active = False
            self.cursor_info['on'] = False
            if self.gui.active_object == self:
                self.move_cursor(len(self.second_text['value']))
                self.gui.active_object = None

        self.colour = self.colours[self.tb_colours[self.active]]

    def move_cursor(self, amount):
        if amount < 0 and len(self.primary_text['value']) > 0:
            self.second_text['value'] = self.primary_text['value'][amount] + self.second_text['value']
            self.remove_text(amount)
        elif amount > 0 and len(self.second_text['value']) > 0:
            self.append_text(self.second_text['value'][:amount])
            self.second_text['value'] = self.second_text['value'][amount:]

    def update_text(self):
        super().update_text()

        if self.active:

            if self.primary_text['pos'].width + self.cursor_info['pos'].width > (self.dimensions[0] - 2 * MARGIN):
                self.primary_text['pos'] = (self.primary_text['text'].get_rect(
                    right=(self.dimensions[0] - MARGIN) - self.cursor_info['pos'].width,
                    centery=self.primary_text['pos'].centery))

            second_text_left = self.cursor_info['pos'].right

        else:
            second_text_left = self.primary_text['pos'].right

        self.update_cursor()

        self.second_text['text'] = self.font.render(self.second_text['value'], 1, self.font_colour)
        self.second_text['pos'] = self.second_text['text'].get_rect(
            left=second_text_left,
            centery=self.primary_text['pos'].centery)

    def toggle_cursor(self):
        self.cursor_info['on'] = not self.cursor_info['on']

    def set_text(self, text):
        super().set_text(text)
        self.second_text['value'] = ''

    def get_text(self):
        return self.primary_text['value'] + self.second_text['value']

    def append_text(self, text):
        super().append_text(text)

    def remove_text(self, amount=-1):
        super().remove_text(amount)

    def keyboard_event_handler(self, event):
        if (event.mod - KMOD_BASE == py_locals.KMOD_LCTRL or
                event.mod - KMOD_BASE == py_locals.KMOD_RCTRL or
                event.mod - KMOD_BASE == py_locals.KMOD_CTRL):
            character = pygame.key.name(event.key)
            if character == 'x':
                pyperclip.copy(self.primary_text['value'] + self.second_text['value'])
                self.second_text['value'] = ''
                self.set_text('')
            elif character == 'c':
                pyperclip.copy(self.primary_text['value'] + self.second_text['value'])
            elif character == 'v':
                text = pyperclip.paste()
                self.second_text['value'] = ''
                self.set_text(text)

            elif character in ['a', 's', 'z', 'y', 'x', 'c', 'v']:
                print('Get to this...')
        elif event.key == py_locals.K_RETURN:
            pass
        elif event.key == py_locals.K_BACKSPACE:
            self.remove_text()
        elif event.key == py_locals.K_DELETE:
            self.second_text['value'] = self.second_text['value'][1:]
        elif event.key == py_locals.K_LEFT:
            self.move_cursor(-1)
        elif event.key == py_locals.K_RIGHT:
            self.move_cursor(1)
        else:
            self.append_text(event.unicode)

        self.update_text()

    def blit_text(self):
        super().blit_text()
        self.surface.blit(self.cursor_info['text'], self.cursor_info['pos'])
        self.surface.blit(self.second_text['text'], self.second_text['pos'])


class Slider(Button):

    def __init__(self, **kwargs):

        self.min_limits, self.max_limits = kwargs['move_limits']
        self.dropdown = kwargs['dropdown']
        assert self.min_limits[0] <= self.max_limits[0] and self.min_limits[1] <= self.max_limits[1]

        super().__init__(**kwargs)

        self.offset = [0, 0]
        self.set_mouse_handlers({'left_mouse_down': self.hold_slider,
                                 'left_mouse_up': self.release_slider,
                                 'move_mouse': self.drag_slider})

    def set_x_pos(self, x_pos):
        new_x = (self.max_limits[0] - self.min_limits[0]) * x_pos + self.min_limits[0]
        self.update_coordinates(x=new_x)

    def set_y_pos(self, y_pos):
        new_y = (self.max_limits[1] - self.min_limits[1]) * y_pos + self.min_limits[1]
        self.update_coordinates(y=new_y)

    def update_coordinates(self, x=None, y=None):
        if x is None:
            x = self.coordinates[0]
        if y is None:
            y = self.coordinates[1]

        self.move(x=x, y=y)

    def drag_slider(self, event):
        if self.held:
            if self.max_limits[0] - self.min_limits[0] != 0:
                x = event.pos[0] + self.offset[0]
                if x < self.min_limits[0]:
                    x = self.min_limits[0]
                elif x > self.max_limits[0]:
                    x = self.max_limits[0]
            else:
                x = self.coordinates[0]

            if self.max_limits[1] - self.min_limits[1] != 0:
                y = event.pos[1] + self.offset[1]
                if y < self.min_limits[1]:
                    y = self.min_limits[1]
                elif y > self.max_limits[1]:
                    y = self.max_limits[1]
            else:
                y = self.coordinates[1]

            self.move(x=x, y=y)
            self.dropdown.rel_scroll_list((y - self.min_limits[1]) / (self.max_limits[1] - self.min_limits[1]))

    def hold_slider(self, event):
        isCollision = self.check_collision(event)
        if isCollision:
            self.held = True
            for i in range(2):
                self.offset[i] = self.coordinates[i] - event.pos[i]

    def release_slider(self, isCollision):
        self.held = False
        self.offset = [0, 0]


class Dropdown(Block):

    def __init__(self, **kwargs):
        # Check for overdefined coordinates
        x_count, y_count = 0, 0
        align_x, align_y = None, None
        if kwargs.get('coordinates', None) is not None:
            self.coordinates = kwargs['coordinates']
            x_count += 1
            y_count += 1
        else:
            self.coordinates = [None, None]

        if kwargs.get('coord_x', None) is not None:
            self.coordinates[0] = kwargs['coord_x']
            x_count += 1
        if kwargs.get('coord_y', None) is not None:
            self.coordinates[1] = kwargs['coord_y']
            y_count += 1
        if kwargs.get('align_x', None) is not None:
            align_x = kwargs['align_x']
            x_count += 1
        if kwargs.get('align_y', None) is not None:
            align_y = kwargs['align_y']
            y_count += 1
        assert x_count == 1 and y_count == 1

        self.alignments = align_x, align_y
        self.gui = kwargs['gui']
        self.parent = kwargs['parent']
        self.dimensions = kwargs['dimensions']

        if type(self.coordinates) is list:
            if any(self.alignments):
                align_x, align_y = self.alignments
                if align_x == 'left':
                    self.coordinates[0] = 0
                elif align_x == 'centre':
                    self.coordinates[0] = (self.parent.dimensions[0] - self.dimensions[0]) // 2
                elif align_x == 'right':
                    self.coordinates[0] = self.parent.dimensions[0] - self.dimensions[0]
                elif align_x is not None:
                    raise ValueError(f'{align_x} is not a valid alignment.')

                if align_y == 'top':
                    self.coordinates[1] = 0
                elif align_y == 'centre':
                    self.coordinates[1] = (self.parent.dimensions[1] - self.dimensions[1]) // 2
                elif align_y == 'bottom':
                    self.coordinates[1] = self.parent.dimensions[1] - self.dimensions[1]
                elif align_y is not None:
                    raise ValueError(f'{align_y} is not a valid alignment.')

            self.coordinates = tuple(self.coordinates)

        self.options_list = kwargs.get('options_list', None)
        if self.options_list is None:
            self.options_list = [f'{i}' for i in range(50)]
        self.options_list.sort()
        assert len(self.options_list) > 0

        self.textbox = None
        self.button = None
        self.dropdown = None
        self.scroll_handle = None
        self.item_dict = {}

        self.active = False
        self.scroll_amount = 0
        self.scroll_constant = 10
        self.max_scroll = 0

        self.create_object()

    def create_object(self):
        total_width, total_height = self.dimensions
        textbox_width = max(total_width - total_height, total_width // 2)
        button_width = total_width - textbox_width

        x_coord, y_coord = self.coordinates

        # TextBox portion
        textbox_dim = textbox_width, total_height
        textbox_coords = x_coord, y_coord
        self.textbox = TextBox(gui=self.gui, parent=self.parent, dimensions=textbox_dim, coordinates=textbox_coords)

        def dropdown_child(func):

            def inner(*args):
                func(*args)
                self.filter_options()
                return

            return inner

        self.textbox.append_text = dropdown_child(self.textbox.append_text)
        self.textbox.remove_text = dropdown_child(self.textbox.remove_text)

        def dropdown_textbox_toggle(event):
            textboxCollision = self.textbox.check_collision(event)
            buttonCollision = self.button.check_collision(event)
            dropdownCollision = 0 if self.dropdown is None else self.dropdown.check_collision(event)

            if textboxCollision or buttonCollision:
                self.textbox.active = True
                self.gui.active_object = self
            if not any([textboxCollision, buttonCollision, dropdownCollision]):
                self.textbox.active = False
                self.textbox.cursor_info['on'] = False
                if self.gui.active_object == self:
                    self.textbox.move_cursor(len(self.textbox.second_text['value']))
                    self.gui.active_object = None

            self.textbox.colour = self.textbox.colours[self.textbox.tb_colours[self.textbox.active]]

        self.textbox.set_mouse_handlers({'left_mouse_down': dropdown_textbox_toggle})

        # Dropdown button portion
        button_dim = button_width, total_height
        button_coords = x_coord + textbox_width, y_coord
        # Button triangle
        colour = (50, 50, 50)
        points = [(10, 15), (30, 15), (20, 30)]

        self.button = Button(gui=self.gui, parent=self.parent,
            dimensions=button_dim, coordinates=button_coords, colour='tile_colour',
            polygon=(colour, points))

        def dropdown_button_up(event):
            buttonCollision = self.button.check_collision(event)
            dropdownCollision = False if self.dropdown is None else self.dropdown.check_collision(event)

            if buttonCollision and self.button.held:
                if self.active:
                    self.close_dropdown_list()
                else:
                    self.textbox.active = True
                    self.open_dropdown_list()

        def dropdown_button_down(event):
            textboxCollision = self.textbox.check_collision(event)
            buttonCollision = self.button.check_collision(event)
            dropdownCollision = False if self.dropdown is None else self.dropdown.check_collision(event)

            if not any([textboxCollision, buttonCollision, dropdownCollision]) and self.active:
                self.close_dropdown_list()

        self.button.set_mouse_handlers({'left_mouse_up': dropdown_button_up,
                                        'left_mouse_down': dropdown_button_down})

    def abs_scroll_list(self, scroll):
        self.scroll_amount += scroll * self.scroll_constant
        if self.scroll_amount < 0:
            self.scroll_amount = 0
        if self.scroll_amount > self.max_scroll:
            self.scroll_amount = self.max_scroll

        scroll_ratio = self.scroll_amount / self.max_scroll if self.max_scroll else 0
        self.scroll_handle.set_y_pos(scroll_ratio)
        self.update_item_positions()

    def rel_scroll_list(self, scroll_ratio):
        self.scroll_amount = int(scroll_ratio * self.max_scroll)
        self.update_item_positions()

    def open_dropdown_list(self):
        self.active = True

        x_coord, y_coord = self.coordinates
        total_width, total_height = self.dimensions
        item_width, item_height = max(total_width - total_height, total_width // 2), total_height

        # Find distance to bottom of screen
        parent_tmp = self.parent
        y_coord_tmp = self.coordinates[1]
        while parent_tmp != self.gui.window:
            y_coord_tmp += parent_tmp.coordinates[1]
            parent_tmp = parent_tmp.parent

        available_space = parent_tmp.surface.get_height() - (y_coord_tmp + total_height + MARGIN)
        max_items = min(len(self.options_list), available_space // item_height)

        dropdown_dimensions = total_width, max_items * item_height
        dropdown_coords = x_coord, y_coord + total_height
        self.dropdown = Button(
            gui=self.gui,
            parent=self.parent,
            dimensions=dropdown_dimensions,
            coordinates=dropdown_coords,
            colour='white',
            priority=99)

        self.max_scroll = max(0, len(self.options_list) * item_height - dropdown_dimensions[1])

        item_dim = item_width, item_height
        for i, item in enumerate(self.options_list):
            item_coords = 0, i * item_height - self.scroll_amount
            button = Button(
                gui=self.gui,
                parent=self.dropdown,
                dimensions=item_dim,
                coordinates=item_coords,
                colour='white',
                text_value=item,
                text_alignment='left')

            def create_function():
                value_copy = item
                tmp_button = button

                def button_func(event):
                    if tmp_button.check_collision(event) and tmp_button.held:
                        self.close_dropdown_list()
                        self.textbox.set_text(value_copy)

                return button_func

            func_dict = {'left_mouse_up': create_function()}
            button.set_mouse_handlers(func_dict)

            self.item_dict[i] = button

        scroll_handle_dimensions = total_width - item_width, int(dropdown_dimensions[1] ** 2 / (len(self.options_list) * item_height))
        scroll_handle_initial_coords = item_width, 0
        limits = (item_width, 0), (item_width, dropdown_dimensions[1] - scroll_handle_dimensions[1])
        self.scroll_handle = Slider(
            gui=self.gui,
            parent=self.dropdown,
            dimensions=scroll_handle_dimensions,
            coordinates=scroll_handle_initial_coords,
            colour='tile_colour',
            dropdown=self,
            move_limits=limits)

        self.dropdown.set_mouse_handlers(
            {'scroll_mouse': lambda event, scroll: self.abs_scroll_list(scroll) if self.dropdown.check_collision(event) else None}
        )

    def close_dropdown_list(self):
        self.active = False
        self.scroll_amount = 0
        self.dropdown.__delitem__()
        self.dropdown = None

    def update_item_positions(self):
        for i, item in self.item_dict.items():
            item.move(y=i * self.dimensions[1] - self.scroll_amount)

    def filter_options(self):
        text = self.textbox.primary_text['value'] + self.textbox.second_text['value']
        for i, option in enumerate(self.options_list):
            if len(text) > 0 and text == option[:len(text)]:
                self.scroll_amount = min(i * self.dimensions[1], self.max_scroll)
                self.update_item_positions()
                if not self.active:
                    self.open_dropdown_list()
                self.scroll_handle.set_y_pos(self.scroll_amount / self.max_scroll)
                break

    def toggle_cursor(self):
        self.textbox.toggle_cursor()

    def keyboard_event_handler(self, event):
        self.textbox.keyboard_event_handler(event)


class MyGUI:

    def __init__(self, *args, **kwargs):
        """window_size, caption, win_colour, colour_palette=None -> myGUI
        """

        arg_names = ('dimensions', 'caption', 'colour', 'colour_palette')
        kwargs['gui'] = self
        for i, arg in enumerate(args):
            kwargs[arg_names[i]] = arg
        self.window = RootBlock(**kwargs)
        self.active_object = None
        self.running = False

        self.arg_names = ('parent', 'dimensions', 'coordinates', 'colour', 'text_value', 'text_colour', 'text_size')

    def run_gui(self):
        self.running = True
        pygame.init()

        self.window.draw_block()
        pygame.display.flip()

        count = 0
        delay_time = 20

        pygame.key.set_repeat(500, 50)
        while self.running:
            pygame.time.delay(delay_time)

            count += 1
            if self.active_object and count >= 1000 // (2 * delay_time):
                self.active_object.toggle_cursor()
                count = 0

            for event in pygame.event.get():
                # Keyboard Events
                if event.type == py_locals.KEYDOWN:
                    if event.key == py_locals.K_ESCAPE:
                        self.quit_gui()  # Allows user to overwrite quit process
                    if (event.mod - KMOD_BASE == py_locals.KMOD_LCTRL or
                            event.mod - KMOD_BASE == py_locals.KMOD_RCTRL or
                            event.mod - KMOD_BASE == py_locals.KMOD_CTRL):
                        character = pygame.key.name(event.key)
                        if character == 's':
                            self.save()
                    else:
                        if self.active_object:
                            self.active_object.keyboard_event_handler(event)

                if event.type == pygame.QUIT:
                    self.quit_gui()

                # Mouse Events
                if (event.type == pygame.MOUSEBUTTONDOWN or
                        event.type == pygame.MOUSEBUTTONUP or
                        event.type == pygame.MOUSEMOTION):
                    self.window.mouse_event_handler(event)

            self.window.draw_block()
            pygame.display.flip()

        pygame.quit()

    def quit_gui(self):
        self.running = False

    def clear_gui(self):
        for child in list(self.window.children):
            child.__delitem__()

    def save(self):
        pass

    # -------------------------- Object Creation ----------------------------

    def create_block(self, *args, **kwargs):
        kwargs['gui'] = self
        for i, arg in enumerate(args):
            kwargs[self.arg_names[i]] = arg
        return Block(**kwargs)

    def create_text(self, *args, **kwargs):
        kwargs['gui'] = self
        for i, arg in enumerate(args):
            kwargs[self.arg_names[i]] = arg
        return Text(**kwargs)

    def create_button(self, *args, **kwargs):
        kwargs['gui'] = self
        for i, arg in enumerate(args):
            kwargs[self.arg_names[i]] = arg
        return Button(**kwargs)

    def create_textbox(self, *args, **kwargs):
        kwargs['gui'] = self
        for i, arg in enumerate(args):
            kwargs[self.arg_names[i]] = arg
        return TextBox(**kwargs)

    def create_dropdown(self, *args, **kwargs):
        kwargs['gui'] = self
        for i, arg in enumerate(args):
            kwargs[self.arg_names[i]] = arg
        return Dropdown(**kwargs)


if __name__ == '__main__':
    # Create test GUI
    caption = "Test GUI"
    window_size = win_width, win_height = (int(UNIT * 70 - 1),
                                           int(UNIT * 40))
    fill_colour = 'bg_colour'

    gui1 = MyGUI(window_size, caption, fill_colour)

    # Add GUI elements
    block_info = {
        'parent': gui1.window,
        'dimensions': (10 * UNIT, 4 * UNIT),
        'coordinates': (6 * UNIT, 2 * UNIT),
        'colour': 'white'
    }

    gui1.create_block(**block_info)

    gui1.create_text(gui1.window, (10 * UNIT, 4 * UNIT), (6 * UNIT, 8 * UNIT), 'white', 'Test')

    button1 = gui1.create_button(gui1.window, (10 * UNIT, 4 * UNIT), (6 * UNIT, 14 * UNIT), 'white', 'QUIT')

    func_dict = {
        'left_mouse_up': lambda event: gui1.quit_gui() if button1.check_collision(event) and button1.held else None,
        'middle_mouse_up': lambda event: print(1)
    }
    button1.set_mouse_handlers(func_dict)

    gui1.create_textbox(gui1.window, (16 * UNIT, 4 * UNIT), (6 * UNIT, 20 * UNIT))

    gui1.create_dropdown(gui1.window, (16 * UNIT, 4 * UNIT), (18 * UNIT, 2 * UNIT))

    gui1.run_gui()
