# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/friend_glade/ny_resources_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class State(Enum):
    AVAILABLE = 'Available'
    TIMER = 'Timer'
    NOTFAVORITE = 'NotFavorite'
    LIMIT = 'Limit'
    LIMITTIMER = 'LimitTimer'
    FINISHED = 'Finished'
    FINISHEDHIDDEN = 'FinishedHidden'


class NyResourcesViewModel(ViewModel):
    __slots__ = ('onCollect', 'onSetFavoriteFriend', 'onGoToFriends', 'onHideFinishedStatus')

    def __init__(self, properties=3, commands=4):
        super(NyResourcesViewModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getCooldown(self):
        return self._getNumber(1)

    def setCooldown(self, value):
        self._setNumber(1, value)

    def getCollectAmount(self):
        return self._getNumber(2)

    def setCollectAmount(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(NyResourcesViewModel, self)._initialize()
        self._addStringProperty('state', State.AVAILABLE.value)
        self._addNumberProperty('cooldown', 0)
        self._addNumberProperty('collectAmount', 0)
        self.onCollect = self._addCommand('onCollect')
        self.onSetFavoriteFriend = self._addCommand('onSetFavoriteFriend')
        self.onGoToFriends = self._addCommand('onGoToFriends')
        self.onHideFinishedStatus = self._addCommand('onHideFinishedStatus')
