from pygame_gui.gui_base import GUIBase
import pygame_gui.components as gui


class ExampleGUI(GUIBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add GUI elements
        block_info = {
            'dimensions': (10, 4),
            'coordinates': (6, 2),
            'colour': 'white'
        }

        gui.Block(self.window, **block_info)

        gui.Text(self.window, (10, 4), (6, 8), 'white', 'Test')

        button1 = gui.Button(self.window, (10, 4), (6, 14), 'white', 'QUIT')

        func_dict = {
            'left_mouse_up': lambda event: self.quit_gui() if button1.check_collision(event) and button1.held else None,
            'middle_mouse_up': lambda event: print(1)
        }
        button1.set_mouse_handlers(func_dict)

        gui.TextBox(self.window, (16, 4), (6, 20))

        gui.Dropdown(self.window, (16, 4), (18, 2))


if __name__ == '__main__':
    gui_inst = ExampleGUI(
        dimensions=(70, 40),
        caption="Example GUI",
        bg_colour='bg_colour'
    )
    gui_inst.run()
