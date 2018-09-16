# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview20/items_kit_helper.py
import itertools
from collections import Container
from gui.Scaleform.locale.COMMON import COMMON
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_SHOP import RES_SHOP
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.gui_items.Tankman import CrewTypes
from items import EQUIPMENT_TYPES
from items import makeIntCompactDescrByID as makeCD
from items.components.c11n_constants import CustomizationType
from items.vehicles import NUM_OPTIONAL_DEVICE_SLOTS, NUM_EQUIPMENT_SLOTS_BY_TYPE, NUM_SHELLS_SLOTS
from skeletons.gui.goodies import IGoodiesCache
from web_client_api.common import ItemPackType, ItemPackTypeGroup
from gui.shared.gui_items import vehicle_adjusters
from shared_utils import first
from gui.shared.gui_items import GUI_ITEM_TYPE
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from helpers import dependency
from helpers.i18n import makeString as _ms
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
_NUM_REGULAR_EQUIPMENT_SLOTS = NUM_EQUIPMENT_SLOTS_BY_TYPE[EQUIPMENT_TYPES.regular]
_UNLIMITED_ITEMS_COUNT = -1
_ANY_ITEM_TYPE = {v for _, v in ItemPackType.getIterator()} - set(ItemPackTypeGroup.CREW)
_NATIVE_ITEM_TYPE = set(itertools.chain(ItemPackTypeGroup.VEHICLE, ItemPackTypeGroup.ITEM))
_CUSTOMIZATION_ITEM_TYPE = set(itertools.chain(ItemPackTypeGroup.STYLE, ItemPackTypeGroup.CAMOUFLAGE, ItemPackTypeGroup.PAINT, ItemPackTypeGroup.DECAL, ItemPackTypeGroup.MODIFICATION))
_CUSTOMIZATION_TYPES_MAP = {ItemPackType.STYLE: CustomizationType.STYLE,
 ItemPackType.CAMOUFLAGE_SUMMER: CustomizationType.CAMOUFLAGE,
 ItemPackType.CAMOUFLAGE_WINTER: CustomizationType.CAMOUFLAGE,
 ItemPackType.CAMOUFLAGE_DESERT: CustomizationType.CAMOUFLAGE,
 ItemPackType.CAMOUFLAGE: CustomizationType.CAMOUFLAGE,
 ItemPackType.PAINT_SUMMER: CustomizationType.PAINT,
 ItemPackType.PAINT_WINTER: CustomizationType.PAINT,
 ItemPackType.PAINT_DESERT: CustomizationType.PAINT,
 ItemPackType.PAINT: CustomizationType.PAINT,
 ItemPackType.DECAL_1: CustomizationType.DECAL,
 ItemPackType.DECAL_2: CustomizationType.DECAL,
 ItemPackType.DECAL: CustomizationType.DECAL,
 ItemPackType.MODIFICATION: CustomizationType.MODIFICATION}
_BOOSTER_ITEM_TYPE = set(ItemPackTypeGroup.GOODIE)
_UNCOUNTABLE_ITEM_TYPE = {ItemPackType.CUSTOM_PREMIUM,
 ItemPackType.CUSTOM_CREDITS,
 ItemPackType.CUSTOM_CRYSTAL,
 ItemPackType.CUSTOM_GOLD}
_PACK_ITEMS_SORT_ORDER = list(itertools.chain(ItemPackTypeGroup.CUSTOM, ItemPackTypeGroup.TOKEN, ItemPackTypeGroup.GOODIE, ItemPackTypeGroup.CREW, ItemPackTypeGroup.STYLE, ItemPackTypeGroup.CAMOUFLAGE, ItemPackTypeGroup.DECAL, ItemPackTypeGroup.MODIFICATION, ItemPackTypeGroup.PAINT, ItemPackTypeGroup.ITEM))
_TOOLTIP_TYPE = {ItemPackType.ITEM_DEVICE: TOOLTIPS_CONSTANTS.AWARD_MODULE,
 ItemPackType.ITEM_EQUIPMENT: TOOLTIPS_CONSTANTS.AWARD_MODULE,
 ItemPackType.ITEM_SHELL: TOOLTIPS_CONSTANTS.AWARD_SHELL,
 ItemPackType.GOODIE: TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO,
 ItemPackType.GOODIE_CREDITS: TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO,
 ItemPackType.GOODIE_EXPERIENCE: TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO,
 ItemPackType.GOODIE_CREW_EXPERIENCE: TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO,
 ItemPackType.GOODIE_FREE_EXPERIENCE: TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO,
 ItemPackType.VEHICLE: TOOLTIPS_CONSTANTS.AWARD_VEHICLE,
 ItemPackType.VEHICLE_MEDIUM: TOOLTIPS_CONSTANTS.AWARD_VEHICLE,
 ItemPackType.VEHICLE_HEAVY: TOOLTIPS_CONSTANTS.AWARD_VEHICLE,
 ItemPackType.VEHICLE_LIGHT: TOOLTIPS_CONSTANTS.AWARD_VEHICLE,
 ItemPackType.VEHICLE_SPG: TOOLTIPS_CONSTANTS.AWARD_VEHICLE,
 ItemPackType.VEHICLE_AT_SPG: TOOLTIPS_CONSTANTS.AWARD_VEHICLE,
 ItemPackType.STYLE: TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM,
 ItemPackType.PAINT: TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM,
 ItemPackType.PAINT_DESERT: TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM,
 ItemPackType.PAINT_SUMMER: TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM,
 ItemPackType.PAINT_WINTER: TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM,
 ItemPackType.DECAL: TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM,
 ItemPackType.DECAL_1: TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM,
 ItemPackType.DECAL_2: TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM,
 ItemPackType.MODIFICATION: TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM,
 ItemPackType.CAMOUFLAGE: TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM,
 ItemPackType.CAMOUFLAGE_DESERT: TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM,
 ItemPackType.CAMOUFLAGE_SUMMER: TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM,
 ItemPackType.CAMOUFLAGE_WINTER: TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM}
_ICONS = {ItemPackType.CAMOUFLAGE: RES_SHOP.MAPS_SHOP_REWARDS_48X48_PRIZE_CAMOUFLAGE,
 ItemPackType.CAMOUFLAGE_WINTER: RES_SHOP.MAPS_SHOP_REWARDS_48X48_PRIZE_CAMOUFLAGE,
 ItemPackType.CAMOUFLAGE_SUMMER: RES_SHOP.MAPS_SHOP_REWARDS_48X48_PRIZE_CAMOUFLAGE,
 ItemPackType.CAMOUFLAGE_DESERT: RES_SHOP.MAPS_SHOP_REWARDS_48X48_PRIZE_CAMOUFLAGE,
 ItemPackType.STYLE: RES_SHOP.MAPS_SHOP_REWARDS_48X48_STYLE_ICON,
 ItemPackType.DECAL: RES_SHOP.MAPS_SHOP_REWARDS_48X48_PRIZE_EMBLEM,
 ItemPackType.DECAL_1: RES_SHOP.MAPS_SHOP_REWARDS_48X48_PRIZE_EMBLEM,
 ItemPackType.DECAL_2: RES_SHOP.MAPS_SHOP_REWARDS_48X48_PRIZE_EMBLEM,
 ItemPackType.MODIFICATION: RES_SHOP.MAPS_SHOP_REWARDS_48X48_EFFECT_ICON,
 ItemPackType.PAINT: RES_SHOP.MAPS_SHOP_REWARDS_48X48_PAINT_ICON,
 ItemPackType.PAINT_WINTER: RES_SHOP.MAPS_SHOP_REWARDS_48X48_PAINT_ICON,
 ItemPackType.PAINT_SUMMER: RES_SHOP.MAPS_SHOP_REWARDS_48X48_PAINT_ICON,
 ItemPackType.PAINT_DESERT: RES_SHOP.MAPS_SHOP_REWARDS_48X48_PAINT_ICON,
 ItemPackType.CUSTOM_GOLD: RES_SHOP.MAPS_SHOP_REWARDS_48X48_MONEY_GOLD,
 ItemPackType.CUSTOM_CREDITS: RES_SHOP.MAPS_SHOP_REWARDS_48X48_MONEY_SILVER,
 ItemPackType.CUSTOM_CRYSTAL: RES_SHOP.MAPS_SHOP_REWARDS_48X48_MONEY_BONDS,
 ItemPackType.CUSTOM_SLOT: RES_SHOP.MAPS_SHOP_REWARDS_48X48_PRIZE_HANGARSLOT}
_NOT_FOUND_ICONS = {ItemPackType.TOKEN: RES_ICONS.MAPS_ICONS_QUESTS_ICON_BATTLE_MISSIONS_PRIZE_TOKEN}
_PREM_ICONS = {1: RES_SHOP.MAPS_SHOP_REWARDS_48X48_ICON_BATTLE_MISSIONS_PRIZE_1DAYPREM,
 2: RES_SHOP.MAPS_SHOP_REWARDS_48X48_ICON_BATTLE_MISSIONS_PRIZE_2DAYPREM,
 3: RES_SHOP.MAPS_SHOP_REWARDS_48X48_ICON_BATTLE_MISSIONS_PRIZE_3DAYPREM,
 7: RES_SHOP.MAPS_SHOP_REWARDS_48X48_ICON_BATTLE_MISSIONS_PRIZE_7DAYPREM,
 30: RES_SHOP.MAPS_SHOP_REWARDS_48X48_ICON_BATTLE_MISSIONS_PRIZE_30DAYPREM,
 180: RES_SHOP.MAPS_SHOP_REWARDS_48X48_ICON_BATTLE_MISSIONS_PRIZE_180DAYPREM,
 360: RES_SHOP.MAPS_SHOP_REWARDS_48X48_ICON_BATTLE_MISSIONS_PRIZE_360DAYPREM}
_BOX_ITEM = None
BOX_TYPE = 'box'
_OPEN_QUOTES = _ms(COMMON.COMMON_OPEN_QUOTES)
_DOUBLE_OPEN_QUOTES = _OPEN_QUOTES + _OPEN_QUOTES
_CLOSE_QUOTES = _ms(COMMON.COMMON_CLOSE_QUOTES)
_DOUBLE_CLOSE_QUOTES = _CLOSE_QUOTES + _CLOSE_QUOTES

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


def getCompensateItemsCount(rawItem, itemsCache):
    if rawItem.compensation is not None:
        isVehicle = rawItem.type in ItemPackTypeGroup.VEHICLE
        isCustomisation = not isVehicle and rawItem.type in _CUSTOMIZATION_ITEM_TYPE
        item = itemsCache.items.getItemByCD(rawItem.id) if isVehicle or isCustomisation else None
        if item is not None:
            if isVehicle:
                if item.isInInventory:
                    return 1
                return 0
            if item.descriptor.maxNumber > 0:
                inventoryFreeSpace = item.descriptor.maxNumber - item.inventoryCount
                itemsPackEntryCount = rawItem.count
                if inventoryFreeSpace < itemsPackEntryCount:
                    return itemsPackEntryCount - inventoryFreeSpace
    return 0


@dependency.replace_none_kwargs(c11nService=ICustomizationService)
def previewStyle(vehicle, style, c11nService=None):
    if style.itemTypeID == GUI_ITEM_TYPE.STYLE and style.mayInstall(vehicle):
        c11nService.tryOnOutfit(style.getOutfit(first(style.seasons)))


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
        else:
            icon = _ICONS.get(rawItem.type, '')
        icon = icon or _NOT_FOUND_ICONS.get(rawItem.type, RES_ICONS.MAPS_ICONS_ARTEFACT_NOTFOUND)
    return icon


def getItemTitle(rawItem, item, forBox=False):
    if item is not None:
        title = item.userName
        if forBox:
            tooltipKey = TOOLTIPS.getItemBoxTooltip(item.itemTypeName)
            if tooltipKey:
                title = _ms(tooltipKey, value=item.userName)
                title = title.replace(_DOUBLE_OPEN_QUOTES, _OPEN_QUOTES).replace(_DOUBLE_CLOSE_QUOTES, _CLOSE_QUOTES)
    elif rawItem.type == ItemPackType.CUSTOM_SLOT:
        title = _ms(key=TOOLTIPS.AWARDITEM_SLOTS_HEADER)
    elif rawItem.type == ItemPackType.CUSTOM_GOLD:
        title = _ms(key=QUESTS.BONUSES_GOLD_DESCRIPTION, value=rawItem.count)
    elif rawItem.type == ItemPackType.CUSTOM_CREDITS:
        title = _ms(key=QUESTS.BONUSES_CREDITS_DESCRIPTION, value=rawItem.count)
    elif rawItem.type == ItemPackType.CUSTOM_CRYSTAL:
        title = _ms(key=QUESTS.BONUSES_CRYSTAL_DESCRIPTION, value=rawItem.count)
    elif rawItem.type == ItemPackType.CUSTOM_PREMIUM:
        title = _ms(TOOLTIPS.PREMIUM_DAYS_HEADER, rawItem.count)
    elif rawItem.type in ItemPackTypeGroup.CREW:
        title = _ms(TOOLTIPS.CREW_HEADER)
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
    elif rawItem.type == ItemPackType.CUSTOM_PREMIUM:
        description = _ms(TOOLTIPS.AWARDITEM_PREMIUM_BODY)
    elif rawItem.type in ItemPackTypeGroup.CREW:
        description = _ms(TOOLTIPS.CREW_BODY, value={ItemPackType.CREW_50: CrewTypes.SKILL_50,
         ItemPackType.CREW_75: CrewTypes.SKILL_75,
         ItemPackType.CREW_100: CrewTypes.SKILL_100}.get(rawItem.type))
    else:
        description = rawItem.description or ''
    return description


def getItemTooltipType(rawItem, item):
    isEquipment = rawItem.type == ItemPackType.ITEM_EQUIPMENT
    return TOOLTIPS_CONSTANTS.AWARD_BATTLE_BOOSTER if isEquipment and item is not None and item.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER else _TOOLTIP_TYPE.get(rawItem.type)


def showItemTooltip(toolTipMgr, rawItem, item):
    itemId = rawItem.id
    itemType = rawItem.type
    tooltipType = getItemTooltipType(rawItem, item)
    if tooltipType is not None:
        withLongIntArgs = {ItemPackType.ITEM_SHELL}
        withLongBoolArgs = set(itertools.chain(ItemPackTypeGroup.MODIFICATION, ItemPackTypeGroup.DECAL, ItemPackTypeGroup.PAINT, ItemPackTypeGroup.CAMOUFLAGE, ItemPackTypeGroup.STYLE))
        withLongOnlyArgs = set(itertools.chain(ItemPackTypeGroup.VEHICLE, ItemPackTypeGroup.GOODIE, (ItemPackType.ITEM_DEVICE, ItemPackType.ITEM_EQUIPMENT)))
        if itemType in withLongIntArgs:
            toolTipMgr.onCreateTypedTooltip(tooltipType, [itemId, 0], 'INFO')
        elif itemType in withLongBoolArgs:
            toolTipMgr.onCreateTypedTooltip(tooltipType, [itemId, False], 'INFO')
        elif itemType in withLongOnlyArgs:
            toolTipMgr.onCreateTypedTooltip(tooltipType, [itemId], 'INFO')
    else:
        header = getItemTitle(rawItem, item)
        body = getItemDescription(rawItem, item)
        tooltip = '{HEADER}%s{/HEADER}{BODY}%s{/BODY}' % (header, body)
        toolTipMgr.onCreateComplexTooltip(tooltip, 'INFO')
    return


def _createItemVO(rawItem, itemsCache, goodiesCache, slotIndex, rawTooltipData=None):
    if rawItem == _BOX_ITEM:
        cd = 0
        icon = RES_ICONS.MAPS_ICONS_RANKEDBATTLES_BOXES_48X48_METAL_1
        count = 0
        hasCompensation = False
    else:
        fittingItem = lookupItem(rawItem, itemsCache, goodiesCache)
        cd = fittingItem.intCD if fittingItem is not None else 0
        icon = getItemIcon(rawItem, fittingItem)
        if rawItem.type in _UNCOUNTABLE_ITEM_TYPE:
            count = 1
        else:
            count = rawItem.count
        hasCompensation = getCompensateItemsCount(rawItem, itemsCache) > 0
    return {'id': cd,
     'icon': icon,
     'type': rawItem.type if rawItem is not None else BOX_TYPE,
     'iconAlt': RES_ICONS.MAPS_ICONS_ARTEFACT_NOTFOUND,
     'slotIndex': slotIndex,
     'count': 'x{}'.format(count) if count > 1 else '',
     'rawData': rawTooltipData,
     'hasCompensation': hasCompensation}


def _getBoxTooltipVO(rawItems, itemsCache, goodiesCache):
    items = []
    for rawItem in rawItems:
        fittingItem = lookupItem(rawItem, itemsCache, goodiesCache)
        if fittingItem is not None and fittingItem.itemTypeID in GUI_ITEM_TYPE.CUSTOMIZATIONS:
            icon = RES_ICONS.getBonusIcon('small', fittingItem.itemTypeName)
        else:
            icon = getItemIcon(rawItem, fittingItem)
        items.append({'count': str(rawItem.count) if rawItem.type not in _UNCOUNTABLE_ITEM_TYPE else '',
         'icon': icon,
         'desc': getItemTitle(rawItem, fittingItem, forBox=True),
         'hasCompensation': getCompensateItemsCount(rawItem, itemsCache) > 0})

    vo = {'icon': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_BOXES_48X48_METAL_1,
     'count': len(rawItems),
     'items': items}
    return vo


@dependency.replace_none_kwargs(factory=IGuiItemsFactory, c11nService=ICustomizationService)
def _applyCamouflage(vehicle, factory=None, c11nService=None):
    camo = first(c11nService.getCamouflages(vehicle=vehicle).itervalues())
    if camo:
        outfit = factory.createOutfit(isEnabled=True, isInstalled=True)
        outfit.hull.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).set(camo)
        vehicle.setCustomOutfit(first(camo.seasons), outfit)


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
        result = []
        self._sortChildren()
        for i, child in enumerate(self._children):
            result.append(_createItemVO(child, self.itemsCache, self.goodiesCache, i))

        return result

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


class _PriorityNodeContainer(_NodeContainer):

    def __init__(self, childCount, nextNode=None):
        super(_PriorityNodeContainer, self).__init__(childCount, _ANY_ITEM_TYPE, nextNode)

    def addItem(self, item, vehicle, vehicleGroupId):
        itemAllowed = _checkItemType(item.type, self._itemTypeOrGroup)
        if itemAllowed:
            self._children.append(item)
            maxIndex = len(_PACK_ITEMS_SORT_ORDER)
            self._children.sort(key=lambda i: _PACK_ITEMS_SORT_ORDER.index(i.type) if i.type in _PACK_ITEMS_SORT_ORDER else maxIndex)
            excluded = None
            if self._maxChildCount != _UNLIMITED_ITEMS_COUNT and len(self._children) > self._maxChildCount:
                excluded = self._children.pop()
                self._addItemToNextNode(excluded, vehicle, vehicleGroupId)
            if excluded != item:
                self._applyItem(item, vehicle)
        else:
            self._addItemToNextNode(item, vehicle, vehicleGroupId)
        return

    def getVO(self):
        if len(self._children) <= 1:
            return super(_PriorityNodeContainer, self).getVO()
        rawTooltipData = _getBoxTooltipVO(self._children, self.itemsCache, self.goodiesCache)
        return [_createItemVO(_BOX_ITEM, self.itemsCache, self.goodiesCache, 0, rawTooltipData)]

    def _applyItem(self, item, vehicle):
        fittingItem = lookupItem(item, self.itemsCache, self.goodiesCache)
        if fittingItem is None:
            return
        else:
            if item.type == ItemPackType.STYLE:
                _applyCamouflage(vehicle)
                previewStyle(vehicle, fittingItem)
            return


def getDataOneVehicle(itemsPack, vehicle, vehicleGroupId):
    root = _OptDeviceNodeContainer(nextNode=_ShellNodeContainer(nextNode=_EquipmentNodeContainer(nextNode=_PriorityNodeContainer(1, nextNode=_PriorityNodeContainer(_UNLIMITED_ITEMS_COUNT)))))
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

    return itemsVOs


def getDataMultiVehicles(itemsPack, vehicle):
    container = _PriorityNodeContainer(_UNLIMITED_ITEMS_COUNT)
    for item in itemsPack:
        container.addItem(item, vehicle, None)

    return [container.getVO()]
