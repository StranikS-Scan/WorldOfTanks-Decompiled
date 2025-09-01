# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/menu_item_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.hangar.notification_model import NotificationModel

class MenuItemModel(ViewModel):
    __slots__ = ()
    DISABLED = 'disabled'
    ENABLED = 'enabled'

    def __init__(self, properties=3, commands=0):
        super(MenuItemModel, self).__init__(properties=properties, commands=commands)

    @property
    def notification(self):
        return self._getViewModel(0)

    @staticmethod
    def getNotificationType():
        return NotificationModel

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getState(self):
        return self._getString(2)

    def setState(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(MenuItemModel, self)._initialize()
        self._addViewModelProperty('notification', NotificationModel())
        self._addStringProperty('name', '')
        self._addStringProperty('state', 'enabled')
