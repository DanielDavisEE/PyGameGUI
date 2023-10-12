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

import pygame, pyperclip
from pygame.locals import *

BASE_UNIT = 2
UNIT = 10
KMOD_BASE = 4096
MARGIN = 4

class RootBlock():

    def __init__(self, gui, dimensions, colour, caption='', colour_palette=None):
        if colour_palette is None:
            self.colours = {
                'bg_colour': (230, 220, 205),
                'title_colour': (238, 201, 0),
                'board_colour': (105, 95, 80),
                'tile_colour': (134, 122, 102),
                'black': (0, 0, 0),
                'white': (255, 255, 255),
                'offwhite': (240, 240, 240),
            }
        else:
            self.colours = colour_palette

        self.gui = gui

        self.dimensions = dimensions
        if type(colour) is str:
            self.colour = self.colours[colour]
        elif type(colour) is tuple:
            self.colour = colour
        self.caption = caption

        self.children = []
        self.surface = None

        self.create_object()


    def create_object(self):
        pygame.display.set_caption(self.caption)
        self.surface = pygame.display.set_mode([x * BASE_UNIT for x in self.dimensions])


    def mouse_event_handler(self, event):
        for child in self.children:
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

    def __init__(self, gui, parent, dimensions, coordinates=None, colour='white',
                 polygon=None, priority=0, alignx=False, aligny=False, coordx=None, coordy=None):
        # Check for overdefined coordinates
        x_count, y_count = 0, 0
        if coordinates:
            x_count += 1
            y_count += 1
        if coordx:
            x_count += 1
        if coordy:
            y_count += 1
        if alignx:
            x_count += 1
        if aligny:
            y_count += 1
        assert x_count == 1 and y_count == 1

        self.parent = parent
        self.coordinates = coordinates
        if self.coordinates is None:
            self.coordinates = [None, None]

            if coordx is not None:
                self.coordinates[0] = coordx

            if coordy is not None:
                self.coordinates[1] = coordy

        self.alignment = alignx, aligny
        self.priority = priority
        self.polygon = polygon

        super().__init__(gui, dimensions, colour)


    def create_object(self):
        if type(self.coordinates) is list:
            if any(self.alignment):
                alignx, aligny = self.alignment
                if alignx == 'left':
                    self.coordinates[0] = 0
                elif alignx == 'centre':
                    self.coordinates[0] = (self.parent.dimensions[0] - self.dimensions[0]) // 2
                elif alignx == 'right':
                    self.coordinates[0] = self.parent.dimension[0] - self.dimensions[0]
                else:
                    raise ValueError(f'{alignx} is not a valid alignment.')

                if aligny == 'left':
                    self.coordinates[1] = 0
                elif aligny == 'centre':
                    self.coordinates[1] = (self.parent.dimensions[1] - self.dimensions[1]) // 2
                elif aligny == 'right':
                    self.coordinates[1] = self.parent.dimension[1] - self.dimensions[1]
                else:
                    raise ValueError(f'{aligny} is not a valid alignment.')

            self.coordinates = tuple(self.coordinates)

        self.parent.children.append(self)


    def __delitem__(self):
        for child in self.children.copy():
            child.__delitem__()

        self.parent.children.remove(self)

        self = None


    def create_surface(self):
        block_size = [int(dim * BASE_UNIT) for dim in self.dimensions]

        block = pygame.Surface(block_size)
        block = block.convert()
        block.fill(self.colour)
        self.surface = block


    def move(self, del_x=0, del_y=0, x=None, y=None):
        if x is None:
            x = self.coordinates[0] + del_x
        else:
            del_x = x - self.coordinates[0]
        if y is None:
            y = self.coordinates[1] + del_y
        else:
            del_y = y - self.coordinates[1]

        # Update coordinates
        self.coordinates = tuple([x, y])


    def draw_block(self):
        self.create_surface()
        self.blit_text()

        for child in sorted(self.children, key=lambda x: x.priority):
            child.draw_block()

        if self.polygon:
            pygame.draw.polygon(self.surface, *self.polygon)

        block_pos = [int(coord * BASE_UNIT) for coord in self.coordinates]
        self.parent.surface.blit(self.surface, block_pos)



class Text(Block):

    def __init__(self, gui, parent, dimensions, coordinates, colour, text_info, polygon=None, alignment='centre', priority=0):
        alignments = ['left', 'centre', 'right']
        assert alignment in alignments
        self.text_alignment = alignment

        value, self.font_colour, self.font = text_info
        self.text = {
            'value': str(value),
            'text': None,
            'pos': None
        }

        super().__init__(gui, parent, dimensions, coordinates, colour, polygon, priority)

    def create_object(self):
        super().create_object()

        try:
            self.font = pygame.font.Font(None, self.font)
        except pygame.error:
            pygame.init()
            self.font = pygame.font.Font(None, self.font)

        self.font_colour = self.colours[self.font_colour]


    def update_text(self):
        centre_coords = [int(n * BASE_UNIT // 2) for n in self.dimensions]

        self.text['text'] = self.font.render(self.text['value'], 1, self.font_colour)
        if self.text_alignment == 'left':
            self.text['pos'] = (self.text['text'].get_rect(left=MARGIN * BASE_UNIT,
                                 centery=centre_coords[1]))
        elif self.text_alignment == 'centre':
            self.text['pos'] = (self.text['text'].get_rect(center=centre_coords))
        elif self.text_alignment == 'right':
            self.text['pos'] = (self.text['text'].get_rect(right=(self.dimensions[0] - MARGIN) * BASE_UNIT,
                                 centery=centre_coords[1]))


    def set_text(self, text):
        self.text['value'] = text


    def get_text(self):
        return self.text['value']


    def append_text(self, text):
        self.text['value'] += text


    def remove_text(self, amount=-1):
        assert amount < 0
        self.text['value'] = self.text['value'][:amount]


    def blit_text(self):
        self.update_text()
        self.surface.blit(self.text['text'], self.text['pos'])



class Button(Text):

    def __init__(self, gui, parent, dimensions, coordinates, colour, text_info=None, polygon=None, alignment='centre', priority=0):
        if text_info is None:
            text_info = ('', 'black', 20)

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

        super().__init__(gui, parent, dimensions, coordinates, colour, text_info, alignment=alignment, polygon=polygon, priority=priority)

        def hold_down(event):
            if self.checkCollision(event):
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
        self.button_rect = Rect([int(coord * BASE_UNIT) for coord in self.overall_coords],
                                [int(dim * BASE_UNIT) for dim in self.dimensions])


    def set_mouse_handlers(self, function_dict):
        for func_name, func in function_dict.items():

            def modify_default(func, new_func):

                def inner(*arg):
                    new_func(*arg)
                    func(*arg)
                return inner

            self.event_function_dict[func_name] = modify_default(self.default_mouse_handlers.get(func_name, lambda *_: None), func)


    def mouse_event_handler(self, event):

        super().mouse_event_handler(event)

        if event.type == pygame.MOUSEMOTION:
            self.event_function_dict['move_mouse'](event)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button < 4:
            if event.button == 1: # Left mouse
                self.event_function_dict['left_mouse_down'](event)
            elif event.button == 2: # Right mouse
                self.event_function_dict['right_mouse_down'](event)
            elif event.button == 3: # Middle mouse
                self.event_function_dict['middle_mouse_down'](event)
        elif event.type == pygame.MOUSEBUTTONUP and event.button < 4:
            if event.button == 1: # Left mouse
                self.event_function_dict['left_mouse_up'](event)
            elif event.button == 2: # Right mouse
                self.event_function_dict['right_mouse_up'](event)
            elif event.button == 3: # Middle mouse
                self.event_function_dict['middle_mouse_up'](event)
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


    def checkCollision(self, event):
        mouse_pos = event.pos
        return self.button_rect.collidepoint(mouse_pos)


    def keyboard_event_handler(self, event):
        if event.key == RETURN:
            self.event_function_dict['left_mouse_up'](event)


    def move(self, del_x=0, del_y=0, x=None, y=None):
        super().move(del_x, del_y, x, y)

        # Update rect
        self.overall_coords[0] += del_x
        self.overall_coords[1] += del_y

        self.create_rect()



class TextBox(Button):

    def __init__(self, gui, parent, dimensions, coordinates, default_text=''):

        self.active = False
        self.tb_colours = {
            True: 'white',
            False: 'offwhite'
        }
        colour = self.tb_colours[self.active]

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
        self.extra_info = [self.cursor_info, self.second_text]

        super().__init__(gui, parent, dimensions, coordinates,
                         colour, text_info=None, alignment='left')

        self.set_mouse_handlers({'left_mouse_down': self.toggle_select})

        self.cursor_info['colour'] = self.colour


    def update_cursor(self):

        text_rect = self.text['pos']

        cursor_colour = self.font_colour if self.cursor_info['on'] else self.colour

        self.cursor_info['text'] = self.font.render('|', 1, cursor_colour)
        self.cursor_info['pos'] = self.cursor_info['text'].get_rect(left=text_rect.right, centery=text_rect.centery)


    def toggle_select(self, event):
        isCollision = self.checkCollision(event)
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
        if amount < 0 and len(self.text['value']) > 0:
            self.second_text['value'] = self.text['value'][amount] + self.second_text['value']
            self.remove_text(amount)
        elif amount > 0 and len(self.second_text['value']) > 0:
            self.append_text(self.second_text['value'][:amount])
            self.second_text['value'] = self.second_text['value'][amount:]


    def update_text(self):
        super().update_text()

        if self.active:

            if self.text['pos'].width + self.cursor_info['pos'].width > (self.dimensions[0] - 2 * MARGIN) * BASE_UNIT:
                self.text['pos'] = (self.text['text'].get_rect(right=(self.dimensions[0] - MARGIN) * BASE_UNIT - self.cursor_info['pos'].width,
                                     centery=self.text['pos'].centery))

            second_text_left = self.cursor_info['pos'].right

        else:
            second_text_left = self.text['pos'].right

        self.update_cursor()

        self.second_text['text'] = self.font.render(self.second_text['value'], 1, self.font_colour)
        self.second_text['pos'] = self.second_text['text'].get_rect(left=second_text_left,
                                                                    centery=self.text['pos'].centery)


    def toggle_cursor(self):
        self.cursor_info['on'] = not self.cursor_info['on']


    def set_text(self, text):
        super().set_text(text)
        self.second_text['value'] = ''


    def get_text(self):
        return self.text['value'] + self.second_text['value']


    def append_text(self, text):
        super().append_text(text)


    def remove_text(self, amount=-1):
        super().remove_text(amount)


    def keyboard_event_handler(self, event):
        if (event.mod - KMOD_BASE == KMOD_LCTRL or
            event.mod - KMOD_BASE == KMOD_RCTRL or
            event.mod - KMOD_BASE == KMOD_CTRL):
            character = pygame.key.name(event.key)
            if character == 'x':
                pyperclip.copy(self.text['value'] + self.second_text['value'])
                self.second_text['value'] = ''
                self.set_text('')
            elif character =='c':
                pyperclip.copy(self.text['value'] + self.second_text['value'])
            elif character == 'v':
                text = pyperclip.paste()
                self.second_text['value'] = ''
                self.set_text(text)

            elif character in ['a', 's', 'z', 'y', 'x', 'c', 'v']:
                print('Get to this...')
        elif event.key == K_RETURN:
            pass
        elif event.key == K_BACKSPACE:
            self.remove_text()
        elif event.key == K_DELETE:
            self.second_text['value'] = self.second_text['value'][1:]
        elif event.key == K_LEFT:
            self.move_cursor(-1)
        elif event.key == K_RIGHT:
            self.move_cursor(1)
        else:
            self.append_text(event.unicode)

        self.update_text()


    def blit_text(self):
        super().blit_text()
        self.surface.blit(self.cursor_info['text'], self.cursor_info['pos'])
        self.surface.blit(self.second_text['text'], self.second_text['pos'])



class Slider(Button):

    def __init__(self, gui, parent, dimensions, coordinates, colour, dropdown, move_limits):

        self.min_limits, self.max_limits = move_limits
        assert self.min_limits[0] <= self.max_limits[0] and self.min_limits[1] <= self.max_limits[1]

        super().__init__(gui, parent, dimensions, coordinates, colour)

        self.offset = [0, 0]
        self.dropdown = dropdown
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
            mouse_pos = [n // BASE_UNIT for n in event.pos]
            if self.max_limits[0] - self.min_limits[0] != 0:
                x = mouse_pos[0] + self.offset[0]
                if x < self.min_limits[0]:
                    x = self.min_limits[0]
                elif x > self.max_limits[0]:
                    x = self.max_limits[0]
            else:
                x = self.coordinates[0]

            if self.max_limits[1] - self.min_limits[1] != 0:
                y = mouse_pos[1] + self.offset[1]
                if y < self.min_limits[1]:
                    y = self.min_limits[1]
                elif y > self.max_limits[1]:
                    y = self.max_limits[1]
            else:
                y = self.coordinates[1]

            self.move(x=x, y=y)
            self.dropdown.rel_scroll_list((y - self.min_limits[1]) / (self.max_limits[1] - self.min_limits[1]))


    def hold_slider(self, event):
        isCollision = self.checkCollision(event)
        if isCollision:
            self.held = True
            for i in range(2):
                self.offset[i] = self.coordinates[i] - event.pos[i] // BASE_UNIT


    def release_slider(self, isCollision):
        self.held = False
        self.offset = [0, 0]



class Dropdown(Block):

    def __init__(self, gui, parent, dimensions, coordinates, options_list=None):

        self.gui = gui
        self.parent = parent
        self.dimensions = dimensions
        self.coordinates = coordinates
        self.options_list = options_list

        if self.options_list is None:
            self.options_list = [f'{i}word{i}' for i in range(50)]
        self.options_list.sort()

        self.textbox = None
        self.button = None
        self.dropdown = None
        self.scroll_handle = None
        self.item_dict = {}

        self.active = False
        self.scroll_amount = 0
        self.scroll_constant = 5
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
        self.textbox = TextBox(self.gui, self.parent, textbox_dim, textbox_coords)

        def dropdown_child(func):

            def inner(*args):
                func(*args)
                self.filter_options()
                return

            return inner

        self.textbox.append_text = dropdown_child(self.textbox.append_text)
        self.textbox.remove_text = dropdown_child(self.textbox.remove_text)

        def dropdown_textbox_toggle(event):
            textboxCollision = self.textbox.checkCollision(event)
            buttonCollision = self.button.checkCollision(event)
            dropdownCollision = 0 if self.dropdown is None else self.dropdown.checkCollision(event)

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
        button_text_info = ('', 'black', 20)
        # Button triangle
        colour = (50, 50, 50)
        points = [(10, 15), (30, 15), (20, 30)]

        self.button = Button(self.gui, self.parent,
                             button_dim, button_coords, 'tile_colour',
                             button_text_info, polygon=(colour, points))


        def dropdown_button_up(event):
            buttonCollision = self.button.checkCollision(event)
            dropdownCollision = False if self.dropdown is None else self.dropdown.checkCollision(event)

            if buttonCollision and self.button.held:
                if self.active:
                    self.close_dropdown_list()
                else:
                    self.textbox.active = True
                    self.open_dropdown_list()

        def dropdown_button_down(event):
            textboxCollision = self.textbox.checkCollision(event)
            buttonCollision = self.button.checkCollision(event)
            dropdownCollision = False if self.dropdown is None else self.dropdown.checkCollision(event)

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
        item_width, item_height = max(total_width - total_height, total_width // 2), 2 * UNIT

        # Find distance to bottom of screen
        parent_tmp = self.parent
        y_coord_tmp = self.coordinates[1]
        while parent_tmp != self.gui.window:
            y_coord_tmp += parent_tmp.coordinates[1]
            parent_tmp = parent_tmp.parent

        available_space = parent_tmp.surface.get_height() // BASE_UNIT - (y_coord_tmp + total_height)
        max_items = min(len(self.options_list), available_space // item_height)


        dropdown_dimensions = total_width, max_items * item_height
        dropdown_coords = x_coord, y_coord + total_height
        self.dropdown = Button(self.gui, self.parent, dropdown_dimensions,
                               dropdown_coords, 'white', priority=99)

        self.max_scroll = max(0, len(self.options_list) * item_height - dropdown_dimensions[1])

        item_dim = item_width, item_height
        for i, item in enumerate(self.options_list):
            item_coords = 0, i * total_height - self.scroll_amount
            button_text_info = (item, 'black', 20)
            button = Button(self.gui, self.dropdown, item_dim, item_coords,
                            'white', button_text_info, alignment='left')

            def create_function():
                value_copy = item
                tmp_button = button

                def button_func(event):
                    if tmp_button.checkCollision(event) and tmp_button.held:
                        self.close_dropdown_list()
                        self.textbox.set_text(value_copy)

                return button_func

            func_dict = {'left_mouse_up': create_function()}
            button.set_mouse_handlers(func_dict)

            self.item_dict[i] = button


        scroll_handle_dimensions = total_width - item_width, int(dropdown_dimensions[1] ** 2 / (len(self.options_list) * item_height))
        scroll_handle_initial_coords = item_width, 0
        limits = (item_width, 0), (item_width, dropdown_dimensions[1] - scroll_handle_dimensions[1])
        self.scroll_handle = Slider(self.gui, self.dropdown, scroll_handle_dimensions,
                                    scroll_handle_initial_coords, 'tile_colour', self, limits)

        self.dropdown.set_mouse_handlers({'scroll_mouse': lambda event, scroll: self.abs_scroll_list(scroll) if self.dropdown.checkCollision(event) else None})


    def close_dropdown_list(self):
        self.active = False
        self.scroll_amount = 0
        self.dropdown.__delitem__()
        self.dropdown = None


    def update_item_positions(self):
        for i, item in self.item_dict.items():
            item.move(y=i * self.dimensions[1] - self.scroll_amount)


    def filter_options(self):
        text = self.textbox.text['value'] + self.textbox.second_text['value']
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



class myGUI():

    def __init__(self, window_size, caption, win_colour, colour_palette=None):

        self.window = RootBlock(self, window_size, win_colour, caption=caption, colour_palette=colour_palette)
        self.active_object = None


    def run_GUI(self):
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
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.quit_gui() # Allows user to overwrite quit process
                    if (event.mod - KMOD_BASE == KMOD_LCTRL or
                        event.mod - KMOD_BASE == KMOD_RCTRL or
                        event.mod - KMOD_BASE == KMOD_CTRL):
                        character = pygame.key.name(event.key)
                        if character == 's':
                            pass
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

    # -------------------------- Object Creation ----------------------------

    def create_block(self, *args, **kwargs):
        return Block(self, *args, **kwargs)


    def create_text(self, *args, **kwargs):
        return Text(self, *args, **kwargs)


    def create_button(self, *args, **kwargs):
        return Button(self, *args, **kwargs)


    def create_textbox(self, *args, **kwargs):
        return TextBox(self, *args, **kwargs)


    def create_dropdown(self, *args, **kwargs):
        return Dropdown(self, *args, **kwargs)


if __name__ == '__main__':
    # Create test GUI

    caption = "Test GUI"
    window_size = win_width, win_height = (int(BASE_UNIT * UNIT * 35 - BASE_UNIT),
                                           int(BASE_UNIT * UNIT * 20))
    fill_colour = 'bg_colour'

    gui1 = myGUI(window_size, caption, fill_colour)

    # Add GUI elements
    block_info = {
        'parent': gui1.window,
        'dimensions': (5 * UNIT, 2 * UNIT),
        'coordinates': (3 * UNIT, 1 * UNIT),
        'colour': 'white'
    }

    gui1.create_block(**block_info)

    text_info = ('Test', 'black', 20)
    gui1.create_text(gui1.window, (5 * UNIT, 2 * UNIT), (3 * UNIT, 4 * UNIT), 'white', text_info)


    button_text_info = ('QUIT', 'black', 20)
    button1 = gui1.create_button(gui1.window, (5 * UNIT, 2 * UNIT), (3 * UNIT, 7 * UNIT), 'white', button_text_info)

    func_dict = {
        'left_mouse_up': lambda event: gui1.quit_gui() if button1.checkCollision(event) and button1.held else None
    }
    button1.set_mouse_handlers(func_dict)

    gui1.create_textbox(gui1.window, (8 * UNIT, 2 * UNIT), (3 * UNIT, 10 * UNIT))

    gui1.create_dropdown(gui1.window, (8 * UNIT, 2 * UNIT), (9 * UNIT, 1 * UNIT))

    gui1.run_GUI()
