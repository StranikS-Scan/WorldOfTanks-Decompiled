# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/gen/view_models/views/lobby/progression/progression_view_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from comp7_light.gui.impl.gen.view_models.views.lobby.battle_quests_model import BattleQuestsModel
from comp7_light.gui.impl.gen.view_models.views.lobby.progression.progress_level_model import ProgressLevelModel
from comp7_light.gui.impl.gen.view_models.views.lobby.schedule_info_model import ScheduleInfoModel

class ProgressionState(Enum):
    INPROGRESS = 'inProgress'
    COMPLETED = 'completed'


class ProgressionViewModel(ViewModel):
    __slots__ = ('onClose', 'onAboutClicked')

    def __init__(self, properties=7, commands=2):
        super(ProgressionViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def battleQuests(self):
        return self._getViewModel(0)

    @staticmethod
    def getBattleQuestsType():
        return BattleQuestsModel

    @property
    def scheduleInfo(self):
        return self._getViewModel(1)

    @staticmethod
    def getScheduleInfoType():
        return ScheduleInfoModel

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

    def _initialize(self):
        super(ProgressionViewModel, self)._initialize()
        self._addViewModelProperty('battleQuests', BattleQuestsModel())
        self._addViewModelProperty('scheduleInfo', ScheduleInfoModel())
        self._addStringProperty('state')
        self._addNumberProperty('curProgressPoints', 0)
        self._addNumberProperty('prevProgressPoints', 0)
        self._addNumberProperty('pointsForLevel', 0)
        self._addArrayProperty('progressLevels', Array())
        self.onClose = self._addCommand('onClose')
        self.onAboutClicked = self._addCommand('onAboutClicked')
