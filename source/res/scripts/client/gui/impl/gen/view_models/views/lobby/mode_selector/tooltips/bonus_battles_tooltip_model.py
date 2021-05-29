# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/tooltips/bonus_battles_tooltip_model.py
from frameworks.wulf import ViewModel

class BonusBattlesTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(BonusBattlesTooltipModel, self).__init__(properties=properties, commands=commands)

    def getBattles(self):
        return self._getNumber(0)

    def setBattles(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(BonusBattlesTooltipModel, self)._initialize()
        self._addNumberProperty('battles', 0)
