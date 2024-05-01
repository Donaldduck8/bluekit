# coding:utf-8
from PyQt5.QtWidgets import QTreeWidgetItem

from ..data import MiscFiles
from .base_tree_frame import BaseTreeFrame
from .base_tree_json_interface import BaseTreeAndJsonEditWidget


class MiscFilesTreeFrame(BaseTreeFrame):
    data: MiscFiles

    def __init__(self, parent=None, data: MiscFiles = None):
        headers = ["Name", "Location"]
        super().__init__(parent, headers, data)
        self.update_data(data)

    def populate_tree(self):
        for category, value in self.data.files.items():
            category_item = QTreeWidgetItem([category])
            self.tree.addTopLevelItem(category_item)

            for file in value:
                for source in file.sources:
                    entry_item = QTreeWidgetItem([source.split("/")[-1], file.target])
                    category_item.addChild(entry_item)

        self.tree.expandAll()


class MiscFilesTreeWidget(BaseTreeAndJsonEditWidget):
    def create_custom_view(self, parent, data):
        return MiscFilesTreeFrame(parent, data)
