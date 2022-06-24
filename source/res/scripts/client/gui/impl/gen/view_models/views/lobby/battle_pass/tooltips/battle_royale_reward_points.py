# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/tooltips/battle_royale_reward_points.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.reward_points_by_place_model import RewardPointsByPlaceModel

class BattleRoyaleRewardPoints(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BattleRoyaleRewardPoints, self).__init__(properties=properties, commands=commands)

    def getSoloMode(self):
        return self._getArray(0)

    def setSoloMode(self, value):
        self._setArray(0, value)

    @staticmethod
    def getSoloModeType():
        return RewardPointsByPlaceModel

    def getSquadMode(self):
        return self._getArray(1)

    def setSquadMode(self, value):
        self._setArray(1, value)

    @staticmethod
    def getSquadModeType():
        return RewardPointsByPlaceModel

    def _initialize(self):
        super(BattleRoyaleRewardPoints, self)._initialize()
        self._addArrayProperty('soloMode', Array())
        self._addArrayProperty('squadMode', Array())
