import unittest

from pygame_gui.gui_components import (Block, Button, Dropdown, MyGUI, RootBlock, Slider, Text, TextBox)


class TestRootBlock(unittest.TestCase):
    def setUp(self) -> None:
        self.block = RootBlock()


class TestBlock(unittest.TestCase):
    def setUp(self) -> None:
        self.block = Block()


class TestText(unittest.TestCase):
    def setUp(self) -> None:
        self.block = Text()


class TestButton(unittest.TestCase):
    def setUp(self) -> None:
        self.block = Button()


class TestTextBox(unittest.TestCase):
    def setUp(self) -> None:
        self.block = TextBox()


class TestSlider(unittest.TestCase):
    def setUp(self) -> None:
        self.block = Slider()


class TestDropdown(unittest.TestCase):
    def setUp(self) -> None:
        self.block = Dropdown()


class TestMyGUI(unittest.TestCase):
    def setUp(self) -> None:
        self.block = MyGUI()
