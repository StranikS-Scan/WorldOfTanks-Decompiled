# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/game_objects/festivalrace_objects/race_sound_zone.py
import NetworkComponents
import Vehicle
import WWISE

class RaceSoundZoneSoundManager(object):
    SOUND_ZONE_ENTER = 'ev_race_fly_zone_enter'
    SOUND_ZONE_EXIT = 'ev_race_fly_zone_exit'

    @staticmethod
    def playEvent(event):
        WWISE.WW_eventGlobal(event)


def onVehicleEnterZone(who, where):
    vehicle = _getPlayerVehicle(who)
    if vehicle is None:
        return
    elif not vehicle.isPlayerVehicle:
        return
    else:
        RaceSoundZoneSoundManager.playEvent(RaceSoundZoneSoundManager.SOUND_ZONE_ENTER)
        return


def onVehicleExitZone(who, where):
    vehicle = _getPlayerVehicle(who)
    if vehicle is None:
        return
    elif not vehicle.isPlayerVehicle:
        return
    else:
        RaceSoundZoneSoundManager.playEvent(RaceSoundZoneSoundManager.SOUND_ZONE_EXIT)
        return


def _getPlayerVehicle(who):
    playerEntityRef = who.findComponentByType(NetworkComponents.NetworkEntity)
    if playerEntityRef is None:
        return
    else:
        playerVehicleEntity = playerEntityRef.implementation
        return None if not isinstance(playerVehicleEntity, Vehicle.Vehicle) else playerVehicleEntity
