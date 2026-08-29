# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/widget/widget_quest_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.user_missions.common.base_quest_model import BaseQuestModel
from gui.impl.gen.view_models.views.lobby.user_missions.widget.bonus_model import BonusModel

class WidgetQuestModel(BaseQuestModel):
    __slots__ = ()

    def __init__(self, properties=15, commands=0):
        super(WidgetQuestModel, self).__init__(properties=properties, commands=commands)

    def getCountdown(self):
        return self._getNumber(10)

    def setCountdown(self, value):
        self._setNumber(10, value)

    def getMissionType(self):
        return self._getString(11)

    def setMissionType(self, value):
        self._setString(11, value)

    def getBonuses(self):
        return self._getArray(12)

    def setBonuses(self, value):
        self._setArray(12, value)

    @staticmethod
    def getBonusesType():
        return BonusModel

    def getCommonConditionId(self):
        return self._getNumber(13)

    def setCommonConditionId(self, value):
        self._setNumber(13, value)

    def getSpecialConditionIds(self):
        return self._getArray(14)

    def setSpecialConditionIds(self, value):
        self._setArray(14, value)

    @staticmethod
    def getSpecialConditionIdsType():
        return int

    def _initialize(self):
        super(WidgetQuestModel, self)._initialize()
        self._addNumberProperty('countdown', 0)
        self._addStringProperty('missionType', '')
        self._addArrayProperty('bonuses', Array())
        self._addNumberProperty('commonConditionId', 0)
        self._addArrayProperty('specialConditionIds', Array())
