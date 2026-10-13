# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/tooltips/key_tooltip_view_model.py
from frameworks.wulf import ViewModel

class KeyTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(KeyTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getKeyCount(self):
        return self._getNumber(0)

    def setKeyCount(self, value):
        self._setNumber(0, value)

    def getEndDate(self):
        return self._getNumber(1)

    def setEndDate(self, value):
        self._setNumber(1, value)

    def getEffective(self):
        return self._getNumber(2)

    def setEffective(self, value):
        self._setNumber(2, value)

    def getBoss(self):
        return self._getNumber(3)

    def setBoss(self, value):
        self._setNumber(3, value)

    def getDaily(self):
        return self._getNumber(4)

    def setDaily(self, value):
        self._setNumber(4, value)

    def getIsPostBatle(self):
        return self._getBool(5)

    def setIsPostBatle(self, value):
        self._setBool(5, value)

    def getSecret(self):
        return self._getNumber(6)

    def setSecret(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(KeyTooltipViewModel, self)._initialize()
        self._addNumberProperty('keyCount', 0)
        self._addNumberProperty('endDate', 0)
        self._addNumberProperty('effective', 0)
        self._addNumberProperty('boss', 0)
        self._addNumberProperty('daily', 0)
        self._addBoolProperty('isPostBatle', False)
        self._addNumberProperty('secret', 0)
