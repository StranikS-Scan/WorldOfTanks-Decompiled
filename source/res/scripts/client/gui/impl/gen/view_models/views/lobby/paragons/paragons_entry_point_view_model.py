# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/paragons_entry_point_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.paragons.common.chapter_model import ChapterModel

class ProgressState(Enum):
    ACTIVE = 'active'
    CHAPTERNOTCHOSEN = 'chapterNotChosen'
    ALLCHAPTERSCOMPLETED = 'allChaptersCompleted'
    PAUSED = 'paused'


class ParagonsEntryPointViewModel(ViewModel):
    __slots__ = ('onEntryPointClick',)

    def __init__(self, properties=4, commands=1):
        super(ParagonsEntryPointViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def currentChapter(self):
        return self._getViewModel(0)

    @staticmethod
    def getCurrentChapterType():
        return ChapterModel

    def getIsAnySelectableReward(self):
        return self._getBool(1)

    def setIsAnySelectableReward(self, value):
        self._setBool(1, value)

    def getIsAnySelectableRewardInInventory(self):
        return self._getBool(2)

    def setIsAnySelectableRewardInInventory(self, value):
        self._setBool(2, value)

    def getProgressState(self):
        return ProgressState(self._getString(3))

    def setProgressState(self, value):
        self._setString(3, value.value)

    def _initialize(self):
        super(ParagonsEntryPointViewModel, self)._initialize()
        self._addViewModelProperty('currentChapter', ChapterModel())
        self._addBoolProperty('isAnySelectableReward', False)
        self._addBoolProperty('isAnySelectableRewardInInventory', False)
        self._addStringProperty('progressState', ProgressState.ACTIVE.value)
        self.onEntryPointClick = self._addCommand('onEntryPointClick')
