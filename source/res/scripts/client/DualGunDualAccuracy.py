# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DualGunDualAccuracy.py
import BigWorld
import CGF
from DualAccuracyBase import DualAccuracyBase
from cgf_components.dual_gun_dual_accuracy_heat_component import DualGunDualAccuracyHeatManager
from constants import DUAL_GUN, DUAL_ACCURACY_STATE
from collections import namedtuple
from debug_utils import LOG_ERROR
CoolingTiming = namedtuple('CoolingTiming', ['gun', 'endTime'])

class DualGunDualAccuracy(DualAccuracyBase):

    def __init__(self):
        self.__activeGun = CoolingTiming(gun=DUAL_GUN.ACTIVE_GUN.LEFT, endTime=0)
        self.__wasDualShot = False
        super(DualGunDualAccuracy, self).__init__()
        if self.gunStatesPublic:
            self.__processHeatingAnimation()

    def isShouldSkipDispersion(self):
        wasDualShot = self.__wasDualShot
        self.__wasDualShot = False
        return not wasDualShot and self.__activeGun.endTime <= BigWorld.time()

    def getActiveGun(self):
        return self.__activeGun.gun

    def setDualShotStatus(self, wasDualShot):
        self.__wasDualShot = wasDualShot

    def getGunCoolingLeftTime(self):
        curTime = BigWorld.time()
        return 0.0 if self.__activeGun.endTime <= curTime else float(self.__activeGun.endTime - curTime)

    def onCoolingDataUpdated(self, activeGun, coolingTime):
        self.__setCoolingEnd(activeGun, coolingTime)
        self.updateDualAccuracyData()

    def onPrefabLoaded(self):
        self.__processHeatingAnimation()

    def set_gunStatesPublic(self, _=None):
        self.__processHeatingAnimation()

    def __setCoolingEnd(self, gun, currentCoolingDelay):
        endTime = BigWorld.time() + currentCoolingDelay
        self.__activeGun = CoolingTiming(gun=gun, endTime=endTime)

    def __processHeatingAnimation(self):
        manager = CGF.getManager(self.entity.spaceID, DualGunDualAccuracyHeatManager)
        if not manager:
            LOG_ERROR('failed to update particle effects. Manager is None', self.entity.id)
            return
        comp = manager.getAccuracyComponent(self.entity.id)
        if not comp:
            return
        comp.toggleState(DUAL_GUN.ACTIVE_GUN.LEFT, self.gunStatesPublic[DUAL_GUN.ACTIVE_GUN.LEFT] == DUAL_ACCURACY_STATE.ACTIVE)
        comp.toggleState(DUAL_GUN.ACTIVE_GUN.RIGHT, self.gunStatesPublic[DUAL_GUN.ACTIVE_GUN.RIGHT] == DUAL_ACCURACY_STATE.ACTIVE)
