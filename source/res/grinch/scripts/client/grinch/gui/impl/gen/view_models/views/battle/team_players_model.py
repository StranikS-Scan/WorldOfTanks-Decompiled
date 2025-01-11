# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/impl/gen/view_models/views/battle/team_players_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from grinch.gui.impl.gen.view_models.views.battle.grinch_player_model import GrinchPlayerModel

class TeamColorEnum(Enum):
    YELLOW = 'yellow'
    BLUE = 'blue'
    MAGENTA = 'magenta'
    NEUTRAL = 'neutral'


class TeamPlayersModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(TeamPlayersModel, self).__init__(properties=properties, commands=commands)

    def getPlayers(self):
        return self._getArray(0)

    def setPlayers(self, value):
        self._setArray(0, value)

    @staticmethod
    def getPlayersType():
        return GrinchPlayerModel

    def getTeamColor(self):
        return TeamColorEnum(self._getString(1))

    def setTeamColor(self, value):
        self._setString(1, value.value)

    def _initialize(self):
        super(TeamPlayersModel, self)._initialize()
        self._addArrayProperty('players', Array())
        self._addStringProperty('teamColor', TeamColorEnum.YELLOW.value)
