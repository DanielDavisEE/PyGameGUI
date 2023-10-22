import time

import pygame
import pyperclip

from pygame_gui.components.constants import KMOD_BASE, MARGIN, Alignment, MouseEvents
from pygame_gui.components.button_block import Button


class TextBox(Button):
    tb_colours = {
        True: 'white',
        False: 'offwhite'
    }
    cursor_tick_time = 1  # s

    CTRL = {pygame.KMOD_CTRL}
    SHIFT = {pygame.KMOD_SHIFT}
    ALT = {pygame.KMOD_ALT}

    CTRL_SHIFT = {pygame.KMOD_CTRL, pygame.KMOD_SHIFT}
    CTRL_ALT = {pygame.KMOD_CTRL, pygame.KMOD_ALT}
    SHIFT_ALT = {pygame.KMOD_SHIFT, pygame.KMOD_ALT}

    CTRL_SHIFT_ALT = {pygame.KMOD_CTRL, pygame.KMOD_SHIFT, pygame.KMOD_ALT}

    def __init__(self, parent, *,
                 active=False,
                 **kwargs):
        super().__init__(
            parent,
            colour=self.tb_colours[active],
            text_alignment=Alignment.LEFT,
            **kwargs)

        self.active = active
        self.last_tick_time = time.time()

        self.cursor_info = {
            'on': False,
            # 'surface': Surface,
            # 'rect': tuple[int, int]
        }
        self.secondary_text = {
            'value': '',
            # 'surface': Surface,
            # 'rect': tuple[int, int]
        }
        self.set_mouse_handlers({MouseEvents.LEFT_MOUSE_DOWN: self.check_for_select})

    def update_cursor(self):

        text_rect = self.primary_text['rect']

        cursor_colour = self.font_colour if self.cursor_info['on'] else self.colour

        self.cursor_info['surface'] = self.font.render('|', 1, cursor_colour)
        self.cursor_info['rect'] = self.cursor_info['surface'].get_rect(
            left=text_rect.right,
            centery=text_rect.centery)

    def check_for_select(self, event):
        if self.check_collision(event):
            self.active = True
        else:
            self.cursor_info['on'] = False
            if self.active:
                self.move_cursor(len(self.secondary_text['value']))
            self.active = False

        self.colour = self.colour_palette[self.tb_colours[self.active]]

    def move_cursor(self, amount: int):
        if amount < 0:  # Left
            if not len(self.primary_text['value']):
                return

            self.secondary_text['value'] = self.primary_text['value'][amount:] + self.secondary_text['value']
            self.primary_text['value'] = self.primary_text['value'][:amount]

        elif amount > 0:  # Right
            if not len(self.secondary_text['value']):
                return

            self.primary_text['value'] = self.primary_text['value'] + self.secondary_text['value'][:amount]
            self.secondary_text['value'] = self.secondary_text['value'][amount:]

    def update_text(self):
        super().update_text()

        if self.active:

            if self.primary_text['rect'].width + self.cursor_info['rect'].width > (self.dimensions[0] - 2 * MARGIN):
                self.primary_text['rect'] = (self.primary_text['surface'].get_rect(
                    right=(self.dimensions[0] - MARGIN) - self.cursor_info['rect'].width,
                    centery=self.primary_text['rect'].centery))

            second_text_left = self.cursor_info['rect'].right

            current_time = time.time()
            if self.last_tick_time + self.cursor_tick_time < current_time:
                self.toggle_cursor()
                self.last_tick_time = current_time

        else:
            second_text_left = self.primary_text['rect'].right

        self.update_cursor()

        self.secondary_text['surface'] = self.font.render(self.secondary_text['value'], 1, self.font_colour)
        self.secondary_text['rect'] = self.secondary_text['surface'].get_rect(
            left=second_text_left,
            centery=self.primary_text['rect'].centery)

    def toggle_cursor(self):
        self.cursor_info['on'] = not self.cursor_info['on']

    def set_text(self, text):
        super().set_text(text)
        self.secondary_text['value'] = ''

    def get_text(self):
        return self.primary_text['value'] + self.secondary_text['value']

    def _is_modified_by(self, event, modifiers: set):
        for modifier in modifiers:
            if not event.mod & modifier:
                return False
        for modifier in (self.CTRL_SHIFT_ALT - modifiers):
            if event.mod & modifier:
                return False
        return True

    def _handle_modified_commands(self, event):
        if self._is_modified_by(event, self.CTRL):
            character = pygame.key.name(event.key)
            if character == 'x':
                pyperclip.copy(self.primary_text['value'] + self.secondary_text['value'])
                self.primary_text['value'] = ''
                self.secondary_text['value'] = ''
            elif character == 'c':
                pyperclip.copy(self.primary_text['value'] + self.secondary_text['value'])
            elif character == 'v':
                text = pyperclip.paste()
                self.primary_text['value'] = text
                self.secondary_text['value'] = ''

            elif event.key == pygame.K_BACKSPACE:
                self.primary_text['value'] = ''
            elif event.key == pygame.K_DELETE:
                self.secondary_text['value'] = ''
            elif event.key == pygame.K_LEFT:
                self.move_cursor(-len(self.primary_text['value']))
            elif event.key == pygame.K_RIGHT:
                self.move_cursor(len(self.secondary_text['value']))

            elif character in {'a', 's', 'z', 'y'}:
                self.log.debug(f'Get to this... (ctrl {character})')
        elif self._is_modified_by(event, self.SHIFT):
            pass

    def keyboard_event_handler(self, event):
        super().keyboard_event_handler(event)

        if self.active and event.type == pygame.KEYDOWN:
            self.log.debug(f"({event.key=}, {event.type=}, {event.mod=}) received by {self}")

            if event.mod:
                self._handle_modified_commands(event)

            elif event.key == pygame.K_RETURN:
                pass
            elif event.key == pygame.K_BACKSPACE:
                self.pop_text()
            elif event.key == pygame.K_DELETE:
                self.secondary_text['value'] = self.secondary_text['value'][1:]
            elif event.key == pygame.K_LEFT:
                self.move_cursor(-1)
            elif event.key == pygame.K_RIGHT:
                self.move_cursor(1)
            else:
                self.append_text(event.unicode)

            self.update_text()

    def blit_text(self):
        super().blit_text()
        self.surface.blit(self.cursor_info['surface'], self.cursor_info['rect'])
        self.surface.blit(self.secondary_text['surface'], self.secondary_text['rect'])
