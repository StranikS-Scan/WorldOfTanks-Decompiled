# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/vehicle_audition_wwise.py
import SoundGroups
import Math
import svarog_script.py_component
import BattleReplay

class TrackCrashAudition(svarog_script.py_component.Component):

    def deactivate(self):
        pass

    def playCrashSound(self, isLeft=True, restore=False):
        pass


class SingleEvent(object):
    __slots__ = ('__name',)

    def __init__(self, name):
        self.__name = name

    def play(self, o):
        o.play(self.__name)


class MultipleEvent(object):
    __slots__ = ('__names',)

    def __init__(self, names):
        self.__names = names

    def play(self, o):
        for name in self.__names:
            o.play(name)


_EFFECT_MATERIALS_HARDNESS_RTPC = {'ground': 0.1,
 'stone': 1,
 'wood': 0.5,
 'snow': 0.3,
 'sand': 0,
 'water': 0.2}
_FRICTION_ANG_FACTOR = 0.8
_FRICTION_ANG_BOUND = 0.5
_FRICTION_STRAFE_FACTOR = 0.4
_FRICTION_STRAFE_BOUND = 1.0
_PERIODIC_TIME = 0.25
_ENABLE_SOUND_DEBUG = False

class TrackCrashAuditionWWISE(TrackCrashAudition):

    def __init__(self, trackCenterMProvs):
        self.__trackCenterMProvs = trackCenterMProvs

    def deactivate(self):
        self.__trackCenterMProvs = None
        return

    def playCrashSound(self, isLeft=True, restore=False):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isTimeWarpInProgress:
            return
        else:
            if self.__trackCenterMProvs is not None:
                positionMatrix = Math.Matrix(self.__trackCenterMProvs[0 if isLeft else 1])
                if restore:
                    SoundGroups.g_instance.playSoundPos('repair_treads', positionMatrix.translation)
                else:
                    SoundGroups.g_instance.playSoundPos('brakedown_treads', positionMatrix.translation)
            return
