# Embedded file name: scripts/client/gui/battle_control/avatar_getter.py
import BigWorld
import constants
from debug_utils import LOG_WARNING, LOG_CURRENT_EXCEPTION

def isForcedGuiControlMode(avatar = None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        result = avatar.isForcedGuiControlMode
    except AttributeError:
        LOG_WARNING('Attribute "isForcedGuiControlMode" is not found')
        result = False

    return result


def getPlayerName(avatar = None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        result = avatar.name
    except AttributeError:
        LOG_WARNING('Attribute "name" is not found')
        result = ''

    return result


def getPlayerTeam(avatar = None):
    if avatar is None:
        avatar = BigWorld.player()
    return getattr(avatar, 'team', 0)


def getPlayerVehicleID(avatar = None):
    if avatar is None:
        avatar = BigWorld.player()
    return getattr(avatar, 'playerVehicleID', 0)


def isVehicleAlive(avatar = None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        result = avatar.isVehicleAlive
    except AttributeError:
        LOG_WARNING('Attribute "isVehicleAlive" is not found')
        result = False

    return result


def isVehicleInFire(avatar = None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        result = avatar.fireInVehicle
    except AttributeError:
        LOG_WARNING('Attribute "fireInVehicle" is not found')
        result = False

    return result


def getVehicleDeviceStates(avatar = None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        result = avatar.deviceStates
    except AttributeError:
        LOG_WARNING('Attribute "deviceStates" is not found')
        result = {}

    return result


def getVehicleTypeDescriptor(avatar = None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        result = avatar.vehicleTypeDescriptor
    except AttributeError:
        LOG_WARNING('Attribute "vehicleTypeDescriptor" is not found')
        result = None

    return result


def getVehicleExtrasDict(avatar = None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        result = avatar.vehicleTypeDescriptor.extrasDict
    except AttributeError:
        LOG_WARNING('Attribute "vehicleTypeDescriptor.extrasDict" is not found')
        result = {}

    return result


def getSoundNotifications(avatar = None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        result = avatar.soundNotifications
    except AttributeError:
        LOG_WARNING('Attribute "soundNotifications" is not found')
        result = None

    return result


def isPlayerOnArena(avatar = None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        result = avatar.isOnArena
    except AttributeError:
        LOG_WARNING('Attribute "isOnArena" is not found')
        result = False

    return result


def getInputHandler(avatar = None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        result = avatar.inputHandler
    except AttributeError:
        LOG_WARNING('Attribute "inputHandler" is not found')
        result = None

    return result


def getArena(avatar = None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        result = avatar.arena
    except AttributeError:
        LOG_WARNING('Attribute "arena" is not found')
        result = None

    return result


def getArenaUniqueID(avatar = None):
    try:
        return getArena(avatar).arenaUniqueID
    except AttributeError:
        LOG_WARNING('Attribute "arenaUniqueID" is not found')

    return None


def getMaxTeamsOnArena(avatar = None):
    try:
        return getArena(avatar).arenaType.maxTeamsInArena
    except AttributeError:
        LOG_WARNING('Attribute "arenaType" or "maxTeamsInArena" is not found')

    return constants.TEAMS_IN_ARENA.MIN_TEAMS


def updateVehicleSetting(code, value, avatar = None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        avatar.updateVehicleSetting(code, value)
    except AttributeError:
        LOG_CURRENT_EXCEPTION()
        LOG_WARNING('Attribute "updateVehicleSetting" is not found')

    return


def changeVehicleSetting(code, value, avatar = None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        avatar.base.vehicle_changeSetting(code, value)
    except AttributeError:
        LOG_WARNING('Attribute "base.vehicle_changeSetting" is not found')

    return


def activateAvatarEquipment(equipmentID, avatar = None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        avatar.cell.activateEquipment(equipmentID)
    except AttributeError:
        LOG_WARNING('Attribute "cell.activateEquipment" is not found')

    return


def leaveArena(avatar = None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        avatar.leaveArena()
    except AttributeError:
        LOG_WARNING('Attribute "leaveArena" is not found', avatar)

    return


def refreshShotDispersionAngle(avatar = None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        avatar.getOwnVehicleShotDispersionAngle(avatar.gunRotator.turretRotationSpeed, 1)
    except AttributeError:
        LOG_WARNING('Attribute "getOwnVehicleShotDispersionAngle" is not found')

    return
