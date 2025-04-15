# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/gen/view_models/views/lobby/mission_selection_view_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from story_mode.gui.impl.gen.view_models.views.lobby.mission_model import MissionModel
from story_mode.gui.impl.gen.view_models.views.lobby.parallax_model import ParallaxModel
from story_mode.gui.impl.gen.view_models.views.lobby.selected_mission_model import SelectedMissionModel
from story_mode.gui.impl.gen.view_models.views.lobby.task_model import TaskModel

class TabsEnum(IntEnum):
    NEWBIES = 0
    EVENT = 1


class MissionSelectionViewModel(ViewModel):
    __slots__ = ('onQuit', 'onMissionSelect', 'onLoaded', 'onChangeTab', 'onSelectedMissionTaskUnlocked', 'onAboutClick')

    def __init__(self, properties=7, commands=6):
        super(MissionSelectionViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def selectedMission(self):
        return self._getViewModel(0)

    @staticmethod
    def getSelectedMissionType():
        return SelectedMissionModel

    @property
    def parallax(self):
        return self._getViewModel(1)

    @staticmethod
    def getParallaxType():
        return ParallaxModel

    def getSelectedTab(self):
        return TabsEnum(self._getNumber(2))

    def setSelectedTab(self, value):
        self._setNumber(2, value.value)

    def getIsParallaxEnabled(self):
        return self._getBool(3)

    def setIsParallaxEnabled(self, value):
        self._setBool(3, value)

    def getIsTabsVisible(self):
        return self._getBool(4)

    def setIsTabsVisible(self, value):
        self._setBool(4, value)

    def getMissions(self):
        return self._getArray(5)

    def setMissions(self, value):
        self._setArray(5, value)

    @staticmethod
    def getMissionsType():
        return MissionModel

    def getTasks(self):
        return self._getArray(6)

    def setTasks(self, value):
        self._setArray(6, value)

    @staticmethod
    def getTasksType():
        return TaskModel

    def _initialize(self):
        super(MissionSelectionViewModel, self)._initialize()
        self._addViewModelProperty('selectedMission', SelectedMissionModel())
        self._addViewModelProperty('parallax', ParallaxModel())
        self._addNumberProperty('selectedTab')
        self._addBoolProperty('isParallaxEnabled', False)
        self._addBoolProperty('isTabsVisible', False)
        self._addArrayProperty('missions', Array())
        self._addArrayProperty('tasks', Array())
        self.onQuit = self._addCommand('onQuit')
        self.onMissionSelect = self._addCommand('onMissionSelect')
        self.onLoaded = self._addCommand('onLoaded')
        self.onChangeTab = self._addCommand('onChangeTab')
        self.onSelectedMissionTaskUnlocked = self._addCommand('onSelectedMissionTaskUnlocked')
        self.onAboutClick = self._addCommand('onAboutClick')
