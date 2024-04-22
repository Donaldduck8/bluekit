import PyQt5.QtWidgets
from qfluentwidgets import TreeWidget

from .base_frame import BaseFrame


class BaseTreeFrame(BaseFrame):
    def __init__(self, parent=None, headers=None, data=None):
        if not headers:
            headers = []

        super().__init__(parent)
        self.data = data
        self.tree = TreeWidget(self)
        self.tree.setColumnCount(len(headers))
        self.tree.setHeaderLabels(headers)
        self.addWidget(self.tree)
        self.tree.header().setSectionResizeMode(0, PyQt5.QtWidgets.QHeaderView.ResizeToContents)
        self.setContentsMargins(50, 30, 50, 30)
        self.tree.setBorderVisible(True)
        self.tree.setBorderRadius(8)
        self.setMinimumWidth(800)

        # Set background color
        tree_style_sheet = self.tree.styleSheet()
        tree_style_sheet = tree_style_sheet.replace("background-color: transparent;", "background-color: rgb(251, 251, 252);")
        self.tree.setStyleSheet(tree_style_sheet)

    def update_data(self, data: dict):
        self.tree.clear()  # Clear the existing items
        self.data = data
        self.populate_tree()

    def populate_tree(self):
        raise NotImplementedError("populate_tree method must be implemented in the subclass")
