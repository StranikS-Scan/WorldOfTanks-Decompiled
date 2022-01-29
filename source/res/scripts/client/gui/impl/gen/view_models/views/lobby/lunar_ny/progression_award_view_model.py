# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lunar_ny/progression_award_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class ProgressionAwardViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(ProgressionAwardViewModel, self).__init__(properties=properties, commands=commands)

    def getReceivedLevel(self):
        return self._getNumber(0)

    def setReceivedLevel(self, value):
        self._setNumber(0, value)

    def getRewards(self):
        return self._getArray(1)

    def setRewards(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(ProgressionAwardViewModel, self)._initialize()
        self._addNumberProperty('receivedLevel', 0)
        self._addArrayProperty('rewards', Array())
