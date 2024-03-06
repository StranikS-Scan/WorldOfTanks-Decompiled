# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/chapter_choice_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.awards_widget_model import AwardsWidgetModel
from gui.impl.gen.view_models.views.lobby.battle_pass.chapter_model import ChapterModel

class ChapterChoiceViewModel(ViewModel):
    __slots__ = ('onPreviewClick', 'onChapterSelect', 'onAboutClick', 'onPointsInfoClick', 'onBuyClick', 'onViewLoaded', 'onClose')

    def __init__(self, properties=5, commands=7):
        super(ChapterChoiceViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def awardsWidget(self):
        return self._getViewModel(0)

    @staticmethod
    def getAwardsWidgetType():
        return AwardsWidgetModel

    def getChapters(self):
        return self._getArray(1)

    def setChapters(self, value):
        self._setArray(1, value)

    @staticmethod
    def getChaptersType():
        return ChapterModel

    def getFreePoints(self):
        return self._getNumber(2)

    def setFreePoints(self, value):
        self._setNumber(2, value)

    def getIsCustomSeason(self):
        return self._getBool(3)

    def setIsCustomSeason(self, value):
        self._setBool(3, value)

    def getSeasonNum(self):
        return self._getNumber(4)

    def setSeasonNum(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(ChapterChoiceViewModel, self)._initialize()
        self._addViewModelProperty('awardsWidget', AwardsWidgetModel())
        self._addArrayProperty('chapters', Array())
        self._addNumberProperty('freePoints', 0)
        self._addBoolProperty('isCustomSeason', False)
        self._addNumberProperty('seasonNum', 0)
        self.onPreviewClick = self._addCommand('onPreviewClick')
        self.onChapterSelect = self._addCommand('onChapterSelect')
        self.onAboutClick = self._addCommand('onAboutClick')
        self.onPointsInfoClick = self._addCommand('onPointsInfoClick')
        self.onBuyClick = self._addCommand('onBuyClick')
        self.onViewLoaded = self._addCommand('onViewLoaded')
        self.onClose = self._addCommand('onClose')
