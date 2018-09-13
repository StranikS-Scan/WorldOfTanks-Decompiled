# Embedded file name: scripts/client/gui/battle_control/avatar_getter.py
import BigWorld

def isForcedGuiControlMode():
    return getattr(BigWorld.player(), 'isForcedGuiControlMode', False)


def isVehicleAlive():
    return getattr(BigWorld.player(), 'isVehicleAlive', False)


def getSoundNotifications():
    return getattr(BigWorld.player(), 'soundNotifications', None)


def isPlayerOnArena():
    return getattr(BigWorld.player(), 'isOnArena', False)


def getInputHandler():
    return getattr(BigWorld.player(), 'inputHandler', None)


def getArena():
    return getattr(BigWorld.player(), 'arena', None)
