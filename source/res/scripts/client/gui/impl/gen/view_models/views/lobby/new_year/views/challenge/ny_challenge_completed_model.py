# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/ny_challenge_completed_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_progress_model import NewYearChallengeProgressModel

class NyChallengeCompletedModel(ViewModel):
    __slots__ = ('onStylePreview',)

    def __init__(self, properties=1, commands=1):
        super(NyChallengeCompletedModel, self).__init__(properties=properties, commands=commands)

    def getProgressRewards(self):
        return self._getArray(0)

    def setProgressRewards(self, value):
        self._setArray(0, value)

    @staticmethod
    def getProgressRewardsType():
        return NewYearChallengeProgressModel

    def _initialize(self):
        super(NyChallengeCompletedModel, self)._initialize()
        self._addArrayProperty('progressRewards', Array())
        self.onStylePreview = self._addCommand('onStylePreview')
