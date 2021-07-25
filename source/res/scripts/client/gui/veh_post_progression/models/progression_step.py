# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_post_progression/models/progression_step.py
import typing
from enum import Enum, unique
from gui.veh_post_progression.models.ext_money import ExtendedMoney, ExtendedGuiItemEconomyCode
from gui.veh_post_progression.models.modifications import getActionModel
from gui.veh_post_progression.models.purchase import PurchaseProvider, PurchaseCheckResult, VALID_CHECK_RESULT
from items.components.post_progression_components import TreeStep
if typing.TYPE_CHECKING:
    from items.artefacts_helpers import VehicleFilter
    from gui.veh_post_progression.models.modifications import SimpleModItem, MultiModsItem, FeatureModItem, RoleSlotModItem
    from gui.veh_post_progression.models.progression import PostProgressionItem
    from post_progression_common import VehicleState

@unique
class PostProgressionStepState(Enum):
    RESTRICTED = 'restricted'
    LOCKED = 'locked'
    UNLOCKED = 'unlocked'
    RECEIVED = 'received'


_STATE_TO_RESTRICTION = {PostProgressionStepState.RESTRICTED: ExtendedGuiItemEconomyCode.STEP_RESTRICTED,
 PostProgressionStepState.LOCKED: ExtendedGuiItemEconomyCode.STEP_LOCKED,
 PostProgressionStepState.UNLOCKED: ExtendedGuiItemEconomyCode.UNDEFINED,
 PostProgressionStepState.RECEIVED: ExtendedGuiItemEconomyCode.STEP_RECIEVED}

class PostProgressionStepItem(PurchaseProvider):
    __slots__ = ('__action', '__descriptor', '__isRestricted', '__price', '__state')

    def __init__(self, descriptor, progression):
        limits = descriptor.vehicleFilter
        self.__action = getActionModel(descriptor.id, descriptor.action, progression)
        self.__descriptor = descriptor
        self.__isRestricted = limits is not None and not limits.checkCompatibilityWithVehType(progression.getVehType())
        self.__price = ExtendedMoney(**descriptor.price)
        self.__state = self.__getState(progression.getState(implicitCopy=False))
        return

    def __repr__(self):
        return 'PostProgressionStepItem <stepID: {}, state: {}>'.format(self.stepID, self.getState().value)

    @property
    def action(self):
        return self.__action

    @property
    def stepID(self):
        return self.__descriptor.id

    def isLocked(self):
        return self.getState() is PostProgressionStepState.LOCKED

    def isReceived(self):
        return self.getState() is PostProgressionStepState.RECEIVED

    def isRestricted(self):
        return self.__isRestricted

    def isUnlocked(self):
        return self.getState() is PostProgressionStepState.UNLOCKED

    def getLevel(self):
        return self.__descriptor.level

    def getNextStepIDs(self):
        return self.__descriptor.unlocks

    def getParentStepID(self):
        return self.__descriptor.requiredUnlocks[0] if self.__descriptor.requiredUnlocks else None

    def getPrice(self):
        return self.__price

    def getRestrictions(self):
        return self.__descriptor.vehicleFilter

    def getState(self):
        return self.__state

    def mayPurchase(self, balance, ignoreState=False):
        stateCheck = VALID_CHECK_RESULT if ignoreState else self.__getStateCheckResult()
        return stateCheck and self.mayConsume(balance, self.getPrice())

    def mayPurchaseWithExchange(self, balance, creditsRate, ignoreState=False):
        stateCheck = VALID_CHECK_RESULT if ignoreState else self.__getStateCheckResult()
        return stateCheck and self.mayConsumeWithExhange(balance, self.getPrice(), creditsRate)

    def __getState(self, progressionState):
        if self.isRestricted():
            return PostProgressionStepState.RESTRICTED
        if progressionState.isUnlocked(self.stepID):
            return PostProgressionStepState.RECEIVED
        for stepID in self.__descriptor.requiredUnlocks:
            if not progressionState.isUnlocked(stepID):
                return PostProgressionStepState.LOCKED

        return PostProgressionStepState.UNLOCKED

    def __getStateCheckResult(self):
        restriction = _STATE_TO_RESTRICTION[self.getState()]
        return PurchaseCheckResult(restriction == ExtendedGuiItemEconomyCode.UNDEFINED, restriction)
