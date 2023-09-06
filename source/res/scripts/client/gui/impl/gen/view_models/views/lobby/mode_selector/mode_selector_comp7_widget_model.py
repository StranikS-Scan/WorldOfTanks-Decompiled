# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_comp7_widget_model.py
from enum import IntEnum
from gui.impl.gen.view_models.views.lobby.comp7.division_info_model import DivisionInfoModel
from gui.impl.gen.view_models.views.lobby.comp7.qualification_model import QualificationModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_base_widget_model import ModeSelectorBaseWidgetModel

class Rank(IntEnum):
    FIRST = 6
    SECOND = 5
    THIRD = 4
    FOURTH = 3
    FIFTH = 2
    SIXTH = 1


class ModeSelectorComp7WidgetModel(ModeSelectorBaseWidgetModel):
    __slots__ = ('onOpenMeta',)

    def __init__(self, properties=9, commands=1):
        super(ModeSelectorComp7WidgetModel, self).__init__(properties=properties, commands=commands)

    @property
    def divisionInfo(self):
        return self._getViewModel(1)

    @staticmethod
    def getDivisionInfoType():
        return DivisionInfoModel

    @property
    def qualificationModel(self):
        return self._getViewModel(2)

    @staticmethod
    def getQualificationModelType():
        return QualificationModel

    def getRank(self):
        return Rank(self._getNumber(3))

    def setRank(self, value):
        self._setNumber(3, value.value)

    def getCurrentScore(self):
        return self._getNumber(4)

    def setCurrentScore(self, value):
        self._setNumber(4, value)

    def getPrevScore(self):
        return self._getNumber(5)

    def setPrevScore(self, value):
        self._setNumber(5, value)

    def getTopPercentage(self):
        return self._getNumber(6)

    def setTopPercentage(self, value):
        self._setNumber(6, value)

    def getRankInactivityCount(self):
        return self._getNumber(7)

    def setRankInactivityCount(self, value):
        self._setNumber(7, value)

    def getHasRankInactivityWarning(self):
        return self._getBool(8)

    def setHasRankInactivityWarning(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(ModeSelectorComp7WidgetModel, self)._initialize()
        self._addViewModelProperty('divisionInfo', DivisionInfoModel())
        self._addViewModelProperty('qualificationModel', QualificationModel())
        self._addNumberProperty('rank')
        self._addNumberProperty('currentScore', 0)
        self._addNumberProperty('prevScore', 0)
        self._addNumberProperty('topPercentage', 0)
        self._addNumberProperty('rankInactivityCount', -1)
        self._addBoolProperty('hasRankInactivityWarning', False)
        self.onOpenMeta = self._addCommand('onOpenMeta')
