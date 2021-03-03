# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/bm2021/black_market_entry_point_model.py
from frameworks.wulf import ViewModel

class BlackMarketEntryPointModel(ViewModel):
    __slots__ = ('onWidgetClick',)

    def __init__(self, properties=2, commands=1):
        super(BlackMarketEntryPointModel, self).__init__(properties=properties, commands=commands)

    def getTimeLeft(self):
        return self._getNumber(0)

    def setTimeLeft(self, value):
        self._setNumber(0, value)

    def getIsSmall(self):
        return self._getBool(1)

    def setIsSmall(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(BlackMarketEntryPointModel, self)._initialize()
        self._addNumberProperty('timeLeft', 0)
        self._addBoolProperty('isSmall', False)
        self.onWidgetClick = self._addCommand('onWidgetClick')
