# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/wrappers/user_list_model.py
import typing
import logging
import Event
from gui.impl.gen.view_models.ui_kit.list_model import ListModel
_logger = logging.getLogger(__name__)

class UserListModel(ListModel):
    __slots__ = ('onUserSelectionChanged', 'onUserItemClicked')

    def __init__(self):
        super(UserListModel, self).__init__()
        self.onUserSelectionChanged = Event.Event()
        self.onUserItemClicked = Event.Event()

    def addNumber(self, value, isSelected=False):
        self.getItems().addNumber(value)
        if isSelected:
            self.addSelectedIndex(self.getItemsLength() - 1)

    def addReal(self, value, isSelected=False):
        self.getItems().addReal(value)
        if isSelected:
            self.addSelectedIndex(self.getItemsLength() - 1)

    def addBool(self, value, isSelected=False):
        self.getItems().addBool(value)
        if isSelected:
            self.addSelectedIndex(self.getItemsLength() - 1)

    def addString(self, value, isSelected=False):
        self.getItems().addString(value)
        if isSelected:
            self.addSelectedIndex(self.getItemsLength() - 1)

    def addViewModel(self, value, isSelected=False):
        self.getItems().addViewModel(value)
        if isSelected:
            self.addSelectedIndex(self.getItemsLength() - 1)

    def addArray(self, value, isSelected=False):
        self.getItems().addArray(value)
        if isSelected:
            self.addSelectedIndex(self.getItemsLength() - 1)

    def getItem(self, index):
        try:
            return self.getItems()[index]
        except IndexError:
            _logger.error('Index %d is out of range', index)
            return None

        return None

    def findItems(self, predicate):
        return [ item for item in self.getItems() if predicate(item) ]

    def clearItems(self):
        self.getItems().clear()

    def getItemsLength(self):
        return len(self.getItems())

    def getSelectedItem(self):
        selectedItemsIndices = self.getSelectedIndices()
        return self.getItem(selectedItemsIndices[0]) if selectedItemsIndices else None

    def getSelectedItems(self):
        result = []
        selectedItemsIndices = self.getSelectedIndices()
        for index in selectedItemsIndices:
            result.append(self.getItem(index))

        return result

    def addSelectedIndex(self, index):
        self.getSelectedIndices().addNumber(index)

    def removeItemByIndex(self, index):
        self.getItems().remove(index)

    def removeItemByIndexes(self, indexes):
        self.getItems().removeValues(indexes)

    def removeSelectedIndexes(self):
        selectedItems = self.getSelectedIndices()
        if selectedItems:
            self.removeItemByIndexes(selectedItems)
        else:
            _logger.error('There are no selected items in list')

    def invalidate(self):
        self.getItems().invalidate()

    def reserve(self, capacity):
        self.getItems().reserve(capacity)

    def _initialize(self):
        super(UserListModel, self)._initialize()
        self.onSelectionChanged += self.__onSelectionChanged
        self.onItemClicked += self.__onItemClicked

    def _finalize(self):
        self.onSelectionChanged -= self.__onSelectionChanged
        self.onItemClicked -= self.__onItemClicked
        self.onUserSelectionChanged.clear()
        self.onUserItemClicked.clear()
        super(UserListModel, self)._finalize()

    def __onSelectionChanged(self, args=None):
        if 'selectedIndex' not in args or 'unselectedIndex' not in args:
            _logger.error('%r: Arguments "selectedIndex" or "unselectedIndex" is not defined in %r', self, args)
        index = args['selectedIndex']
        if index is not None and index >= 0:
            item = self.getItem(index)
            if item is not None:
                self.onUserSelectionChanged(item)
        return

    def __onItemClicked(self, args=None):
        if 'index' not in args:
            _logger.error('%r: Argument "index" is not defined in %r', self, args)
            return
        else:
            item = self.getItem(args['index'])
            if item is not None:
                self.onUserItemClicked(item)
            return
