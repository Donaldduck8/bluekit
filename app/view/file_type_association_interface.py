# coding:utf-8
from PyQt5.QtWidgets import QTreeWidgetItem

from ..data import FileTypeAssociations
from .base_tree_frame import BaseTreeFrame
from .base_tree_json_interface import BaseTreeAndJsonEditWidget


class FileTypeAssocTreeFrame(BaseTreeFrame):
    data: FileTypeAssociations

    def __init__(self, parent=None, data: FileTypeAssociations = None):
        headers = ["Name", "Arguments"]
        super().__init__(parent, headers, data)
        self.update_data(data)

    def populate_tree(self):
        for category, value in self.data.associations.items():
            category_item = QTreeWidgetItem([category])
            self.tree.addTopLevelItem(category_item)

            entry_item = QTreeWidgetItem([value.program_name, " ".join(value.arguments)])
            category_item.addChild(entry_item)

            file_types_item = QTreeWidgetItem(["File Types"])
            entry_item.addChild(file_types_item)

            for file_extension in value.file_types:
                file_types_item.addChild(QTreeWidgetItem(["." + file_extension]))

        self.tree.expandAll()


class FileTypeAssocWidget(BaseTreeAndJsonEditWidget):
    def create_custom_view(self, parent, data):
        return FileTypeAssocTreeFrame(parent, data)
