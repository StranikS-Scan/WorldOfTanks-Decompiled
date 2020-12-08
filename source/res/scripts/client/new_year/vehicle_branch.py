# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/vehicle_branch.py
import logging
from typing import Tuple, Optional, List, TYPE_CHECKING
import BigWorld
from adisp import async, process
from constants import REQUEST_COOLDOWN
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.dialogs.dialogs import showSetVehicleBranchConfirm
from gui.impl.gen import R
from gui.impl.new_year.new_year_helper import formatRomanNumber
from gui.shared.formatters.currency import getBWFormatter
from gui.shared.gui_items.processors import Processor, makeI18nError, plugins, makeNYSuccess
from gui.shared.money import Money, Currency
from helpers import dependency, isPlayerAccount
from helpers.time_utils import getServerUTCTime
from items.components.ny_constants import NY_BRANCH_MIN_LEVEL, NY_BRANCH_MAX_LEVEL, VEH_BRANCH_EXTRA_SLOT_TOKEN
from new_year.ny_constants import PERCENT
from ny_common.VehBranchConfig import BRANCH_SLOT_TYPE
from ny_common.settings import NYVehBranchConsts
from shared_utils import first
from skeletons.festivity_factory import IFestivityFactory
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from cache import cached_property
if TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
_logger = logging.getLogger(__name__)
EMPTY_VEH_INV_ID = 0
SlotBonusType = Tuple[Optional[str], Optional[float]]
EmptyBonus = (None, None)

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
    return lobbyCtx.getServerSettings().getNewYearVehBranchConfig().get(NYVehBranchConsts.VEH_CHANGE_COOLDOWN, {})


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getRegularSlotBonusConfig(lobbyCtx=None):
    config = lobbyCtx.getServerSettings().getNewYearVehBranchConfig().get(NYVehBranchConsts.REGULAR_SLOT_BONUS, {})
    return {vehType:_unpackVehicleBonus(vehBonus) for vehType, vehBonus in config.iteritems()}


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getExtraSlotBonusesConfig(lobbyCtx=None):
    config = lobbyCtx.getServerSettings().getNewYearVehBranchConfig().get(NYVehBranchConsts.EXTRA_SLOT_BONUS_CHOICES, {})
    return {choiceID:_unpackVehicleBonus(vehBonus) for choiceID, vehBonus in config.iteritems()}


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getVehicleSlotsInfo(lobbyCtx=None):
    return lobbyCtx.getServerSettings().getNewYearVehBranchConfig().get(NYVehBranchConsts.SLOTS, {})


class VehicleSlot(object):
    __slots__ = ('__slotID',)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, slotID):
        self.__slotID = slotID

    def getVehicle(self):
        invID = self._getVehicleInvID()
        return self._itemsCache.items.getVehicle(invID) if invID != EMPTY_VEH_INV_ID else None

    def getCooldown(self):
        cooldown = 0
        vehicleCooldown = self._itemsCache.items.festivity.getVehicleCooldown()
        if len(vehicleCooldown) > self.__slotID:
            cooldown = vehicleCooldown[self.__slotID] - getServerUTCTime()
        return cooldown if cooldown > 0 else None

    def getBonusChoiceID(self):
        return self._itemsCache.items.festivity.getVehicleBonusChoices()[self.__slotID]

    def getVehicleLvl(self, slotsInfo=None):
        if slotsInfo is None:
            slotsInfo = getVehicleSlotsInfo()
        return min(slotsInfo[self.__slotID][NYVehBranchConsts.VEHICLE_LEVELS])

    def getSlotID(self):
        return self.__slotID

    def isAvailable(self):
        slotInfo = getVehicleSlotsInfo()[self.__slotID]
        slotType = slotInfo[NYVehBranchConsts.SLOT_TYPE]
        if slotType == BRANCH_SLOT_TYPE.REGULAR:
            return self._itemsCache.items.festivity.getMaxLevel() >= min(slotInfo[NYVehBranchConsts.VEHICLE_LEVELS])
        return self._itemsCache.items.tokens.isTokenAvailable(VEH_BRANCH_EXTRA_SLOT_TOKEN) if slotType == BRANCH_SLOT_TYPE.EXTRA else False

    def getChangePrice(self):
        price = getVehicleChangePrice()[self.getSlotType()]
        return Money(credits=price.get('credits', 0), gold=price.get('gold', 0))

    def isFree(self):
        return self.isAvailable() and self.getVehicle() is None and self.getCooldown() is None

    def getVehicleLevelsRange(self):
        levelsRange = sorted(getVehicleSlotsInfo()[self.__slotID][NYVehBranchConsts.VEHICLE_LEVELS])
        if self.getSlotType() == BRANCH_SLOT_TYPE.REGULAR:
            resultLevelsRange = levelsRange
        else:
            maxLevel = max(self._itemsCache.items.festivity.getMaxLevel(), levelsRange[0])
            resultLevelsRange = [ level for level in levelsRange if level <= maxLevel ]
        return resultLevelsRange

    def getSlotType(self, slotsInfo=None):
        if slotsInfo is None:
            slotsInfo = getVehicleSlotsInfo()
        return slotsInfo[self.__slotID][NYVehBranchConsts.SLOT_TYPE]

    def getLevelStr(self):
        if self.getSlotType() == BRANCH_SLOT_TYPE.REGULAR:
            level = formatRomanNumber(self.getVehicleLvl())
        else:
            levelsRange = self.getVehicleLevelsRange()
            if len(levelsRange) == 1:
                level = formatRomanNumber(levelsRange[0])
            else:
                level = backport.text(R.strings.ny.vehiclesView.levelsStr(), minLevel=formatRomanNumber(levelsRange[0]), maxLevel=formatRomanNumber(levelsRange[-1]))
        return level

    def getExtraSlotBonus(self, choiceID):
        return getExtraSlotBonusesConfig().get(choiceID, None) if self.getSlotType() == BRANCH_SLOT_TYPE.EXTRA else None

    def getDefaultSlotCooldown(self):
        return getInEventCooldown().get(self.getSlotType(), None)

    def getSlotBonus(self):
        if self.getSlotType() == BRANCH_SLOT_TYPE.EXTRA:
            choiceID = self.getBonusChoiceID()
            return getExtraSlotBonusesConfig().get(choiceID, EmptyBonus)
        else:
            vehicle = self.getVehicle()
            if vehicle is not None:
                config = getRegularSlotBonusConfig()
                return config.get(vehicle.type, EmptyBonus)
            return EmptyBonus

    def isBonusChoiceAllowed(self):
        return self.getSlotType() == BRANCH_SLOT_TYPE.EXTRA

    def _getVehicleInvID(self):
        return self._itemsCache.items.festivity.getVehicleBranch()[self.__slotID]


class VehicleBranch(object):
    _itemsCache = dependency.descriptor(IItemsCache)

    @cached_property
    def __slots(self):
        return [ VehicleSlot(ind) for ind in getVehicleSlotsInfo().iterkeys() ]

    def getVehicleSlots(self):
        return self.__slots

    def hasSlotWithLevel(self, level):
        return True if NY_BRANCH_MIN_LEVEL <= level <= NY_BRANCH_MAX_LEVEL else False

    def isVehicleInBranch(self, vehicle):
        return vehicle.invID in self._itemsCache.items.festivity.getVehicleBranch()

    def getFreeVehicleSlots(self):
        return [ slot for slot in self.__slots if slot.isFree() ]

    def hasAvailableSlots(self):
        items = self._itemsCache.items
        return items.festivity.getMaxLevel() >= NY_BRANCH_MIN_LEVEL or items.tokens.isTokenAvailable(VEH_BRANCH_EXTRA_SLOT_TOKEN)

    def getSlotForVehicle(self, vehInvID):
        vehicleBranch = self._itemsCache.items.festivity.getVehicleBranch()
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


class SetVehicleBranchProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)
    _CURRENCY_TO_SM_TYPE = {Currency.CREDITS: SM_TYPE.NewYearVehicleBranchCredits,
     Currency.GOLD: SM_TYPE.NewYearVehicleBranchGold,
     None: SM_TYPE.NewYearVehicleBranchSetVehicle}

    def __init__(self, invID, slotID):
        self.__isPaidVehicleSet = False
        confirmators = []
        slot = self._getSlot(slotID)
        if invID and slot.getCooldown() is not None and self._festivityFactory.getController().isPostEvent():
            confirmators.append(plugins.AsyncDialogConfirmator(showSetVehicleBranchConfirm, invID, slotID))
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
        slot = self._getSlot(self.__slotID)
        slotType = BRANCH_SLOT_TYPE.getSlotTypeNameByID(slot.getSlotType())
        if self.__isPaidVehicleSet:
            price = slot.getChangePrice()
            currency = price.getCurrency()
            amount = int(price.get(currency))
            return makeNYSuccess(self._getSysMsgKey(slotType, currency), type=self._getSysMsgType(currency), money=getBWFormatter(currency)(amount))
        else:
            return makeNYSuccess(self._getSysMsgKey(slotType), type=self._getSysMsgType(None)) if slot.getVehicle() is not None else super(SetVehicleBranchProcessor, self)._successHandler(code, ctx)

    def _request(self, callback):
        _logger.debug('Make server request to set vehicle slot in vehicle branch:(slotID - %s)', self.__slotID)
        self._festivityFactory.getProcessor().setVehicleBranch(self.__invID, self.__slotID, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))

    def _getSlot(self, slotID):
        return self._festivityFactory.getController().getVehicleBranch().getVehicleSlots()[slotID]

    def _getSysMsgKey(self, slotType, currency=None):
        return '{}/{}/{}/success'.format(self._getMessagePrefix(), slotType, currency) if currency is not None else '{}/{}/success'.format(self._getMessagePrefix(), slotType)

    def _getSysMsgType(self, currency):
        return self._CURRENCY_TO_SM_TYPE.get(currency, SM_TYPE.NewYearVehicleBranchSetVehicle)


class SetVehicleBranchSlotBonusProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, slotID, choiceID):
        super(SetVehicleBranchSlotBonusProcessor, self).__init__()
        self.__slotID = slotID
        self.__choiceID = choiceID

    def _getMessagePrefix(self):
        pass

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('{}/server_error'.format(self._getMessagePrefix()))

    def _successHandler(self, code, ctx=None):
        bonus = self._getSlot(self.__slotID).getExtraSlotBonus(self.__choiceID)
        return makeNYSuccess(self._getSysMsgKey(bonus[0]), type=SM_TYPE.NewYearVehicleBranchBonus, bonus=str(int(bonus[1] * PERCENT)) + '%') if bonus is not None else super(SetVehicleBranchSlotBonusProcessor, self)._successHandler(code, ctx)

    def _request(self, callback):
        _logger.debug('Make server request to set vehicle slot bonus in vehicle branch:(slotID - %s)', self.__slotID)
        self._festivityFactory.getProcessor().setVehicleBranchSlotBonus(self.__slotID, self.__choiceID, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))

    def _getSlot(self, slotID):
        return self._festivityFactory.getController().getVehicleBranch().getVehicleSlots()[slotID]

    def _getSysMsgKey(self, bonusName):
        return '{}/{}/success'.format(self._getMessagePrefix(), bonusName)


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
