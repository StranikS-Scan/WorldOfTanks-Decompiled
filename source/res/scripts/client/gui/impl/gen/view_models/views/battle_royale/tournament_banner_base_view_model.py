# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/tournament_banner_base_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class TournamentState(Enum):
    BEFORETOURNAMENT = 'beforeTournament'
    ACTIVETOURNAMENT = 'activeTournament'
    AFTERTOURNAMENT = 'afterTournament'
    ANNOUNCEMENTSTREAM = 'announcementStream'
    ACTIVESTREAM = 'activeStream'


class TournamentBannerBaseViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(TournamentBannerBaseViewModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return TournamentState(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getDateStart(self):
        return self._getNumber(1)

    def setDateStart(self, value):
        self._setNumber(1, value)

    def getDateEnd(self):
        return self._getNumber(2)

    def setDateEnd(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(TournamentBannerBaseViewModel, self)._initialize()
        self._addStringProperty('state')
        self._addNumberProperty('dateStart', 0)
        self._addNumberProperty('dateEnd', 0)
