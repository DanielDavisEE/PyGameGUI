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
import pygame
import pygame.locals as py_locals

from pygame_gui.base_blocks import RootBlock


class GUIBase:
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
