# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/tooltips/tournament_entry_point_tooltip_model.py
from enum import IntEnum
from comp7.gui.impl.gen.view_models.views.lobby.enums import TournamentName
from frameworks.wulf import ViewModel

class TournamentState(IntEnum):
    STARTINGSOON = 0
    LIVE = 1
    BETWEENSHOWMATCHES = 2
    FINISHED = 3


class TournamentEntryPointTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(TournamentEntryPointTooltipModel, self).__init__(properties=properties, commands=commands)

    def getTournamentName(self):
        return TournamentName(self._getString(0))

    def setTournamentName(self, value):
        self._setString(0, value.value)

    def getState(self):
        return TournamentState(self._getNumber(1))

    def setState(self, value):
        self._setNumber(1, value.value)

    def getTimeLeftUntilLiveMatch(self):
        return self._getNumber(2)

    def setTimeLeftUntilLiveMatch(self, value):
        self._setNumber(2, value)

    def getTimeLeftUntilNextShowMatchDay(self):
        return self._getNumber(3)

    def setTimeLeftUntilNextShowMatchDay(self, value):
        self._setNumber(3, value)

    def getStartTimestamp(self):
        return self._getNumber(4)

    def setStartTimestamp(self, value):
        self._setNumber(4, value)

    def getEndTimestamp(self):
        return self._getNumber(5)

    def setEndTimestamp(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(TournamentEntryPointTooltipModel, self)._initialize()
        self._addStringProperty('tournamentName')
        self._addNumberProperty('state')
        self._addNumberProperty('timeLeftUntilLiveMatch', 0)
        self._addNumberProperty('timeLeftUntilNextShowMatchDay', 0)
        self._addNumberProperty('startTimestamp', 0)
        self._addNumberProperty('endTimestamp', 0)
