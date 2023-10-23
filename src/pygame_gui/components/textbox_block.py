import time

import pygame
import pyperclip

from pygame_gui.components.constants import KMOD_BASE, MARGIN, Alignment, KeyboardModifiers, MouseEvents
from pygame_gui.components.button_block import Button


class TextBox(Button):
    tb_colours = {
        True: 'white',
        False: 'offwhite'
    }
    cursor_tick_time = 1  # s

    def __init__(self, parent, *,
                 text_value='',
                 active=False,
                 **kwargs):
        super().__init__(
            parent,
            colour=self.tb_colours[active],
            text_value=text_value,
            text_alignment=Alignment.LEFT,
            **kwargs)

        self.active = active
        self.last_tick_time = time.time()
        self.shift_held = False

        self.cursor_info = {
            'on': False,
            'location': len(text_value),
            # 'surface': Surface,
            # 'rect': tuple[int, int]
        }
        self.set_mouse_handlers({MouseEvents.LEFT_MOUSE_DOWN: self.check_for_select})

    def check_for_select(self, event):
        if self.check_collision(event):
            self.active = True
        else:
            self.cursor_info['on'] = False
            if self.active:
                self.move_cursor(end=True)
            self.active = False

        self.colour = self.colour_palette[self.tb_colours[self.active]]

    def update_cursor(self):

        cursor_colour = self.font_colour if self.cursor_info['on'] else self.colour
        self.cursor_info['surface'] = self.font.render('|', True, cursor_colour)

        if self.text_alignment == Alignment.LEFT:
            # TODO: Get better letter width
            self.cursor_info['rect'] = (self.cursor_info['surface'].get_rect(
                left=self.cursor_info['location'] * 7 + MARGIN,
                centery=self.text_info['rect'].centery))
        elif self.text_alignment == Alignment.CENTRE:
            self.cursor_info['rect'] = (self.cursor_info['surface'].get_rect(
                left=MARGIN,
                centery=self.text_info['rect'].centery))
        elif self.text_alignment == Alignment.RIGHT:
            self.cursor_info['rect'] = (self.cursor_info['surface'].get_rect(
                right=MARGIN,
                centery=self.text_info['rect'].centery))

    def toggle_cursor(self):
        self.cursor_info['on'] = not self.cursor_info['on']

    def move_cursor(self, amount: int = None, *, start=False, end=False):
        if amount:
            new_location = self.cursor_info['location'] + amount
        elif start:
            new_location = 0
        elif end:
            new_location = len(self.text_info['value'])
        else:
            raise ValueError

        new_location = max(
            new_location,
            0)
        new_location = min(
            new_location,
            len(self.text_info['value']))

        self.cursor_info['location'] = new_location

    def update_text(self):
        super().update_text()

        if self.active:
            # Force right align if text is wider than text box
            if self.text_info['rect'].width + self.cursor_info['rect'].width > (self.dimensions[0] - 2 * MARGIN):
                self.text_info['rect'] = (self.text_info['surface'].get_rect(
                    right=(self.dimensions[0] - MARGIN) - self.cursor_info['rect'].width,
                    centery=self.text_info['rect'].centery))

            # Toggle cursor if cursor_tick_time has elapsed
            current_time = time.time()
            if self.last_tick_time + self.cursor_tick_time < current_time:
                self.toggle_cursor()
                self.last_tick_time = current_time

        self.update_cursor()

    def set_text(self, text: str):
        super().set_text(text)
        self.cursor_info['location'] = len(text)

    def _is_modified_by(self, event, modifiers: KeyboardModifiers):
        for modifier in modifiers:
            if not event.mod & modifier:
                return False

        # ctrl, shift and alt combine uniquely
        # for modifier in (self.CTRL_SHIFT_ALT - modifiers):
        #     if event.mod & modifier:
        #         return False

        return True

    def _handle_ctrl_modified_commands(self, event):
        character = pygame.key.name(event.key)
        if character == 'x':
            pyperclip.copy(self.text_info['value'])
            self.text_info['value'] = ''
        elif character == 'c':
            pyperclip.copy(self.text_info['value'])
        elif character == 'v':
            text = pyperclip.paste()
            self.text_info['value'] = text

        elif event.key == pygame.K_BACKSPACE:
            self.text_info['value'] = ''
        elif event.key == pygame.K_DELETE:
            pass
        elif event.key == pygame.K_LEFT:
            self.move_cursor(start=True)
        elif event.key == pygame.K_RIGHT:
            self.move_cursor(end=True)

        elif character in {'a', 's', 'z', 'y'}:
            self.log.debug(f'Get to this... (ctrl {character})')

    def insert_text(self, text: str):
        i = self.cursor_info['location']
        self.text_info['value'] = self.text_info['value'][:i] + text + self.text_info['value'][i:]
        self.cursor_info['location'] += len(text)

    def remove_text(self, length=1):
        pass

    def _handle_delete_input(self, unicode_val):
        i = self.cursor_info['location']
        if unicode_val == '\x08':  # Backspace
            if i == 0:
                return
            self.text_info['value'] = self.text_info['value'][:i - 1] + self.text_info['value'][i:]
            self.cursor_info['location'] -= 1

        elif unicode_val == '\x7f':  # Delete
            if i == len(self.text_info['value']):
                return
            self.text_info['value'] = self.text_info['value'][:i] + self.text_info['value'][i + 1:]

    def keyboard_event_handler(self, event):
        super().keyboard_event_handler(event)

        movement_keys = {
            pygame.K_HOME: lambda *_: self.move_cursor(start=True),
            pygame.K_END: lambda *_: self.move_cursor(end=True),
            pygame.K_LEFT: lambda *_: self.move_cursor(-1),
            pygame.K_RIGHT: lambda *_: self.move_cursor(1),
            pygame.K_UP: lambda *_: self.move_cursor(start=True),
            pygame.K_DOWN: lambda *_: self.move_cursor(end=True),
        }

        unique_unicode_actions = {
            '\r': lambda *_: None,
            '\x08': lambda *_: self._handle_delete_input('\x08'),
            '\x7f': lambda *_: self._handle_delete_input('\x7f'),
        }

        # for mod in sorted(modifiers, key=lambda m: constants.__dict__[m]):
        #     print(f'{mod}\t{constants.__dict__[mod]: >5}\t{constants.__dict__[mod]:0>15b}')

        if self.active:
            self.cursor_info['on'] = True
            self.last_tick_time = time.time()

            if event.type == pygame.KEYUP:
                if KeyboardModifiers(event.key) in KeyboardModifiers.SHIFT:
                    self.shift_held = False

            if event.type == pygame.KEYDOWN:
                self.log.debug(f"({event.key=}, {event.type=}, {event.mod=}, {event.unicode=}) received by {self}")

                if self._is_modified_by(event, KeyboardModifiers.CTRL):
                    # self._handle_ctrl_modified_commands(event)
                    pass

                if event.unicode:
                    if event.unicode in unique_unicode_actions:
                        unique_unicode_actions[event.unicode]()
                    else:
                        self.insert_text(event.unicode)

                elif event.key in movement_keys:
                    movement_keys[event.key]()

                if KeyboardModifiers(event.key) in KeyboardModifiers.SHIFT:
                    self.shift_held = True

                self.update_text()

    def blit_text(self):
        super().blit_text()
        self.surface.blit(self.cursor_info['surface'], self.cursor_info['rect'])
