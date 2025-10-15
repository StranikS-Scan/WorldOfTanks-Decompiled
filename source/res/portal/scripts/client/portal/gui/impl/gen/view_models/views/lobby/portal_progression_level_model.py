# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/portal_progression_level_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class PortalProgressionLevelModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(PortalProgressionLevelModel, self).__init__(properties=properties, commands=commands)

    def getRewards(self):
        return self._getArray(0)

    def setRewards(self, value):
        self._setArray(0, value)

    @staticmethod
    def getRewardsType():
        return BonusModel

    def getPointsNeededPerStage(self):
        return self._getNumber(1)

    def setPointsNeededPerStage(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(PortalProgressionLevelModel, self)._initialize()
        self._addArrayProperty('rewards', Array())
        self._addNumberProperty('pointsNeededPerStage', 0)
