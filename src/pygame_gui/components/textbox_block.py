import pygame
import pyperclip

from pygame_gui.components.constants import KMOD_BASE
from pygame_gui.components.button_block import Button


class TextBox(Button):

    def __init__(self, parent, **kwargs):

        self.active = False
        self.tb_colours = {
            True: 'white',
            False: 'offwhite'
        }

        self.cursor_info = {
            'on': False,
            'text': None,
            'pos': None
        }
        self.second_text = {
            'value': '',
            'text': None,
            'pos': None
        }

        kwargs['colour'] = self.tb_colours[self.active]
        kwargs['text_alignment'] = 'left'

        super().__init__(parent, **kwargs)

        self.set_mouse_handlers({'left_mouse_down': self.toggle_select})

        self.cursor_info['colour'] = self.colour

    def update_cursor(self):

        text_rect = self.primary_text['pos']

        cursor_colour = self.font_colour if self.cursor_info['on'] else self.colour

        self.cursor_info['text'] = self.font.render('|', 1, cursor_colour)
        self.cursor_info['pos'] = self.cursor_info['text'].get_rect(
            left=text_rect.right,
            centery=text_rect.centery)

    def toggle_select(self, event):
        isCollision = self.check_collision(event)
        if isCollision:
            self.active = True
            self.gui.active_object = self
        if not isCollision:
            self.active = False
            self.cursor_info['on'] = False
            if self.gui.active_object == self:
                self.move_cursor(len(self.second_text['value']))
                self.gui.active_object = None

        self.colour = self.colour_palette[self.tb_colours[self.active]]

    def move_cursor(self, amount):
        if amount < 0 and len(self.primary_text['value']) > 0:
            self.second_text['value'] = self.primary_text['value'][amount] + self.second_text['value']
            self.remove_text(amount)
        elif amount > 0 and len(self.second_text['value']) > 0:
            self.append_text(self.second_text['value'][:amount])
            self.second_text['value'] = self.second_text['value'][amount:]

    def update_text(self):
        super().update_text()

        if self.active:

            if self.primary_text['pos'].width + self.cursor_info['pos'].width > (self.dimensions[0] - 2 * self._MARGIN):
                self.primary_text['pos'] = (self.primary_text['text'].get_rect(
                    right=(self.dimensions[0] - self._MARGIN) - self.cursor_info['pos'].width,
                    centery=self.primary_text['pos'].centery))

            second_text_left = self.cursor_info['pos'].right

        else:
            second_text_left = self.primary_text['pos'].right

        self.update_cursor()

        self.second_text['text'] = self.font.render(self.second_text['value'], 1, self.font_colour)
        self.second_text['pos'] = self.second_text['text'].get_rect(
            left=second_text_left,
            centery=self.primary_text['pos'].centery)

    def toggle_cursor(self):
        self.cursor_info['on'] = not self.cursor_info['on']

    def set_text(self, text):
        super().set_text(text)
        self.second_text['value'] = ''

    def get_text(self):
        return self.primary_text['value'] + self.second_text['value']

    def append_text(self, text):
        super().append_text(text)

    def remove_text(self, amount=-1):
        super().remove_text(amount)

    def keyboard_event_handler(self, event):
        if (event.mod - KMOD_BASE) in {pygame.KMOD_LCTRL, pygame.KMOD_RCTRL, pygame.KMOD_CTRL}:
            character = pygame.key.name(event.key)
            if character == 'x':
                pyperclip.copy(self.primary_text['value'] + self.second_text['value'])
                self.second_text['value'] = ''
                self.set_text('')
            elif character == 'c':
                pyperclip.copy(self.primary_text['value'] + self.second_text['value'])
            elif character == 'v':
                text = pyperclip.paste()
                self.second_text['value'] = ''
                self.set_text(text)

            elif character in ['a', 's', 'z', 'y', 'x', 'c', 'v']:
                print('Get to this...')
        elif event.key == pygame.K_RETURN:
            pass
        elif event.key == pygame.K_BACKSPACE:
            self.remove_text()
        elif event.key == pygame.K_DELETE:
            self.second_text['value'] = self.second_text['value'][1:]
        elif event.key == pygame.K_LEFT:
            self.move_cursor(-1)
        elif event.key == pygame.K_RIGHT:
            self.move_cursor(1)
        else:
            self.append_text(event.unicode)

        self.update_text()

    def blit_text(self):
        super().blit_text()
        self.surface.blit(self.cursor_info['text'], self.cursor_info['pos'])
        self.surface.blit(self.second_text['text'], self.second_text['pos'])
