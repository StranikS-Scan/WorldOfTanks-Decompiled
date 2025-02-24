# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/server_side_replay/gui/impl/gen/view_models/views/lobby/top_replay_model.py
from enum import Enum
from server_side_replay.gui.impl.gen.view_models.views.lobby.replay_model import ReplayModel

class StatParams(Enum):
    EARNEDXP = 'earnedXp'
    DAMAGEDEALT = 'damageDealt'
    DAMAGEASSISTED = 'damageAssisted'
    DAMAGEBLOCKEDBYARMOR = 'damageBlockedByArmor'
    KILLS = 'kills'
    MARKSOFMASTERY = 'marksOfMastery'
    DATE = 'date'


class TopReplayModel(ReplayModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
        super(TopReplayModel, self).__init__(properties=properties, commands=commands)

    def getParam(self):
        return StatParams(self._getString(13))

    def setParam(self, value):
        self._setString(13, value.value)

    def _initialize(self):
        super(TopReplayModel, self)._initialize()
        self._addStringProperty('param', StatParams.EARNEDXP.value)
