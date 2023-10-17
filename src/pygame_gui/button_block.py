import pygame
import pygame.locals as py_locals

from pygame_gui import Text


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
