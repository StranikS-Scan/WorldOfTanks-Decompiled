# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/achievements/views/achievements_main_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.achievements.views.summary.summary_view_model import SummaryViewModel

class AchievementsViews(IntEnum):
    SUMMARY = 0


class AchievementsMainViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=3, commands=1):
        super(AchievementsMainViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def summaryModel(self):
        return self._getViewModel(0)

    @staticmethod
    def getSummaryModelType():
        return SummaryViewModel

    def getViewType(self):
        return AchievementsViews(self._getNumber(1))

    def setViewType(self, value):
        self._setNumber(1, value.value)

    def getIsOtherPlayer(self):
        return self._getBool(2)

    def setIsOtherPlayer(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(AchievementsMainViewModel, self)._initialize()
        self._addViewModelProperty('summaryModel', SummaryViewModel())
        self._addNumberProperty('viewType')
        self._addBoolProperty('isOtherPlayer', False)
        self.onClose = self._addCommand('onClose')
