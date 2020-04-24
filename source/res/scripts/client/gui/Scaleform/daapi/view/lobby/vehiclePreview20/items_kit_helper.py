# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview20/items_kit_helper.py
import itertools
import typing
from collections import Container, namedtuple
from sys import maxint
from CurrentVehicle import g_currentPreviewVehicle, g_currentVehicle
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from gui.Scaleform.locale.COMMON import COMMON
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_SHOP import RES_SHOP
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.VEHICLE_PREVIEW import VEHICLE_PREVIEW
from gui.shared.gui_items.Tankman import CrewTypes
from gui.shared.money import Currency, Money, MONEY_ZERO_GOLD
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.impl import backport
from gui.impl.gen import R
from items import EQUIPMENT_TYPES
from items import makeIntCompactDescrByID as makeCD
from items.components.c11n_constants import CustomizationType
from items.vehicles import NUM_OPTIONAL_DEVICE_SLOTS, NUM_EQUIPMENT_SLOTS_BY_TYPE, NUM_SHELLS_SLOTS
from shared_utils import findFirst, first, CONST_CONTAINER
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.goodies import IGoodiesCache
from web.web_client_api.common import ItemPackType, ItemPackTypeGroup, ItemPackEntry
from gui.shared.gui_items import vehicle_adjusters
from gui.shared.gui_items import GUI_ITEM_TYPE
from skeletons.gui.shared import IItemsCache
from helpers import dependency
from helpers.i18n import makeString as _ms
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.formatters import text_styles, icons

class ITEM_SORT_RULE(CONST_CONTAINER):
    REGULAR = 'regular'
    FRONTLINE = 'frontline'


OFFER_CHANGED_EVENT = 'offerChanged'
_NUM_REGULAR_EQUIPMENT_SLOTS = NUM_EQUIPMENT_SLOTS_BY_TYPE[EQUIPMENT_TYPES.regular]
_UNLIMITED_ITEMS_COUNT = -1
_EXCLUDE_ITEMS = {v for v in ItemPackTypeGroup.CREW} | {ItemPackType.FRONTLINE_TOKEN}
_ANY_ITEM_TYPE = {v for _, v in ItemPackType.getIterator()} - _EXCLUDE_ITEMS
_FRONTLINE_GIFTS = {v for _, v in ItemPackType.getIterator()} - {ItemPackType.FRONTLINE_TOKEN}
_NATIVE_ITEM_TYPE = set(itertools.chain(ItemPackTypeGroup.VEHICLE, ItemPackTypeGroup.ITEM))
_CUSTOMIZATION_ITEM_TYPE = set(itertools.chain(ItemPackTypeGroup.STYLE, ItemPackTypeGroup.CAMOUFLAGE, ItemPackTypeGroup.PAINT, ItemPackTypeGroup.DECAL, ItemPackTypeGroup.PROJECTION_DECAL, ItemPackTypeGroup.PERSONAL_NUMBER, ItemPackTypeGroup.MODIFICATION))
_CUSTOMIZATION_TYPES_MAP = {ItemPackType.STYLE: CustomizationType.STYLE,
 ItemPackType.CAMOUFLAGE_ALL: CustomizationType.CAMOUFLAGE,
 ItemPackType.CAMOUFLAGE_SUMMER: CustomizationType.CAMOUFLAGE,
 ItemPackType.CAMOUFLAGE_WINTER: CustomizationType.CAMOUFLAGE,
 ItemPackType.CAMOUFLAGE_DESERT: CustomizationType.CAMOUFLAGE,
 ItemPackType.PAINT_ALL: CustomizationType.PAINT,
 ItemPackType.PAINT_SUMMER: CustomizationType.PAINT,
 ItemPackType.PAINT_WINTER: CustomizationType.PAINT,
 ItemPackType.PAINT_DESERT: CustomizationType.PAINT,
 ItemPackType.DECAL_1: CustomizationType.DECAL,
 ItemPackType.DECAL_2: CustomizationType.DECAL,
 ItemPackType.PROJECTION_DECAL: CustomizationType.PROJECTION_DECAL,
 ItemPackType.PERSONAL_NUMBER: CustomizationType.PERSONAL_NUMBER,
 ItemPackType.MODIFICATION: CustomizationType.MODIFICATION}
_BOOSTER_ITEM_TYPE = set(ItemPackTypeGroup.GOODIE)
_UNCOUNTABLE_ITEM_TYPE = {ItemPackType.CUSTOM_PREMIUM,
 ItemPackType.CUSTOM_PREMIUM_PLUS,
 ItemPackType.CUSTOM_CREDITS,
 ItemPackType.CUSTOM_CRYSTAL,
 ItemPackType.CUSTOM_GOLD,
 ItemPackType.CUSTOM_EVENT_COIN,
 ItemPackType.CUSTOM_EVENT_COIN_EXTERNAL}
_PACK_ITEMS_SORT_ORDER = list(itertools.chain(ItemPackTypeGroup.DISCOUNT, ItemPackTypeGroup.CUSTOM, ItemPackTypeGroup.TOKEN, ItemPackTypeGroup.GOODIE, ItemPackTypeGroup.CREW, ItemPackTypeGroup.STYLE, ItemPackTypeGroup.CAMOUFLAGE, ItemPackTypeGroup.DECAL, ItemPackTypeGroup.MODIFICATION, ItemPackTypeGroup.PAINT, ItemPackTypeGroup.ITEM))
_TOOLTIP_TYPE = {ItemPackType.ITEM_DEVICE: TOOLTIPS_CONSTANTS.SHOP_20_MODULE,
 ItemPackType.ITEM_EQUIPMENT: TOOLTIPS_CONSTANTS.SHOP_20_MODULE,
 ItemPackType.ITEM_SHELL: TOOLTIPS_CONSTANTS.SHOP_20_SHELL,
 ItemPackType.GOODIE_CREDITS: TOOLTIPS_CONSTANTS.SHOP_20_BOOSTER,
 ItemPackType.GOODIE_EXPERIENCE: TOOLTIPS_CONSTANTS.SHOP_20_BOOSTER,
 ItemPackType.GOODIE_CREW_EXPERIENCE: TOOLTIPS_CONSTANTS.SHOP_20_BOOSTER,
 ItemPackType.GOODIE_FREE_EXPERIENCE: TOOLTIPS_CONSTANTS.SHOP_20_BOOSTER,
 ItemPackType.GOODIE_FRONTLINE_EXPERIENCE: TOOLTIPS_CONSTANTS.SHOP_20_BOOSTER,
 ItemPackType.VEHICLE_MEDIUM: TOOLTIPS_CONSTANTS.AWARD_VEHICLE,
 ItemPackType.VEHICLE_HEAVY: TOOLTIPS_CONSTANTS.AWARD_VEHICLE,
 ItemPackType.VEHICLE_LIGHT: TOOLTIPS_CONSTANTS.AWARD_VEHICLE,
 ItemPackType.VEHICLE_SPG: TOOLTIPS_CONSTANTS.AWARD_VEHICLE,
 ItemPackType.VEHICLE_AT_SPG: TOOLTIPS_CONSTANTS.AWARD_VEHICLE,
 ItemPackType.STYLE: TOOLTIPS_CONSTANTS.SHOP_20_CUSTOMIZATION_ITEM,
 ItemPackType.PAINT_ALL: TOOLTIPS_CONSTANTS.SHOP_20_CUSTOMIZATION_ITEM,
 ItemPackType.PAINT_DESERT: TOOLTIPS_CONSTANTS.SHOP_20_CUSTOMIZATION_ITEM,
 ItemPackType.PAINT_SUMMER: TOOLTIPS_CONSTANTS.SHOP_20_CUSTOMIZATION_ITEM,
 ItemPackType.PAINT_WINTER: TOOLTIPS_CONSTANTS.SHOP_20_CUSTOMIZATION_ITEM,
 ItemPackType.DECAL_1: TOOLTIPS_CONSTANTS.SHOP_20_CUSTOMIZATION_ITEM,
 ItemPackType.DECAL_2: TOOLTIPS_CONSTANTS.SHOP_20_CUSTOMIZATION_ITEM,
 ItemPackType.PROJECTION_DECAL: TOOLTIPS_CONSTANTS.SHOP_20_CUSTOMIZATION_ITEM,
 ItemPackType.PERSONAL_NUMBER: TOOLTIPS_CONSTANTS.SHOP_20_CUSTOMIZATION_ITEM,
 ItemPackType.MODIFICATION: TOOLTIPS_CONSTANTS.SHOP_20_CUSTOMIZATION_ITEM,
 ItemPackType.CAMOUFLAGE_ALL: TOOLTIPS_CONSTANTS.SHOP_20_CUSTOMIZATION_ITEM,
 ItemPackType.CAMOUFLAGE_DESERT: TOOLTIPS_CONSTANTS.SHOP_20_CUSTOMIZATION_ITEM,
 ItemPackType.CAMOUFLAGE_SUMMER: TOOLTIPS_CONSTANTS.SHOP_20_CUSTOMIZATION_ITEM,
 ItemPackType.CAMOUFLAGE_WINTER: TOOLTIPS_CONSTANTS.SHOP_20_CUSTOMIZATION_ITEM,
 ItemPackType.ACHIEVEMENT: TOOLTIPS_CONSTANTS.SHOP_20_ACHIEVEMENT,
 ItemPackType.SINGLE_ACHIEVEMENTS: TOOLTIPS_CONSTANTS.SHOP_20_ACHIEVEMENT,
 ItemPackType.BADGE: TOOLTIPS_CONSTANTS.SHOP_20_BADGE,
 ItemPackType.REFERRAL_BADGE: TOOLTIPS_CONSTANTS.REFERRAL_BADGE,
 ItemPackType.PLAYER_BADGE: TOOLTIPS_CONSTANTS.SHOP_20_BADGE,
 ItemPackType.TRADE_IN_INFO: TOOLTIPS_CONSTANTS.TRADE_IN_INFO,
 ItemPackType.CREW_BUNDLE: TOOLTIPS_CONSTANTS.SHOP_20_CREW_BUNDLE}
_ICONS = {ItemPackType.CAMOUFLAGE_ALL: RES_SHOP.MAPS_SHOP_REWARDS_48X48_PRIZE_CAMOUFLAGE,
 ItemPackType.CAMOUFLAGE_WINTER: RES_SHOP.MAPS_SHOP_REWARDS_48X48_PRIZE_CAMOUFLAGE,
 ItemPackType.CAMOUFLAGE_SUMMER: RES_SHOP.MAPS_SHOP_REWARDS_48X48_PRIZE_CAMOUFLAGE,
 ItemPackType.CAMOUFLAGE_DESERT: RES_SHOP.MAPS_SHOP_REWARDS_48X48_PRIZE_CAMOUFLAGE,
 ItemPackType.STYLE: RES_SHOP.MAPS_SHOP_REWARDS_48X48_STYLE_ICON,
 ItemPackType.DECAL_1: RES_SHOP.MAPS_SHOP_REWARDS_48X48_PRIZE_EMBLEM,
 ItemPackType.DECAL_2: RES_SHOP.MAPS_SHOP_REWARDS_48X48_PRIZE_INSCRIPTION,
 ItemPackType.MODIFICATION: RES_SHOP.MAPS_SHOP_REWARDS_48X48_EFFECT_ICON,
 ItemPackType.PAINT_ALL: RES_SHOP.MAPS_SHOP_REWARDS_48X48_PAINT_ICON,
 ItemPackType.PAINT_WINTER: RES_SHOP.MAPS_SHOP_REWARDS_48X48_PAINT_ICON,
 ItemPackType.PAINT_SUMMER: RES_SHOP.MAPS_SHOP_REWARDS_48X48_PAINT_ICON,
 ItemPackType.PAINT_DESERT: RES_SHOP.MAPS_SHOP_REWARDS_48X48_PAINT_ICON,
 ItemPackType.CUSTOM_GOLD: RES_SHOP.MAPS_SHOP_REWARDS_48X48_MONEY_GOLD,
 ItemPackType.CUSTOM_CREDITS: RES_SHOP.MAPS_SHOP_REWARDS_48X48_MONEY_SILVER,
 ItemPackType.CUSTOM_CRYSTAL: RES_SHOP.MAPS_SHOP_REWARDS_48X48_MONEY_BONDS,
 ItemPackType.CUSTOM_EVENT_COIN: RES_SHOP.MAPS_SHOP_REWARDS_48X48_MONEY_EVENT_COIN,
 ItemPackType.CUSTOM_EVENT_COIN_EXTERNAL: RES_SHOP.MAPS_SHOP_REWARDS_48X48_MONEY_EVENT_COIN,
 ItemPackType.CUSTOM_SLOT: RES_SHOP.MAPS_SHOP_REWARDS_48X48_PRIZE_HANGARSLOT,
 ItemPackType.CUSTOM_REFERRAL_CREW: RES_SHOP.MAPS_SHOP_REWARDS_48X48_PRIZECREW,
 ItemPackType.CREW_100: RES_SHOP.MAPS_SHOP_REWARDS_48X48_PRIZECREW}
_NOT_FOUND_ICONS = {ItemPackType.TOKEN: RES_ICONS.MAPS_ICONS_QUESTS_ICON_BATTLE_MISSIONS_PRIZE_TOKEN}
_PREM_ICONS = {1: RES_SHOP.MAPS_SHOP_REWARDS_48X48_ICON_BATTLE_MISSIONS_PRIZE_1DAYPREM,
 2: RES_SHOP.MAPS_SHOP_REWARDS_48X48_ICON_BATTLE_MISSIONS_PRIZE_2DAYPREM,
 3: RES_SHOP.MAPS_SHOP_REWARDS_48X48_ICON_BATTLE_MISSIONS_PRIZE_3DAYPREM,
 7: RES_SHOP.MAPS_SHOP_REWARDS_48X48_ICON_BATTLE_MISSIONS_PRIZE_7DAYPREM,
 14: RES_SHOP.MAPS_SHOP_REWARDS_48X48_ICON_BATTLE_MISSIONS_PRIZE_14DAYPREM,
 30: RES_SHOP.MAPS_SHOP_REWARDS_48X48_ICON_BATTLE_MISSIONS_PRIZE_30DAYPREM,
 90: RES_SHOP.MAPS_SHOP_REWARDS_48X48_ICON_BATTLE_MISSIONS_PRIZE_90DAYPREM,
 180: RES_SHOP.MAPS_SHOP_REWARDS_48X48_ICON_BATTLE_MISSIONS_PRIZE_180DAYPREM,
 360: RES_SHOP.MAPS_SHOP_REWARDS_48X48_ICON_BATTLE_MISSIONS_PRIZE_360DAYPREM}

def __getPremiumPlusIcon(days):
    r = R.images.gui.maps.icons.quests.bonuses.small.dyn('premium_plus_{}'.format(days))
    return backport.image(r()) if r.exists() else ''


_BOX_ITEM = None
BOX_TYPE = 'box'
_OPEN_QUOTES = _ms(COMMON.COMMON_OPEN_QUOTES)
_DOUBLE_OPEN_QUOTES = _OPEN_QUOTES + _OPEN_QUOTES
_CLOSE_QUOTES = _ms(COMMON.COMMON_CLOSE_QUOTES)
_DOUBLE_CLOSE_QUOTES = _CLOSE_QUOTES + _CLOSE_QUOTES
StyleInstallInfo = namedtuple('StyleInstallInfo', ('canInstall', 'style', 'vehicle'))

class BoosterGUIItemProxy(object):

    def __init__(self, booster):
        self.__booster = booster

    @property
    def intCD(self):
        return self.__booster.boosterID

    @property
    def icon(self):
        return self.__booster.icon

    @property
    def userName(self):
        return self.__booster.description

    @property
    def itemTypeID(self):
        pass

    @property
    def itemTypeName(self):
        pass

    @property
    def mayInstall(self):
        return False

    @staticmethod
    def getHighlightType():
        return SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT


def getCompensateItemsCount(rawItem, itemsCache):
    if rawItem.compensation is not None:
        isVehicle = rawItem.type in ItemPackTypeGroup.VEHICLE
        isCustomisation = not isVehicle and rawItem.type in _CUSTOMIZATION_ITEM_TYPE
        item = itemsCache.items.getItemByCD(rawItem.id) if isVehicle or isCustomisation else None
        if item is not None:
            if isVehicle:
                if item.isInInventory and not item.isRented:
                    return 1
                return 0
            if item.isLimited:
                buyCount = max(item.descriptor.maxNumber - item.boundInventoryCount.get(-1, 0), 0)
                if buyCount > 0:
                    return rawItem.count - buyCount
                return rawItem.count
    return 0


def _getSuitableShellsForVehicle(vehicle):
    return [ shot.shell.compactDescr for shot in vehicle.gun.descriptor.shots ]


def getCDFromId(itemType, itemId):
    return makeCD('customizationItem', _CUSTOMIZATION_TYPES_MAP[itemType], itemId) if itemType in _CUSTOMIZATION_ITEM_TYPE else itemId


def lookupItem(rawItem, itemsCache, goodiesCache):
    itemType = rawItem.type
    itemId = rawItem.id
    if itemType in _NATIVE_ITEM_TYPE or itemType in _CUSTOMIZATION_ITEM_TYPE:
        return itemsCache.items.getItemByCD(itemId)
    else:
        return BoosterGUIItemProxy(goodiesCache.getBooster(itemId)) if itemType in _BOOSTER_ITEM_TYPE else None


def getItemIcon(rawItem, item):
    icon = rawItem.iconSource
    if not icon:
        if item is not None:
            icon = _ICONS.get(rawItem.type, item.icon)
        elif rawItem.type == ItemPackType.CUSTOM_PREMIUM:
            icon = _PREM_ICONS.get(rawItem.count, '')
        elif rawItem.type == ItemPackType.CUSTOM_PREMIUM_PLUS:
            icon = __getPremiumPlusIcon(rawItem.count)
        else:
            icon = _ICONS.get(rawItem.type, '')
        icon = icon or _NOT_FOUND_ICONS.get(rawItem.type, RES_ICONS.MAPS_ICONS_ARTEFACT_NOTFOUND)
    return icon


def getItemTitle(rawItem, item, forBox=False):
    if item is not None:
        title = item.userName
        if forBox and item.itemTypeName != '':
            tooltipKey = TOOLTIPS.getItemBoxTooltip(item.itemTypeName)
            if tooltipKey:
                title = _ms(tooltipKey, group=item.userType, value=item.userName)
                title = title.replace(_DOUBLE_OPEN_QUOTES, _OPEN_QUOTES).replace(_DOUBLE_CLOSE_QUOTES, _CLOSE_QUOTES)
    elif rawItem.type == ItemPackType.CUSTOM_SLOT:
        title = _ms(key=TOOLTIPS.AWARDITEM_SLOTS_HEADER)
    elif rawItem.type == ItemPackType.CUSTOM_GOLD:
        title = _ms(key=QUESTS.BONUSES_GOLD_DESCRIPTION, value=rawItem.count)
    elif rawItem.type == ItemPackType.CUSTOM_CREDITS:
        title = backport.text(R.strings.quests.bonuses.credits.description(), value=backport.getIntegralFormat(rawItem.count))
    elif rawItem.type == ItemPackType.CUSTOM_CRYSTAL:
        title = _ms(key=QUESTS.BONUSES_CRYSTAL_DESCRIPTION, value=rawItem.count)
    elif rawItem.type in (ItemPackType.CUSTOM_EVENT_COIN, ItemPackType.CUSTOM_EVENT_COIN_EXTERNAL):
        title = _ms(key=QUESTS.BONUSES_EVENTCOIN_DESCRIPTION, value=rawItem.count)
    elif rawItem.type == ItemPackType.CUSTOM_SUPPLY_POINT:
        title = _ms(EPIC_BATTLE.EPICBATTLEITEM_SUPPLYPOINTS_HEADER)
    elif rawItem.type == ItemPackType.CUSTOM_REWARD_POINT:
        title = _ms(EPIC_BATTLE.EPICBATTLEITEM_REWARDPOINTS_HEADER)
    elif rawItem.type == ItemPackType.CUSTOM_PREMIUM:
        title = backport.text(R.strings.tooltips.premium.days.header(), rawItem.count)
    elif rawItem.type == ItemPackType.CUSTOM_PREMIUM_PLUS:
        title = backport.text(R.strings.tooltips.premiumPlus.days.header(), rawItem.count)
    elif rawItem.type == ItemPackType.CUSTOM_REFERRAL_CREW:
        vehicle = g_currentPreviewVehicle.item
        title = _ms(TOOLTIPS.CUSTOMCREW_REFERRAL_HEADER, vehicle=vehicle.userName)
    elif rawItem.type in ItemPackTypeGroup.CREW:
        title = _ms(TOOLTIPS.CREW_HEADER)
    elif rawItem.type == ItemPackType.CUSTOM_EVENT_PROGRESSION_REWARD_POINT:
        title = backport.text(R.strings.tooltips.vehiclePreview.buyingPanel.eventProgression.price.header())
    else:
        title = rawItem.title or ''
    return title


def getItemDescription(rawItem, item):
    if item is not None:
        description = item.fullDescription
    elif rawItem.type == ItemPackType.CUSTOM_SLOT:
        description = _ms(TOOLTIPS.AWARDITEM_SLOTS_BODY)
    elif rawItem.type == ItemPackType.CUSTOM_GOLD:
        description = _ms(TOOLTIPS.AWARDITEM_GOLD_BODY)
    elif rawItem.type == ItemPackType.CUSTOM_CREDITS:
        description = _ms(TOOLTIPS.AWARDITEM_CREDITS_BODY)
    elif rawItem.type == ItemPackType.CUSTOM_CRYSTAL:
        description = _ms(TOOLTIPS.AWARDITEM_CRYSTAL_BODY)
    elif rawItem.type in (ItemPackType.CUSTOM_EVENT_COIN, ItemPackType.CUSTOM_EVENT_COIN_EXTERNAL):
        description = _ms(TOOLTIPS.AWARDITEM_EVENTCOIN_BODY)
    elif rawItem.type == ItemPackType.CUSTOM_PREMIUM:
        description = backport.text(R.strings.tooltips.awardItem.premium.body())
    elif rawItem.type == ItemPackType.CUSTOM_PREMIUM_PLUS:
        description = backport.text(R.strings.tooltips.awardItem.premium_plus.body())
    elif rawItem.type == ItemPackType.CUSTOM_REFERRAL_CREW:
        description = _ms(TOOLTIPS.CUSTOMCREW_REFERRAL_BODY, value=CrewTypes.SKILL_100)
    elif rawItem.type == ItemPackType.CUSTOM_SUPPLY_POINT:
        description = _ms(EPIC_BATTLE.EPICBATTLEITEM_SUPPLYPOINTS_DESCRIPTION)
    elif rawItem.type == ItemPackType.CUSTOM_REWARD_POINT:
        description = _ms(EPIC_BATTLE.EPICBATTLEITEM_REWARDPOINTS_DESCRIPTION)
    elif rawItem.type in ItemPackTypeGroup.CREW:
        if rawItem.type == ItemPackType.CREW_CUSTOM:
            description = _ms(TOOLTIPS.CREWCUSTOM_BODY)
        else:
            description = _ms(TOOLTIPS.CREW_BODY, value={ItemPackType.CREW_50: CrewTypes.SKILL_50,
             ItemPackType.CREW_75: CrewTypes.SKILL_75,
             ItemPackType.CREW_100: CrewTypes.SKILL_100,
             ItemPackType.CUSTOM_CREW_100: CrewTypes.SKILL_100}.get(rawItem.type))
    elif rawItem.type == ItemPackType.CUSTOM_EVENT_PROGRESSION_REWARD_POINT:
        description = backport.text(R.strings.tooltips.vehiclePreview.buyingPanel.eventProgression.price.body())
    else:
        description = rawItem.description or ''
    return description


def getItemTooltipType(rawItem, item):
    isEquipment = rawItem.type == ItemPackType.ITEM_EQUIPMENT
    return TOOLTIPS_CONSTANTS.SHOP_20_BATTLE_BOOSTER if isEquipment and item is not None and item.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER else _TOOLTIP_TYPE.get(rawItem.type)


def showItemTooltip(toolTipMgr, rawItem, item):
    tooltipType = getItemTooltipType(rawItem, item)
    if tooltipType is not None:
        toolTipMgr.onCreateTypedTooltip(tooltipType, [rawItem.id], 'INFO')
    else:
        header = getItemTitle(rawItem, item)
        body = getItemDescription(rawItem, item)
        tooltip = makeTooltip(header, body)
        toolTipMgr.onCreateComplexTooltip(tooltip, 'INFO')
    return


def collapseItemsPack(items):
    if items is None or len(items) < 2:
        return items
    else:
        uniqueItems = []
        for _, group in itertools.groupby(sorted(items, key=_getItemKey), key=_getItemKey):
            items = list(group)
            item = items[0]
            uniqueItems.append(ItemPackEntry(type=item.type, id=item.id, count=sum((item.count for item in items)), groupID=item.groupID, compensation=item.compensation, iconSource=item.iconSource, title=item.title, description=item.description))

        return uniqueItems


def _getItemKey(item):
    return (item.id, item.type)


def _createItemVO(rawItem, itemsCache, goodiesCache, slotIndex, rawTooltipData=None):
    countFormat = ''
    if rawItem == _BOX_ITEM:
        cd = 0
        icon = backport.image(R.images.gui.maps.icons.rankedBattles.boxes.c_48x48.metal_1())
        overlay = SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT
    else:
        fittingItem = lookupItem(rawItem, itemsCache, goodiesCache)
        cd = fittingItem.intCD if fittingItem is not None else rawItem.id
        icon = getItemIcon(rawItem, fittingItem)
        overlay = fittingItem.getHighlightType() if fittingItem is not None else SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT
        if rawItem.type in ItemPackTypeGroup.CREW:
            countFormat = _formatCrew(rawItem)
        elif rawItem.type in _UNCOUNTABLE_ITEM_TYPE:
            countFormat = ''
        else:
            count = rawItem.count
            countFormat = 'x{}'.format(count) if count > 1 else ''
    return {'id': str(cd),
     'icon': icon,
     'overlayType': overlay,
     'type': rawItem.type if rawItem is not None else BOX_TYPE,
     'iconAlt': RES_ICONS.MAPS_ICONS_ARTEFACT_NOTFOUND,
     'slotIndex': slotIndex,
     'count': countFormat,
     'rawData': rawTooltipData}


def _formatCrew(item):
    if item.type in (ItemPackType.CREW_100, ItemPackType.CUSTOM_CREW_100):
        return '100%'
    if item.type == ItemPackType.CREW_75:
        return '75%'
    return '50%' if item.type == ItemPackType.CREW_50 else ''


def _getBoxTooltipVO(rawItems, itemsCache, goodiesCache):
    items = []
    rawItems = collapseItemsPack(rawItems)
    for rawItem in rawItems:
        fittingItem = lookupItem(rawItem, itemsCache, goodiesCache)
        if fittingItem is not None and fittingItem.itemTypeID in GUI_ITEM_TYPE.CUSTOMIZATIONS:
            icon = RES_ICONS.getBonusIcon('small', fittingItem.itemTypeName)
        else:
            icon = getItemIcon(rawItem, fittingItem)
        if fittingItem is not None:
            overlay = fittingItem.getHighlightType()
        else:
            overlay = SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT
        items.append({'id': rawItem.id,
         'type': rawItem.type,
         'count': str(rawItem.count) if rawItem.type not in _UNCOUNTABLE_ITEM_TYPE and rawItem.count > 1 else '',
         'icon': icon,
         'overlay': overlay,
         'desc': getItemTitle(rawItem, fittingItem, forBox=True)})

    vo = {'icon': backport.image(R.images.gui.maps.icons.rankedBattles.boxes.c_48x48.metal_1()),
     'count': len(rawItems),
     'items': items}
    return vo


def _checkItemType(a, b):
    return a in b if isinstance(b, Container) else a == b


class _NodeContainer(object):
    itemsCache = dependency.descriptor(IItemsCache)
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, childCount, itemTypeOrGroup, nextNode=None):
        super(_NodeContainer, self).__init__()
        self._maxChildCount = childCount
        self._nextNode = nextNode
        self._children = []
        self._itemTypeOrGroup = itemTypeOrGroup

    def getVO(self):
        items = []
        self._sortChildren()
        for i, child in enumerate(self._children):
            items.append(_createItemVO(child, self.itemsCache, self.goodiesCache, i))

        return self.wrapVO(items)

    def getNextNode(self):
        return self._nextNode

    def destroy(self):
        self._nextNode = None
        return

    def addItem(self, item, vehicle, vehicleGroupId):
        if _checkItemType(item.type, self._itemTypeOrGroup) and item.groupID == vehicleGroupId:
            slotIdx = len(self._children)
            if slotIdx < self._maxChildCount:
                mayInstall, counterLimit = self._install(item, vehicle, slotIdx)
                if mayInstall:
                    itemsCount = item.count
                    if counterLimit == _UNLIMITED_ITEMS_COUNT or itemsCount <= counterLimit:
                        self._children.append(item)
                        return
                    self._children.append(item.replace({'count': counterLimit}))
                    itemsLeft = itemsCount - counterLimit
                    item = item.replace({'count': itemsLeft})
        self._addItemToNextNode(item, vehicle, vehicleGroupId)

    @staticmethod
    def wrapVO(items):
        result = {}
        if items:
            result = {'items': items,
             'isEnabled': True,
             'topTitle': '',
             'topTitleSmall': ''}
        return result

    def _install(self, item, vehicle, slotIdx):
        for child in self._children:
            if child.id == item.id:
                return (False, 1)

        return (True, 1)

    def _addItemToNextNode(self, item, vehicle, vehicleGroupId):
        if self._nextNode:
            self._nextNode.addItem(item, vehicle, vehicleGroupId)

    def _sortChildren(self):
        pass


class _OptDeviceNodeContainer(_NodeContainer):

    def __init__(self, nextNode=None):
        super(_OptDeviceNodeContainer, self).__init__(NUM_OPTIONAL_DEVICE_SLOTS, ItemPackType.ITEM_DEVICE, nextNode)

    def _install(self, item, vehicle, slotIdx):
        optDev = self.itemsCache.items.getItemByCD(item.id)
        if optDev is None:
            return (False, 0)
        else:
            result = optDev.mayInstall(vehicle, slotIdx)[0]
            if result:
                vehicle_adjusters.installOptionalDevice(vehicle, optDev.intCD, slotIdx)
            return (result, 1)


class _ShellNodeContainer(_NodeContainer):

    def __init__(self, nextNode=None):
        super(_ShellNodeContainer, self).__init__(NUM_SHELLS_SLOTS, ItemPackType.ITEM_SHELL, nextNode)
        self.__vehicle = None
        return

    def _install(self, item, vehicle, slotIdx):
        shell = self.itemsCache.items.getItemByCD(item.id)
        if shell is None:
            return (False, 0)
        else:
            shells = _getSuitableShellsForVehicle(vehicle)
            if item.id not in shells:
                return (False, 0)
            self.__vehicle = vehicle
            return (True, _UNLIMITED_ITEMS_COUNT)

    def _sortChildren(self):
        self._children.sort(key=lambda item: item.id)
        if self.__vehicle is not None and self._children:
            vehicle_adjusters.changeShell(self.__vehicle, 0)
        return


class _EquipmentNodeContainer(_NodeContainer):

    def __init__(self, nextNode=None):
        super(_EquipmentNodeContainer, self).__init__(_NUM_REGULAR_EQUIPMENT_SLOTS, ItemPackType.ITEM_EQUIPMENT, nextNode)

    def _install(self, item, vehicle, slotIdx):
        equipment = self.itemsCache.items.getItemByCD(item.id)
        if equipment is None:
            return (False, 0)
        else:
            result = equipment.mayInstall(vehicle, slotIdx)[0]
            if result:
                if equipment.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER:
                    vehicle_adjusters.installBattleBoosterOnVehicle(vehicle, equipment.intCD)
                else:
                    vehicle_adjusters.installEquipment(vehicle, equipment.intCD, slotIdx)
            return (result, 1)


class _BuiltinEquipmentNodeContainer(_NodeContainer):

    def __init__(self, nextNode=None):
        super(_BuiltinEquipmentNodeContainer, self).__init__(_NUM_REGULAR_EQUIPMENT_SLOTS, ItemPackType.ITEM_EQUIPMENT, nextNode)

    def _install(self, item, vehicle, slotIdx):
        equipment = self.itemsCache.items.getItemByCD(item.id)
        if equipment is None:
            return (False, 0)
        elif not equipment.isBuiltIn:
            return (False, 0)
        else:
            result = equipment.mayInstall(vehicle, slotIdx)[0]
            if result:
                vehicle_adjusters.installEquipment(vehicle, equipment.intCD, slotIdx)
            return (result, 1)


class _PriorityNodeContainer(_NodeContainer):

    def __init__(self, childCount, nextNode=None):
        super(_PriorityNodeContainer, self).__init__(childCount, _ANY_ITEM_TYPE, nextNode)

    def addItem(self, item, vehicle, vehicleGroupId):
        itemAllowed = _checkItemType(item.type, self._itemTypeOrGroup)
        if itemAllowed:
            self._children.append(item)
            self._children = _sortItemsByOrder(self._children)
            if self._maxChildCount != _UNLIMITED_ITEMS_COUNT and len(self._children) > self._maxChildCount:
                excluded = self._children.pop()
                self._addItemToNextNode(excluded, vehicle, vehicleGroupId)
        else:
            self._addItemToNextNode(item, vehicle, vehicleGroupId)

    def getVO(self):
        if len(self._children) <= 1:
            return super(_PriorityNodeContainer, self).getVO()
        rawTooltipData = _getBoxTooltipVO(self._children, self.itemsCache, self.goodiesCache)
        items = [_createItemVO(_BOX_ITEM, self.itemsCache, self.goodiesCache, 0, rawTooltipData)]
        return self.wrapVO(items)


class _FrontlineNodeContainer(_NodeContainer):

    def __init__(self, nextNode=None):
        super(_FrontlineNodeContainer, self).__init__(_UNLIMITED_ITEMS_COUNT, ItemPackType.FRONTLINE_TOKEN, nextNode)

    def addItem(self, item, vehicle, vehicleGroupId):
        if item.type == self._itemTypeOrGroup:
            self._children.append(item)
        else:
            self._addItemToNextNode(item, vehicle, vehicleGroupId)

    @staticmethod
    def wrapVO(items):
        return {}


class _GiftNodeContainer(_NodeContainer):

    def __init__(self, nextNode=None):
        super(_GiftNodeContainer, self).__init__(_UNLIMITED_ITEMS_COUNT, _FRONTLINE_GIFTS, nextNode)

    def addItem(self, item, vehicle, vehicleGroupId):
        itemAllowed = _checkItemType(item.type, self._itemTypeOrGroup)
        if itemAllowed:
            self._children.append(item)
        else:
            self._addItemToNextNode(item, vehicle, vehicleGroupId)

    @staticmethod
    def wrapVO(items):
        result = {}
        if items:
            result = {'items': items,
             'isEnabled': True,
             'topTitle': text_styles.concatStylesToSingleLine(icons.makeImageTag(source=backport.image(R.images.gui.maps.icons.library.icon_gift()), width=17, height=15, vSpace=0), text_styles.vehicleStatusCriticalTextSmall(VEHICLE_PREVIEW.BUYINGPANEL_PRESENT)),
             'topTitleSmall': icons.makeImageTag(source=backport.image(R.images.gui.maps.icons.library.icon_gift()), width=17, height=15, vSpace=0)}
        return result

    def _sortChildren(self):
        self._children = _sortItemsByOrder(self._children)


class _CustomCrewSkillsNodeContainer(_NodeContainer):
    CREW_COUNT = 1

    def __init__(self, nextNode=None):
        super(_CustomCrewSkillsNodeContainer, self).__init__(self.CREW_COUNT, ItemPackType.CREW_CUSTOM, nextNode)

    def getVO(self):
        return []

    def parseCrewSkills(self, item):
        return {idx:tankmanItem.get('skills', []) + tankmanItem.get('freeSkills', []) for idx, tankmanItem in enumerate(item.extra['tankmen'])}

    def _install(self, item, vehicle, slotIdx):
        crewSkills = self.parseCrewSkills(item)
        if crewSkills is None:
            return (False, 0)
        else:
            vehicle_adjusters.applyTankmanSkillOnVehicle(vehicle, crewSkills)
            return (True, 0)


def getDataOneVehicle(itemsPack, vehicle, vehicleGroupId):
    rule = __getItemsSortRule(itemsPack)
    if rule == ITEM_SORT_RULE.FRONTLINE:
        root = __getFrontlinePackRule()
    else:
        root = __getDefaultPackRule()
    return _packDataOneVehicle(root, itemsPack, vehicle, vehicleGroupId)


def getCouponDiscountForItemPack(itemsPack, price=maxint):
    discount = 0
    if itemsPack is None:
        return Money(gold=discount)
    else:
        for item in itemsPack:
            if item.type in ItemPackTypeGroup.DISCOUNT:
                discount += item.count

        return Money(gold=min(discount, price))


def getCouponBonusesForItemPack(itemsPack):
    result = []
    if itemsPack:
        itemsPack = _sortItemsByOrder(itemsPack)
        for item in itemsPack:
            if item.type not in ItemPackTypeGroup.DISCOUNT + ItemPackTypeGroup.VEHICLE:
                result.append({'img': getItemIcon(item, None),
                 'text': getItemTitle(item, None)})

    return result


def getDataMultiVehicles(itemsPack, vehicle):
    rule = __getItemsSortRule(itemsPack)
    return [] if rule == ITEM_SORT_RULE.FRONTLINE else _packDataMultiVehicles(itemsPack, vehicle)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def addCompensationInfo(itemsVOs, itemsPack, itemsCache=None):
    compensationInfo = [ {'id': str(item.id),
     'type': item.type,
     'hasCompensation': getCompensateItemsCount(item, itemsCache) > 0} for item in collapseItemsPack(itemsPack) ]

    def hasCompensation(itemVO):
        for ci in compensationInfo:
            if ci['id'] == str(itemVO['id']) and ci['type'] == itemVO['type']:
                return ci['hasCompensation']

        return False

    for itemsVO in itemsVOs:
        for vo in itemsVO['items']:
            vo['hasCompensation'] = hasCompensation(vo)
            for insideBoxVO in vo['rawData']['items'] if vo['rawData'] else []:
                insideBoxVO['hasCompensation'] = hasCompensation(insideBoxVO)

    return itemsVOs


def getActiveOffer(offers):
    return findFirst(lambda o: o.preferred, offers) or findFirst(lambda o: o.bestOffer, offers) or first(offers)


def addBuiltInEquipment(packItems, itemsCache, vehicleCD):
    if packItems and itemsCache and vehicleCD:
        vehicle = itemsCache.items.getItemByCD(vehicleCD)
        groupID = 1
        for item in packItems:
            if item.id == vehicleCD:
                groupID = item.groupID

        for eqId in vehicle.getBuiltInEquipmentIDs():
            eqItem = ItemPackEntry(type=ItemPackType.ITEM_EQUIPMENT, id=eqId, count=1, groupID=groupID)
            packItems.append(eqItem)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def mayObtainWithMoneyExchange(itemPrice, itemsCache=None):
    return itemPrice <= itemsCache.items.stats.money.exchange(Currency.GOLD, Currency.CREDITS, itemsCache.items.shop.exchangeRate, default=0)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def mayObtainForMoney(itemPrice, itemsCache=None):
    return itemPrice <= itemsCache.items.stats.money


@dependency.replace_none_kwargs(service=ICustomizationService)
def canInstallStyle(styleId, service=None):
    style = service.getItemByID(GUI_ITEM_TYPE.STYLE, styleId)
    if not style.isInInventory:
        return StyleInstallInfo(canInstall=False, style=style, vehicle=None)
    else:
        vehicle = g_currentVehicle.item
        if not style.mayInstall(vehicle):
            vehicle = __findVehicle(style)
            if vehicle is None:
                return StyleInstallInfo(canInstall=False, style=style, vehicle=None)
        return StyleInstallInfo(canInstall=True, style=style, vehicle=vehicle)


def _sortItemsByOrder(items, rule=None):
    if rule is None:
        rule = _PACK_ITEMS_SORT_ORDER
    maxIndex = len(rule)
    items.sort(key=lambda i: rule.index(i.type) if i.type in rule else maxIndex)
    return items


def _packDataOneVehicle(root, itemsPack, vehicle, vehicleGroupId):
    for item in itemsPack:
        root.addItem(item, vehicle, vehicleGroupId)

    itemsVOs = []
    while root:
        vo = root.getVO()
        if vo:
            itemsVOs.append(vo)
        prevNode = root
        root = prevNode.getNextNode()
        prevNode.destroy()

    return addCompensationInfo(itemsVOs, itemsPack)


def _packDataMultiVehicles(itemsPack, vehicle):
    container = _PriorityNodeContainer(_UNLIMITED_ITEMS_COUNT)
    for item in itemsPack:
        container.addItem(item, vehicle, None)

    inContainerVOs = container.getVO()
    return addCompensationInfo([inContainerVOs], itemsPack) if inContainerVOs else []


def __getItemsSortRule(itemsPack):
    frontlineOffer = getCouponDiscountForItemPack(itemsPack) != MONEY_ZERO_GOLD
    return ITEM_SORT_RULE.FRONTLINE if frontlineOffer else ITEM_SORT_RULE.REGULAR


def __getDefaultPackRule():
    return _BuiltinEquipmentNodeContainer(nextNode=_CustomCrewSkillsNodeContainer(nextNode=_OptDeviceNodeContainer(nextNode=_ShellNodeContainer(nextNode=_EquipmentNodeContainer(nextNode=_PriorityNodeContainer(1, nextNode=_PriorityNodeContainer(_UNLIMITED_ITEMS_COUNT)))))))


def __getFrontlinePackRule():
    return _FrontlineNodeContainer(nextNode=_GiftNodeContainer())


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def __findVehicle(style, itemsCache=None):
    criteria = REQ_CRITERIA.IN_OWNERSHIP | ~REQ_CRITERIA.VEHICLE.IS_IN_BATTLE
    vehicles = [ vehicle for vehicle in itemsCache.items.getVehicles(criteria=criteria).itervalues() if style.mayInstall(vehicle) ]
    randomStats = itemsCache.items.getAccountDossier().getRandomStats()
    vehRandomStats = randomStats.getVehicles()

    def vehicleComparator(item):
        if item.intCD not in vehRandomStats:
            return (0, item.level)
        battlesCount, _, _ = vehRandomStats.get(item.intCD)
        return (battlesCount if battlesCount else 0, item.level)

    vehicles = sorted(vehicles, key=vehicleComparator, reverse=True)
    return findFirst(None, vehicles)
