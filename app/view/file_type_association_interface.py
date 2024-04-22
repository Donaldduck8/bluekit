# coding:utf-8
from PyQt5.QtWidgets import QTreeWidgetItem

from .base_tree_frame import BaseTreeFrame
from .base_tree_json_interface import BaseTreeAndJsonEditWidget


class FileTypeAssocTreeFrame(BaseTreeFrame):
    def __init__(self, parent=None, data: dict = None):
        headers = ["Name", "Arguments"]
        super().__init__(parent, headers, data)
        self.update_data(data)

    def update_data(self, data: dict):
        self.tree.clear()  # Clear the existing items
        self.data = data
        self.populate_tree()

    def populate_tree(self):
        if not isinstance(self.data, dict):
            return

        for category, value in self.data.items():
            if not isinstance(value, dict):
                continue

            category_item = QTreeWidgetItem([category])
            self.tree.addTopLevelItem(category_item)

            entry_item = QTreeWidgetItem([value["program_name"], " ".join(value["arguments"])])
            category_item.addChild(entry_item)

            file_types_item = QTreeWidgetItem(["File Types"])
            entry_item.addChild(file_types_item)

            for file_extension in value["file_types"]:
                file_types_item.addChild(QTreeWidgetItem(["." + file_extension]))

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


class FileTypeAssocWidget(BaseTreeAndJsonEditWidget):
    def create_custom_view(self, parent, data):
        return FileTypeAssocTreeFrame(parent, data)
