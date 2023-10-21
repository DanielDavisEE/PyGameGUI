from pygame_gui.components.button_block import Button


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
