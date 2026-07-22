# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/impl/gen/view_models/views/lobby/tank_academy/tank_academy_rewards_view_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.tank_academy_bonus_model import TankAcademyBonusModel

class State(IntEnum):
    REGULAR = 0
    REWARDSCREENCHAIN = 1
    ENDREWARDSCREENCHAIN = 2
    FIRST = 3
    FINAL = 4


class TankAcademyRewardsViewModel(ViewModel):
    __slots__ = ('onClose', 'goToRewardsSelection', 'goToNextTask', 'goToHangarPreview')

    def __init__(self, properties=4, commands=4):
        super(TankAcademyRewardsViewModel, self).__init__(properties=properties, commands=commands)

    def getStage(self):
        return self._getNumber(0)

    def setStage(self, value):
        self._setNumber(0, value)

    def getState(self):
        return State(self._getNumber(1))

    def setState(self, value):
        self._setNumber(1, value.value)

    def getMainRewards(self):
        return self._getArray(2)

    def setMainRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getMainRewardsType():
        return TankAcademyBonusModel

    def getRewards(self):
        return self._getArray(3)

    def setRewards(self, value):
        self._setArray(3, value)

    @staticmethod
    def getRewardsType():
        return TankAcademyBonusModel

    def _initialize(self):
        super(TankAcademyRewardsViewModel, self)._initialize()
        self._addNumberProperty('stage', 0)
        self._addNumberProperty('state')
        self._addArrayProperty('mainRewards', Array())
        self._addArrayProperty('rewards', Array())
        self.onClose = self._addCommand('onClose')
        self.goToRewardsSelection = self._addCommand('goToRewardsSelection')
        self.goToNextTask = self._addCommand('goToNextTask')
        self.goToHangarPreview = self._addCommand('goToHangarPreview')
