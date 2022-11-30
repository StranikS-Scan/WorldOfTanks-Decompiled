# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/friend_challenge/friend_challenge_card_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class FriendChallengeType(Enum):
    TOURNAMENT = 'tournament'
    GUESTA = 'guest_A'
    GUESTM = 'guest_M'
    GUESTC = 'guest_cat'


class FriendChallengeCardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(FriendChallengeCardModel, self).__init__(properties=properties, commands=commands)

    def getChallengeType(self):
        return FriendChallengeType(self._getString(0))

    def setChallengeType(self, value):
        self._setString(0, value.value)

    def getCurrentQuantity(self):
        return self._getNumber(1)

    def setCurrentQuantity(self, value):
        self._setNumber(1, value)

    def getTotalQuantity(self):
        return self._getNumber(2)

    def setTotalQuantity(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(FriendChallengeCardModel, self)._initialize()
        self._addStringProperty('challengeType')
        self._addNumberProperty('currentQuantity', 0)
        self._addNumberProperty('totalQuantity', 0)
