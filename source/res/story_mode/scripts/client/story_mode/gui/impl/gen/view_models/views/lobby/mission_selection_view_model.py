# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/gen/view_models/views/lobby/mission_selection_view_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from story_mode.gui.impl.gen.view_models.views.lobby.mission_model import MissionModel
from story_mode.gui.impl.gen.view_models.views.lobby.selected_mission_model import SelectedMissionModel
from story_mode.gui.impl.gen.view_models.views.lobby.task_model import TaskModel

class TabsEnum(IntEnum):
    NEWBIES = 0
    EVENT = 1


class MissionSelectionViewModel(ViewModel):
    __slots__ = ('onQuit', 'onMissionSelect', 'onLoaded', 'onChangeTab', 'onSelectedMissionTaskUnlocked', 'onAboutClick')

    def __init__(self, properties=5, commands=6):
        super(MissionSelectionViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def selectedMission(self):
        return self._getViewModel(0)

    @staticmethod
    def getSelectedMissionType():
        return SelectedMissionModel

    def getSelectedTab(self):
        return TabsEnum(self._getNumber(1))

    def setSelectedTab(self, value):
        self._setNumber(1, value.value)

    def getIsTabsVisible(self):
        return self._getBool(2)

    def setIsTabsVisible(self, value):
        self._setBool(2, value)

    def getMissions(self):
        return self._getArray(3)

    def setMissions(self, value):
        self._setArray(3, value)

    @staticmethod
    def getMissionsType():
        return MissionModel

    def getTasks(self):
        return self._getArray(4)

    def setTasks(self, value):
        self._setArray(4, value)

    @staticmethod
    def getTasksType():
        return TaskModel

    def _initialize(self):
        super(MissionSelectionViewModel, self)._initialize()
        self._addViewModelProperty('selectedMission', SelectedMissionModel())
        self._addNumberProperty('selectedTab')
        self._addBoolProperty('isTabsVisible', False)
        self._addArrayProperty('missions', Array())
        self._addArrayProperty('tasks', Array())
        self.onQuit = self._addCommand('onQuit')
        self.onMissionSelect = self._addCommand('onMissionSelect')
        self.onLoaded = self._addCommand('onLoaded')
        self.onChangeTab = self._addCommand('onChangeTab')
        self.onSelectedMissionTaskUnlocked = self._addCommand('onSelectedMissionTaskUnlocked')
        self.onAboutClick = self._addCommand('onAboutClick')
