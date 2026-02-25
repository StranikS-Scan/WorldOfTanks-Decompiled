# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/CoolantTankAbilityEquipment.py
from collections import namedtuple
from AbilityEquipment import AbilityEquipment
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from items import vehicles
from constants import CoolantTankAbilityState
_PenaltyReloadState = namedtuple('_PenaltyReloadState', ('reloadTimeFactor', 'ammoChangeFactor', 'penaltyTime', 'appliedPenaltyReloadTime'))

class _CoolantTankAbilityCtrl(object):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __slots__ = ('__penaltyReloadState', '__currentClientState', '__baseValue', '__prevPenalty')

    def __init__(self):
        self.__penaltyReloadState = None
        self.__currentClientState = CoolantTankAbilityState.ACTIVE
        self.__baseValue = 0.0
        self.__prevPenalty = 0.0
        return

    def subscribe(self):
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onGunReloadTimeSet += self.__onGunReloadTimeSet
        return

    def unsubscribe(self):
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onGunReloadTimeSet -= self.__onGunReloadTimeSet
        return

    def setCurrentClientState(self, state):
        self.__currentClientState = state
        self.calculatePenaltyReloadTime()

    def updatePenaltyReloadState(self, reloadTimeFactor, ammoChangeFactor, penaltyTime, appliedPenaltyReloadTime):
        self.__penaltyReloadState = _PenaltyReloadState(reloadTimeFactor, ammoChangeFactor, penaltyTime, appliedPenaltyReloadTime)
        self.calculatePenaltyReloadTime()
        self.__prevPenalty = self.__penaltyReloadState.penaltyTime

    def calculatePenaltyReloadTime(self):
        if self.__penaltyReloadState is None:
            return
        elif self.__baseValue == -1 and self.__currentClientState != CoolantTankAbilityState.GUN_RELOAD_FINISHED:
            return
        else:
            reloadTimeFactor, ammoChangeFactor, penaltyTime, appliedPenaltyReloadTime = self.__penaltyReloadState
            ammoCtrl = self.__sessionProvider.shared.ammo
            addPenalty = max(penaltyTime - self.__prevPenalty, 0)
            if self.__currentClientState == CoolantTankAbilityState.ACTIVE:
                vehFactors = reloadTimeFactor * ammoChangeFactor
                baseTime = (self.__baseValue - appliedPenaltyReloadTime) / vehFactors
                penaltyReloadTime = round(baseTime + penaltyTime, 2)
            elif self.__currentClientState == CoolantTankAbilityState.DEACTIVATED:
                baseTime = self.__baseValue - appliedPenaltyReloadTime
                penaltyReloadTime = round(baseTime + penaltyTime, 2)
            else:
                penaltyReloadTime = 0
            ammoCtrl.onPenaltyReloadTimeUpdated(self.__baseValue, penaltyReloadTime, addPenalty)
            ammoCtrl.setReloadingPenalty(appliedPenaltyReloadTime)
            return

    def __onGunReloadTimeSet(self, currShellCD, reloadingSnapshot, skipAutoLoader):
        self.__baseValue = reloadingSnapshot.getBaseValue()
        self.calculatePenaltyReloadTime()


class CoolantTankAbilityEquipment(AbilityEquipment):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(CoolantTankAbilityEquipment, self).__init__()
        self._coolantCtrl = _CoolantTankAbilityCtrl()
        self._coolantCtrl.subscribe()

    def onDestroy(self):
        self._coolantCtrl.unsubscribe()

    def set_currentClientState(self, state):
        currentClientState = self.currentClientState
        self._coolantCtrl.setCurrentClientState(currentClientState)

    def updateCurrentPenaltyReloadTime(self, currentPenaltyReloadTime, appliedPenaltyReloadTime, ammoChangeFactor):
        descriptor = vehicles.getItemByCompactDescr(self.compactDescr)
        reloadTimeFactor = 1.0
        for factor in descriptor.factors:
            if factor.name == 'gun/reloadTime':
                reloadTimeFactor = factor.value
                break

        self._coolantCtrl.updatePenaltyReloadState(reloadTimeFactor, ammoChangeFactor, currentPenaltyReloadTime, appliedPenaltyReloadTime)
