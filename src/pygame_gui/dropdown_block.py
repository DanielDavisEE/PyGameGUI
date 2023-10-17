from pygame_gui import (Block, Button, MARGIN, Slider, TextBox)


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
