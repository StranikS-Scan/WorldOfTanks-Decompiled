# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/chapter_choice_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.chapter_model import ChapterModel

class ChapterChoiceViewModel(ViewModel):
    __slots__ = ('onPreviewClick', 'onChapterSelect', 'onAboutClick', 'onPointsInfoClick', 'onBuyClick', 'onViewLoaded', 'onClose', 'onShowPostProgression')

    def __init__(self, properties=5, commands=8):
        super(ChapterChoiceViewModel, self).__init__(properties=properties, commands=commands)

    def getChapters(self):
        return self._getArray(0)

    def setChapters(self, value):
        self._setArray(0, value)

    @staticmethod
    def getChaptersType():
        return ChapterModel

    def getFreePoints(self):
        return self._getNumber(1)

    def setFreePoints(self, value):
        self._setNumber(1, value)

    def getIsSeasonWithAdditionalBackground(self):
        return self._getBool(2)

    def setIsSeasonWithAdditionalBackground(self, value):
        self._setBool(2, value)

    def getSeasonNum(self):
        return self._getNumber(3)

    def setSeasonNum(self, value):
        self._setNumber(3, value)

    def getIsPostProgressionUnlocked(self):
        return self._getBool(4)

    def setIsPostProgressionUnlocked(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(ChapterChoiceViewModel, self)._initialize()
        self._addArrayProperty('chapters', Array())
        self._addNumberProperty('freePoints', 0)
        self._addBoolProperty('isSeasonWithAdditionalBackground', False)
        self._addNumberProperty('seasonNum', 0)
        self._addBoolProperty('isPostProgressionUnlocked', False)
        self.onPreviewClick = self._addCommand('onPreviewClick')
        self.onChapterSelect = self._addCommand('onChapterSelect')
        self.onAboutClick = self._addCommand('onAboutClick')
        self.onPointsInfoClick = self._addCommand('onPointsInfoClick')
        self.onBuyClick = self._addCommand('onBuyClick')
        self.onViewLoaded = self._addCommand('onViewLoaded')
        self.onClose = self._addCommand('onClose')
        self.onShowPostProgression = self._addCommand('onShowPostProgression')
