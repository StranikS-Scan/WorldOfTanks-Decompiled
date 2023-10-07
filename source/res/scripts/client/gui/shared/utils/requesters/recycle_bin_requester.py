# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/recycle_bin_requester.py
from collections import namedtuple
import BigWorld
from ItemRestore import RESTORE_VEHICLE_TYPE
from adisp import adisp_async
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from helpers import time_utils
from skeletons.gui.shared.utils.requesters import IRecycleBinRequester
_VehicleRestoreInfo = namedtuple('_VehicleRestoreInfo', ('restoreType', 'changedAt', 'restoreDuration', 'restoreCooldown'))

class VehicleRestoreInfo(_VehicleRestoreInfo):

    def getRestoreTimeLeft(self):
        return max(self.restoreDuration - self.__getTimeGone(), 0) if self.changedAt else 0

    def getRestoreCooldownTimeLeft(self):
        return max(self.restoreCooldown - self.__getTimeGone(), 0) if self.changedAt else 0

    def isFinite(self):
        return self.restoreType == RESTORE_VEHICLE_TYPE.PREMIUM and 0 < self.getRestoreTimeLeft() < float('inf')

    def isInCooldown(self):
        return self.restoreType == RESTORE_VEHICLE_TYPE.ACTION and self.getRestoreCooldownTimeLeft() > 0 if self.changedAt else False

    def isUnlimited(self):
        return self.restoreType == RESTORE_VEHICLE_TYPE.ACTION and self.getRestoreCooldownTimeLeft() == 0 or self.restoreType == RESTORE_VEHICLE_TYPE.PREMIUM and self.getRestoreTimeLeft() == float('inf')

    def isRestorePossible(self):
        return self.isUnlimited() or self.isFinite() and self.getRestoreTimeLeft() > 0 if self.restoreType == RESTORE_VEHICLE_TYPE.PREMIUM else True

    def __getTimeGone(self):
        return float(time_utils.getTimeDeltaTillNow(time_utils.makeLocalServerTime(self.changedAt))) if self.changedAt else 0


class RecycleBinRequester(AbstractSyncDataRequester, IRecycleBinRequester):

    @property
    def recycleBin(self):
        return self.getCacheValue('recycleBin', {})

    @property
    def vehiclesBuffer(self):
        return self.recycleBin.get('vehicles', {}).get('buffer', {})

    def getVehicleRestoreInfo(self, intCD, restoreDuration, restoreCooldown):
        restoreData = self.vehiclesBuffer.get(intCD)
        if restoreData:
            restoreType, changedAt = restoreData
            return VehicleRestoreInfo(restoreType, changedAt, restoreDuration, restoreCooldown)
        else:
            return None

    def getVehiclesIntCDs(self):
        return self.vehiclesBuffer.keys()

    def getTankmen(self, maxDuration):
        filteredBuffer = {}
        tankmenBuffer = self.recycleBin.get('tankmen', {}).get('buffer', {})
        for tankmanId, (strCD, dismissedAt) in tankmenBuffer.iteritems():
            if time_utils.getTimeDeltaTillNow(dismissedAt) < maxDuration:
                filteredBuffer[tankmanId] = (strCD, dismissedAt)

        return filteredBuffer

    def getTankman(self, invID, maxDuration):
        return self.getTankmen(maxDuration).get(invID)

    @adisp_async
    def _requestCache(self, callback):
        BigWorld.player().recycleBin.getCache(lambda resID, value: self._response(resID, value, callback))
