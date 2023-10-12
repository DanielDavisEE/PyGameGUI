import pygame
from pygame.locals import *
from pygame_gui.custom_storage import MyList

BASE_UNIT = 2
UNIT = 10
KMOD_BASE = 4096

NUMBERS = {
    K_0,
    K_1,
    K_2,
    K_3,
    K_4,
    K_5,
    K_6,
    K_7,
    K_8,
    K_9,
}

LETTERS = {
    K_a,
    K_b,
    K_c,
    K_d,
    K_e,
    K_f,
    K_g,
    K_h,
    K_i,
    K_j,
    K_k,
    K_l,
    K_m,
    K_n,
    K_o,
    K_p,
    K_q,
    K_r,
    K_s,
    K_t,
    K_u,
    K_v,
    K_w,
    K_x,
    K_y,
    K_z
}

PUNCTUATION = {
    K_AMPERSAND,
    K_ASTERISK,
    K_AT,
    K_BACKQUOTE,
    K_BACKSLASH,
    K_CARET,
    K_COLON,
    K_COMMA,
    K_DOLLAR,
    K_EQUALS,
    K_EXCLAIM,
    K_GREATER,
    K_HASH,
    K_LEFTBRACKET,
    K_LEFTPAREN,
    K_LESS,
    K_MINUS,
    K_PERCENT,
    K_PERIOD,
    K_PLUS,
    K_QUESTION,
    K_QUOTE,
    K_QUOTEDBL,
    K_RIGHTBRACKET,
    K_RIGHTPAREN,
    K_SEMICOLON,
    K_SLASH,
    K_UNDERSCORE
}

WHITESPACE = {
    K_SPACE: ' '
}

OTHER = [
    K_BACKSPACE,
    K_BREAK,
    K_CAPSLOCK,
    K_CLEAR,
    K_CURRENCYSUBUNIT,
    K_CURRENCYUNIT,
    K_DELETE,
    K_DOWN,
    K_END,
    K_ESCAPE,
    K_EURO,
    K_F1,
    K_F10,
    K_F11,
    K_F12,
    K_F13,
    K_F14,
    K_F15,
    K_F2,
    K_F3,
    K_F4,
    K_F5,
    K_F6,
    K_F7,
    K_F8,
    K_F9,
    K_HELP,
    K_HOME,
    K_INSERT,
    K_KP0,
    K_KP1,
    K_KP2,
    K_KP3,
    K_KP4,
    K_KP5,
    K_KP6,
    K_KP7,
    K_KP8,
    K_KP9,
    K_KP_0,
    K_KP_1,
    K_KP_2,
    K_KP_3,
    K_KP_4,
    K_KP_5,
    K_KP_6,
    K_KP_7,
    K_KP_8,
    K_KP_9,
    K_KP_DIVIDE,
    K_KP_ENTER,
    K_KP_EQUALS,
    K_KP_MINUS,
    K_KP_MULTIPLY,
    K_KP_PERIOD,
    K_KP_PLUS,
    K_LALT,
    K_LCTRL,
    K_LEFT,
    K_LGUI,
    K_LMETA,
    K_LSHIFT,
    K_LSUPER,
    K_MENU,
    K_MODE,
    K_NUMLOCK,
    K_NUMLOCKCLEAR,
    K_PAGEDOWN,
    K_PAGEUP,
    K_PAUSE,
    K_POWER,
    K_PRINT,
    K_PRINTSCREEN,
    K_RALT,
    K_RCTRL,
    K_RETURN,
    K_RGUI,
    K_RIGHT,
    K_RMETA,
    K_RSHIFT,
    K_RSUPER,
    K_SCROLLLOCK,
    K_SCROLLOCK,
    K_SPACE,
    K_SYSREQ,
    K_TAB,
    K_UNKNOWN,
    K_UP,
]


class GUI_Element():

    def __init__(self):
        if not pygame.font:
            raise ImportError("Fonts not imported")

        self.colours = {
            'bg_colour': (230, 220, 205),
            'title_colour': (238, 201, 0),
            'board_colour': (105, 95, 80),
            'tile_colour': (134, 122, 102),
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'offwhite': (240, 240, 240),
        }

        self.active_object = None

    def adjust_transparency(self, colour, transparency):
        raw_colour = list(colour)[:3]
        raw_colour.append(transparency)
        return tuple(raw_colour)

    # -------------------------- Object Creation ----------------------------

    def create_button(self, block_list, button_dict, function, name, parent, dimensions, coordinates, colour, text_info=None, priority=0):

        if text_info is None:
            # text value, text colour, text size
            text_info = ('', 'black', 20)

        # Coordinates need to be reference from window, not parent surface
        parent_tmp = parent
        overall_coords = list(coordinates)
        while parent_tmp != 'window':
            overall_coords[0] += block_list[parent_tmp].coordinates[0]
            overall_coords[1] += block_list[parent_tmp].coordinates[1]
            parent_tmp = block_list[parent_tmp].parent

        # Create rect object for simplicity of collision detection
        button_rect = Rect([int(coord * BASE_UNIT) for coord in overall_coords],
            [int(dim * BASE_UNIT) for dim in dimensions])
        button_dict[name] = (button_rect, function)

        # Create surface as usual
        block_list.append(name, parent, dimensions, coordinates, colour, priority)

        # Create text on button
        self.create_text(f'{name}_text', name, *text_info)

        return block_list[name]

    def del_button(self, block_list, button_dict, text_dict, name):
        del block_list[name]
        del button_dict[name]

        self.active_object = None

        self.del_text(text_dict, f'{name}_text')

    def create_block(self, block_list, name, parent, dimensions, coordinates, colour, priority=0):
        block_list.append(name, parent, dimensions, coordinates, colour, priority)
        return block_list[name]

    def create_text(self, block_list, text_dict, name, parent, value, colour, size):
        coords = [int(n * BASE_UNIT // 2) for n in block_list[parent].dimensions]

        try:
            font = pygame.font.Font(None, size)
        except pygame.error:
            pygame.init()
            font = pygame.font.Font(None, size)

        text = font.render(str(value), 1, self.colours[colour])
        pos = (text.get_rect(centerx=coords[0],
            centery=coords[1]))
        text_dict[name] = [text, pos, parent]

    def del_text(self, text_dict, name):
        del text_dict[name]

    def create_surface(self, block_info):
        block_size = [int(dim * BASE_UNIT) for dim in block_info.dimensions]

        block = pygame.Surface(block_size)
        block = block.convert()
        block.fill(self.colours[block_info.colour])
        block_info.surface = block


class TextBox(GUI_Element):

    def __init__(self, block_list, button_dict, text_dict, textbox_dict,
                 name, parent, dimensions, coordinates, text='', font_colour='black', font_size=20):
        super().__init__()

        self.block_list = block_list
        self.button_dict = button_dict
        self.text_dict = text_dict
        self.textbox_dict = textbox_dict

        self.name = name
        self.parent = parent
        self.dimensions = dimensions
        self.coordinates = coordinates
        self.font_colour = font_colour
        self.font_size = font_size
        self.text = text

        self.active = False
        self.tb_colours = {
            True: 'white',
            False: 'offwhite'
        }
        self.colour = self.tb_colours[self.active]

        self.text_info = [self.text, font_colour, font_size]

        self.textbox_dict[self.name] = self.set_text, self.append_text, self.remove_text

        self.generate_object()

    def set_text(self, text):
        self.text = text
        self.text_info[0] = self.text
        self.generate_object()

    def append_text(self, text):
        self.text += text
        self.text_info[0] = self.text
        self.generate_object()

    def remove_text(self):
        self.text = self.text[:-1]
        self.text_info[0] = self.text
        self.generate_object()

    def toggle_select(self):
        self.active = not self.active
        self.colour = self.tb_colours[self.active]
        self.generate_object()

    def create_text(self, name, parent, value, colour, size):
        super().create_text(self.block_list, self.text_dict, name, parent,
            value, colour, size)

    def generate_object(self):
        self.create_button(self.block_list, self.button_dict,
            self.toggle_select, self.name, self.parent,
            self.dimensions, self.coordinates, self.colour,
            self.text_info)


class Dropdown(GUI_Element):

    def __init__(self, block_list, button_dict, text_dict, polygon_dict, textbox_dict,
                 name, parent, dimensions, coordinates, options_list=None, text='', font_colour='black', font_size=20):

        super().__init__()

        self.block_list = block_list
        self.button_dict = button_dict
        self.text_dict = text_dict
        self.polygon_dict = polygon_dict
        self.textbox_dict = textbox_dict

        self.name = name
        self.parent = parent
        self.dimensions = dimensions
        self.coordinates = coordinates
        self.options_list = options_list
        self.font_colour = font_colour
        self.font_size = font_size
        self.text = text

        self.active = False
        self.scroll_amount = 0

        self.generate_object()

        self.textbox_dict[self.button_name] = (self.textbox.set_text,
                                               self.textbox.append_text,
                                               self.textbox.remove_text)

    def toggle_select(self):
        self.active = not self.active
        print(self.active)
        self.textbox.toggle_select()
        if self.active:
            self.dropdown_list()
        else:
            to_delete = []
            for child in self.block_list[f'{self.name}_dropdown'].children:
                to_delete.append(child[0])

            for item in to_delete:
                self.del_button(self.block_list, self.button_dict, self.text_dict, item)

            del self.block_list[f'{self.name}_dropdown']

    def create_text(self, name, parent, value, colour, size):
        super().create_text(self.block_list, self.text_dict, name, parent,
            value, colour, size)

    def generate_object(self):
        total_width, total_height = self.dimensions
        textbox_width = max(total_width - total_height, total_width // 2)
        button_width = total_width - textbox_width

        x_coord, y_coord = self.coordinates

        # TextBox portion
        textbox_name = f'{self.name}_text'
        textbox_dim = textbox_width, total_height
        textbox_coords = x_coord, y_coord
        self.textbox = TextBox(self.block_list, self.button_dict, self.text_dict, self.textbox_dict,
            textbox_name, self.parent, textbox_dim, textbox_coords)

        # Dropdown button portion
        button_name = f'{self.name}_button'
        button_dim = button_width, total_height
        button_coords = x_coord + textbox_width, y_coord
        button_text_info = ('', 'black', 20)
        self.create_button(self.block_list, self.button_dict,
            self.toggle_select, button_name, self.parent,
            button_dim, button_coords, 'tile_colour',
            button_text_info)
        self.button_name = button_name

        points = [(10, 15), (30, 15), (20, 30)]
        colour = (50, 50, 50)
        parent = button_name

        self.polygon_dict[f'{button_name}_arrow'] = colour, points, parent

    def dropdown_list(self):
        self.options_list = [
            'word1',
            'word2',
            'word3',
            'word4',
            'word5',
            'word6',
            'word7',
            'word8',
            'word9',
            'word10',
        ]

        x_coord, y_coord = self.coordinates
        total_width, total_height = self.dimensions
        item_width, item_height = max(total_width - total_height, total_width // 2), 2 * UNIT

        # Find distance to bottom of screen
        parent_tmp = self.parent
        y_coord_tmp = self.coordinates[1]
        while parent_tmp != 'window':
            y_coord_tmp += self.block_list[parent_tmp].coordinates[1]
            parent_tmp = self.block_list[parent_tmp].parent

        available_space = self.block_list[parent_tmp].surface.get_height() // BASE_UNIT - (y_coord_tmp + total_height)
        max_items = available_space // (item_height)

        dropdown_name = f'{self.name}_dropdown'
        dropdown_dimensions = total_width, max_items * item_height
        dropdown_coords = x_coord, y_coord + total_height
        self.create_block(self.block_list, dropdown_name, self.parent,
            dropdown_dimensions, dropdown_coords,
            'white', priority=99)

        item_dim = item_width, item_height
        for i, item in enumerate(self.options_list):
            item_coords = 0, i * total_height
            button_text_info = (item, 'black', 20)

            # print(item)
            def create_function():
                value_copy = item
                return lambda: self.textbox.set_text(value_copy)

            # set_text_func()
            set_text_func = create_function()
            self.create_button(self.block_list, self.button_dict,
                set_text_func, f'{dropdown_name}_li{i}', dropdown_name,
                item_dim, item_coords, 'white', button_text_info)

        scroll_func = lambda: 1
        scroll_bar_dimensions = total_width - item_width, max_items * item_height
        scroll_bar_coords = item_width, 0
        self.create_button(self.block_list, self.button_dict,
            scroll_func, f'{dropdown_name}_scrollbar', dropdown_name,
            scroll_bar_dimensions, scroll_bar_coords, 'title_colour')

        scrollhandle_func = lambda: 1
        scrollhandle_dimensions = total_width - item_width, min(item_height, max_items * item_height)
        scrollhandle_coords = item_width, 0
        self.create_button(self.block_list, self.button_dict,
            scrollhandle_func, f'{dropdown_name}_scrollhandle', dropdown_name,
            scrollhandle_dimensions, scrollhandle_coords, 'tile_colour', priority=99)


class myGUI(GUI_Element):

    def __init__(self, window_size, caption, win_colour):

        super().__init__()

        self.win_colour = win_colour

        pygame.display.set_caption(caption)
        self.window = pygame.display.set_mode(window_size)

        self.reset_block_list()

    def run_GUI(self):
        self.running = True
        pygame.init()

        self.draw_board()

        pygame.key.set_repeat(1000, 100)
        while self.running:
            pygame.time.delay(100)
            for event in pygame.event.get():
                # Keyboard Events
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.quit_gui()  # Allows user to overwrite quit process
                elif event.type == KEYDOWN and event.key == K_BACKSPACE:
                    self.textbox_dict[self.active_object][2]()
                elif event.type == KEYDOWN and (event.key in LETTERS or
                                                event.key in NUMBERS or
                                                event.key in PUNCTUATION):

                    character = pygame.key.name(event.key)
                    if (event.mod - KMOD_BASE == KMOD_LSHIFT or
                        event.mod - KMOD_BASE == KMOD_RSHIFT or
                        event.mod - KMOD_BASE == KMOD_SHIFT) and event.key in LETTERS:
                        character = character.upper()

                    if not self.active_object is None:
                        self.textbox_dict[self.active_object][1](character)

                elif event.type == KEYDOWN and event.key in WHITESPACE:
                    self.textbox_dict[self.active_object][1](WHITESPACE[event.key])

                if event.type == pygame.QUIT:
                    self.quit_gui()

                # Mouse Events
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        mouse_pos = event.pos  # gets mouse position

                        call_queue = []
                        # checks if mouse position is over the button
                        for name, info in self.button_dict.items():
                            button_rect, button_func = info

                            if button_rect.collidepoint(mouse_pos):
                                if not self.active_object is None:
                                    call_queue.append(self.button_dict[self.active_object][1])

                                self.active_object = name
                                # Calls relevant function
                                call_queue.append(button_func)


                            # Lose focus on object if clicked elsewhere
                            elif name == self.active_object:
                                self.active_object = None
                                call_queue.append(button_func)

                        for f in call_queue:
                            print(f.__name__)
                            f()

                    elif event.button == 4:  # Scroll up
                        pass
                    elif event.button == 5:  # Scroll down
                        pass

            self.draw_board()

        pygame.quit()

    def quit_gui(self):
        self.running = False

    # -------------------------- Object Creation ----------------------------

    def create_button(self, function, name, parent, dimensions, coordinates, colour,
                      text_info=None):
        return super().create_button(self.block_list, self.button_dict, function,
            name, parent, dimensions, coordinates,
            colour, text_info)

    def create_block(self, name, parent, dimensions, coordinates, colour):
        return super().create_block(self.block_list, name, parent, dimensions,
            coordinates, colour)

    def create_text(self, name, parent, value, colour, size):
        return super().create_text(self.block_list, self.text_dict, name, parent,
            value, colour, size)

    def create_textbox(self, name, parent, dimensions, coordinates, default_text=''):
        textbox = TextBox(self.block_list, self.button_dict, self.text_dict, self.textbox_dict,
            name, parent, dimensions, coordinates, default_text)

    def create_dropdown(self, name, parent, dimensions, coordinates, default_text=''):
        dropdown = Dropdown(self.block_list, self.button_dict, self.text_dict,
            self.polygon_dict, self.textbox_dict, name, parent, dimensions,
            coordinates, default_text)

    # -------------------------- GUI Drawing ----------------------------

    def reset_block_list(self):

        self.block_list = MyList('window', self.window)
        self.text_dict = {}
        self.button_dict = {}
        self.polygon_dict = {}
        self.textbox_dict = {}
        self.dropdown_dict = {}

    def blit_text(self):
        for name, text_object in self.text_dict.items():
            text, position, parent = text_object
            self.block_list[parent].surface.blit(text, position)

    def draw_polygons(self):
        for name, polygon_info in self.polygon_dict.items():
            colour, points, parent = polygon_info
            parent_surface = self.block_list[parent].surface
            pygame.draw.polygon(parent_surface, colour, points)

    def draw_board(self):
        self.window.fill(self.colours[self.win_colour])

        def draw_recurse(block_iter):
            try:
                block_name, block_info = next(block_iter)
            except StopIteration:
                self.blit_text()
                self.draw_polygons()
                return True

            self.create_surface(block_info)

            draw_recurse(block_iter)

            parent_surface = self.block_list[block_info.parent].surface
            block_pos = [int(coord * BASE_UNIT) for coord in block_info.coordinates]
            parent_surface.blit(block_info.surface, block_pos)

        block_iter = iter(self.block_list)
        draw_recurse(block_iter)

        pygame.display.flip()


if __name__ == '__main__':
    # Create test GUI

    caption = "Test GUI"
    window_size = win_width, win_height = (int(BASE_UNIT * UNIT * 35 - BASE_UNIT),
                                           int(BASE_UNIT * UNIT * 20))
    fill_colour = 'bg_colour'

    gui = myGUI(window_size, caption, fill_colour)

    # Add GUI elements
    gui.create_button(gui.quit_gui, 'quit_button', 'window', (5 * UNIT, 2 * UNIT),
        (3 * UNIT, 1 * UNIT), 'white', ('QUIT', 'black', 20))

    gui.create_textbox('textbox_1', 'window', (8 * UNIT, 2 * UNIT),
        (3 * UNIT, 4 * UNIT))

    gui.create_dropdown('dropdown', 'window', (8 * UNIT, 2 * UNIT),
        (3 * UNIT, 7 * UNIT))

    gui.create_textbox('textbox_2', 'window', (8 * UNIT, 2 * UNIT),
        (3 * UNIT, 10 * UNIT))

    gui.run_GUI()

