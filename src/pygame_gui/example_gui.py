from pygame_gui.gui_base import GUIBase
import pygame_gui.components as gui
from pygame_gui.components import MouseEvents


class ExampleGUI(GUIBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add GUI elements
        gui.Block(
            self.window,
            dimensions=(100, 40),
            coordinates=(60, 20),
            colour='white')

        gui.Text(
            self.window,
            dimensions=(100, 40),
            coordinates=(60, 80),
            colour='white',
            text_value='Test')

        button1 = gui.Button(
            self.window,
            dimensions=(100, 40),
            coordinates=(60, 140),
            colour='white',
            text_value='QUIT')

        func_dict = {
            MouseEvents.LEFT_MOUSE_UP: lambda event: self.quit_gui() if button1.check_collision(event) and button1.held else None,
            MouseEvents.MIDDLE_MOUSE_UP: lambda event: print(1)
        }
        button1.set_mouse_handlers(func_dict)

        gui.TextBox(
            self.window,
            dimensions=(160, 40),
            coordinates=(60, 200))

        # gui.Dropdown(self.window,
        #     dimensions=(16, 4),
        #     coordinates=(18, 2))


if __name__ == '__main__':
    gui_inst = ExampleGUI(
        dimensions=(700, 400),
        caption="Example GUI",
        bg_colour='bg_colour'
    )
    gui_inst.run()
