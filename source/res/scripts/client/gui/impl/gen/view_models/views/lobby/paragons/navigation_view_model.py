# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/navigation_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.paragons.all_chapters.allChapters_view_model import AllChaptersViewModel
from gui.impl.gen.view_models.views.lobby.paragons.all_rewards.allrewards_view_model import AllrewardsViewModel
from gui.impl.gen.view_models.views.lobby.paragons.progression.progression_view_model import ProgressionViewModel

class TabId(IntEnum):
    PROGRESS = 0
    CHAPTERS = 2
    ABOUT = 3


class NavigationViewModel(ViewModel):
    __slots__ = ('onTabChange', 'onBack', 'onBackToSeasons', 'onClose', 'onToChaptersView', 'onSelectChapter', 'onToChapterRewards', 'onSeasonActivate')

    def __init__(self, properties=12, commands=8):
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

    def getHasNewProgress(self):
        return self._getBool(3)

    def setHasNewProgress(self, value):
        self._setBool(3, value)

    def getHasNewRewards(self):
        return self._getBool(4)

    def setHasNewRewards(self, value):
        self._setBool(4, value)

    def getHasNewChapters(self):
        return self._getBool(5)

    def setHasNewChapters(self, value):
        self._setBool(5, value)

    def getWasChapterSelected(self):
        return self._getBool(6)

    def setWasChapterSelected(self, value):
        self._setBool(6, value)

    def getCurrentTabId(self):
        return TabId(self._getNumber(7))

    def setCurrentTabId(self, value):
        self._setNumber(7, value.value)

    def getParagonPoints(self):
        return self._getNumber(8)

    def setParagonPoints(self, value):
        self._setNumber(8, value)

    def getNecessaryVehicleCount(self):
        return self._getNumber(9)

    def setNecessaryVehicleCount(self, value):
        self._setNumber(9, value)

    def getVehicleCount(self):
        return self._getNumber(10)

    def setVehicleCount(self, value):
        self._setNumber(10, value)

    def getPreviewSeasonId(self):
        return self._getNumber(11)

    def setPreviewSeasonId(self, value):
        self._setNumber(11, value)

    def _initialize(self):
        super(NavigationViewModel, self)._initialize()
        self._addViewModelProperty('progression', ProgressionViewModel())
        self._addViewModelProperty('allRewards', AllrewardsViewModel())
        self._addViewModelProperty('allChapters', AllChaptersViewModel())
        self._addBoolProperty('hasNewProgress', False)
        self._addBoolProperty('hasNewRewards', False)
        self._addBoolProperty('hasNewChapters', False)
        self._addBoolProperty('wasChapterSelected', False)
        self._addNumberProperty('currentTabId')
        self._addNumberProperty('paragonPoints', 0)
        self._addNumberProperty('necessaryVehicleCount', 0)
        self._addNumberProperty('vehicleCount', 0)
        self._addNumberProperty('previewSeasonId', 0)
        self.onTabChange = self._addCommand('onTabChange')
        self.onBack = self._addCommand('onBack')
        self.onBackToSeasons = self._addCommand('onBackToSeasons')
        self.onClose = self._addCommand('onClose')
        self.onToChaptersView = self._addCommand('onToChaptersView')
        self.onSelectChapter = self._addCommand('onSelectChapter')
        self.onToChapterRewards = self._addCommand('onToChapterRewards')
        self.onSeasonActivate = self._addCommand('onSeasonActivate')
