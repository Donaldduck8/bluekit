# coding:utf-8
from PyQt5.QtWidgets import QTreeWidgetItem

from .base_tree_frame import BaseTreeFrame
from .base_tree_json_interface import BaseTreeAndJsonEditWidget


class RegistryChangesTreeFrame(BaseTreeFrame):
    def __init__(self, parent=None, data: dict = None):
        headers = ["Name", "Description"]
        super().__init__(parent, headers, data)
        self.update_data(data)

    def populate_tree(self):
        for category, items in self.data.items():
            category_item = QTreeWidgetItem([category])
            self.tree.addTopLevelItem(category_item)
            self.populate_tree_item(category_item, items)

        self.tree.expandAll()

    def populate_tree_item(self, parent_item, items):
        for item in items:
            details = [
                item.get('value', ''),
                item.get('description', '')
            ]
            child_item = QTreeWidgetItem(details)
            parent_item.addChild(child_item)


class RegistryChangesWidget(BaseTreeAndJsonEditWidget):
    def create_custom_view(self, parent, data):
        return RegistryChangesTreeFrame(parent, data)
