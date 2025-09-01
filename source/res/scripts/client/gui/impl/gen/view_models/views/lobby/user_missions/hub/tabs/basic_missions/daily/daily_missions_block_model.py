# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/hub/tabs/basic_missions/daily/daily_missions_block_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.daily.daily_bonus_mission_model import DailyBonusMissionModel
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.daily.daily_mission_model import DailyMissionModel

class DailyMissionsBlockModel(ViewModel):
    __slots__ = ('onReroll',)
    BONUS_CARD_DEFAULT_ID = 'BONUS_CARD'

    def __init__(self, properties=5, commands=1):
        super(DailyMissionsBlockModel, self).__init__(properties=properties, commands=commands)

    @property
    def bonusMission(self):
        return self._getViewModel(0)

    @staticmethod
    def getBonusMissionType():
        return DailyBonusMissionModel

    def getMissionsList(self):
        return self._getArray(1)

    def setMissionsList(self, value):
        self._setArray(1, value)

    @staticmethod
    def getMissionsListType():
        return DailyMissionModel

    def getTimeToNextRerol(self):
        return self._getNumber(2)

    def setTimeToNextRerol(self, value):
        self._setNumber(2, value)

    def getAreAllMissionsCompleted(self):
        return self._getBool(3)

    def setAreAllMissionsCompleted(self, value):
        self._setBool(3, value)

    def getTimeToMissionsUpdate(self):
        return self._getNumber(4)

    def setTimeToMissionsUpdate(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(DailyMissionsBlockModel, self)._initialize()
        self._addViewModelProperty('bonusMission', DailyBonusMissionModel())
        self._addArrayProperty('missionsList', Array())
        self._addNumberProperty('timeToNextRerol', 0)
        self._addBoolProperty('areAllMissionsCompleted', False)
        self._addNumberProperty('timeToMissionsUpdate', 0)
        self.onReroll = self._addCommand('onReroll')
