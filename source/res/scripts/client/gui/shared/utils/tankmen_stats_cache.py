# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/tankmen_stats_cache.py
from AccountCommands import LOCK_REASON
from debug_utils import LOG_DEBUG_DEV
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import Tankman
from helpers import dependency
from items import vehicles, crew_junk_convert_helper
from skeletons.gui.shared import IItemsCache

class _TankmanContext(object):
    NOT_INITIALIZED = object()

    def __init__(self, itemsCache, tankman):
        self._itemsCache = itemsCache
        self.tankman = tankman
        self._vehicleData = self.NOT_INITIALIZED
        self._isLockedByVehicle = self.NOT_INITIALIZED
        self._vehicleType = self.NOT_INITIALIZED
        self._isTrashTankman = self.NOT_INITIALIZED

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

    def isTrashTankman(self):
        if self._isTrashTankman == self.NOT_INITIALIZED:
            self._isTrashTankman = crew_junk_convert_helper.isTrashTankman(self.tankman.descriptor)
        return self._isTrashTankman

    def isJunkTankman(self):
        return not self.tankman.isInTank and self.isTrashTankman()

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


class _ResetFillComponent(object):

    def __init__(self, enable=True):
        self._hasAnyTmanForReset = False
        self._hasAnyTmanForFill = False
        self._enabled = enable

    def setEnabled(self, enabled):
        self._enabled = enabled

    def reset(self):
        self._hasAnyTmanForReset = False
        self._hasAnyTmanForFill = False

    def checkTankman(self, tmanCtx):
        if not self._enabled:
            return
        self._hasAnyTmanForReset |= self._canReset(tmanCtx)
        self._hasAnyTmanForFill |= self._canFill(tmanCtx)

    def isComplete(self):
        return True if not self._enabled else self._hasAnyTmanForReset and self._hasAnyTmanForFill

    def hasAnyTmanForReset(self):
        return self._hasAnyTmanForReset

    def hasAnyTmanForFill(self):
        return self._hasAnyTmanForFill

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


class _JunkComponent(object):

    def __init__(self):
        self._hasJunkTankman = False

    def reset(self):
        self._hasJunkTankman = False

    def checkTankman(self, tmanCtx):
        self._hasJunkTankman |= tmanCtx.isJunkTankman()

    def isComplete(self):
        return self._hasJunkTankman

    def hasJunkTankman(self):
        return self._hasJunkTankman


class TankmenStatsCache(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self._needUpdate = True
        self._resetFillComponent = _ResetFillComponent(enable=False)
        self._junkComponent = _JunkComponent()
        self._reset()

    def setResetFillEnabled(self, enabled):
        self._resetFillComponent.setEnabled(enabled)
        self._needUpdate = True

    def hasAnyTmanForReset(self):
        self.update()
        return self._resetFillComponent.hasAnyTmanForReset()

    def hasAnyTmanForFill(self):
        self.update()
        return self._resetFillComponent.hasAnyTmanForFill()

    def hasJunkTankman(self):
        self.update()
        return self._junkComponent.hasJunkTankman()

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
            self._resetFillComponent.checkTankman(tmanCtx)
            self._junkComponent.checkTankman(tmanCtx)
            if self._resetFillComponent.isComplete() and self._junkComponent.isComplete():
                break

        LOG_DEBUG_DEV('TankmenStatsCache checked all tankmen')

    def _reset(self):
        self._resetFillComponent.reset()
        self._junkComponent.reset()
