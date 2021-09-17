# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_post_progression/models/modifications.py
import typing
from enum import Enum, unique
from gui.impl.gen import R
from gui.impl.gen_utils import DynAccessor
from gui.veh_post_progression.models.ext_money import ExtendedMoney, ExtendedGuiItemEconomyCode, EXT_MONEY_UNDEFINED, EXT_MONEY_ZERO_CREDITS
from gui.veh_post_progression.models.purchase import PurchaseProvider, PurchaseCheckResult, VALID_CHECK_RESULT
from gui.shared.gui_items import collectKpi, KPI, GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from helpers import dependency
from items import vehicles
from items.components.supply_slot_categories import SlotCategories
from post_progression_common import ACTION_TYPES, PAIR_TYPES, ROLESLOT_FEATURE
from post_progression_prices_common import getPostProgressionPrice
from shared_utils import first
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.shared.gui_items.items_actions.actions import SetEquipmentSlotType, PurchasePostProgressionPair, DiscardPostProgressionPairs
    from gui.veh_post_progression.models.progression import PostProgressionItem
    from items.components.post_progression_components import Modification, PairModification, ProgressionFeature

@unique
class PostProgressionActionState(Enum):
    CHANGEABLE = 'changeable'
    PERSISTENT = 'persistent'
    SELECTABLE = 'selectable'


@unique
class PostProgressionActionTooltip(Enum):
    SIMPLEMOD = 'simplemod'
    MULTIMOD = 'multimod'
    FEATURE = 'feature'
    ROLESLOT = 'roleSlotFeature'


_ACTION_RES_STUB = R.strings.artefacts.actionStub
_IDX_TO_PAIR_TYPE = {0: PAIR_TYPES.FIRST,
 1: PAIR_TYPES.SECOND}
_NOT_PURCHASED_IDX = -1
_PAIR_TYPE_TO_IDX = {val:key for key, val in _IDX_TO_PAIR_TYPE.iteritems()}
_STATE_TO_RESTRICTION = {PostProgressionActionState.CHANGEABLE: ExtendedGuiItemEconomyCode.UNDEFINED,
 PostProgressionActionState.PERSISTENT: ExtendedGuiItemEconomyCode.MOD_PERSISTENT,
 PostProgressionActionState.SELECTABLE: ExtendedGuiItemEconomyCode.UNDEFINED}

class PostProgressionActionItem(PurchaseProvider):
    __slots__ = ('_descriptor', '_parentStepID', '_price', '_state', '_tooltip')

    def __init__(self, parentStepID, descriptor, progression):
        self._descriptor = descriptor
        self._parentStepID = parentStepID
        self._price = self._getDefaultPrice(descriptor)
        self._state = self._getDefaultState(progression)
        self._tooltip = self._getDefaultTooltip()

    def __repr__(self):
        return '{} <id: {}, name: {}>'.format(self.__class__.__name__, self.actionID, self.getTechName())

    @property
    def actionID(self):
        return self._descriptor.id

    @property
    def actionType(self):
        return self._descriptor.actionType

    @property
    def itemTypeID(self):
        return GUI_ITEM_TYPE.VEH_POST_PROGRESSION

    @property
    def itemTypeName(self):
        return GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.VEH_POST_PROGRESSION]

    @property
    def parentStepID(self):
        return self._parentStepID

    def isChangeable(self):
        return self._state is PostProgressionActionState.CHANGEABLE

    def isDisabled(self):
        return False

    def isFeatureAction(self):
        return False

    def isMultiAction(self):
        return False

    def isPersistent(self):
        return self._state is PostProgressionActionState.PERSISTENT

    def isSelectable(self):
        return self._state is PostProgressionActionState.SELECTABLE

    def getActiveID(self):
        return self.actionID

    def getKpi(self, vehicle=None):
        return []

    def getImageName(self):
        return self._descriptor.imgName

    def getLocName(self):
        return self._descriptor.locName

    def getLocNameRes(self):
        return R.strings.artefacts.dyn(self.getLocName(), _ACTION_RES_STUB).name

    def getLocSplitNameRes(self):
        splitName = R.strings.artefacts.dyn(self.getLocName()).dyn('splitName')
        return splitName if splitName.exists() else self.getLocNameRes()

    def getPrice(self):
        return self._price

    def getServerAction(self, factory, vehicle):
        return None

    def getSlotCategory(self):
        return SlotCategories.UNIVERSAL

    def getState(self):
        return self._state

    def getTechName(self):
        return self._descriptor.name

    def getTooltip(self):
        return self._tooltip

    def mayPurchase(self, balance, ignoreState=False):
        stateCheck = VALID_CHECK_RESULT if ignoreState else self._getStateCheckResult()
        return stateCheck and self.mayConsume(balance, self.getPrice())

    def mayPurchaseWithExchange(self, balance, creditsRate, ignoreState=False):
        stateCheck = VALID_CHECK_RESULT if ignoreState else self._getStateCheckResult()
        return stateCheck and self.mayConsumeWithExhange(balance, self.getPrice(), creditsRate)

    def _getDefaultPrice(self, descriptor):
        raise NotImplementedError

    def _getDefaultState(self, progression):
        raise NotImplementedError

    def _getDefaultTooltip(self):
        raise NotImplementedError

    def _getStateCheckResult(self):
        restriction = _STATE_TO_RESTRICTION[self.getState()]
        return PurchaseCheckResult(restriction == ExtendedGuiItemEconomyCode.UNDEFINED, restriction)


class SimpleModItem(PostProgressionActionItem):

    def __init__(self, parentStepID, descriptor, progression, externalPrice=None):
        super(SimpleModItem, self).__init__(parentStepID, descriptor, progression)
        self.__applyExternalPrice(externalPrice)

    def getKpi(self, vehicle=None):
        return collectKpi(self._descriptor, vehicle)

    def _getDefaultPrice(self, descriptor):
        return EXT_MONEY_UNDEFINED

    def _getDefaultState(self, progression):
        return PostProgressionActionState.PERSISTENT

    def _getDefaultTooltip(self):
        return PostProgressionActionTooltip.SIMPLEMOD

    def __applyExternalPrice(self, externalPrice):
        isExternalPrice = bool(externalPrice)
        self._price = externalPrice if isExternalPrice else self._price
        self._state = PostProgressionActionState.CHANGEABLE if isExternalPrice else self._state
        self._tooltip = PostProgressionActionTooltip.MULTIMOD if isExternalPrice else self._tooltip


class MultiModsItem(PostProgressionActionItem):
    __slots__ = ('__modifications', '__purchasedIdx', '__idToIdx')

    def __init__(self, parentStepID, descriptor, progression):
        super(MultiModsItem, self).__init__(parentStepID, descriptor, progression)
        pairType = progression.getState(implicitCopy=False).getPair(self.parentStepID)
        self.__purchasedIdx = _PAIR_TYPE_TO_IDX[pairType] if pairType is not None else -1
        self.__fillModifications(parentStepID, descriptor, progression)
        return

    def __repr__(self):
        innerRepr = ' with mods: {}, purchasedIdx: {}'.format(self.modifications, self.getPurchasedIdx())
        return super(MultiModsItem, self).__repr__() + innerRepr

    @property
    def modifications(self):
        return self.__modifications

    def isMultiAction(self):
        return True

    def isPurchased(self):
        return self.__purchasedIdx != _NOT_PURCHASED_IDX

    def getActiveID(self):
        return self.getPurchasedID()

    def getInnerIdx(self, modificationID):
        return self.__idToIdx[modificationID]

    def getInnerPairType(self, modificationID):
        return _IDX_TO_PAIR_TYPE[self.__idToIdx[modificationID]]

    def getKpi(self, vehicle=None):
        return self.__modifications[self.__purchasedIdx].getKpi() if self.isPurchased() else []

    def getModificationByID(self, modificationID):
        return self.__modifications[self.getInnerIdx(modificationID)]

    def getPurchasedID(self):
        return self.__modifications[self.__purchasedIdx].actionID if self.isPurchased() else None

    def getPurchasedIdx(self):
        return self.__purchasedIdx

    def getPurchasedModification(self):
        return self.__modifications[self.__purchasedIdx] if self.isPurchased() else None

    def getServerAction(self, factory, vehicle, modID=_NOT_PURCHASED_IDX):
        return factory.getAction(factory.DISCARD_POST_PROGRESSION_PAIRS, vehicle, [self.parentStepID], [modID]) if self.getPurchasedID() == modID else factory.getAction(factory.PURCHASE_POST_PROGRESSION_PAIR, vehicle, self.parentStepID, modID)

    def mayDiscardInner(self):
        return PurchaseCheckResult(False, ExtendedGuiItemEconomyCode.MULTI_NOT_PURCHASED) if not self.isPurchased() else VALID_CHECK_RESULT

    def mayPurchaseInner(self, balance, modificationID, ignoreState=False):
        stateCheck = VALID_CHECK_RESULT if ignoreState else self.__getStateCheckResult(modificationID)
        return stateCheck and self.__getModificationByID(modificationID).mayPurchase(balance, ignoreState)

    def mayPurchaseInnerWithExchange(self, balance, creditsRate, modificationID, ignoreState=False):
        stateCheck = VALID_CHECK_RESULT if ignoreState else self.__getStateCheckResult(modificationID)
        return stateCheck and self.__getModificationByID(modificationID).mayPurchaseWithExchange(balance, creditsRate, ignoreState)

    def _getDefaultPrice(self, descriptor):
        return EXT_MONEY_UNDEFINED

    def _getDefaultState(self, progression):
        return PostProgressionActionState.CHANGEABLE

    def _getDefaultTooltip(self):
        return PostProgressionActionTooltip.MULTIMOD

    def __getModificationByID(self, modificationID):
        return self.__modifications[self.__idToIdx[modificationID]]

    def __getStateCheckResult(self, modificationID):
        modificationIdx = self.__idToIdx.get(modificationID)
        if modificationIdx is None:
            return PurchaseCheckResult(False, ExtendedGuiItemEconomyCode.MULTI_NOT_EXISTS)
        else:
            return PurchaseCheckResult(False, ExtendedGuiItemEconomyCode.MULTI_NOT_EMPTY) if self.getPurchasedID() == modificationID else VALID_CHECK_RESULT

    def __fillModifications(self, parentStepID, descriptor, progression):
        self.__idToIdx = {}
        self.__modifications = []
        for idx, (modDesc, priceTag) in enumerate(vehicles.g_cache.postProgression().getChildActions(descriptor)):
            self.__modifications.append(SimpleModItem(parentStepID, modDesc, progression, ExtendedMoney(**getPostProgressionPrice(priceTag, progression.getVehType()))))
            self.__idToIdx[modDesc.id] = idx


class FeatureModItem(PostProgressionActionItem):
    __slots__ = ('__isDisabled',)

    def __init__(self, parentStepID, descriptor, progression):
        super(FeatureModItem, self).__init__(parentStepID, descriptor, progression)
        self.__isDisabled = not progression.isFeatureEnabled(self.getTechName())

    def isDisabled(self):
        return self.__isDisabled

    def isFeatureAction(self):
        return True

    def getActiveID(self):
        return None

    def _getDefaultPrice(self, descriptor):
        return EXT_MONEY_UNDEFINED

    def _getDefaultState(self, progression):
        return PostProgressionActionState.PERSISTENT

    def _getDefaultTooltip(self):
        return PostProgressionActionTooltip.FEATURE


class RoleSlotModItem(FeatureModItem):
    __itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__slotCategory',)

    def __init__(self, parentStepID, descriptor, progression):
        super(RoleSlotModItem, self).__init__(parentStepID, descriptor, progression)
        self.__applyDynamicSlotCategory(progression.getVehType())

    def __repr__(self):
        innerRepr = ' with state: {}, category: {}'.format(self.getState(), self.getSlotCategory())
        return super(RoleSlotModItem, self).__repr__() + innerRepr

    def getServerAction(self, factory, vehicle):
        return factory.getAction(factory.SET_EQUIPMENT_SLOT_TYPE, vehicle)

    def getSlotCategory(self):
        return self.__slotCategory

    def _getDefaultPrice(self, descriptor):
        return EXT_MONEY_ZERO_CREDITS

    def _getDefaultState(self, progression):
        return PostProgressionActionState.SELECTABLE

    def _getDefaultTooltip(self):
        return PostProgressionActionTooltip.ROLESLOT

    def __applyDynamicSlotCategory(self, vehicleType):
        items = self.__itemsCache.items
        dynamicSlotID = items.inventory.getDynSlotTypeID(vehicleType.compactDescr)
        if dynamicSlotID > 0:
            self._price = ExtendedMoney(**items.shop.customRoleSlotChangeCost(vehicleType, isRaw=True))
            self._state = PostProgressionActionState.CHANGEABLE
            self.__slotCategory = first(vehicles.g_cache.supplySlots().slotDescrs[dynamicSlotID].categories)
        else:
            self.__slotCategory = SlotCategories.UNIVERSAL


class _ActionByTypeFactory(object):
    __slots__ = ('_producedType',)

    def __init__(self, producedType):
        self._producedType = producedType

    def construct(self, parentStepID, descriptor, progression):
        return self._construct(self._producedType, parentStepID, descriptor, progression)

    @classmethod
    def _construct(cls, producedType, parentStepID, descriptor, progression):
        return producedType(parentStepID, descriptor, progression)


class _ActionByNameFactory(_ActionByTypeFactory):
    __slots__ = ('_nameToType',)

    def __init__(self, producedType, nameToType):
        super(_ActionByNameFactory, self).__init__(producedType)
        self._nameToType = nameToType

    def construct(self, parentStepID, descriptor, progression):
        producedType = self._nameToType.get(descriptor.name, self._producedType)
        return self._construct(producedType, parentStepID, descriptor, progression)


_ACTION_TYPE_TO_MODEL = {ACTION_TYPES.MODIFICATION: _ActionByTypeFactory(SimpleModItem),
 ACTION_TYPES.PAIR_MODIFICATION: _ActionByTypeFactory(MultiModsItem),
 ACTION_TYPES.FEATURE: _ActionByNameFactory(FeatureModItem, {ROLESLOT_FEATURE: RoleSlotModItem})}

def getActionModel(parentStepID, stepActionInfo, progression):
    actionType, actionID = stepActionInfo
    actionDescriptor = vehicles.g_cache.postProgression().getAction(actionType, actionID)
    return _ACTION_TYPE_TO_MODEL[actionType].construct(parentStepID, actionDescriptor, progression)
