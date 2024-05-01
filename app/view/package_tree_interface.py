# coding:utf-8
from dataclasses import fields

from PyQt5.QtWidgets import QTreeWidgetItem

from .base_tree_frame import BaseTreeFrame
from .base_tree_json_interface import BaseTreeAndJsonEditWidget


class PackageTreeFrame(BaseTreeFrame):
    def __init__(self, parent = None, data = None):
        headers = ["Name", "Description"]
        super().__init__(parent, headers, data)
        self.update_data(data)

    def populate_tree(self):  # pylint: disable=too-many-branches
        for field in fields(self.data):  # pylint: disable=too-many-nested-blocks
            if field.name == "buckets":
                # Add all buckets
                buckets_item = QTreeWidgetItem(["Buckets"])
                for bucket in getattr(self.data, field.name):
                    bucket_item = QTreeWidgetItem([bucket.name])
                    buckets_item.addChild(bucket_item)

                self.tree.addTopLevelItem(buckets_item)

            elif field.name == "required":
                # Add all required packages
                required_item = QTreeWidgetItem(["Required"])

                for package in getattr(self.data, field.name):
                    required_item.addChild(QTreeWidgetItem([package.name, package.description]))
                self.tree.addTopLevelItem(required_item)

            else:
                # Add all the rest of the packages
                stuff = getattr(self.data, field.name)

                if isinstance(stuff, dict):
                    for category, items in stuff.items():
                        item = QTreeWidgetItem([category])
                        for sub_item in items:
                            if sub_item.alternative is not None:
                                # Make this sub item have another sub item
                                main_item = QTreeWidgetItem([sub_item.name, sub_item.description])
                                alt_item = QTreeWidgetItem([sub_item.alternative.name, sub_item.alternative.description])
                                item.addChild(main_item)
                                main_item.addChild(alt_item)
                            else:
                                item.addChild(QTreeWidgetItem([sub_item.name, sub_item.description]))

                        self.tree.addTopLevelItem(item)
                else:
                    item = QTreeWidgetItem([field.name.capitalize()])
                    for sub_item in stuff:
                        item.addChild(QTreeWidgetItem([sub_item.name, sub_item.description]))
                    self.tree.addTopLevelItem(item)

        self.tree.expandAll()


class PackageTreeWidget(BaseTreeAndJsonEditWidget):
    def create_custom_view(self, parent, data):
        return PackageTreeFrame(parent, data)
