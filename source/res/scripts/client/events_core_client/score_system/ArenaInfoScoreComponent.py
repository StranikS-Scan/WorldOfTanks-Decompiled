# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/events_core_client/score_system/ArenaInfoScoreComponent.py
import typing
import BigWorld
from events_core_client.score_system.PlayerInfoScoreComponent import PlayerInfoScoreComponent
if typing.TYPE_CHECKING:
    from typing import Optional

def getArenaInfoScoreComponent():
    player = BigWorld.player()
    if player and player.arena is not None:
        arenaInfo = player.arena.arenaInfo
        if arenaInfo:
            return arenaInfo.dynamicComponents.get('arenaInfoScoreComponent', None)
    return


class ArenaInfoScoreComponent(PlayerInfoScoreComponent):
    pass
