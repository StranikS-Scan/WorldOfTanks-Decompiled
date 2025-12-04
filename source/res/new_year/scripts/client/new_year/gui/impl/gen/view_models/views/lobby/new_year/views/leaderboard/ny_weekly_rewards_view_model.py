# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/leaderboard/ny_weekly_rewards_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.leaderboard.ny_stage_model import NyStageModel

class NyWeeklyRewardsViewModel(ViewModel):
    __slots__ = ('onClose', 'onInfoClick', 'onPreviewClick', 'onTabSelected')

    def __init__(self, properties=2, commands=4):
        super(NyWeeklyRewardsViewModel, self).__init__(properties=properties, commands=commands)

    def getCurrentStage(self):
        return self._getNumber(0)

    def setCurrentStage(self, value):
        self._setNumber(0, value)

    def getStages(self):
        return self._getArray(1)

    def setStages(self, value):
        self._setArray(1, value)

    @staticmethod
    def getStagesType():
        return NyStageModel

    def _initialize(self):
        super(NyWeeklyRewardsViewModel, self)._initialize()
        self._addNumberProperty('currentStage', 0)
        self._addArrayProperty('stages', Array())
        self.onClose = self._addCommand('onClose')
        self.onInfoClick = self._addCommand('onInfoClick')
        self.onPreviewClick = self._addCommand('onPreviewClick')
        self.onTabSelected = self._addCommand('onTabSelected')
