# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/auto_shoot_guns/auto_shoot_helpers.py
import BigWorld
from auto_shoot_guns.auto_shoot_guns_common import BURST_ACTIVATION_MIN_TIMEOUT, BURST_ACTIVATION_MAX_TIMEOUT, BURST_DEACTIVATION_MIN_TIMEOUT, BURST_DEACTIVATION_MAX_TIMEOUT
from gui.shared.utils.functions import clamp
from vehicle_systems.tankStructure import TankSoundObjectsIndexes

def getBurstActivationTimeout():
    return clamp(BigWorld.LatencyInfo().value[3] * 0.5, BURST_ACTIVATION_MIN_TIMEOUT, BURST_ACTIVATION_MAX_TIMEOUT)


def getBurstDeactivationTimeout():
    return clamp(BigWorld.LatencyInfo().value[3] * 0.5, BURST_DEACTIVATION_MIN_TIMEOUT, BURST_DEACTIVATION_MAX_TIMEOUT)


def getGunSoundObject(vehicle):
    if vehicle.appearance is not None and vehicle.appearance.engineAudition is not None:
        soundObject = vehicle.appearance.engineAudition.getSoundObject(TankSoundObjectsIndexes.GUN)
        if soundObject is not None:
            return soundObject
        return SOUND_OBJECT_STUB
    else:
        return SOUND_OBJECT_STUB


class SoundObjectStub(object):

    def play(self, *_, **__):
        pass

    def setRTPC(self, *_, **__):
        pass


SOUND_OBJECT_STUB = SoundObjectStub()
