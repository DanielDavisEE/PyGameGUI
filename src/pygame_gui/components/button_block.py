import pygame
from pygame import K_RETURN

from pygame_gui.components.constants import MouseEvents
from pygame_gui.components.text_block import Text


class Button(Text):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.held = False
        self.event_function_dict = {
            MouseEvents.LEFT_MOUSE_UP: lambda *_: None,
            MouseEvents.MIDDLE_MOUSE_UP: lambda *_: None,
            MouseEvents.RIGHT_MOUSE_UP: lambda *_: None,
            MouseEvents.SCROLL_MOUSE_UP: lambda *_: None,

            MouseEvents.LEFT_MOUSE_DOWN: lambda *_: None,
            MouseEvents.MIDDLE_MOUSE_DOWN: lambda *_: None,
            MouseEvents.RIGHT_MOUSE_DOWN: lambda *_: None,
            MouseEvents.SCROLL_MOUSE_DOWN: lambda *_: None,

            MouseEvents.MOVE_MOUSE: lambda *_: None,
        }

        def _hold_down(event):
            if self.check_collision(event):
                self.log.debug(f'Holding {self}')
                self.held = True

        def _release(event):
            if self.held:
                self.log.debug(f'Releasing {self}')
                self.held = False

        self.default_mouse_handlers = {MouseEvents.LEFT_MOUSE_DOWN: _hold_down,
                                       MouseEvents.LEFT_MOUSE_UP: _release}
        self.set_mouse_handlers(self.event_function_dict)

    def _create_surface(self):
        super()._create_surface()

        # Coordinates need to be reference from window, not parent surface
        this_parent = self.parent
        self.overall_coords = list(self.coordinates)
        while hasattr(this_parent, 'parent'):
            self.overall_coords[0] += this_parent.parent.coordinates[0]
            self.overall_coords[1] += this_parent.parent.coordinates[1]
            this_parent = this_parent.parent

        self.create_rect()

    def create_rect(self):
        # Create rect object for simplicity of collision detection
        self.button_rect = pygame.Rect(self.overall_coords, self.dimensions)

    def set_mouse_handlers(self, function_dict):
        for func_name, func in function_dict.items():
            def modify_default(default_func, new_func):
                def inner(*arg):
                    new_func(*arg)
                    default_func(*arg)

                return inner

            self.event_function_dict[func_name] = modify_default(self.default_mouse_handlers.get(func_name, lambda *_: None), func)

    def _scroll_event_to_distance(self, event):
        scroll = event.button
        scroll -= 3
        if scroll % 2 == 1:
            scroll += 1
            scroll *= -1
        scroll //= 2
        return scroll

    def mouse_event_handler(self, event):
        super().mouse_event_handler(event)

        event_id = [event.type]
        if hasattr(event, 'button'):
            event_id.append(event.button)

        try:
            mouse_event = MouseEvents(tuple(event_id))
        except ValueError:
            self.log.error(f'Unknown MouseEvent: {tuple(event_id)}')
        else:
            f = self.event_function_dict.get(mouse_event, None)
            if f:
                f(event)

    def check_collision(self, event):
        collided = self.button_rect.collidepoint(event.pos)
        if collided:
            self.log.debug(f"Collision detected with {self}")
        return collided

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
