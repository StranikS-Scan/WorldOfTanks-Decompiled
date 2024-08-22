# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/tankmen_stats_cache.py
from AccountCommands import LOCK_REASON
from debug_utils import LOG_DEBUG_DEV
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import Tankman
from helpers import dependency
from items import vehicles
from skeletons.gui.shared import IItemsCache

class _TankmanContext(object):
    NOT_INITIALIZED = object()

    def __init__(self, itemsCache, tankman):
        self._itemsCache = itemsCache
        self.tankman = tankman
        self._vehicleData = self.NOT_INITIALIZED
        self._isLockedByVehicle = self.NOT_INITIALIZED
        self._vehicleType = self.NOT_INITIALIZED

    def vehicleData(self):
        if self._vehicleData == self.NOT_INITIALIZED:
            vehInvID = self.tankman.vehicleInvID
            if vehInvID == Tankman.NO_VEHICLE_INV_ID:
                self._vehicleData = None
            else:
                self._vehicleData = self._itemsCache.items.inventory.getItems(GUI_ITEM_TYPE.VEHICLE, vehInvID)
        return self._vehicleData

    def vehicleType(self):
        if self._vehicleType == self.NOT_INITIALIZED:
            vehData = self.vehicleData()
            if vehData is None:
                self._vehicleType = None
            else:
                nationID, vehTypeID = vehicles.parseVehicleCompactDescr(vehData['compDescr'])
                self._vehicleType = vehicles.g_cache.vehicle(nationID, vehTypeID)
        return self._vehicleType

    def isLockedByVehicle(self):
        if self._isLockedByVehicle == self.NOT_INITIALIZED:
            vehType = self.vehicleType()
            if vehType is None:
                self._isLockedByVehicle = False
            else:
                isLockedByVehicle = 'lockCrewSkills' in vehType.tags
                isLockedByVehicle |= self._isVehicleLocked()
                self._isLockedByVehicle = isLockedByVehicle
        return self._isLockedByVehicle

    def _isVehicleLocked(self):
        vehData = self.vehicleData()
        lock = vehData.get('lock')
        return lock is not None and lock[0] != LOCK_REASON.NONE

    def canAddAnyMajorSkill(self):
        return self.tankman.descriptor.totalMajorSkills - self.tankman.skillsCount > 0

    def canAddAnyBonusSkill(self):
        bonusRoles = set()
        curVehTypeID = None
        if self.tankman.vehicleInvID != Tankman.NO_VEHICLE_INV_ID:
            curVehData = self.vehicleData()
            curVehType = self.vehicleType()
            curVehTypeID = curVehType.innationID
            slotIdx = curVehData['crew'].index(self.tankman.invID)
            bonusRoles.update(curVehType.crewRoles[slotIdx][1:])
        nativeVehTypeID = self.tankman.descriptor.vehicleTypeID
        if curVehTypeID != nativeVehTypeID:
            nativeVehType = vehicles.g_cache.vehicle(self.tankman.nationID, nativeVehTypeID)
            for roles in nativeVehType.crewRoles:
                if roles[0] == self.tankman.role:
                    bonusRoles.update(roles[1:])

        for role in bonusRoles:
            if self.tankman.descriptor.getNewBonusSkillsCount(role) > 0:
                return True

        return False


class TankmenStatsCache(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self._needUpdate = True
        self._reset()

    def hasAnyTmanForReset(self):
        self.update()
        return self._hasAnyTmanForReset

    def hasAnyTmanForFill(self):
        self.update()
        return self._hasAnyTmanForFill

    def setNeedUpdate(self):
        self._needUpdate = True

    def update(self):
        if not self._needUpdate:
            return
        self._needUpdate = False
        self._reset()
        tankmen = self.itemsCache.items.getInventoryTankmenRO()
        for tankman in tankmen.itervalues():
            tmanCtx = _TankmanContext(self.itemsCache, tankman)
            self._hasAnyTmanForReset |= self._canReset(tmanCtx)
            self._hasAnyTmanForFill |= self._canFill(tmanCtx)
            if self._hasAnyTmanForReset and self._hasAnyTmanForFill:
                break

        LOG_DEBUG_DEV('TankmenStatsCache checked all tankmen')

    def _reset(self):
        self._hasAnyTmanForReset = False
        self._hasAnyTmanForFill = False

    @staticmethod
    def _canReset(tmanCtx):
        canReset = tmanCtx.tankman.descriptor.hasSkills()
        canReset &= not tmanCtx.isLockedByVehicle()
        return canReset

    @staticmethod
    def _canFill(tmanCtx):
        canFill = tmanCtx.canAddAnyMajorSkill()
        if canFill and tmanCtx.isLockedByVehicle():
            return False
        canFill |= tmanCtx.canAddAnyBonusSkill()
        return canFill
