# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/widget/widget_quest_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.user_missions.common.base_quest_model import BaseQuestModel
from gui.impl.gen.view_models.views.lobby.user_missions.widget.bonus_model import BonusModel

class WidgetQuestModel(BaseQuestModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
        super(WidgetQuestModel, self).__init__(properties=properties, commands=commands)

    def getCountdown(self):
        return self._getNumber(9)

    def setCountdown(self, value):
        self._setNumber(9, value)

    def getMissionType(self):
        return self._getString(10)

    def setMissionType(self, value):
        self._setString(10, value)

    def getBonuses(self):
        return self._getArray(11)

    def setBonuses(self, value):
        self._setArray(11, value)

    @staticmethod
    def getBonusesType():
        return BonusModel

    def getCommonConditionId(self):
        return self._getNumber(12)

    def setCommonConditionId(self, value):
        self._setNumber(12, value)

    def getSpecialConditionIds(self):
        return self._getArray(13)

    def setSpecialConditionIds(self, value):
        self._setArray(13, value)

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
