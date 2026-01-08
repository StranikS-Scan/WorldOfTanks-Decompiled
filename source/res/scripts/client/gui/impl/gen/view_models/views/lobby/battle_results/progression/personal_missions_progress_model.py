# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/progression/personal_missions_progress_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.personal_missions_30.common.enums import MissionCategory
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.impl.gen.view_models.views.lobby.personal_missions_30.quest_model import QuestModel

class PM3Status(Enum):
    OPERATION_MISSION_PROGRESS = 'operation_mission_progress'
    OPERATION_MISSION_COMPLETE = 'operation_mission_complete'
    OPERATION_COMPLETED_WITH_HONOR = 'operation_completed_with_honor'
    CAMPAIGN_COMPLETED_WITH_HONOR = 'campaign_completed_with_honor'


class PersonalMissionsProgressModel(ViewModel):
    __slots__ = ('onNavigate',)
    PATH = 'coui://gui/gameface/_dist/production/mono/plugins/personal_missions_30/post_battle/post_battle.js'

    def __init__(self, properties=9, commands=1):
        super(PersonalMissionsProgressModel, self).__init__(properties=properties, commands=commands)

    def getMissionName(self):
        return self._getString(0)

    def setMissionName(self, value):
        self._setString(0, value)

    def getMissionCategory(self):
        return MissionCategory(self._getString(1))

    def setMissionCategory(self, value):
        self._setString(1, value.value)

    def getQuests(self):
        return self._getArray(2)

    def setQuests(self, value):
        self._setArray(2, value)

    @staticmethod
    def getQuestsType():
        return QuestModel

    def getAllQuestsRequired(self):
        return self._getBool(3)

    def setAllQuestsRequired(self, value):
        self._setBool(3, value)

    def getCurrentProgress(self):
        return self._getNumber(4)

    def setCurrentProgress(self, value):
        self._setNumber(4, value)

    def getMaxProgress(self):
        return self._getNumber(5)

    def setMaxProgress(self, value):
        self._setNumber(5, value)

    def getRewards(self):
        return self._getArray(6)

    def setRewards(self, value):
        self._setArray(6, value)

    @staticmethod
    def getRewardsType():
        return IconBonusModel

    def getCurrentPM3Status(self):
        return PM3Status(self._getString(7))

    def setCurrentPM3Status(self, value):
        self._setString(7, value.value)

    def getNavigationEnabled(self):
        return self._getBool(8)

    def setNavigationEnabled(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(PersonalMissionsProgressModel, self)._initialize()
        self._addStringProperty('missionName', '')
        self._addStringProperty('missionCategory')
        self._addArrayProperty('quests', Array())
        self._addBoolProperty('allQuestsRequired', False)
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('maxProgress', 0)
        self._addArrayProperty('rewards', Array())
        self._addStringProperty('currentPM3Status')
        self._addBoolProperty('navigationEnabled', False)
        self.onNavigate = self._addCommand('onNavigate')
