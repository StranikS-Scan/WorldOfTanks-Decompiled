# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_hub/views/sub_models/menu_item_model.py
from frameworks.wulf import ViewModel

class MenuItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(MenuItemModel, self).__init__(properties=properties, commands=commands)

    def getTabName(self):
        return self._getString(0)

    def setTabName(self, value):
        self._setString(0, value)

    def getCounter(self):
        return self._getNumber(1)

    def setCounter(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(MenuItemModel, self)._initialize()
        self._addStringProperty('tabName', '')
        self._addNumberProperty('counter', 0)
