# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/action_menu_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.secret_event.menu_item_model import MenuItemModel

class ActionMenuModel(ViewModel):
    __slots__ = ('onClose', 'onEscPressed', 'onLoadView')
    BASE = 'base'
    MISSION = 'mission'
    SUBDIVISION = 'subdivision'
    ORDERS = 'orders'
    SHOP = 'shop'
    ABOUT = 'about'
    BERLIN = 'berlin'

    def __init__(self, properties=4, commands=3):
        super(ActionMenuModel, self).__init__(properties=properties, commands=commands)

    @property
    def menuItems(self):
        return self._getViewModel(0)

    def getCurrentView(self):
        return self._getString(1)

    def setCurrentView(self, value):
        self._setString(1, value)

    def getPreviousView(self):
        return self._getString(2)

    def setPreviousView(self, value):
        self._setString(2, value)

    def getPreviousViewName(self):
        return self._getResource(3)

    def setPreviousViewName(self, value):
        self._setResource(3, value)

    def _initialize(self):
        super(ActionMenuModel, self)._initialize()
        self._addViewModelProperty('menuItems', UserListModel())
        self._addStringProperty('currentView', '')
        self._addStringProperty('previousView', '')
        self._addResourceProperty('previousViewName', R.invalid())
        self.onClose = self._addCommand('onClose')
        self.onEscPressed = self._addCommand('onEscPressed')
        self.onLoadView = self._addCommand('onLoadView')
