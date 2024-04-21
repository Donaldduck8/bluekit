# coding:utf-8
from PyQt5.QtWidgets import (QTreeWidgetItem)

from .base_tree_frame import BaseTreeFrame
from .base_tree_json_interface import BaseTreeAndJsonEditWidget


class MiscFilesTreeFrame(BaseTreeFrame):
    def __init__(self, parent=None, data: dict = None):
        headers = ["Name", "Description"]
        super().__init__(parent, headers, data)
        self.update_data(data)

    def update_data(self, data: dict):
        self.tree.clear()  # Clear the existing items
        self.data = data
        self.populate_tree()

    def populate_tree(self):
        if isinstance(self.data, dict):
            for category, configs in self.data.items():
                category_item = QTreeWidgetItem([category])  # Create a category item
                self.populate_tree_item(category_item, configs)  # Populate this category with its configs
                self.tree.addTopLevelItem(category_item)  # Add category to tree
        self.tree.expandAll()

    def populate_tree_item(self, parent_item, items):
        for item in items:
            if isinstance(item, dict):
                # Use the description as the main label and target as a sublabel or tooltip
                config_item = QTreeWidgetItem([item['description'], item['target']])
                parent_item.addChild(config_item)  # Add the config item under the category

                # Optionally add each source as a child node of the config item
                for source in item['sources']:
                    file_name = source.split('/')[-1]
                    source_item = QTreeWidgetItem([file_name])
                    config_item.addChild(source_item)
        self.tree.expandAll()


class MiscFilesTreeWidget(BaseTreeAndJsonEditWidget):
    def create_custom_view(self, parent, data):
        return MiscFilesTreeFrame(parent, data)
