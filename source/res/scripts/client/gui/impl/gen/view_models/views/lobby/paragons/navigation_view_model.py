# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/navigation_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.paragons.about_view_model import AboutViewModel
from gui.impl.gen.view_models.views.lobby.paragons.all_chapters.allChapters_view_model import AllChaptersViewModel
from gui.impl.gen.view_models.views.lobby.paragons.all_rewards.allrewards_view_model import AllrewardsViewModel
from gui.impl.gen.view_models.views.lobby.paragons.progression.progression_view_model import ProgressionViewModel

class TabId(IntEnum):
    PROGRESS = 0
    REWARDS = 1
    CHAPTERS = 2
    ABOUT = 3


class NavigationViewModel(ViewModel):
    __slots__ = ('onTabChange', 'onBack', 'onClose', 'onToChaptersView', 'onSelectChapter', 'onToChapterRewards')

    def __init__(self, properties=10, commands=6):
        super(NavigationViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def progression(self):
        return self._getViewModel(0)

    @staticmethod
    def getProgressionType():
        return ProgressionViewModel

    @property
    def allRewards(self):
        return self._getViewModel(1)

    @staticmethod
    def getAllRewardsType():
        return AllrewardsViewModel

    @property
    def allChapters(self):
        return self._getViewModel(2)

    @staticmethod
    def getAllChaptersType():
        return AllChaptersViewModel

    @property
    def about(self):
        return self._getViewModel(3)

    @staticmethod
    def getAboutType():
        return AboutViewModel

    def getHasNewProgress(self):
        return self._getBool(4)

    def setHasNewProgress(self, value):
        self._setBool(4, value)

    def getHasNewRewards(self):
        return self._getBool(5)

    def setHasNewRewards(self, value):
        self._setBool(5, value)

    def getHasNewChapters(self):
        return self._getBool(6)

    def setHasNewChapters(self, value):
        self._setBool(6, value)

    def getWasChapterSelected(self):
        return self._getBool(7)

    def setWasChapterSelected(self, value):
        self._setBool(7, value)

    def getCurrentTabId(self):
        return self._getNumber(8)

    def setCurrentTabId(self, value):
        self._setNumber(8, value)

    def getParagonPoints(self):
        return self._getNumber(9)

    def setParagonPoints(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(NavigationViewModel, self)._initialize()
        self._addViewModelProperty('progression', ProgressionViewModel())
        self._addViewModelProperty('allRewards', AllrewardsViewModel())
        self._addViewModelProperty('allChapters', AllChaptersViewModel())
        self._addViewModelProperty('about', AboutViewModel())
        self._addBoolProperty('hasNewProgress', False)
        self._addBoolProperty('hasNewRewards', False)
        self._addBoolProperty('hasNewChapters', False)
        self._addBoolProperty('wasChapterSelected', False)
        self._addNumberProperty('currentTabId', 0)
        self._addNumberProperty('paragonPoints', 0)
        self.onTabChange = self._addCommand('onTabChange')
        self.onBack = self._addCommand('onBack')
        self.onClose = self._addCommand('onClose')
        self.onToChaptersView = self._addCommand('onToChaptersView')
        self.onSelectChapter = self._addCommand('onSelectChapter')
        self.onToChapterRewards = self._addCommand('onToChapterRewards')
