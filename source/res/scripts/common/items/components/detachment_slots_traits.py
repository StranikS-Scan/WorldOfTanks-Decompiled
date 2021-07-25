# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/detachment_slots_traits.py
from enum import IntEnum
from typing import TYPE_CHECKING, Tuple, List, Any, Optional
from items.utils.common import SoftAssert
from crew2 import settings_globals
from items.components.detachment_constants import DetachmentLockMaskBits, INVALID_INSTRUCTOR_SLOT_ID
from items.components.detachment_components import validatePropertyLock, getCommonClassForVehicles
from items.utils.common import getBit, setBit
from items.utils.detachment import validateSpecialization, validateInstructor
if TYPE_CHECKING:
    from items.detachment import DetachmentDescr
    from items.instructor import InstructorDescr

class SlotsTraits(object):
    __slots__ = ('_owner',)

    def __init__(self, owner):
        self._owner = owner

    @property
    def owner(self):
        return self._owner

    def getMax(self):
        raise NotImplementedError('must override me')

    def getMask(self):
        raise NotImplementedError('must override me')

    def getSlots(self):
        raise NotImplementedError('must override me')

    def setSlotValue(self, slotID, value, validate=True, skipLockMask=False):
        raise NotImplementedError('must override me')

    def canSetSlotValue(self, slotID, value, skipLockMask=False):
        raise NotImplementedError('must override me')

    def validate(self, complexValue):
        raise NotImplementedError('must override me')

    def recalculate(self, slotID):
        raise NotImplementedError('must override me')

    def swapSlotsValues(self, slotIndex1, slotIndex2, slotsInfo):
        raise NotImplementedError('must override me')


class VehiclesSlotsTraits(SlotsTraits):

    def getMax(self):
        return self.owner._maxVehicleSlots

    def getMask(self):
        return DetachmentLockMaskBits.VEHICLE_SLOTS

    def getSlots(self):
        return self.owner._vehicleSlots

    def setSlotValue(self, slotID, value, validate=True, skipLockMask=False):
        slots = self.getSlots()
        SoftAssert(value not in slots, 'slot values is already present')
        if not skipLockMask:
            validatePropertyLock(self.owner, self.getMask(), slotID)
        SoftAssert(0 <= slotID < len(slots), 'slot #{} is not available'.format(slotID))
        if value is not None:
            if validate:
                SoftAssert(*self.validate(value))
            slots[slotID] = value
        else:
            slots[slotID] = None
        self.recalculate(slotID)
        return

    def validate(self, complexValue):
        return validateSpecialization(self.owner, complexValue)

    def recalculate(self, _):
        self.owner._classID = getCommonClassForVehicles(self.owner._vehicleSlots)

    def swapSlotsValues(self, slotIndex1, slotIndex2, slotsInfo):
        SoftAssert(slotIndex1 != slotIndex2, 'Slot indexes are equal, no need to swap')
        slots = self.getSlots()
        slotsIsEmpty = True
        for ix in [slotIndex1, slotIndex2]:
            slotInfo = slotsInfo[ix]
            SoftAssert(slotInfo.available, 'Slot {} not available'.format(ix))
            SoftAssert(not slotInfo.locked, 'Slot {} is locked'.format(ix))
            slotsIsEmpty = slotsIsEmpty and slotInfo.typeCompDescr is None

        SoftAssert(not slotsIsEmpty, "Can't swap empty slots")
        slots[slotIndex1], slots[slotIndex2] = slots[slotIndex2], slots[slotIndex1]
        return


class Direction(IntEnum):
    LEFT = 0
    RIGHT = 1


class InstructorsSlotsTraits(SlotsTraits):

    def getMax(self):
        return settings_globals.g_detachmentSettings.maxInstructorSlots

    def getMask(self):
        return DetachmentLockMaskBits.INSTRUCTORS

    def getSlots(self):
        return self.owner._instructorSlots

    def setSlotValue(self, slotID, value, validate=True, skipLockMask=False):
        slots = self.getSlots()
        if not skipLockMask:
            validatePropertyLock(self.owner, self.getMask(), slotID)
        SoftAssert(0 <= slotID < len(slots), 'slot #{} is not available'.format(slotID))
        if value is not None:
            newVal, instrDescr = value
            SoftAssert(newVal not in slots, 'slot values is already present')
            if validate:
                SoftAssert(*self.validate(value))
            SoftAssert(slots[slotID] is None, "can't set value to slot={}, slot is occupied".format(slotID))
            slotsCount = instrDescr.getSlotsCount()
            self._insertValueToSlots(newVal, slotID, slotsCount, skipLockMask)
        else:
            self._removeValueFromSlot(slots, slotID)
        self.recalculate(slotID)
        return

    def canSetSlotValue(self, slotID, value, skipLockMask=False):
        slots = self.getSlots()
        newVal, instrDescr = value
        leftPart = slots[:slotID]
        rightPart = slots[slotID:]
        needSlotsCount = instrDescr.getSlotsCount()
        slotsRemovedCount = self._removeFreeSlotsFrom(rightPart, Direction.RIGHT, skipLockMask, slotsCount=needSlotsCount)
        needSlotsCount = needSlotsCount - slotsRemovedCount
        if needSlotsCount == 0:
            return True
        slotsRemovedCount = self._removeFreeSlotsFrom(leftPart, Direction.LEFT, skipLockMask, slotsCount=needSlotsCount)
        needSlotsCount = needSlotsCount - slotsRemovedCount
        return needSlotsCount == 0

    def validate(self, complexValue):
        _, instrDescr = complexValue
        return validateInstructor(self.owner, instrDescr)

    def recalculate(self, slotID):
        if self.owner._activeInstructorSlotID == slotID and self.owner._instructorSlots[slotID] is None:
            self.owner._activeInstructorSlotID = INVALID_INSTRUCTOR_SLOT_ID
        return

    def move(self, slotID, steps):
        slots = self.getSlots()
        value = slots[slotID]
        capacity = slots.count(value)
        SoftAssert(value is not None, "slot shouldn't be empty")
        while steps != 0:
            direction = Direction.RIGHT if steps > 0 else Direction.LEFT
            steps -= abs(steps) / steps
            slotID = slots.index(value)
            nextSlotID = slotID + capacity if direction == Direction.RIGHT else slotID - 1
            SoftAssert(0 <= nextSlotID < len(slots), 'slot out of range')
            nextSlotValue = slots[nextSlotID]
            nextSlotCapacity = slots.count(nextSlotValue) if nextSlotValue else 1
            startID = slotID if direction == Direction.RIGHT else nextSlotID - nextSlotCapacity + 1
            endID = startID + capacity + nextSlotCapacity
            slots[startID:endID] = slots[startID:endID][::-1]
            lockMask = self.owner.lockMask
            bitList = [ getBit(lockMask, self.getMask(), i) for i in xrange(len(slots)) ]
            bitList[startID:endID] = bitList[startID:endID][::-1]
            for i, val in enumerate(bitList):
                lockMask = setBit(lockMask, self.getMask(), i, bool(val))

            self.owner.setLockMask(lockMask)

        return

    def _insertValueToSlots(self, newVal, slotID, capacity, skipLockMask):
        slots = self.getSlots()
        leftPart = slots[:slotID]
        rightPart = slots[slotID:]
        needSlotsCount = capacity
        slotsRemovedCount = self._removeFreeSlotsFrom(rightPart, Direction.RIGHT, skipLockMask, slotsCount=needSlotsCount)
        if slotsRemovedCount:
            rightPart = [newVal] * slotsRemovedCount + rightPart
        needSlotsCount = needSlotsCount - slotsRemovedCount
        if needSlotsCount:
            slotsRemovedCount = self._removeFreeSlotsFrom(leftPart, Direction.LEFT, skipLockMask, slotsCount=needSlotsCount)
            if slotsRemovedCount:
                leftPart = leftPart + [newVal] * slotsRemovedCount
            needSlotsCount = needSlotsCount - slotsRemovedCount
        SoftAssert(needSlotsCount == 0, "can't set value={} to slot={}, not enough capacity={}".format(newVal, slotID, capacity))
        self.owner._instructorSlots = leftPart + rightPart
        return self.owner._instructorSlots

    def _removeFreeSlotsFrom(self, slots, direction, skipLockMask, slotsCount=1):
        slotsRemovedCount = 0
        if direction == Direction.RIGHT:
            start, end, step = 0, len(slots), 1
        else:
            start, end, step = len(slots) - 1, -1, -1
        freeSlots = self._getFreeSlotIndexesInRange(slots, start, end, step, skipLockMask, maxSlots=slotsCount)
        if direction == Direction.RIGHT:
            freeSlots = freeSlots[::-1]
        for idx in freeSlots:
            slots.pop(idx)
            slotsRemovedCount += 1

        return slotsRemovedCount

    def _getFreeSlotIndexesInRange(self, slots, start, end, step, skipLockMask, maxSlots=None):
        resFreeSlots = []
        for idx in xrange(start, end, step):
            if len(resFreeSlots) == maxSlots:
                break
            if not skipLockMask and getBit(self.owner.lockMask, self.getMask(), idx):
                break
            if slots[idx] is None:
                resFreeSlots.append(idx)

        return resFreeSlots

    def _removeValueFromSlot(self, slots, slotID):
        invID = slots[slotID]
        if invID is None:
            return
        else:
            for index, value in enumerate(slots):
                if value == invID:
                    slots[index] = None

            return
