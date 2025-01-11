# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/notifications/ny_challenge_rewards_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.new_year.notifications.receiving_rewards_model import ReceivingRewardsModel

class Type(Enum):
    CHALLENGE = 'challenge'
    QUEST = 'quest'


class NyChallengeRewardsModel(ReceivingRewardsModel):
    __slots__ = ('onGoToExterior', 'onGoToGarage')

    def __init__(self, properties=13, commands=6):
        super(NyChallengeRewardsModel, self).__init__(properties=properties, commands=commands)

    def getCompletedQuestsQuantity(self):
        return self._getNumber(6)

    def setCompletedQuestsQuantity(self, value):
        self._setNumber(6, value)

    def getTotalQuestsQuantity(self):
        return self._getNumber(7)

    def setTotalQuestsQuantity(self, value):
        self._setNumber(7, value)

    def getQuestsQuantity(self):
        return self._getNumber(8)

    def setQuestsQuantity(self, value):
        self._setNumber(8, value)

    def getOtherBonusCount(self):
        return self._getNumber(9)

    def setOtherBonusCount(self, value):
        self._setNumber(9, value)

    def getIsFirstAttach(self):
        return self._getBool(10)

    def setIsFirstAttach(self, value):
        self._setBool(10, value)

    def getType(self):
        return Type(self._getString(11))

    def setType(self, value):
        self._setString(11, value.value)

    def getCelebrity(self):
        return self._getString(12)

    def setCelebrity(self, value):
        self._setString(12, value)

    def _initialize(self):
        super(NyChallengeRewardsModel, self)._initialize()
        self._addNumberProperty('completedQuestsQuantity', 0)
        self._addNumberProperty('totalQuestsQuantity', 0)
        self._addNumberProperty('questsQuantity', 0)
        self._addNumberProperty('otherBonusCount', 0)
        self._addBoolProperty('isFirstAttach', False)
        self._addStringProperty('type', Type.CHALLENGE.value)
        self._addStringProperty('celebrity', '')
        self.onGoToExterior = self._addCommand('onGoToExterior')
        self.onGoToGarage = self._addCommand('onGoToGarage')
