# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/hangar_music_stage/cam_sound_balancer.py
import math
from collections import namedtuple
from sounds import setRTPC
_Range = namedtuple('_Range', ('r1', 'r2'))

class CameraSoundBalancerMixin(object):

    def __init__(self):
        self.__leftRange = None
        self.__rightRange = None
        self.__leftSoundRange = _Range(0, -100.0)
        self.__rightSoundRange = _Range(0, 100.0)
        return

    def _startBalanceSound(self, initialYaw, yawConstraints):
        rightYaw, leftYaw = yawConstraints
        initialYaw = math.degrees(initialYaw)
        self.__leftRange = _Range(initialYaw, leftYaw)
        self.__rightRange = _Range(initialYaw, rightYaw)
        setRTPC('RTPC_off_concert_camera_position', 0)

    def _stopBalanceSound(self):
        self.__leftRange = self.__rightRange = None
        setRTPC('RTPC_off_concert_camera_position', 0)
        return

    def _onCameraAnglesChanged(self, nextYaw):
        if self.__leftRange is None or self.__rightRange is None:
            return
        else:
            nextYaw = math.degrees(nextYaw)
            if nextYaw >= self.__leftRange.r1:
                if nextYaw > self.__leftRange.r2:
                    nextYaw = self.__leftRange.r2
                val = self.__mapValueBetweenRanges(nextYaw, self.__leftRange, self.__leftSoundRange)
            else:
                if nextYaw < self.__rightRange.r2:
                    nextYaw = self.__rightRange.r2
                val = self.__mapValueBetweenRanges(nextYaw, self.__rightRange, self.__rightSoundRange)
            setRTPC('RTPC_off_concert_camera_position', val)
            return

    @staticmethod
    def __mapValueBetweenRanges(a, rangeA, rangeB):
        b = (a - rangeA.r1) * (rangeB.r2 - rangeB.r1) / (rangeA.r2 - rangeA.r1) + rangeB.r1
        return b
