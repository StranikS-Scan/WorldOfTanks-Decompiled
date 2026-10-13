# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/widgets/shop_style_panel_model.py
from frameworks.wulf import ViewModel

class ShopStylePanelModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=3, commands=1):
        super(ShopStylePanelModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getTimer(self):
        return self._getNumber(1)

    def setTimer(self, value):
        self._setNumber(1, value)

    def getIsOwned(self):
        return self._getBool(2)

    def setIsOwned(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(ShopStylePanelModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addNumberProperty('timer', 0)
        self._addBoolProperty('isOwned', False)
        self.onClick = self._addCommand('onClick')
