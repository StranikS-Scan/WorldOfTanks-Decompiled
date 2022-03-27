# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/commander/cursor.py
import BattleReplay
import BigWorld
import GUI
from AvatarInputHandler import cameras

def getMousePositionOnTerrain():
    direction, start = cameras.getWorldRayAndPoint(*getRTSMCursorPosition())
    collideResult = BigWorld.wg_collideSegment(BigWorld.player().spaceID, start, start + direction * 10000.0, 119)
    return collideResult.closestPoint if collideResult is not None else None


def getRTSMCursorPosition():
    replayCtrl = BattleReplay.g_replayCtrl
    return replayCtrl.mouseCursor.position if replayCtrl.isPlaying else GUI.mcursor().position
