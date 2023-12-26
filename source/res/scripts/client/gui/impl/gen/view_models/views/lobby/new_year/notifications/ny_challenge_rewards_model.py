# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/notifications/ny_challenge_rewards_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.new_year.notifications.receiving_rewards_model import ReceivingRewardsModel

class Type(Enum):
    CHALLENGE = 'challenge'
    QUEST = 'quest'


class NyChallengeRewardsModel(ReceivingRewardsModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=4):
        super(NyChallengeRewardsModel, self).__init__(properties=properties, commands=commands)

    def getCompletedQuestsQuantity(self):
        return self._getNumber(5)

    def setCompletedQuestsQuantity(self, value):
        self._setNumber(5, value)

    def getTotalQuestsQuantity(self):
        return self._getNumber(6)

    def setTotalQuestsQuantity(self, value):
        self._setNumber(6, value)

    def getType(self):
        return Type(self._getString(7))

    def setType(self, value):
        self._setString(7, value.value)

    def getCelebrity(self):
        return self._getString(8)

    def setCelebrity(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(NyChallengeRewardsModel, self)._initialize()
        self._addNumberProperty('completedQuestsQuantity', 0)
        self._addNumberProperty('totalQuestsQuantity', 0)
        self._addStringProperty('type', Type.CHALLENGE.value)
        self._addStringProperty('celebrity', '')
