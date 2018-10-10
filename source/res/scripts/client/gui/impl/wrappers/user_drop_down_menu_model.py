# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/wrappers/user_drop_down_menu_model.py
import logging
import Event
from gui.impl.gen.view_models.ui_kit.drop_down_menu_item_model import DropDownMenuItemModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel
_logger = logging.getLogger(__name__)

class UserDropDownMenuModel(ListModel):
    __slots__ = ('onUserSelectionChanged',)

    def __init__(self):
        super(UserDropDownMenuModel, self).__init__()
        self.onUserSelectionChanged = Event.Event()

    def _initialize(self):
        super(UserDropDownMenuModel, self)._initialize()
        self.onSelectionChanged += self.__onSelectionChanged

    def _finalize(self):
        self.onSelectionChanged -= self.__onSelectionChanged
        self.onUserSelectionChanged.clear()
        super(UserDropDownMenuModel, self)._finalize()

    def addItem(self, actionID, label, icon=None, isEnabled=True):
        item = DropDownMenuItemModel()
        item.setId(actionID)
        item.setLabel(label)
        item.setIsEnabled(isEnabled)
        if icon is not None:
            item.setIcon(icon)
        self.getItems().addViewModel(item)
        return

    def getItemByID(self, actionID):
        try:
            return next((item for item in self.getItems() if item.getId() == actionID))
        except StopIteration:
            _logger.error("Item with actionID '%d' is not found in drop down list", actionID)
            return None

        return None

    def getItem(self, index):
        try:
            return self.getItems()[index]
        except IndexError:
            _logger.error('Index %d is out of rage', self.getSelectedIndex())
            return None

        return None

    def getSelectedItem(self):
        return self.getItem(self.getSelectedIndex())

    def __onSelectionChanged(self):
        item = self.getSelectedItem()
        if item is not None:
            self.onUserSelectionChanged(item)
        return
