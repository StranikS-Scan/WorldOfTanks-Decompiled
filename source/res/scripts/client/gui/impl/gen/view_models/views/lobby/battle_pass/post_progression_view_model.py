# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/post_progression_view_model.py
from enum import IntEnum
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.awards_widget_model import AwardsWidgetModel
from gui.impl.gen.view_models.views.lobby.battle_pass.chapter_simple_model import ChapterSimpleModel
from gui.impl.gen.view_models.views.lobby.battle_pass.level_model import LevelModel

class PostProgressionStatus(IntEnum):
    LOCKED = 0
    UNLOCKED = 1
    PAUSED = 2


class PostProgressionViewModel(ViewModel):
    __slots__ = ('onOpenPointsInfo', 'onOpenInfoPage', 'onOpenChaptersBuyView', 'onClose', 'onProgressAchieved', 'onCycleCompleted')

    def __init__(self, properties=12, commands=6):
        super(PostProgressionViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def awardsWidget(self):
        return self._getViewModel(0)

    @staticmethod
    def getAwardsWidgetType():
        return AwardsWidgetModel

    def getPreviousLevel(self):
        return self._getNumber(1)

    def setPreviousLevel(self, value):
        self._setNumber(1, value)

    def getCurrentLevel(self):
        return self._getNumber(2)

    def setCurrentLevel(self, value):
        self._setNumber(2, value)

    def getPreviousLevelPoints(self):
        return self._getNumber(3)

    def setPreviousLevelPoints(self, value):
        self._setNumber(3, value)

    def getCurrentLevelPoints(self):
        return self._getNumber(4)

    def setCurrentLevelPoints(self, value):
        self._setNumber(4, value)

    def getPreviousCyclesCompletedCount(self):
        return self._getNumber(5)

    def setPreviousCyclesCompletedCount(self, value):
        self._setNumber(5, value)

    def getCyclesCompletedCount(self):
        return self._getNumber(6)

    def setCyclesCompletedCount(self, value):
        self._setNumber(6, value)

    def getEndDate(self):
        return self._getNumber(7)

    def setEndDate(self, value):
        self._setNumber(7, value)

    def getChapterID(self):
        return self._getNumber(8)

    def setChapterID(self, value):
        self._setNumber(8, value)

    def getLevels(self):
        return self._getArray(9)

    def setLevels(self, value):
        self._setArray(9, value)

    @staticmethod
    def getLevelsType():
        return LevelModel

    def getChapters(self):
        return self._getArray(10)

    def setChapters(self, value):
        self._setArray(10, value)

    @staticmethod
    def getChaptersType():
        return ChapterSimpleModel

    def getPostProgressionStatus(self):
        return PostProgressionStatus(self._getNumber(11))

    def setPostProgressionStatus(self, value):
        self._setNumber(11, value.value)

    def _initialize(self):
        super(PostProgressionViewModel, self)._initialize()
        self._addViewModelProperty('awardsWidget', AwardsWidgetModel())
        self._addNumberProperty('previousLevel', 0)
        self._addNumberProperty('currentLevel', 0)
        self._addNumberProperty('previousLevelPoints', 0)
        self._addNumberProperty('currentLevelPoints', 0)
        self._addNumberProperty('previousCyclesCompletedCount', 0)
        self._addNumberProperty('cyclesCompletedCount', 0)
        self._addNumberProperty('endDate', 0)
        self._addNumberProperty('chapterID', 0)
        self._addArrayProperty('levels', Array())
        self._addArrayProperty('chapters', Array())
        self._addNumberProperty('postProgressionStatus')
        self.onOpenPointsInfo = self._addCommand('onOpenPointsInfo')
        self.onOpenInfoPage = self._addCommand('onOpenInfoPage')
        self.onOpenChaptersBuyView = self._addCommand('onOpenChaptersBuyView')
        self.onClose = self._addCommand('onClose')
        self.onProgressAchieved = self._addCommand('onProgressAchieved')
        self.onCycleCompleted = self._addCommand('onCycleCompleted')
