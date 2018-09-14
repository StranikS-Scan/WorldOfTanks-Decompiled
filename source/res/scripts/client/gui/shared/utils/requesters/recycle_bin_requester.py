# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/recycle_bin_requester.py
from collections import namedtuple
import BigWorld
from ItemRestore import RESTORE_VEHICLE_TYPE
from adisp import async
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from helpers import time_utils
from skeletons.gui.shared.utils.requesters import IRecycleBinRequester
_VehicleRestoreInfo = namedtuple('_VehicleRestoreInfo', ('restoreType', 'changedAt', 'restoreDuration', 'restoreCooldown'))

class VehicleRestoreInfo(_VehicleRestoreInfo):

    def getRestoreTimeLeft(self):
        """
        Get restore left time in seconds for regular premium vehicles
        :return: <int>
        """
        return max(self.restoreDuration - self.__getTimeGone(), 0) if self.changedAt else 0

    def getRestoreCooldownTimeLeft(self):
        """
        Get restore cooldown left time in seconds for notInShop vehicles
        :return: <int>
        """
        return max(self.restoreCooldown - self.__getTimeGone(), 0) if self.changedAt else 0

    def isLimited(self):
        """
        Check if vehicle restore is limited in time,
        only regular premium vehicles has limited restore
        :return: <bool>
        """
        return self.restoreType == RESTORE_VEHICLE_TYPE.PREMIUM and self.changedAt != 0

    def isInCooldown(self):
        """
        Check if vehicle restore is in cooldown,
        only notInShop vehicles has restore cooldown
        :return: <bool>
        """
        return self.restoreType == RESTORE_VEHICLE_TYPE.ACTION and self.getRestoreCooldownTimeLeft() > 0 if self.changedAt else False

    def isUnlimited(self):
        """
        Check if vehicle restore is unlimited in time,
        only notInShop vehicles has unlimited restore
        :return: <bool>
        """
        return self.restoreType == RESTORE_VEHICLE_TYPE.ACTION and self.changedAt == 0

    def isRestorePossible(self):
        """
        Check the possibility of vehicle restore, right now or in future
        for notInShop vehicle in moment of sold return True
        for regular premium vehicle check its restore left time
        :return:<bool>
        """
        return self.restoreType == RESTORE_VEHICLE_TYPE.ACTION or self.isLimited() and self.getRestoreTimeLeft() > 0

    def __getTimeGone(self):
        """
        Get time gone in seconds from last operation
        (restore operation for notInShop vehicles or sell operation for regular premium vehicles)
        :return: <int>
        """
        return float(time_utils.getTimeDeltaTilNow(time_utils.makeLocalServerTime(self.changedAt))) if self.changedAt else 0


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

    def getTankmen(self, maxDuration):
        filteredBuffer = {}
        tankmenBuffer = self.recycleBin.get('tankmen', {}).get('buffer', {})
        for tankmanId, (strCD, dismissedAt) in tankmenBuffer.iteritems():
            if time_utils.getTimeDeltaTilNow(dismissedAt) < maxDuration:
                filteredBuffer[tankmanId] = (strCD, dismissedAt)

        return dict(map(lambda (k, v): (k * -1, v), filteredBuffer.iteritems()))

    def getTankman(self, invID, maxDuration):
        return self.getTankmen(maxDuration).get(invID)

    @async
    def _requestCache(self, callback):
        BigWorld.player().recycleBin.getCache(lambda resID, value: self._response(resID, value, callback))
