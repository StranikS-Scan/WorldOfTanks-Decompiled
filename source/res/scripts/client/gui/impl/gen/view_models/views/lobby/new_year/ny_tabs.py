# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/ny_tabs.py
from enum import Enum
from frameworks.wulf import ViewModel

class ChallengeViewTabs(Enum):
    TOURNAMENT = 'tournament'
    TOURNAMENTCOMPLETED = 'tournamentCompleted'
    GUESTA = 'guestA'
    GUESTM = 'guestM'
    GUESTC = 'guestC'
    HEADQUARTERS = 'headquarters'
    GUESTD = 'guestD'


class GladeViewTabs(Enum):
    TOWN = 'Town'
    FIR = 'Fir'
    FAIR = 'Fair'
    INSTALLATION = 'Installation'
    RESOURCES = 'Resources'


class FriendGladeViewTabs(Enum):
    TOWN = 'FriendTown'
    FIR = 'FriendFir'
    FAIR = 'FriendFair'
    INSTALLATION = 'FriendInstallation'
    RESOURCES = 'FriendResources'


class NyTabs(ViewModel):
    __slots__ = ()

    def __init__(self, properties=0, commands=0):
        super(NyTabs, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(NyTabs, self)._initialize()
