# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/vehicle_branch.py
import logging
import typing
import BigWorld
from adisp import adisp_async
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.new_year.new_year_helper import formatRomanNumber
from helpers import dependency
from helpers.time_utils import getServerUTCTime
from items.components.ny_constants import NY_BRANCH_MIN_LEVEL, NY_BRANCH_MAX_LEVEL
from shared_utils import first, findFirst
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from cache import cached_property
from new_year.vehicle_branch_helpers import getAvailableVehicleRange
if typing.TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple, Union
    from gui.shared.gui_items.Vehicle import Vehicle
    SlotBonusType = Tuple[Optional[str], Optional[float]]
_logger = logging.getLogger(__name__)
EMPTY_VEH_INV_ID = 0
EmptyBonus = (None, None)
_MIN_SLOT_LVL = 0
_EMPTY_TOKEN = ''

@adisp_async
def _asyncSleep(time, callback=None):
    BigWorld.callback(time, lambda *_: callback(None))


def _unpackVehicleBonus(dictBonus):
    return first(dictBonus.iteritems())


def getSlotBonusByType(bonusType):
    _, bValue = findFirst(lambda (t, v): t == bonusType, getSlotBonusChoicesConfig().itervalues(), ('', 0))
    return int(100 * bValue)


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getInEventCooldown(lobbyCtx=None):
    pass


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getSlotBonusChoicesConfig(lobbyCtx=None):
    return {}


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getVehicleSlotsInfo(lobbyCtx=None):
    return {}


def _getSlotName(slot, case='acc'):
    slotKey = 'level'
    return backport.text(R.strings.ny.vehicleBranch.slotTypeName.dyn(case).dyn(slotKey)())


class VehicleSlot(object):
    __slots__ = ('__slotID',)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, slotID):
        self.__slotID = slotID

    def getSlotBonus(self):
        return getSlotBonusChoicesConfig().get(self.getBonusChoiceID(), EmptyBonus)

    def getBonusChoiceID(self):
        return self.__itemsCache.items.festivity.getVehicleBonusChoices()[self.__slotID]

    @staticmethod
    def getVehicleLvl():
        return NY_BRANCH_MIN_LEVEL

    def getSlotID(self):
        return self.__slotID

    def isFree(self):
        return self.isAvailable() and self._getVehicleInvID() == EMPTY_VEH_INV_ID and self.getCooldown() is None

    def isAvailable(self):
        return False

    def getRestrictionType(self):
        pass

    def getLevel(self):
        pass

    def getToken(self):
        pass

    def getVehicle(self):
        invID = self._getVehicleInvID()
        return self.__itemsCache.items.getVehicle(invID) if invID != EMPTY_VEH_INV_ID else None

    def getCooldown(self):
        cooldown = 0
        vehicleCooldown = self.__itemsCache.items.festivity.getVehicleCooldown()
        if len(vehicleCooldown) > self.__slotID:
            cooldown = vehicleCooldown[self.__slotID] - getServerUTCTime()
        return cooldown if cooldown > 0 else None

    @staticmethod
    def getLevelStr():
        levelsRange = getAvailableVehicleRange()
        if len(levelsRange) == 1:
            level = formatRomanNumber(levelsRange[0])
        else:
            level = backport.text(R.strings.ny.vehiclesView.levelsStr(), minLevel=formatRomanNumber(levelsRange[0]), maxLevel=formatRomanNumber(levelsRange[-1]))
        return level

    @staticmethod
    def getExtraSlotBonus(choiceID):
        return getSlotBonusChoicesConfig().get(choiceID, None)

    @staticmethod
    def getDefaultSlotCooldown():
        return getInEventCooldown()

    @staticmethod
    def isBonusChoiceAllowed():
        return True

    def _getVehicleInvID(self):
        return self.__itemsCache.items.festivity.getVehicleBranch()[self.__slotID]


class VehicleBranch(object):
    __itemsCache = dependency.descriptor(IItemsCache)

    @cached_property
    def __slots(self):
        return [ VehicleSlot(ind) for ind in getVehicleSlotsInfo().iterkeys() ]

    def getVehicleSlots(self):
        return self.__slots

    @staticmethod
    def hasSlotWithLevel(level):
        return True if NY_BRANCH_MIN_LEVEL <= level <= NY_BRANCH_MAX_LEVEL else False

    def isVehicleInBranch(self, vehicle):
        return vehicle.invID in self.__itemsCache.items.festivity.getVehicleBranch()

    def getFreeVehicleSlots(self):
        return [ slot for slot in self.__slots if slot.isFree() ]

    def hasAvailableSlots(self):
        items = self.__itemsCache.items
        return items.festivity.getMaxLevel() >= NY_BRANCH_MIN_LEVEL

    def getSlotForVehicle(self, vehInvID):
        vehicleBranch = self.__itemsCache.items.festivity.getVehicleBranch()
        for idx, vehInvIDInBranch in enumerate(vehicleBranch):
            if vehInvID == vehInvIDInBranch:
                slot = self.__slots[idx]
                return slot

        return None

    def getVehiclesWithBonusChoice(self):
        res = []
        for slot in self.__slots:
            if not slot.isBonusChoiceAllowed():
                continue
            vehicle = slot.getVehicle()
            if vehicle is None:
                continue
            res.append(vehicle.invID)

        return res
