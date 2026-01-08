# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/tournaments/match_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from comp7.gui.impl.gen.view_models.views.lobby.tournaments.team_model import TeamModel

class MatchState(Enum):
    NOTSTARTED = 'notStarted'
    COMPLETED = 'completed'
    LIVE = 'live'


class MatchStage(Enum):
    ROUNDROBIN = 'roundRobin'
    UBSEMIFINALS = 'UBSemifinals'
    UBFINALS = 'UBFinals'
    LBROUND1 = 'LBRound1'
    LBROUND2 = 'LBRound2'
    LBSEMIFINALS = 'LBSemifinals'
    LBFINALS = 'LBFinals'
    GRANDFINALS = 'grandFinals'


class MatchModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(MatchModel, self).__init__(properties=properties, commands=commands)

    @property
    def team1(self):
        return self._getViewModel(0)

    @staticmethod
    def getTeam1Type():
        return TeamModel

    @property
    def team2(self):
        return self._getViewModel(1)

    @staticmethod
    def getTeam2Type():
        return TeamModel

    def getStartOfMatchTimestamp(self):
        return self._getNumber(2)

    def setStartOfMatchTimestamp(self, value):
        self._setNumber(2, value)

    def getMatchStage(self):
        return MatchStage(self._getString(3))

    def setMatchStage(self, value):
        self._setString(3, value.value)

    def getBestOf(self):
        return self._getNumber(4)

    def setBestOf(self, value):
        self._setNumber(4, value)

    def getPhase(self):
        return self._getNumber(5)

    def setPhase(self, value):
        self._setNumber(5, value)

    def getRound(self):
        return self._getNumber(6)

    def setRound(self, value):
        self._setNumber(6, value)

    def getMatchState(self):
        return MatchState(self._getString(7))

    def setMatchState(self, value):
        self._setString(7, value.value)

    def _initialize(self):
        super(MatchModel, self)._initialize()
        self._addViewModelProperty('team1', TeamModel())
        self._addViewModelProperty('team2', TeamModel())
        self._addNumberProperty('startOfMatchTimestamp', 0)
        self._addStringProperty('matchStage')
        self._addNumberProperty('bestOf', 0)
        self._addNumberProperty('phase', 0)
        self._addNumberProperty('round', 0)
        self._addStringProperty('matchState')
