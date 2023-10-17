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

import pygame_gui.components as gui


class GUIBase:
    refresh_rate = 50

    def __init__(self,
                 dimensions: tuple[int, int] | None,
                 bg_colour: str | tuple[int, int, int] = 'white',
                 caption: str = '',
                 **kwargs):
        """window_size, caption, win_colour, colour_palette=None -> myGUI
        """
        self.window = gui.Window(
            dimensions=dimensions,
            caption=caption,
            colour=bg_colour,
            **kwargs
        )

        self.running = False
        pygame.key.set_repeat(500, 50)

        self._keyboard_event_handlers = {}
        self.add_keyboard_event_handler(key=pygame.K_ESCAPE, callable=self.quit_gui)

    def run(self):
        self.running = True
        pygame.init()

        self.window.draw_block()
        pygame.display.flip()

        while self.running:
            pygame.time.delay(int(1000 / self.refresh_rate))

            self.window.clock()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_gui()

                # Keyboard Events
                if event.type in {pygame.KEYDOWN,
                                  pygame.KEYUP}:
                    self.run_keyboard_event_handlers(event)
                    self.window.keyboard_event_handler(event)

                # Mouse Events
                if event.type in {pygame.MOUSEBUTTONDOWN,
                                  pygame.MOUSEBUTTONUP,
                                  pygame.MOUSEMOTION}:
                    self.window.mouse_event_handler(event)

            self.window.draw_block()
            pygame.display.flip()

        pygame.quit()

    def quit_gui(self):
        self.running = False

    def reset_gui(self):
        for child in list(self.window.children):
            child.__delitem__()

    def save(self):
        pass

    def add_keyboard_event_handler(self, *, mod=None, key=None, type=None, callable):
        self._keyboard_event_handlers[(mod, key, type)] = callable

    def run_keyboard_event_handlers(self, event):
        for (mod, key, type), callable in self._keyboard_event_handlers:

            mod_match = (mod is None) or (event.mod == mod)
            key_match = (key is None) or (event.key == key)
            type_match = (type is None) or (event.type == type)

            if mod_match and key_match and type_match:
                callable()
