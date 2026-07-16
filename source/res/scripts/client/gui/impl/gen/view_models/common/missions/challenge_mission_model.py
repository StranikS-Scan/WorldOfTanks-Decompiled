# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/missions/challenge_mission_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.missions.quest_model import QuestModel
from gui.impl.gen.view_models.views.lobby.challenges.bonus_model import BonusModel

class ChallengeMissionModel(QuestModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(ChallengeMissionModel, self).__init__(properties=properties, commands=commands)

    def getBonuses(self):
        return self._getArray(11)

    def setBonuses(self, value):
        self._setArray(11, value)

    @staticmethod
    def getBonusesType():
        return BonusModel

    def _initialize(self):
        super(ChallengeMissionModel, self)._initialize()
        self._addArrayProperty('bonuses', Array())
