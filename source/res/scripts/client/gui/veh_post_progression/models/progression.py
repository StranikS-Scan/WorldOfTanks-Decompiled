# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_post_progression/models/progression.py
import typing
from collections import namedtuple
from enum import Enum, unique
from AccountCommands import LOCK_REASON
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.veh_post_progression.models.ext_money import ExtendedMoney
from gui.veh_post_progression.models.iterators import OrderedStepsIterator, UnorederdStepsIterator
from gui.veh_post_progression.models.progression_step import PostProgressionStepItem
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from items import vehicles
from post_progression_common import FEATURE_BY_GROUP_ID, ROLESLOT_FEATURE, VehicleState
from skeletons.gui.game_control import IVehiclePostProgressionController
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
    from helpers.server_settings import VehiclePostProgressionConfig
    from items.components.post_progression_components import ProgressionTree
    from items.vehicles import VehicleType

@unique
class PostProgressionAvailability(Enum):
    AVAILABLE = 'available'
    NOT_EXISTS = 'not_exits'
    VEH_NOT_ELITE = ' veh_not_elite'
    VEH_NOT_IN_INVENTORY = 'veh_not_in_inventory'
    VEH_IS_RENTED = 'veh_is_rented'
    VEH_IS_RENT_OVER = 'veh_is_rent_over'
    VEH_IN_BATTLE = 'veh_in_battle'
    VEH_IN_FORMATION = 'veh_in_formation'
    VEH_IN_QUEUE = 'veh_in_queue'
    VEH_IN_BREAKER = 'veh_in_breaker'
    VEH_IS_BROKEN = 'veh_is_broken'


@unique
class PostProgressionCompletion(Enum):
    EMPTY = 'empty'
    PARTIAL = 'partial'
    FULL = 'full'


class AvailabilityCheckResult(namedtuple('AvailabilityCheckResult', 'result, reason')):

    def __nonzero__(self):
        return self.result


_LOCK_TO_STATE = {LOCK_REASON.ON_ARENA: PostProgressionAvailability.VEH_IN_BATTLE,
 LOCK_REASON.IN_QUEUE: PostProgressionAvailability.VEH_IN_QUEUE,
 LOCK_REASON.PREBATTLE: PostProgressionAvailability.VEH_IN_FORMATION,
 LOCK_REASON.UNIT: PostProgressionAvailability.VEH_IN_FORMATION,
 LOCK_REASON.BREAKER: PostProgressionAvailability.VEH_IN_BREAKER}

class PostProgressionItem(object):
    __postProgressionCtrl = dependency.descriptor(IVehiclePostProgressionController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__state', '__stepsCache', '__tree', '__vehType')

    def __init__(self, state, vehType):
        self.__state = state
        self.__stepsCache = {}
        self.__tree = vehicles.g_cache.postProgression().trees.get(vehType.postProgressionTree)
        self.__vehType = vehType

    def __repr__(self):
        return 'PostProgressionItem <vehCD: {}, treeID: {}>'.format(self.__vehType.compactDescr, self.__vehType.postProgressionTree)

    @property
    def itemTypeID(self):
        return GUI_ITEM_TYPE.VEH_POST_PROGRESSION

    @property
    def itemTypeName(self):
        return GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.VEH_POST_PROGRESSION]

    def isActive(self, veh):
        settings = self.__postProgressionCtrl.getSettings()
        return self.isExists(settings) and not self.isDisabled(veh, settings)

    def isAvailable(self, veh, unlockOnly=False):
        result = PostProgressionAvailability.AVAILABLE
        enabledRentedVehicles = self.__postProgressionCtrl.getSettings().enabledRentedVehicles
        if not self.isExists():
            result = PostProgressionAvailability.NOT_EXISTS
        elif veh.isRented and veh.intCD not in enabledRentedVehicles:
            result = PostProgressionAvailability.VEH_IS_RENTED
        elif veh.rentalIsOver and veh.intCD in enabledRentedVehicles and not unlockOnly:
            result = PostProgressionAvailability.VEH_IS_RENT_OVER
        elif not veh.isElite:
            result = PostProgressionAvailability.VEH_NOT_ELITE
        elif not veh.isInInventory:
            result = PostProgressionAvailability.VEH_NOT_IN_INVENTORY
        elif veh.isLocked and not unlockOnly:
            result = _LOCK_TO_STATE[veh.lock[0]]
        elif veh.isBroken and not unlockOnly:
            result = PostProgressionAvailability.VEH_IS_BROKEN
        return AvailabilityCheckResult(result is PostProgressionAvailability.AVAILABLE, result)

    def isDefined(self):
        return self.__tree is not None

    def isDisabled(self, veh, settings=None, skipRentalIsOver=False):
        return self.__postProgressionCtrl.isDisabledFor(veh, settings, skipRentalIsOver)

    def isExists(self, settings=None):
        return self.__postProgressionCtrl.isExistsFor(self.__vehType, settings)

    def isFeatureEnabled(self, featureName):
        settings = self.__postProgressionCtrl.getSettings()
        return self.isExists(settings) and featureName in settings.enabledFeatures

    def isRoleSlotActive(self, veh):
        return self.isRoleSlotExists() and not self.isDisabled(veh)

    def isRoleSlotExists(self, externalState=None):
        state = externalState or self.__state
        hasFeature = state.hasFeature(vehicles.g_cache.postProgression().featureIDs[ROLESLOT_FEATURE])
        return self.isFeatureEnabled(ROLESLOT_FEATURE) and hasFeature

    def isSetupSwitchActive(self, veh, gID):
        hasFeature = self.__state.hasFeature(vehicles.g_cache.postProgression().featureIDs[FEATURE_BY_GROUP_ID[gID]])
        return self.isFeatureEnabled(FEATURE_BY_GROUP_ID[gID]) and not self.isDisabled(veh, skipRentalIsOver=True) and hasFeature

    def isPrebattleSwitchDisabled(self, groupID):
        return self.__state.isSwitchDisabled(groupID)

    def getFirstPurchasableStep(self, balance):
        for stepItem in self.iterOrderedSteps():
            if stepItem.mayPurchase(balance):
                return stepItem

        return None

    def getActiveModifications(self, vehicle, ignoreDisabled=False):
        if self.isExists() and (ignoreDisabled or not self.isDisabled(vehicle)):
            return [ stepItem.action.getActiveID() for stepItem in self.iterUnorderedSteps() if stepItem.isReceived() and stepItem.action.getActiveID() is not None ]
        else:
            return []

    def getCompletion(self):
        if not self.__state.unlocks:
            return PostProgressionCompletion.EMPTY
        for step in self.iterUnorderedSteps():
            if step.isLocked() or step.isUnlocked():
                return PostProgressionCompletion.PARTIAL

        return PostProgressionCompletion.FULL

    def getInstalledMultiIds(self):
        stepIDs = list(self.__state.pairs)
        return (stepIDs, [ self.getStep(stepID).action.getPurchasedID() for stepID in stepIDs ])

    def getRawTree(self):
        return self.__tree

    def getState(self, implicitCopy=True):
        return VehicleState(self.__state.toRawData()) if implicitCopy else self.__state

    def getStep(self, stepID):
        return self.__stepsCache.get(stepID) or self.__buildPostProgressionStep(stepID)

    def getVehType(self):
        return self.__vehType

    def setState(self, state):
        self.__state = state
        self.__stepsCache.clear()

    def clone(self):
        return PostProgressionItem(self.getState(), self.__vehType)

    def iterOrderedSteps(self):
        return OrderedStepsIterator(self) if self.isExists() else ()

    def iterUnorderedSteps(self):
        return UnorederdStepsIterator(self) if self.isExists() else ()

    def __buildPostProgressionStep(self, stepID):
        stepItem = self.__stepsCache[stepID] = PostProgressionStepItem(self.__tree.steps[stepID], self)
        return stepItem
