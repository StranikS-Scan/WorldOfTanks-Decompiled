# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/popovers/random_battle_popover_item_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class RandomBattlePopoverItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(RandomBattlePopoverItemModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getResource(0)

    def setTitle(self, value):
        self._setResource(0, value)

    def getTooltipHeader(self):
        return self._getResource(1)

    def setTooltipHeader(self, value):
        self._setResource(1, value)

    def getTooltipBody(self):
        return self._getResource(2)

    def setTooltipBody(self, value):
        self._setResource(2, value)

    def getTooltipAlert(self):
        return self._getString(3)

    def setTooltipAlert(self, value):
        self._setString(3, value)

    def getType(self):
        return self._getString(4)

    def setType(self, value):
        self._setString(4, value)

    def getIsChecked(self):
        return self._getBool(5)

    def setIsChecked(self, value):
        self._setBool(5, value)

    def getIsEnabled(self):
        return self._getBool(6)

    def setIsEnabled(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(RandomBattlePopoverItemModel, self)._initialize()
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('tooltipHeader', R.invalid())
        self._addResourceProperty('tooltipBody', R.invalid())
        self._addStringProperty('tooltipAlert', '')
        self._addStringProperty('type', '')
        self._addBoolProperty('isChecked', False)
        self._addBoolProperty('isEnabled', False)
