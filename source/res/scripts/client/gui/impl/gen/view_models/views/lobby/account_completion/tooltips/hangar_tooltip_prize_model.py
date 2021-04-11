# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_completion/tooltips/hangar_tooltip_prize_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class HangarTooltipPrizeModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(HangarTooltipPrizeModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getResource(0)

    def setIcon(self, value):
        self._setResource(0, value)

    def getTitle(self):
        return self._getResource(1)

    def setTitle(self, value):
        self._setResource(1, value)

    def getValue(self):
        return self._getNumber(2)

    def setValue(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(HangarTooltipPrizeModel, self)._initialize()
        self._addResourceProperty('icon', R.invalid())
        self._addResourceProperty('title', R.invalid())
        self._addNumberProperty('value', 0)
