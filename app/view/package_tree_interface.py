# coding:utf-8
from PyQt5.QtWidgets import QTreeWidgetItem

from .base_tree_frame import BaseTreeFrame
from .base_tree_json_interface import BaseTreeAndJsonEditWidget


class PackageTreeFrame(BaseTreeFrame):
    def __init__(self, parent=None, data: dict = None):
        headers = ["Name", "Description"]
        super().__init__(parent, headers, data)
        self.update_data(data)

    def populate_tree(self):
        if isinstance(self.data, dict):
            for category, items in self.data.items():
                item = QTreeWidgetItem([category])
                for sub_item in items:
                    if isinstance(sub_item, list):
                        if len(sub_item) != 3:
                            continue
                        item.addChild(QTreeWidgetItem([sub_item[1], sub_item[2]]))

                    elif isinstance(sub_item, (dict, tuple)):
                        if sub_item.get("type") == "one_of":
                            main_item = QTreeWidgetItem([sub_item["main"][1], sub_item["main"][2]])
                            alt_item = QTreeWidgetItem([sub_item["alternative"][1], sub_item["alternative"][2]])
                            item.addChild(main_item)
                            main_item.addChild(alt_item)

                self.tree.addTopLevelItem(item)
        elif isinstance(self.data, list):
            for item in self.data:
                self.tree.addTopLevelItem(QTreeWidgetItem([item[1], item[2]]))

        self.tree.expandAll()

    def populate_tree_item(self, parent_item, items):
        for sub_item in items:
            if isinstance(sub_item, tuple) and len(sub_item) == 3:
                parent_item.addChild(QTreeWidgetItem([sub_item[1], sub_item[2]]))
            elif isinstance(sub_item, dict) and sub_item.get("type") == "one_of":
                main_item = QTreeWidgetItem([sub_item["main"][1], sub_item["main"][2]])
                alt_item = QTreeWidgetItem([sub_item["alternative"][1], sub_item["alternative"][2]])
                parent_item.addChild(main_item)
                main_item.addChild(alt_item)
        self.tree.expandAll()


class PackageTreeWidget(BaseTreeAndJsonEditWidget):
    def create_custom_view(self, parent, data):
        return PackageTreeFrame(parent, data)
