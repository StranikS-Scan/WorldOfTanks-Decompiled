# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/perk_available_tooltip_model.py
from frameworks.wulf import ViewModel

class PerkAvailableTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(PerkAvailableTooltipModel, self).__init__(properties=properties, commands=commands)

    def getPerkCount(self):
        return self._getNumber(0)

    def setPerkCount(self, value):
        self._setNumber(0, value)

    def getZeroPerkCount(self):
        return self._getNumber(1)

    def setZeroPerkCount(self, value):
        self._setNumber(1, value)

    def getLastPerkLevel(self):
        return self._getNumber(2)

    def setLastPerkLevel(self, value):
        self._setNumber(2, value)

    def getIsAllSlotsTrained(self):
        return self._getBool(3)

    def setIsAllSlotsTrained(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(PerkAvailableTooltipModel, self)._initialize()
        self._addNumberProperty('perkCount', 0)
        self._addNumberProperty('zeroPerkCount', 0)
        self._addNumberProperty('lastPerkLevel', 0)
        self._addBoolProperty('isAllSlotsTrained', False)
