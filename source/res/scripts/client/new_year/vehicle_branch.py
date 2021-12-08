# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/vehicle_branch.py
import logging
import typing
import BigWorld
from adisp import async
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.lobby.new_year.dialogs.dialogs import showSetVehicleBranchConfirm
from gui.impl.gen import R
from gui.impl.new_year.new_year_helper import formatRomanNumber
from gui.shared.formatters.currency import getBWFormatter
from gui.shared.gui_items.processors import Processor, makeI18nError, plugins, makeNYSuccess
from gui.shared.money import Money, Currency
from helpers import dependency
from helpers.time_utils import getServerUTCTime
from items.components.ny_constants import NY_BRANCH_MIN_LEVEL, NY_BRANCH_MAX_LEVEL, VEH_BRANCH_EXTRA_SLOT_TOKEN
from new_year.ny_constants import PERCENT
from ny_common.settings import NYVehBranchConsts
from shared_utils import first, findFirst
from skeletons.festivity_factory import IFestivityFactory
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from cache import cached_property
from new_year.vehicle_branch_helpers import getVehicleChangePrice, getAvailableVehicleRange
if typing.TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple, Union
    from gui.shared.gui_items.Vehicle import Vehicle
    SlotBonusType = Tuple[Optional[str], Optional[float]]
_logger = logging.getLogger(__name__)
EMPTY_VEH_INV_ID = 0
EmptyBonus = (None, None)
_MIN_SLOT_LVL = 0
_EMPTY_TOKEN = ''

@async
def _asyncSleep(time, callback=None):
    BigWorld.callback(time, lambda *_: callback(None))


def _unpackVehicleBonus(dictBonus):
    return first(dictBonus.iteritems())


def getSlotBonusByType(bonusType):
    _, bValue = findFirst(lambda (t, v): t == bonusType, getSlotBonusChoicesConfig().itervalues(), ('', 0))
    return int(PERCENT * bValue)


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getInEventCooldown(lobbyCtx=None):
    return lobbyCtx.getServerSettings().getNewYearVehBranchConfig().get(NYVehBranchConsts.VEH_CHANGE_COOLDOWN, 0)


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getSlotBonusChoicesConfig(lobbyCtx=None):
    config = lobbyCtx.getServerSettings().getNewYearVehBranchConfig().get(NYVehBranchConsts.SLOT_BONUS_CHOICES, {})
    return {choiceID:_unpackVehicleBonus(vehBonus) for choiceID, vehBonus in config.iteritems()}


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getVehicleSlotsInfo(lobbyCtx=None):
    return lobbyCtx.getServerSettings().getNewYearVehBranchConfig().get(NYVehBranchConsts.SLOTS, {})


def _getSlotName(slot, case='acc'):
    slotType = slot.getRestrictionType()
    slotKey = 'celeb' if slotType == NYVehBranchConsts.TOKEN else 'level'
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
        restriction = self.getRestrictionType()
        if restriction == NYVehBranchConsts.TOKEN:
            return self.__itemsCache.items.tokens.isTokenAvailable(self.getToken())
        return self.__itemsCache.items.festivity.getMaxLevel() >= self.getLevel() if restriction == NYVehBranchConsts.LEVEL else False

    def getRestrictionType(self):
        slotInfo = getVehicleSlotsInfo()[self.__slotID]
        if NYVehBranchConsts.LEVEL in slotInfo:
            return NYVehBranchConsts.LEVEL
        return NYVehBranchConsts.TOKEN if NYVehBranchConsts.TOKEN in slotInfo else NYVehBranchConsts.UNDEFINED

    def getLevel(self):
        return getVehicleSlotsInfo()[self.__slotID].get(NYVehBranchConsts.LEVEL, _MIN_SLOT_LVL)

    def getToken(self):
        return getVehicleSlotsInfo()[self.__slotID].get(NYVehBranchConsts.TOKEN, _EMPTY_TOKEN)

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
        return items.festivity.getMaxLevel() >= NY_BRANCH_MIN_LEVEL or items.tokens.isTokenAvailable(VEH_BRANCH_EXTRA_SLOT_TOKEN)

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


class SetVehicleBranchProcessor(Processor):
    __festivityFactory = dependency.descriptor(IFestivityFactory)
    __CURRENCY_TO_SM_TYPE = {Currency.CREDITS: SM_TYPE.NewYearVehicleBranchCredits,
     Currency.GOLD: SM_TYPE.NewYearVehicleBranchGold,
     None: SM_TYPE.NewYearVehicleBranchSetVehicle}

    def __init__(self, invID, slotID):
        self.__isPaidVehicleSet = False
        confirmators = []
        slot = self.__getSlot(slotID)
        if invID and slot.getCooldown() is not None and self.__festivityFactory.getController().isPostEvent():
            confirmators.append(plugins.AsyncDialogConfirmator(showSetVehicleBranchConfirm, invID, slotID))
            self.__isPaidVehicleSet = True
        super(SetVehicleBranchProcessor, self).__init__(confirmators)
        self.__invID = invID
        self.__slotID = slotID
        return

    def _request(self, callback):
        _logger.debug('Make server request to set vehicle slot in vehicle branch:(slotID - %s)', self.__slotID)
        self.__festivityFactory.getProcessor().setVehicleBranch(self.__invID, self.__slotID, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('{}/server_error'.format(self.__getMessagePrefix()))

    def _successHandler(self, code, ctx=None):
        slot = self.__getSlot(self.__slotID)
        if self.__isPaidVehicleSet:
            price = getVehicleChangePrice()
            currency = price.getCurrency()
            amount = int(price.get(currency))
            return self.__makeSuccess(currency, slot, money=getBWFormatter(currency)(amount))
        else:
            return self.__makeSuccess(None, slot) if slot.getVehicle() is not None else super(SetVehicleBranchProcessor, self)._successHandler(code, ctx)

    def __getSlot(self, slotID):
        return self.__festivityFactory.getController().getVehicleBranch().getVehicleSlots()[slotID]

    def __makeSuccess(self, currency, slot, **kwargs):
        return makeNYSuccess(self.__getSysMsgKey(currency), msgType=self.__getSysMsgType(currency), slotName=_getSlotName(slot), **kwargs)

    def __getSysMsgType(self, currency):
        return self.__CURRENCY_TO_SM_TYPE.get(currency, SM_TYPE.NewYearVehicleBranchSetVehicle)

    def __getSysMsgKey(self, currency=None):
        return '{}/{}/success'.format(self.__getMessagePrefix(), currency) if currency is not None else '{}/success'.format(self.__getMessagePrefix())

    def __getMessagePrefix(self):
        pass


class SetVehicleBranchSlotBonusProcessor(Processor):
    __festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, slotID, choiceID):
        super(SetVehicleBranchSlotBonusProcessor, self).__init__()
        self.__slotID = slotID
        self.__choiceID = choiceID

    def _getMessagePrefix(self):
        pass

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('{}/server_error'.format(self._getMessagePrefix()))

    def _successHandler(self, code, ctx=None):
        slot = self._getSlot(self.__slotID)
        bonus = slot.getExtraSlotBonus(self.__choiceID)
        return makeNYSuccess(self._getSysMsgKey(bonus[0]), msgType=SM_TYPE.NewYearVehicleBranchBonus, slotName=_getSlotName(slot, case='gen'), bonus=str(int(bonus[1] * PERCENT)) + '%') if bonus is not None else super(SetVehicleBranchSlotBonusProcessor, self)._successHandler(code, ctx)

    def _request(self, callback):
        _logger.debug('Make server request to set vehicle slot bonus in vehicle branch:(slotID - %s)', self.__slotID)
        self.__festivityFactory.getProcessor().setVehicleBranchSlotBonus(self.__slotID, self.__choiceID, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))

    def _getSlot(self, slotID):
        return self.__festivityFactory.getController().getVehicleBranch().getVehicleSlots()[slotID]

    def _getSysMsgKey(self, bonusName):
        return '{}/{}/success'.format(self._getMessagePrefix(), bonusName)
