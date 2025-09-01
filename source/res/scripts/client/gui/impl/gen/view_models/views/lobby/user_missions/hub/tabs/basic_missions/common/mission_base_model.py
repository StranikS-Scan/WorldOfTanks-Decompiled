# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/hub/tabs/basic_missions/common/mission_base_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.user_missions.common.base_quest_model import BaseQuestModel

class MissionBaseModel(BaseQuestModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(MissionBaseModel, self).__init__(properties=properties, commands=commands)

    def getBonuses(self):
        return self._getArray(9)

    def setBonuses(self, value):
        self._setArray(9, value)

    @staticmethod
    def getBonusesType():
        return BonusModel

    def _initialize(self):
        super(MissionBaseModel, self)._initialize()
        self._addArrayProperty('bonuses', Array())
