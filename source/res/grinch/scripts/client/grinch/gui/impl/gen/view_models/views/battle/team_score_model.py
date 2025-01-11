# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/impl/gen/view_models/views/battle/team_score_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class TeamColorEnum(Enum):
    YELLOW = 'yellow'
    BLUE = 'blue'
    MAGENTA = 'magenta'
    NEUTRAL = 'neutral'


class TeamScoreModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(TeamScoreModel, self).__init__(properties=properties, commands=commands)

    def getTeam(self):
        return self._getNumber(0)

    def setTeam(self, value):
        self._setNumber(0, value)

    def getTeamColor(self):
        return TeamColorEnum(self._getString(1))

    def setTeamColor(self, value):
        self._setString(1, value.value)

    def getScore(self):
        return self._getNumber(2)

    def setScore(self, value):
        self._setNumber(2, value)

    def getScoreLimit(self):
        return self._getNumber(3)

    def setScoreLimit(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(TeamScoreModel, self)._initialize()
        self._addNumberProperty('team', 0)
        self._addStringProperty('teamColor', TeamColorEnum.YELLOW.value)
        self._addNumberProperty('score', 0)
        self._addNumberProperty('scoreLimit', 0)
