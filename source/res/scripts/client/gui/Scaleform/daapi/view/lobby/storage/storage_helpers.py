# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/storage_helpers.py
import random
from functools import partial
import nations
from account_helpers import AccountSettings
from account_helpers.AccountSettings import LAST_STORAGE_VISITED_TIMESTAMP
from goodies.goodie_constants import GOODIE_STATE
from gui import g_htmlTemplates
from gui.Scaleform import MENU
from gui.Scaleform.daapi.settings import BUTTON_LINKAGES
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.MENU import MENU as _MENU
from gui.Scaleform.locale.RES_SHOP import RES_SHOP
from gui.Scaleform.locale.STORAGE import STORAGE
from gui.impl import backport
from gui.shared.event_dispatcher import showVehiclePreview, showStorage
from gui.shared.formatters import text_styles, getItemPricesVO, icons, getMoneyVO
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from helpers.i18n import makeString as _ms
from gui.shared.money import Currency
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import getTypeUserName, getVehicleStateIcon, Vehicle
from gui.shared.items_parameters import params_helper
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import i18n, dependency, int2roman, time_utils, func_utils
from helpers.time_utils import getCurrentTimestamp
from skeletons.gui.shared import IItemsCache
_MAX_COMPATIBLE_VEHS_COUNT = 5
_MAX_COMPATIBLE_GUNS_COUNT = 2
_HANDLERS_MAP = {GUI_ITEM_TYPE.OPTIONALDEVICE: (CONTEXT_MENU_HANDLER_TYPE.STORAGE_EQUIPMENT_ITEM,),
 GUI_ITEM_TYPE.EQUIPMENT: (CONTEXT_MENU_HANDLER_TYPE.STORAGE_EQUIPMENT_ITEM,),
 GUI_ITEM_TYPE.BATTLE_BOOSTER: (CONTEXT_MENU_HANDLER_TYPE.STORAGE_BONS_ITEM,),
 GUI_ITEM_TYPE.TURRET: (CONTEXT_MENU_HANDLER_TYPE.STORAGE_MODULES_SHELLS_ITEM,),
 GUI_ITEM_TYPE.ENGINE: (CONTEXT_MENU_HANDLER_TYPE.STORAGE_MODULES_SHELLS_ITEM,),
 GUI_ITEM_TYPE.GUN: (CONTEXT_MENU_HANDLER_TYPE.STORAGE_MODULES_SHELLS_ITEM,),
 GUI_ITEM_TYPE.RADIO: (CONTEXT_MENU_HANDLER_TYPE.STORAGE_MODULES_SHELLS_ITEM,),
 GUI_ITEM_TYPE.CHASSIS: (CONTEXT_MENU_HANDLER_TYPE.STORAGE_MODULES_SHELLS_ITEM,),
 GUI_ITEM_TYPE.SHELL: (CONTEXT_MENU_HANDLER_TYPE.STORAGE_MODULES_SHELLS_ITEM,),
 GUI_ITEM_TYPE.CREW_BOOKS: (CONTEXT_MENU_HANDLER_TYPE.STORAGE_CREW_BOOKS_NO_SALE_ITEM, CONTEXT_MENU_HANDLER_TYPE.STORAGE_MODULES_SHELLS_ITEM)}

def _getContextMenuHandlerID(item):
    itemTypeID = item.itemTypeID
    if itemTypeID not in _HANDLERS_MAP:
        return ''
    handlers = _HANDLERS_MAP[item.itemTypeID]
    return handlers[item.isForSale] if len(handlers) > 1 else handlers[0]


_CUSTOMIZATION_VEHICLE_CRITERIA = ~REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR | ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE | ~REQ_CRITERIA.VEHICLE.IS_BOT
_BIG_HIGHLIGHT_TYPES_MAP = {SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER_CREW_REPLACE: SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER_CREW_REPLACE_BIG,
 SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER: SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER_BIG,
 SLOT_HIGHLIGHT_TYPES.EQUIPMENT_PLUS: SLOT_HIGHLIGHT_TYPES.EQUIPMENT_PLUS_BIG,
 SLOT_HIGHLIGHT_TYPES.BUILT_IN_EQUIPMENT: SLOT_HIGHLIGHT_TYPES.BUILT_IN_EQUIPMENT_BIG,
 SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT: SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT}

def getStorageItemDescr(item):
    itemType = item.itemTypeID
    if itemType in GUI_ITEM_TYPE.VEHICLE_MODULES:
        return _generateDescr(item, i18n.makeString(STORAGE.MODULECOMPATIBLE_LABEL), STORAGE.MODULECOMPATIBLE_MOREVEHICLES, ('vehicles', 'clipVehicles', 'uniChargedVehicles'), _MAX_COMPATIBLE_VEHS_COUNT)
    elif itemType == GUI_ITEM_TYPE.SHELL:
        return _generateDescr(item, i18n.makeString(STORAGE.SHELLCOMPATIBLE_LABEL), STORAGE.SHELLCOMPATIBLE_MOREGUNS, ('shellGuns',), _MAX_COMPATIBLE_GUNS_COUNT)
    elif itemType == GUI_ITEM_TYPE.BATTLE_BOOSTER:
        if item.isCrewBooster():
            desc = item.shortDescriptionSpecial
            return text_styles.main(desc)
        return text_styles.main(item.getOptDeviceBoosterDescription(None, text_styles.bonusAppliedText))
    else:
        template = g_htmlTemplates['html_templates:lobby/popovers']['optionalDevice']
        desc = item.formattedShortDescription(template.source)
        return text_styles.main(desc)


def createStorageDefVO(itemID, title, description, count, price, image, imageAlt, itemType='', nationFlagIcon='', enabled=True, contextMenuId='', additionalInfo='', active=GOODIE_STATE.INACTIVE):
    return {'id': itemID,
     'title': title,
     'description': description,
     'count': count,
     'price': price,
     'image': image,
     'imageAlt': imageAlt,
     'type': itemType,
     'nationFlagIcon': nationFlagIcon,
     'enabled': enabled,
     'additionalInfo': additionalInfo,
     'active': active == GOODIE_STATE.ACTIVE,
     'contextMenuId': contextMenuId}


def getStorageVehicleVo(vehicle):
    name = getVehicleName(vehicle)
    description = _getVehicleDescription(vehicle)
    imageSmall = func_utils.makeFlashPath(vehicle.getShopIcon(STORE_CONSTANTS.ICON_SIZE_SMALL))
    stateIcon, stateText = _getVehicleInfo(vehicle)
    if not imageSmall and not stateText:
        stateText = text_styles.vehicleStatusInfoText(_ms(STORAGE.INHANGAR_NOIMAGE))
    vo = createStorageDefVO(vehicle.intCD, name, description, vehicle.inventoryCount, getItemPricesVO(vehicle.getSellPrice())[0], imageSmall, RES_SHOP.getVehicleIcon(STORE_CONSTANTS.ICON_SIZE_SMALL, 'empty_tank'), itemType=getSlotOverlayIconType(vehicle), nationFlagIcon=RES_SHOP.getNationFlagIcon(nations.NAMES[vehicle.nationID]), contextMenuId=CONTEXT_MENU_HANDLER_TYPE.STORAGE_VEHICLES_MULTI_NATION_ITEM if vehicle.hasNationGroup else CONTEXT_MENU_HANDLER_TYPE.STORAGE_VEHICLES_REGULAR_ITEM)
    vo.update({'infoImgSrc': stateIcon,
     'infoText': stateText})
    if vehicle.canTradeOff:
        vo.update({'tradeOffPrice': {'price': getMoneyVO(vehicle.tradeOffPrice)}})
    return vo


def getVehicleName(vehicle):
    return ' '.join((getTypeUserName(vehicle.type, False), text_styles.neutral(int2roman(vehicle.level)), vehicle.shortUserName))


def _getVehicleDescription(vehicle):
    return ' '.join((_ms(STORAGE.CARD_VEHICLE_HOVER_MAXADDITIONALPRICELABEL), backport.getIntegralFormat(_calculateVehicleMaxAdditionalPrice(vehicle)), icons.credits()))


def _getVehicleInfo(vehicle):
    vState, vStateLvl = vehicle.getState()
    if vState not in Vehicle.CAN_SELL_STATES:
        infoTextStyle = text_styles.vehicleStatusCriticalText if vStateLvl == Vehicle.VEHICLE_STATE_LEVEL.CRITICAL else text_styles.vehicleStatusInfoText
        stateText = infoTextStyle(_ms(_MENU.tankcarousel_vehiclestates(vState)))
        stateIcon = getVehicleStateIcon(vState)
        return (stateIcon, stateText)
    else:
        return (None, None)


def _calculateVehicleMaxAdditionalPrice(vehicle):
    items = list(vehicle.equipment.regularConsumables) + vehicle.optDevices + vehicle.shells
    return sum((item.getSellPrice().price.get(Currency.CREDITS, 0) * getattr(item, 'count', 1) for item in items if item is not None))


def getStorageModuleName(item):
    if item.itemTypeID in GUI_ITEM_TYPE.VEHICLE_MODULES:
        return '{} {}'.format(text_styles.neutral(int2roman(item.level)), item.longUserName)
    return item.longUserNameAbbr if item.itemTypeID == GUI_ITEM_TYPE.SHELL else item.userName


def getStorageShellsCriteria(itemsCache, invVehicles, compatible):
    shellsList = set()
    criteria = REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.SUITABLE(invVehicles)
    myGuns = itemsCache.items.getItems(GUI_ITEM_TYPE.GUN, criteria).values()
    for gun in myGuns:
        shellsList.update((x.intCD for x in gun.defaultAmmo))

    for vehicle in invVehicles:
        shellsList.update((x.intCD for x in vehicle.gun.defaultAmmo))

    requestCriteria = REQ_CRITERIA.INVENTORY
    cdListCriteria = REQ_CRITERIA.IN_CD_LIST(shellsList)
    if compatible:
        requestCriteria |= cdListCriteria
    else:
        requestCriteria |= ~cdListCriteria
    return requestCriteria


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getStorageShellsData(invVehicles, isCompatible, comparator=None, itemsCache=None):
    requestCriteria = getStorageShellsCriteria(itemsCache, invVehicles, isCompatible)
    items = itemsCache.items.getItems(GUI_ITEM_TYPE.SHELL, requestCriteria)
    result = []
    for item in sorted(items.itervalues(), cmp=comparator):
        result.append(item)

    return result


def _generateDescr(item, label, moreLabel, paramsNames, maxItemsCount):
    moduleCompatibles = params_helper.getCompatibles(item)
    compatiblesSet = set()
    for paramType, compatible in moduleCompatibles:
        if paramType in paramsNames:
            compatiblesSet |= set(compatible.split(', '))

    compatiblesSet = list(compatiblesSet)
    compatiblesCount = len(compatiblesSet)
    descrItems = [label, ', '.join(compatiblesSet[:maxItemsCount])]
    if compatiblesCount > maxItemsCount:
        descrItems.append(i18n.makeString(moreLabel, vehCount=text_styles.stats(compatiblesCount - maxItemsCount)))
    return ' '.join(descrItems)


def getSlotOverlayIconType(item, isBig=False, vehicle=None):
    if item is None:
        return SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT
    else:
        highlightType = SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT
        itemTypeID = item.itemTypeID
        if itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER:
            highlightType = SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER
            if item.isCrewBooster():
                skillLearnt = item.isAffectedSkillLearnt(vehicle)
                highlightType = SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER if skillLearnt else SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER_CREW_REPLACE
        elif itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and item.isDeluxe():
            highlightType = SLOT_HIGHLIGHT_TYPES.EQUIPMENT_PLUS
        elif itemTypeID == GUI_ITEM_TYPE.EQUIPMENT and item.isBuiltIn:
            highlightType = SLOT_HIGHLIGHT_TYPES.BUILT_IN_EQUIPMENT
        return _BIG_HIGHLIGHT_TYPES_MAP[highlightType] if isBig else highlightType


def getStorageItemIcon(item, size=STORE_CONSTANTS.ICON_SIZE_MEDIUM):
    if item.itemTypeID in GUI_ITEM_TYPE.VEHICLE_COMPONENTS:
        icon = func_utils.makeFlashPath(item.getShopIcon(size))
    elif item.itemTypeID == GUI_ITEM_TYPE.CREW_BOOKS:
        icon = item.getOldStyleIcon()
    else:
        icon = item.icon
    return icon


def dummyFormatter(label, btnLabel='', btnTooltip=''):
    return {'iconSource': RES_ICONS.MAPS_ICONS_LIBRARY_ALERTBIGICON,
     'htmlText': text_styles.main(_ms(label)),
     'alignCenter': True,
     'inlineIcon': True,
     'btnVisible': bool(btnLabel),
     'btnLabel': btnLabel,
     'btnTooltip': btnTooltip,
     'btnEvent': 'ResetFilterEvent',
     'btnLinkage': BUTTON_LINKAGES.BUTTON_BLACK}


def enoughCreditsForRestore(restoreCreditsPrice, itemsCache):
    currentMoney = itemsCache.items.stats.money
    currentCredits = currentMoney.credits
    liquidityCredits = currentCredits + currentMoney.gold * itemsCache.items.shop.exchangeRate
    return (restoreCreditsPrice <= liquidityCredits, restoreCreditsPrice > currentCredits)


def getVehicleRestoreInfo(vehicle):
    info = vehicle.restoreInfo
    if info.isInCooldown():
        enabled = False
        timeLeft = info.getRestoreCooldownTimeLeft()
        icon = RES_ICONS.MAPS_ICONS_LIBRARY_ICON_SAND_WATCH
        if timeLeft > time_utils.ONE_DAY:
            description = i18n.makeString(MENU.VEHICLE_RESTORECOOLDOWNLEFT_DAYS, time=int(timeLeft / time_utils.ONE_DAY))
        else:
            if timeLeft > time_utils.ONE_HOUR:
                timeValue = int(timeLeft / time_utils.ONE_HOUR)
            else:
                timeValue = '&lt;1'
            description = i18n.makeString(MENU.VEHICLE_RESTORECOOLDOWNLEFT_HOURS, time=timeValue)
    else:
        enabled = True
        timeLeft = 0 if info.isUnlimited() else info.getRestoreTimeLeft()
        description = i18n.makeString(STORAGE.CARD_VEHICLE_HOVER_RESTOREAVAILABLELABEL)
        icon = RES_ICONS.MAPS_ICONS_LIBRARY_CLOCKICON_1
    if timeLeft:
        timeStr = time_utils.getTillTimeString(timeLeft, MENU.TIME_TIMEVALUESHORT)
    else:
        timeStr = i18n.makeString(STORAGE.RESTORETIMELEFT_TIMELESS)
    return (enabled,
     timeStr,
     description,
     icon)


def getItemVo(item):

    def getItemNationID(item):
        compatibleNations = []
        if item.itemTypeName == STORE_CONSTANTS.EQUIPMENT:
            item.descriptor.compatibleNations()
        return compatibleNations[0] if len(compatibleNations) == 1 else item.nationID

    priceVO = getItemPricesVO(item.getSellPrice())[0]
    itemNationID = getItemNationID(item)
    nationFlagIcon = RES_SHOP.getNationFlagIcon(nations.NAMES[itemNationID]) if itemNationID != nations.NONE_INDEX else ''
    vo = createStorageDefVO(item.intCD, getStorageModuleName(item), getStorageItemDescr(item), item.inventoryCount, priceVO, getStorageItemIcon(item, STORE_CONSTANTS.ICON_SIZE_SMALL), 'altimage', itemType=getSlotOverlayIconType(item), nationFlagIcon=nationFlagIcon, enabled=item.isForSale, contextMenuId=_getContextMenuHandlerID(item))
    return vo


def isStorageSessionTimeout():
    lastVisitTime = AccountSettings.getSessionSettings(LAST_STORAGE_VISITED_TIMESTAMP)
    return getCurrentTimestamp() - lastVisitTime > STORAGE_CONSTANTS.SESSION_TIMEOUT


def customizationAvailableForSell(item):
    return item.inventoryCount > 0 and item.getSellPrice() != ITEM_PRICE_EMPTY and not item.isRentable and not item.isHidden


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def customizationPreview(itemCD, itemsCache=None):
    item = itemsCache.items.getItemByCD(itemCD)
    vehicles = []
    req = _CUSTOMIZATION_VEHICLE_CRITERIA | ~REQ_CRITERIA.SECRET
    for vehCD, vehicle in itemsCache.items.getVehicles(req).iteritems():
        if not vehicle.isOutfitLocked and item.mayInstall(vehicle):
            vehicles.append(vehCD)

    if not vehicles:
        secretReq = _CUSTOMIZATION_VEHICLE_CRITERIA | REQ_CRITERIA.SECRET
        for vehCD, vehicle in itemsCache.items.getVehicles(secretReq).iteritems():
            if not vehicle.isOutfitLocked and item.mayInstall(vehicle):
                vehicles.append(vehCD)

    showVehiclePreview(random.choice(vehicles), previewBackCb=partial(showStorage, defaultSection=STORAGE_CONSTANTS.CUSTOMIZATION), previewAlias=VIEW_ALIAS.LOBBY_STORAGE, vehParams={'styleCD': itemCD})
