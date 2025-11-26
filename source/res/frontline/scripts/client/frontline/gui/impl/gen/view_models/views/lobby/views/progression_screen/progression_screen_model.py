# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/progression_screen/progression_screen_model.py
from frameworks.wulf import Array, ViewModel
from frontline.gui.impl.gen.view_models.views.lobby.views.progression_screen.tiers_section_model import TiersSectionModel

class ProgressionScreenModel(ViewModel):
    __slots__ = ('onClaimRewards', 'onClose')

    def __init__(self, properties=9, commands=2):
        super(ProgressionScreenModel, self).__init__(properties=properties, commands=commands)

    def getFrontlineState(self):
        return self._getString(0)

    def setFrontlineState(self, value):
        self._setString(0, value)

    def getCountdownSeconds(self):
        return self._getNumber(1)

    def setCountdownSeconds(self, value):
        self._setNumber(1, value)

    def getLevel(self):
        return self._getNumber(2)

    def setLevel(self, value):
        self._setNumber(2, value)

    def getIsMaxLevel(self):
        return self._getBool(3)

    def setIsMaxLevel(self, value):
        self._setBool(3, value)

    def getCurrentPoints(self):
        return self._getNumber(4)

    def setCurrentPoints(self, value):
        self._setNumber(4, value)

    def getNeededPoints(self):
        return self._getNumber(5)

    def setNeededPoints(self, value):
        self._setNumber(5, value)

    def getAmountRewardsToClaim(self):
        return self._getNumber(6)

    def setAmountRewardsToClaim(self, value):
        self._setNumber(6, value)

    def getAreRewardsJustEarned(self):
        return self._getBool(7)

    def setAreRewardsJustEarned(self, value):
        self._setBool(7, value)

    def getTiersSections(self):
        return self._getArray(8)

    def setTiersSections(self, value):
        self._setArray(8, value)

    @staticmethod
    def getTiersSectionsType():
        return TiersSectionModel

    def _initialize(self):
        super(ProgressionScreenModel, self)._initialize()
        self._addStringProperty('frontlineState', '')
        self._addNumberProperty('countdownSeconds', 0)
        self._addNumberProperty('level', 0)
        self._addBoolProperty('isMaxLevel', False)
        self._addNumberProperty('currentPoints', 0)
        self._addNumberProperty('neededPoints', 0)
        self._addNumberProperty('amountRewardsToClaim', 0)
        self._addBoolProperty('areRewardsJustEarned', False)
        self._addArrayProperty('tiersSections', Array())
        self.onClaimRewards = self._addCommand('onClaimRewards')
        self.onClose = self._addCommand('onClose')
