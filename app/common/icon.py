# coding: utf-8
from enum import Enum

from qfluentwidgets import FluentIconBase, Theme, getIconColor


class Icon(FluentIconBase, Enum):

    GRID = "Grid"
    MENU = "Menu"
    TEXT = "Text"
    PRICE = "Price"
    EMOJI_TAB_SYMBOLS = "EmojiTabSymbols"
    OPEN_WITH = "OpenWith"
    CODE = "Code"
    JS = "JS"
    PACKAGE = "Package"
    PYTHON = "Python"
    PLUG_DISCONNECTED = "PlugDisconnected"
    REGISTRY_EDITOR = "RegistryEditor"

    def path(self, theme=Theme.AUTO):
        return f":/gallery/images/icons/{self.value}_{getIconColor(theme)}.svg"
