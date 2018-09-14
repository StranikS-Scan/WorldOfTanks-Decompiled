# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/avatar_getter.py
import BigWorld
import Math
from gui import GUI_CTRL_MODE_FLAG
from debug_utils import LOG_WARNING, LOG_CURRENT_EXCEPTION

def isForcedGuiControlMode(avatar=None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        result = avatar.isForcedGuiControlMode()
    except AttributeError:
        LOG_WARNING('Attribute "isForcedGuiControlMode" is not found')
        result = False

    return result


def getForcedGuiControlModeFlags(avatar=None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        result = avatar.getForcedGuiControlModeFlags()
    except AttributeError:
        LOG_WARNING('Attribute "getForcedGuiControlModeFlags" is not found')
        result = 0

    return result


def setForcedGuiControlMode(value, stopVehicle=False, enableAiming=True, cursorVisible=True):
    if value:
        flags = GUI_CTRL_MODE_FLAG.CURSOR_ATTACHED
        if stopVehicle:
            flags |= GUI_CTRL_MODE_FLAG.MOVING_DISABLED
        if enableAiming:
            flags |= GUI_CTRL_MODE_FLAG.AIMING_ENABLED
        if cursorVisible:
            flags |= GUI_CTRL_MODE_FLAG.CURSOR_VISIBLE
    else:
        flags = GUI_CTRL_MODE_FLAG.CURSOR_DETACHED
    try:
        return BigWorld.player().setForcedGuiControlMode(flags)
    except AttributeError:
        LOG_CURRENT_EXCEPTION()
        return False


def getPlayerName(avatar=None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        result = avatar.name
    except AttributeError:
        LOG_WARNING('Attribute "name" is not found')
        result = ''

    return result


def getPlayerTeam(avatar=None):
    if avatar is None:
        avatar = BigWorld.player()
    return getattr(avatar, 'team', 0)


def getPlayerVehicleID(avatar=None):
    if avatar is None:
        avatar = BigWorld.player()
    return getattr(avatar, 'playerVehicleID', 0)


def isPlayerTeamKillSuspected():
    return bool(getattr(BigWorld.player(), 'tkillIsSuspected', 0))


def isVehicleAlive(avatar=None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        result = avatar.isVehicleAlive
    except AttributeError:
        LOG_WARNING('Attribute "isVehicleAlive" is not found')
        result = False

    return result


def isVehicleOverturned(avatar=None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        result = avatar.isVehicleOverturned
    except AttributeError:
        LOG_WARNING('Attribute "isVehicleOverturned" is not found')
        result = False

    return result


def isVehicleBarrelUnderWater(avatar=None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        result = avatar.isOwnBarrelUnderWater
    except AttributeError:
        LOG_WARNING('Attribute "isOwnBarrelUnderWater" is not found')
        result = False

    return result


def isVehicleInFire(avatar=None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        result = avatar.fireInVehicle
    except AttributeError:
        LOG_WARNING('Attribute "fireInVehicle" is not found')
        result = False

    return result


def getVehicleDeviceStates(avatar=None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        result = avatar.deviceStates
    except AttributeError:
        LOG_WARNING('Attribute "deviceStates" is not found')
        result = {}

    return result


def getVehicleTypeDescriptor(avatar=None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        result = avatar.vehicleTypeDescriptor
    except AttributeError:
        LOG_WARNING('Attribute "vehicleTypeDescriptor" is not found')
        result = None

    return result


def getVehicleExtrasDict(avatar=None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        result = avatar.vehicleTypeDescriptor.extrasDict
    except AttributeError:
        LOG_WARNING('Attribute "vehicleTypeDescriptor.extrasDict" is not found')
        result = {}

    return result


def getSoundNotifications(avatar=None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        result = avatar.soundNotifications
    except AttributeError:
        LOG_WARNING('Attribute "soundNotifications" is not found')
        result = None

    return result


def isPlayerOnArena(avatar=None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        result = avatar.isOnArena
    except AttributeError:
        LOG_WARNING('Attribute "isOnArena" is not found')
        result = False

    return result


def getInputHandler(avatar=None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        result = avatar.inputHandler
    except AttributeError:
        LOG_WARNING('Attribute "inputHandler" is not found')
        result = None

    return result


def getArena(avatar=None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        result = avatar.arena
    except AttributeError:
        LOG_WARNING('Attribute "arena" is not found')
        result = None

    return result


def getArenaUniqueID(avatar=None):
    try:
        return getArena(avatar).arenaUniqueID
    except AttributeError:
        LOG_WARNING('Attribute "arenaUniqueID" is not found')

    return None


def updateVehicleSetting(code, value, avatar=None):
    if avatar is None:
        avatar = BigWorld.player()
    vehicleid = avatar.playerVehicleID
    if avatar.getVehicleAttached() is not None:
        vehicleid = avatar.getVehicleAttached().id
    try:
        avatar.updateVehicleSetting(vehicleid, code, value)
    except AttributeError:
        LOG_CURRENT_EXCEPTION()
        LOG_WARNING('Attribute "updateVehicleSetting" is not found')

    return


def changeVehicleSetting(code, value, avatar=None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        avatar.base.vehicle_changeSetting(code, value)
    except AttributeError:
        LOG_WARNING('Attribute "base.vehicle_changeSetting" is not found')

    return


def activateAvatarEquipment(equipmentID, avatar=None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        avatar.cell.activateEquipment(equipmentID)
    except AttributeError:
        LOG_WARNING('Attribute "cell.activateEquipment" is not found')

    return


def leaveArena(avatar=None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        avatar.leaveArena()
    except AttributeError:
        LOG_WARNING('Attribute "leaveArena" is not found', avatar)

    return


def switchToOtherPlayer(vehicleID, avatar=None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        avatar.selectPlayer(vehicleID)
    except AttributeError:
        LOG_WARNING('Attribute "selectPlayer" is not found')

    return


def setComponentsVisibility(flag, avatar=None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        avatar.setComponentsVisibility(flag)
    except AttributeError:
        LOG_WARNING('Attribute "setComponentsVisibility" is not found')

    return


def getOwnVehiclePosition(avatar=None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        position = avatar.getOwnVehiclePosition()
    except AttributeError:
        position = None
        LOG_WARNING('Attribute "getOwnVehiclePosition" is not found')

    return position


def getDistanceToTarget(target, avatar=None):
    """Gets distance between target and player's vehicle.
    :param target: BigWorld entity.
    :param avatar: instance of player entity (avatar).
    :return: float containing distance in meters.
    """
    ownPosition = getOwnVehiclePosition(avatar=avatar)
    if ownPosition is not None:
        return (target.position - ownPosition).length
    else:
        return 0.0
        return


def getDistanceToGunMarker(avatar=None):
    """Gets distance between player's vehicle and his gun marker position.
    It is used in strategic mode.
    :param avatar: instance of player entity (avatar).
    :return: float containing distance in meters.
    """
    if avatar is None:
        avatar = BigWorld.player()
    ownPosition = getOwnVehiclePosition(avatar=avatar)
    if ownPosition is None:
        return 0.0
    else:
        try:
            gunPosition = avatar.gunRotator.markerInfo[0]
        except AttributeError:
            LOG_WARNING('Attribute "gunRotator.markerInfo" is not found')
            return 0.0

        return (ownPosition - Math.Vector3(*gunPosition)).length
