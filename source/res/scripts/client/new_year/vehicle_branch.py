# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/vehicle_branch.py
import logging
import BigWorld
from adisp import async, process
from constants import REQUEST_COOLDOWN
from gui.SystemMessages import SM_TYPE
from gui.impl.dialogs import dialogs
from gui.shared.formatters.currency import getBWFormatter
from gui.shared.gui_items.processors import Processor, makeI18nError, plugins, makeNYSuccess
from gui.shared.money import Money, Currency
from helpers import dependency, isPlayerAccount
from helpers.time_utils import getServerUTCTime
from items.components.ny_constants import NY_BRANCH_MIN_LEVEL, NY_BRANCH_MAX_LEVEL
from ny_common.settings import NYVehBranchConsts
from shared_utils import first
from skeletons.festivity_factory import IFestivityFactory
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
EMPTY_VEH_INV_ID = 0

@async
def _asyncSleep(time, callback=None):
    BigWorld.callback(time, lambda *_: callback(None))


def _unpackVehicleBonus(dictBonus):
    return first(dictBonus.iteritems())


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getVehicleChangePrice(lobbyCtx=None):
    return lobbyCtx.getServerSettings().getNewYearVehBranchConfig().get(NYVehBranchConsts.VEH_CHANGE_PRICE, [])


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getNewYearStyleID(lobbyCtx=None):
    return lobbyCtx.getServerSettings().getNewYearVehBranchConfig().get(NYVehBranchConsts.STYLE_ID, [])


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getInEventCooldown(lobbyCtx=None):
    return lobbyCtx.getServerSettings().getNewYearVehBranchConfig().get(NYVehBranchConsts.VEH_CHANGE_COOLDOWN, [])


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getVehicleBonusConfig(lobbyCtx=None):
    config = lobbyCtx.getServerSettings().getNewYearVehBranchConfig().get(NYVehBranchConsts.VEH_BRANCH_BONUS, {})
    return {vehType:_unpackVehicleBonus(vehBonus) for vehType, vehBonus in config.iteritems()}


def getBonusByVehicle(vehicle):
    config = getVehicleBonusConfig()
    return config.get(vehicle.type)


class VehicleSlot(object):
    __slots__ = ('__slotID',)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, slotID):
        self.__slotID = slotID

    def getVehicle(self):
        invID = self._itemsCache.items.festivity.getVehicleBranch()[self.__slotID]
        return self._itemsCache.items.getVehicle(invID)

    def getCooldown(self):
        cooldown = 0
        vehicleCooldown = self._itemsCache.items.festivity.getVehicleCooldown()
        if len(vehicleCooldown) > self.__slotID:
            cooldown = vehicleCooldown[self.__slotID] - getServerUTCTime()
        return cooldown if cooldown > 0 else None

    def getVehicleLvl(self):
        return NY_BRANCH_MIN_LEVEL + self.__slotID

    def getSlotID(self):
        return self.__slotID

    def isAvailable(self):
        return self._itemsCache.items.festivity.getMaxLevel() >= self.getVehicleLvl()

    def getChangePrice(self):
        creditsAmount, goldAmount = getVehicleChangePrice()[self.getSlotID()]
        return Money(credits=creditsAmount, gold=goldAmount)

    def isFree(self):
        return self.isAvailable() and self.getVehicle() is None and self.getCooldown() is None


class VehicleBranch(object):
    __slots__ = ('__slots',)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        slotsCount = NY_BRANCH_MAX_LEVEL - NY_BRANCH_MIN_LEVEL + 1
        self.__slots = [ VehicleSlot(ind) for ind in xrange(slotsCount) ]

    def getVehicleSlots(self):
        return self.__slots

    def getSlotByLevel(self, level):
        return self.__slots[level - NY_BRANCH_MIN_LEVEL] if NY_BRANCH_MIN_LEVEL <= level <= NY_BRANCH_MAX_LEVEL else None

    def isVehicleInBranch(self, vehicle):
        return vehicle.invID in self._itemsCache.items.festivity.getVehicleBranch()

    def getFreeVehicleSlots(self):
        return [ slot for slot in self.__slots if slot.isFree() ]

    def hasAvailableSlots(self):
        return self._itemsCache.items.festivity.getMaxLevel() >= NY_BRANCH_MIN_LEVEL


class SetVehicleBranchProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)
    _CURRENCY_TO_SM_TYPE = {Currency.CREDITS: SM_TYPE.NewYearVehicleBranchCredits,
     Currency.GOLD: SM_TYPE.NewYearVehicleBranchGold}

    def __init__(self, invID, slotID):
        self.__isPaidVehicleSet = False
        confirmators = []
        slot = self._getSlot(slotID)
        if invID and slot.getCooldown() is not None and self._festivityFactory.getController().isPostEvent():
            confirmators.append(plugins.AsyncDialogConfirmator(dialogs.showSetVehicleBranchConfirm, invID, slotID))
            self.__isPaidVehicleSet = True
        super(SetVehicleBranchProcessor, self).__init__(confirmators)
        self.__invID = invID
        self.__slotID = slotID
        return

    def _getMessagePrefix(self):
        pass

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('{}/server_error'.format(self._getMessagePrefix()))

    def _successHandler(self, code, ctx=None):
        if self.__isPaidVehicleSet:
            slot = self._getSlot(self.__slotID)
            price = slot.getChangePrice()
            currency = price.getCurrency()
            amount = int(price.get(currency))
            return makeNYSuccess(self._getSysMsgKey(currency), type=self._getSysMsgType(currency), money=getBWFormatter(currency)(amount))
        return super(SetVehicleBranchProcessor, self)._successHandler(code, ctx)

    def _request(self, callback):
        _logger.debug('Make server request to set vehicle slot in vehicle branch:(slotID - %s)', self.__slotID)
        self._festivityFactory.getProcessor().setVehicleBranch(self.__invID, self.__slotID + NY_BRANCH_MIN_LEVEL, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))

    def _getSlot(self, slotID):
        return self._festivityFactory.getController().getVehicleBranch().getVehicleSlots()[slotID]

    def _getSysMsgKey(self, currency):
        return '{}/{}/success'.format(self._getMessagePrefix(), currency)

    def _getSysMsgType(self, currency):
        return self._CURRENCY_TO_SM_TYPE.get(currency, SM_TYPE.NewYearVehicleBranchCredits)


class ApplyVehicleBranchStyleProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, invID, parent=None):
        super(ApplyVehicleBranchStyleProcessor, self).__init__()
        self.__invID = invID

    @process
    def _request(self, callback):
        yield _asyncSleep(REQUEST_COOLDOWN.NEW_YEAR_SET_CAMOUFLAGE)
        if not isPlayerAccount():
            return
        _logger.debug('Make server request to apply style for vehicle from vehicle branch:(invID - %s)', self.__invID)
        self._festivityFactory.getProcessor().setVehicleCamouflage(self.__invID, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))
