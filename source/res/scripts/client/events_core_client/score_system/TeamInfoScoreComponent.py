# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/events_core_client/score_system/TeamInfoScoreComponent.py
import typing
import BigWorld
from events_core_client.score_system.PlayerInfoScoreComponent import PlayerInfoScoreComponent
if typing.TYPE_CHECKING:
    from typing import Optional

def getTeamInfoScoreComponent():
    player = BigWorld.player()
    if player and player.arena is not None:
        teamInfo = player.arena.teamInfo
        if teamInfo:
            return teamInfo.dynamicComponents.get('teamInfoScoreComponent', None)
    return


class TeamInfoScoreComponent(PlayerInfoScoreComponent):
    pass
