# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/shared/utils.py
from __future__ import absolute_import
import BigWorld
from helpers import isPlayerAvatar

def getScoreComponent():
    player = BigWorld.player()
    return None if not (player and isPlayerAvatar() and player.arena and player.arena.arenaInfo) else player.arena.arenaInfo.dynamicComponents.get('FortRushScoreComponent')
