# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/menu_item_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class MenuItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(MenuItemModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getResource(0)

    def setName(self, value):
        self._setResource(0, value)

    def getHeader(self):
        return self._getResource(1)

    def setHeader(self, value):
        self._setResource(1, value)

    def getDescription(self):
        return self._getResource(2)

    def setDescription(self, value):
        self._setResource(2, value)

    def getNotification(self):
        return self._getNumber(3)

    def setNotification(self, value):
        self._setNumber(3, value)

    def getIsNotification(self):
        return self._getBool(4)

    def setIsNotification(self, value):
        self._setBool(4, value)

    def getViewId(self):
        return self._getString(5)

    def setViewId(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(MenuItemModel, self)._initialize()
        self._addResourceProperty('name', R.invalid())
        self._addResourceProperty('header', R.invalid())
        self._addResourceProperty('description', R.invalid())
        self._addNumberProperty('notification', 0)
        self._addBoolProperty('isNotification', False)
        self._addStringProperty('viewId', '')
