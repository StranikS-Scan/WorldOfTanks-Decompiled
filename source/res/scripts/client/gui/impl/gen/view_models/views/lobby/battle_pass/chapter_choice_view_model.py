# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/chapter_choice_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.chapter_model import ChapterModel
from gui.impl.gen.view_models.views.lobby.battle_pass.collection_entry_point_view_model import CollectionEntryPointViewModel

class ChapterChoiceViewModel(ViewModel):
    __slots__ = ('onPreviewClick', 'onChapterSelect', 'onAboutClick', 'onPointsInfoClick', 'onBuyClick', 'onBpbitClick', 'onBpcoinClick', 'onTakeRewardsClick', 'onViewLoaded', 'onClose')

    def __init__(self, properties=8, commands=10):
        super(ChapterChoiceViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def collectionEntryPoint(self):
        return self._getViewModel(0)

    @staticmethod
    def getCollectionEntryPointType():
        return CollectionEntryPointViewModel

    def getChapters(self):
        return self._getArray(1)

    def setChapters(self, value):
        self._setArray(1, value)

    @staticmethod
    def getChaptersType():
        return ChapterModel

    def getBpbitCount(self):
        return self._getNumber(2)

    def setBpbitCount(self, value):
        self._setNumber(2, value)

    def getNotChosenRewardCount(self):
        return self._getNumber(3)

    def setNotChosenRewardCount(self, value):
        self._setNumber(3, value)

    def getBpcoinCount(self):
        return self._getNumber(4)

    def setBpcoinCount(self, value):
        self._setNumber(4, value)

    def getIsBattlePassCompleted(self):
        return self._getBool(5)

    def setIsBattlePassCompleted(self, value):
        self._setBool(5, value)

    def getIsChooseRewardsEnabled(self):
        return self._getBool(6)

    def setIsChooseRewardsEnabled(self, value):
        self._setBool(6, value)

    def getFreePoints(self):
        return self._getNumber(7)

    def setFreePoints(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(ChapterChoiceViewModel, self)._initialize()
        self._addViewModelProperty('collectionEntryPoint', CollectionEntryPointViewModel())
        self._addArrayProperty('chapters', Array())
        self._addNumberProperty('bpbitCount', 0)
        self._addNumberProperty('notChosenRewardCount', 0)
        self._addNumberProperty('bpcoinCount', 0)
        self._addBoolProperty('isBattlePassCompleted', False)
        self._addBoolProperty('isChooseRewardsEnabled', True)
        self._addNumberProperty('freePoints', 0)
        self.onPreviewClick = self._addCommand('onPreviewClick')
        self.onChapterSelect = self._addCommand('onChapterSelect')
        self.onAboutClick = self._addCommand('onAboutClick')
        self.onPointsInfoClick = self._addCommand('onPointsInfoClick')
        self.onBuyClick = self._addCommand('onBuyClick')
        self.onBpbitClick = self._addCommand('onBpbitClick')
        self.onBpcoinClick = self._addCommand('onBpcoinClick')
        self.onTakeRewardsClick = self._addCommand('onTakeRewardsClick')
        self.onViewLoaded = self._addCommand('onViewLoaded')
        self.onClose = self._addCommand('onClose')
