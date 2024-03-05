# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/lobby/rewards_view/rewards_view_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class RewardsViewModel(ViewModel):
    __slots__ = ('onCloseButtonClick', 'onContinueButtonClick')

    def __init__(self, properties=6, commands=2):
        super(RewardsViewModel, self).__init__(properties=properties, commands=commands)

    def getSubtitle(self):
        return self._getResource(0)

    def setSubtitle(self, value):
        self._setResource(0, value)

    def getTitle(self):
        return self._getResource(1)

    def setTitle(self, value):
        self._setResource(1, value)

    def getInfoText(self):
        return self._getResource(2)

    def setInfoText(self, value):
        self._setResource(2, value)

    def getDisplayRewardsCount(self):
        return self._getBool(3)

    def setDisplayRewardsCount(self, value):
        self._setBool(3, value)

    def getProgressionStage(self):
        return self._getNumber(4)

    def setProgressionStage(self, value):
        self._setNumber(4, value)

    def getRewards(self):
        return self._getArray(5)

    def setRewards(self, value):
        self._setArray(5, value)

    @staticmethod
    def getRewardsType():
        return BonusModel

    def _initialize(self):
        super(RewardsViewModel, self)._initialize()
        self._addResourceProperty('subtitle', R.invalid())
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('infoText', R.invalid())
        self._addBoolProperty('displayRewardsCount', False)
        self._addNumberProperty('progressionStage', 0)
        self._addArrayProperty('rewards', Array())
        self.onCloseButtonClick = self._addCommand('onCloseButtonClick')
        self.onContinueButtonClick = self._addCommand('onContinueButtonClick')
