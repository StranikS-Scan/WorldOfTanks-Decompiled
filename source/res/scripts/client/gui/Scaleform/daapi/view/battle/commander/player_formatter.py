# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/commander/player_formatter.py
from gui.battle_control.arena_info.player_format import PlayerFullNameFormatter
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from shared_utils import findFirst

def _isBot(vInfo):
    return vInfo.player.accountDBID == 0


class RTSPlayerNameFormatter(PlayerFullNameFormatter):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def format(self, vInfo, playerName=None):
        commanderInfo = findFirst(lambda vI: vI.isCommander() and vI.team == vInfo.team, self.__sessionProvider.getArenaDP().getVehiclesInfoIterator())
        if commanderInfo is not None and _isBot(vInfo):
            botPlayer = vInfo.player
            commanderPlayer = commanderInfo.player
            botPlayer.name = commanderPlayer.name
            botPlayer.fakeName = commanderPlayer.fakeName
            botPlayer.clanAbbrev = commanderPlayer.clanAbbrev
            botPlayer.igrType = commanderPlayer.igrType
        return super(RTSPlayerNameFormatter, self).format(vInfo)
