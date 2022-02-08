# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/chapter_choice_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.chapter_model import ChapterModel

class ChapterChoiceViewModel(ViewModel):
    __slots__ = ('onPreviewClick', 'onChapterSelect', 'onAboutClick', 'onPointsInfoClick', 'onBuyClick', 'onBpbitClick', 'onBpcoinClick', 'onTakeRewardsClick', 'onViewLoaded', 'onClose')

    def __init__(self, properties=7, commands=10):
        super(ChapterChoiceViewModel, self).__init__(properties=properties, commands=commands)

    def getChapters(self):
        return self._getArray(0)

    def setChapters(self, value):
        self._setArray(0, value)

    def getBpbitCount(self):
        return self._getNumber(1)

    def setBpbitCount(self, value):
        self._setNumber(1, value)

    def getNotChosenRewardCount(self):
        return self._getNumber(2)

    def setNotChosenRewardCount(self, value):
        self._setNumber(2, value)

    def getBpcoinCount(self):
        return self._getNumber(3)

    def setBpcoinCount(self, value):
        self._setNumber(3, value)

    def getIsBattlePassCompleted(self):
        return self._getBool(4)

    def setIsBattlePassCompleted(self, value):
        self._setBool(4, value)

    def getIsChooseRewardsEnabled(self):
        return self._getBool(5)

    def setIsChooseRewardsEnabled(self, value):
        self._setBool(5, value)

    def getFreePoints(self):
        return self._getNumber(6)

    def setFreePoints(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(ChapterChoiceViewModel, self)._initialize()
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
