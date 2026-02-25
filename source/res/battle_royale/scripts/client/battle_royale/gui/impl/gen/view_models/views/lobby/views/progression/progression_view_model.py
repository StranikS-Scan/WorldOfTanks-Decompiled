# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/views/progression/progression_view_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.battle_quests_model import BattleQuestsModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.battle_royale_event_model import BattleRoyaleEventModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.progression.progress_level_model import ProgressLevelModel

class ProgressionState(Enum):
    INPROGRESS = 'inProgress'
    COMPLETED = 'completed'


class ProgressionViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=10, commands=1):
        super(ProgressionViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def battleQuests(self):
        return self._getViewModel(0)

    @staticmethod
    def getBattleQuestsType():
        return BattleQuestsModel

    @property
    def eventInfo(self):
        return self._getViewModel(1)

    @staticmethod
    def getEventInfoType():
        return BattleRoyaleEventModel

    def getState(self):
        return ProgressionState(self._getString(2))

    def setState(self, value):
        self._setString(2, value.value)

    def getCurProgressPoints(self):
        return self._getNumber(3)

    def setCurProgressPoints(self, value):
        self._setNumber(3, value)

    def getPrevProgressPoints(self):
        return self._getNumber(4)

    def setPrevProgressPoints(self, value):
        self._setNumber(4, value)

    def getPointsForLevel(self):
        return self._getNumber(5)

    def setPointsForLevel(self, value):
        self._setNumber(5, value)

    def getProgressLevels(self):
        return self._getArray(6)

    def setProgressLevels(self, value):
        self._setArray(6, value)

    @staticmethod
    def getProgressLevelsType():
        return ProgressLevelModel

    def getStartTimestamp(self):
        return self._getNumber(7)

    def setStartTimestamp(self, value):
        self._setNumber(7, value)

    def getEndTimestamp(self):
        return self._getNumber(8)

    def setEndTimestamp(self, value):
        self._setNumber(8, value)

    def getCalendarTooltipId(self):
        return self._getString(9)

    def setCalendarTooltipId(self, value):
        self._setString(9, value)

    def _initialize(self):
        super(ProgressionViewModel, self)._initialize()
        self._addViewModelProperty('battleQuests', BattleQuestsModel())
        self._addViewModelProperty('eventInfo', BattleRoyaleEventModel())
        self._addStringProperty('state')
        self._addNumberProperty('curProgressPoints', 0)
        self._addNumberProperty('prevProgressPoints', 0)
        self._addNumberProperty('pointsForLevel', 0)
        self._addArrayProperty('progressLevels', Array())
        self._addNumberProperty('startTimestamp', 0)
        self._addNumberProperty('endTimestamp', 0)
        self._addStringProperty('calendarTooltipId', '')
        self.onClose = self._addCommand('onClose')
