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


class RootBlock():

    def __init__(self, gui, name, dimensions, colour, caption='', colour_palette=None):
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

        self.name = name
        self.dimensions = dimensions
        if type(colour) is str:
            self.colour = self.colours[colour]
        else:
            self.colour = colour
        self.caption = caption

        self.children = []
        self.surface = None

        self.create_object()

    def create_object(self):
        pygame.display.set_caption(caption)
        self.surface = pygame.display.set_mode(self.dimensions)

    def fill_window(self):
        self.surface.fill(self.colour)

    def mouse_event_handler(self, event):
        for child, priority in self.children:
            self.gui.gui_info[child].mouse_event_handler(event)

    def keyboard_event_handler(self, event):
        pass

    def blit_text(self):
        pass


class Block(RootBlock):

    def __init__(self, gui, name, parent, dimensions, coordinates, colour, priority=0):
        self.gui_info = gui.gui_info

        self.parent = parent
        self.coordinates = coordinates
        self.priority = priority

        super().__init__(gui, name, dimensions, colour)

    def create_object(self):
        self.gui_info.append(self)

    def __delitem__(self):
        del self.gui_info[self.name]

    def create_surface(self):
        block_info = self.gui_info[self.name]
        block_size = [int(dim * BASE_UNIT) for dim in block_info.dimensions]

        block = pygame.Surface(block_size)
        block = block.convert()
        block.fill(block_info.colour)
        block_info.surface = block

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

        # Update rect
        self.overall_coords[0] += del_x
        self.overall_coords[1] += del_y

        self.create_rect()


class Text(Block):

    def __init__(self, gui, name, parent, dimensions, coordinates, colour, text_info, alignment='centre', priority=0):
        alignments = ['left', 'centre', 'right']
        assert alignment in alignments
        self.text_alignment = alignment

        value, self.font_colour, self.font = text_info
        self.text = {
            'value': str(value),
            'text': None,
            'pos': None
        }

        super().__init__(gui, name, parent, dimensions, coordinates, colour, priority)

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
        margin = 4
        if self.text_alignment == 'left':
            self.text['pos'] = (self.text['text'].get_rect(left=margin * BASE_UNIT,
                centery=centre_coords[1]))
        elif self.text_alignment == 'centre':
            self.text['pos'] = (self.text['text'].get_rect(center=centre_coords))
        elif self.text_alignment == 'right':
            self.text['pos'] = (self.text['text'].get_rect(right=(self.dimensions[0] - margin) * BASE_UNIT,
                centery=centre_coords[1]))

    def set_text(self, text):
        self.text['value'] = text

    def append_text(self, text):
        self.text['value'] += text

    def remove_text(self, amount=-1):
        assert amount < 0
        self.text['value'] = self.text['value'][:amount]

    def blit_text(self):
        self.update_text()
        self.surface.blit(self.text['text'], self.text['pos'])


class Button(Text):

    def __init__(self, gui, name, parent, dimensions, coordinates, colour, text_info=None, alignment='centre', priority=0):
        if text_info is None:
            text_info = ('', 'black', 20)

        self.button_set = gui.gui_info.button_set

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

        super().__init__(gui, name, parent, dimensions, coordinates, colour, text_info, alignment=alignment, priority=priority)

        def hold_down(event):
            if self.checkCollision(event):
                self.held = True

        def release(event):
            self.held = False

        self.set_mouse_handlers({'left_mouse_down': hold_down,
                                 'left_mouse_up': release})

    def create_object(self):
        super().create_object()

        # Coordinates need to be reference from window, not parent surface
        parent_tmp = self.parent
        self.overall_coords = list(self.coordinates)
        while parent_tmp != 'window':
            self.overall_coords[0] += self.gui_info[parent_tmp].coordinates[0]
            self.overall_coords[1] += self.gui_info[parent_tmp].coordinates[1]
            parent_tmp = self.gui_info[parent_tmp].parent

        self.create_rect()

        self.button_set.add(self.name)

    def create_rect(self):
        # Create rect object for simplicity of collision detection
        self.button_rect = Rect([int(coord * BASE_UNIT) for coord in self.overall_coords],
            [int(dim * BASE_UNIT) for dim in self.dimensions])

    def set_mouse_handlers(self, function_dict):
        for func_name, func in function_dict.items():
            eval(compile(f'self.set_{func_name}(func)', "<string>", "eval"))

    def mouse_event_handler(self, event):

        super().mouse_event_handler(event)

        if event.type == pygame.MOUSEMOTION:
            self.event_function_dict['move_mouse'](event)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button < 4:
            if event.button == 1:  # Left mouse
                self.event_function_dict['left_mouse_down'](event)
            elif event.button == 2:  # Right mouse
                self.event_function_dict['right_mouse_down'](event)
            elif event.button == 3:  # Middle mouse
                self.event_function_dict['middle_mouse_down'](event)
        elif event.type == pygame.MOUSEBUTTONUP and event.button < 4:
            if event.button == 1:  # Left mouse
                self.event_function_dict['left_mouse_up'](event)
            elif event.button == 2:  # Right mouse
                self.event_function_dict['right_mouse_up'](event)
            elif event.button == 3:  # Middle mouse
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

    # Setter functions for functions for every mouse event
    def set_left_mouse_down(self, f):
        self.event_function_dict['left_mouse_down'] = f

    def set_right_mouse_down(self, f):
        self.event_function_dict['right_mouse_down'] = f

    def set_middle_mouse_down(self, f):
        self.event_function_dict['middle_mouse_down'] = f

    def set_left_mouse_up(self, f):
        self.event_function_dict['left_mouse_up'] = f

    def set_right_mouse_up(self, f):
        self.event_function_dict['right_mouse_up'] = f

    def set_middle_mouse_up(self, f):
        self.event_function_dict['middle_mouse_up'] = f

    def set_scroll_mouse(self, f):
        self.event_function_dict['scroll_mouse'] = f

    def set_move_mouse(self, f):
        self.event_function_dict['move_mouse'] = f

    def keyboard_event_handler(event):
        if event.key == RETURN:
            self.event_function_dict['left_mouse_up'](event)


class TextBox(Button):

    def __init__(self, gui, name, parent, dimensions, coordinates, default_text=''):

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

        super().__init__(gui, name, parent, dimensions, coordinates,
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
            self.update_text()
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
            margin = 4

            if self.text['pos'].width + self.cursor_info['pos'].width > (self.dimensions[0] - 2 * margin) * BASE_UNIT:
                self.text['pos'] = (self.text['text'].get_rect(right=(self.dimensions[0] - margin) * BASE_UNIT - self.cursor_info['pos'].width,
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
                pyperclip.copy(self.text + self.second_text['value'])
                self.second_text['value'] = ''
                self.set_text('')
            elif character == 'c':
                pyperclip.copy(self.text + self.second_text['value'])
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

    def __init__(self, gui, name, parent, dimensions, coordinates, colour, dropdown, move_limits):

        self.min_limits, self.max_limits = move_limits
        assert self.min_limits[0] <= self.max_limits[0] and self.min_limits[1] <= self.max_limits[1]

        super().__init__(gui, name, parent, dimensions, coordinates, colour)

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

    def __init__(self, gui, name, parent, dimensions, coordinates, options_list=None):

        self.gui = gui
        self.gui_info = gui.gui_info
        self.polygon_dict = gui.gui_info.polygon_dict
        self.name = name
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
        textbox_name = f'{self.name}_text'
        textbox_dim = textbox_width, total_height
        textbox_coords = x_coord, y_coord
        self.textbox = TextBox(self.gui, textbox_name, self.parent, textbox_dim, textbox_coords)

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
            dropdownCollision = False if self.dropdown is None else self.dropdown.checkCollision(event)

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
        button_name = f'{self.name}_button'
        button_dim = button_width, total_height
        button_coords = x_coord + textbox_width, y_coord
        button_text_info = ('', 'black', 20)
        self.button = Button(self.gui, button_name, self.parent,
            button_dim, button_coords, 'tile_colour',
            button_text_info)

        def dropdown_button_up(event):
            buttonCollision = self.button.checkCollision(event)
            dropdownCollision = False if self.dropdown is None else self.dropdown.checkCollision(event)

            if buttonCollision and self.button.held:
                self.active = not self.active
                if self.active:
                    self.textbox.active = True
                    self.dropdown_list()
                else:
                    self.scroll_amount = 0
                    del self.gui_info[self.dropdown.name]
                    self.dropdown = None
            self.button.held = False

        def dropdown_button_down(event):
            textboxCollision = self.textbox.checkCollision(event)
            buttonCollision = self.button.checkCollision(event)
            dropdownCollision = False if self.dropdown is None else self.dropdown.checkCollision(event)

            if buttonCollision:
                self.button.held = True
            elif not any([textboxCollision, buttonCollision, dropdownCollision]) and self.active:
                self.active = False
                self.scroll_amount = 0
                del self.gui_info[self.dropdown.name]
                self.dropdown = None

        self.button.set_mouse_handlers({'left_mouse_up': dropdown_button_up,
                                        'left_mouse_down': dropdown_button_down})

        points = [(10, 15), (30, 15), (20, 30)]
        colour = (50, 50, 50)
        parent = button_name

        self.polygon_dict[parent] = colour, points

    def abs_scroll_list(self, scroll):
        self.scroll_amount += scroll * self.scroll_constant
        if self.scroll_amount < 0:
            self.scroll_amount = 0
        if self.scroll_amount > self.max_scroll:
            self.scroll_amount = self.max_scroll

        self.scroll_handle.set_y_pos(self.scroll_amount / self.max_scroll)
        self.update_item_positions()

    def rel_scroll_list(self, scroll_ratio):
        self.scroll_amount = int(scroll_ratio * self.max_scroll)
        self.update_item_positions()

    def dropdown_list(self):

        x_coord, y_coord = self.coordinates
        total_width, total_height = self.dimensions
        item_width, item_height = max(total_width - total_height, total_width // 2), 2 * UNIT

        # Find distance to bottom of screen
        parent_tmp = self.parent
        y_coord_tmp = self.coordinates[1]
        while parent_tmp != 'window':
            y_coord_tmp += self.gui_info[parent_tmp].coordinates[1]
            parent_tmp = self.gui_info[parent_tmp].parent

        available_space = self.gui_info[parent_tmp].surface.get_height() // BASE_UNIT - (y_coord_tmp + total_height)
        max_items = min(len(self.options_list), available_space // item_height)

        dropdown_name = f'{self.name}_dropdown'
        dropdown_dimensions = total_width, max_items * item_height
        dropdown_coords = x_coord, y_coord + total_height
        self.dropdown = Button(self.gui, dropdown_name, self.parent,
            dropdown_dimensions, dropdown_coords,
            'white', priority=99)

        self.max_scroll = max(0, len(self.options_list) * item_height - dropdown_dimensions[1])

        item_dim = item_width, item_height
        for i, item in enumerate(self.options_list):
            item_coords = 0, i * total_height - self.scroll_amount
            button_text_info = (item, 'black', 20)
            # print(item)
            # set_text_func()
            button = Button(self.gui, f'{dropdown_name}_li{i}', dropdown_name,
                item_dim, item_coords, 'white', button_text_info, alignment='left')

            def create_function():
                value_copy = item
                tmp_button = button

                def button_func(event):
                    if tmp_button.checkCollision(event) and tmp_button.held:
                        self.active = False
                        self.scroll_amount = 0
                        del self.gui_info[self.dropdown.name]
                        self.dropdown = None
                        return self.textbox.set_text(value_copy)

                return button_func

            func_dict = {'left_mouse_up': create_function()}
            button.set_mouse_handlers(func_dict)

            self.item_dict[i] = button

        scroll_handle_dimensions = total_width - item_width, int(dropdown_dimensions[1] ** 2 / (len(self.options_list) * item_height))
        scroll_handle_initial_coords = item_width, 0
        limits = (item_width, 0), (item_width, dropdown_dimensions[1] - scroll_handle_dimensions[1])
        self.scroll_handle = Slider(self.gui, f'{dropdown_name}_scrollhandle', dropdown_name,
            scroll_handle_dimensions, scroll_handle_initial_coords, 'tile_colour', self, limits)

        self.dropdown.set_mouse_handlers({'scroll_mouse': lambda event, scroll: self.abs_scroll_list(scroll) if self.dropdown.checkCollision(event) else None})

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
                    self.active = True
                    self.dropdown_list()
                self.scroll_handle.set_y_pos(self.scroll_amount / self.max_scroll)
                break

    def toggle_cursor(self):
        self.textbox.toggle_cursor()

    def mouse_event_handler(self, event):
        super().mouse_event_handler(event)

    def keyboard_event_handler(self, event):
        self.textbox.keyboard_event_handler(event)

    def blit_text(self):
        pass


class GUIStorage(dict):

    def __init__(self, node):
        self.root_node = node

        self.init_info_storage()

    def init_info_storage(self):
        super().__init__()
        self[self.root_node.name] = self.root_node

        self.button_set = set()
        self.polygon_dict = {}

        self.queue = []

    def append(self, node):
        """name -> name of block
           parent -> name of parent block
           position -> euclidean coordinates of block
        """
        self[node.parent].children.append((node.name, node.priority))
        self[node.name] = node
        return None

    def branch(self, node_name):
        """Returns the branch of the tree beginning at node.
        """
        self.queue = [(node_name, self[node_name].priority)]
        return (x for x in self)

    def __delitem__(self, node_name):
        children = [x[0] for x in self[node_name].children]
        for child_node_name in children:
            del self[child_node_name]

        parent = self[node_name].parent
        priority = self[node_name].priority
        self[parent].children.remove((node_name, priority))

        node_type = type(self[node_name])

        while True:
            if node_type == RootBlock or node_type == Block:
                break

            if node_type == Text:
                break

            self.button_set.remove(node_name)
            if node_type == Button or node_type == Slider:
                break

            # Delete active status
            if node_type == TextBox:
                break

            del self.polygon_dict[node_name]
            if node_type == Dropdown:
                break

            assert 1 == 2  # Checking no rogue blocks exist

        super().__delitem__(node_name)

    def __iter__(self):
        """Iterates through as a depth first search.
        """
        if not self.queue:
            self.queue.extend(sorted(self[self.root_node.name].children, key=lambda x: x[1], reverse=True))

        while self.queue:
            current_object = self.queue.pop(0)[0]
            new_items = sorted(self[current_object].children, key=lambda x: x[1], reverse=True)
            self.queue.extend(new_items)
            yield current_object, self[current_object]


class myGUI():

    def __init__(self, window_size, caption, win_colour):

        window_name = 'window'
        self.window = RootBlock(self, window_name, window_size, win_colour, caption=caption)
        self.gui_info = GUIStorage(self.window)
        self.active_object = None

    def run_GUI(self):
        self.running = True
        pygame.init()

        self.draw_board()
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
                        self.quit_gui()  # Allows user to overwrite quit process
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

            self.draw_board()

        pygame.quit()

    def quit_gui(self):
        self.running = False

    # -------------------------- Object Creation ----------------------------

    def create_block(self, name, parent, dimensions, coordinates, colour, priority=0):
        Block(self, name, parent, dimensions, coordinates, colour, priority)

    def create_text(self, name, parent, dimensions, coordinates, colour, text_info):
        Text(self, name, parent, dimensions, coordinates, colour, text_info)

    def create_button(self, name, parent, dimensions, coordinates, colour, text_info=None):
        return Button(self, name, parent, dimensions, coordinates, colour, text_info)

    def set_button_functions(self, button, function_dict):
        button.set_mouse_handlers(function_dict)

    def create_textbox(self, name, parent, dimensions, coordinates, default_text=''):
        TextBox(self, name, parent, dimensions, coordinates, default_text)

    def create_dropdown(self, name, parent, dimensions, coordinates):
        Dropdown(self, name, parent, dimensions, coordinates)

    # -------------------------- GUI Drawing ----------------------------

    def draw_polygons(self):
        for parent, polygon_info in self.gui_info.polygon_dict.items():
            colour, points = polygon_info
            parent_surface = self.gui_info[parent].surface
            pygame.draw.polygon(parent_surface, colour, points)

    def draw_board(self):

        self.window.fill_window()

        def draw_recurse(block_iter):
            try:
                block_name, block_info = next(block_iter)
            except StopIteration:
                self.draw_polygons()
                return True

            block_info.create_surface()
            block_info.blit_text()

            draw_recurse(block_iter)

            parent_surface = self.gui_info[block_info.parent].surface
            block_pos = [int(coord * BASE_UNIT) for coord in block_info.coordinates]
            parent_surface.blit(block_info.surface, block_pos)

        block_iter = iter(self.gui_info)
        draw_recurse(block_iter)

        pygame.display.flip()


if __name__ == '__main__':
    # Create test GUI

    caption = "Test GUI"
    window_size = win_width, win_height = (int(BASE_UNIT * UNIT * 35 - BASE_UNIT),
                                           int(BASE_UNIT * UNIT * 20))
    fill_colour = 'bg_colour'

    gui1 = myGUI(window_size, caption, fill_colour)

    # Add GUI elements
    gui1.create_block('test_block', 'window', (5 * UNIT, 2 * UNIT), (3 * UNIT, 1 * UNIT), 'white')

    text_info = ('Test', 'black', 20)
    gui1.create_text('test_text', 'window', (5 * UNIT, 2 * UNIT), (3 * UNIT, 4 * UNIT), 'white', text_info)

    button_text_info = ('QUIT', 'black', 20)
    button1 = gui1.create_button('quit_button', 'window', (5 * UNIT, 2 * UNIT), (3 * UNIT, 7 * UNIT), 'white', button_text_info)

    func_dict = {
        'left_mouse_up': lambda event: gui1.quit_gui() if button1.checkCollision(event) and button1.held else None
    }
    gui1.set_button_functions(button1, func_dict)

    gui1.create_textbox('textbox_1', 'window', (8 * UNIT, 2 * UNIT), (3 * UNIT, 10 * UNIT))

    gui1.create_dropdown('dropdown', 'window', (8 * UNIT, 2 * UNIT), (9 * UNIT, 1 * UNIT))

    # gui1.create_textbox('textbox_2', 'window', (8 * UNIT, 2 * UNIT), (3 * UNIT, 16 * UNIT))

    gui1.run_GUI()

