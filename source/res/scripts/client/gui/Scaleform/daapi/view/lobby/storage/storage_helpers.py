# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/storage_helpers.py
import logging
import random
from functools import partial
from itertools import chain
from typing import Optional, List
import nations
from account_helpers import AccountSettings
from account_helpers.AccountSettings import LAST_STORAGE_VISITED_TIMESTAMP
from goodies.goodie_constants import GOODIE_STATE
from gui import g_htmlTemplates
from gui.Scaleform import MENU
from gui.Scaleform.daapi.settings import BUTTON_LINKAGES
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.MENU import MENU as _MENU
from gui.Scaleform.locale.RES_SHOP import RES_SHOP
from gui.Scaleform.locale.STORAGE import STORAGE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.event_dispatcher import showStylePreview, showProgressionStylesStylePreview, showStorage
from gui.shared.formatters import text_styles, getItemPricesVO, icons, getMoneyVO
from gui.shared.gui_items.customization.c11n_items import Customization
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from gui.shared.utils.functions import makeTooltip
from helpers.i18n import makeString as _ms
from gui.shared.money import Currency
from gui.shared.gui_items import GUI_ITEM_TYPE, getKpiValueString, KPI
from gui.shared.gui_items.Vehicle import getTypeUserName, getVehicleStateIcon, Vehicle
from gui.shared.items_parameters import params_helper
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import i18n, dependency, int2roman, time_utils, func_utils
from helpers.time_utils import getCurrentTimestamp
from skeletons.gui.lobby_context import ILobbyContext
from items import vehicles
from items.vehicles import makeVehicleTypeCompDescrByName
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
from items.components.supply_slot_categories import SlotCategories
_logger = logging.getLogger(__name__)
_MAX_COMPATIBLE_VEHS_COUNT = 5
_MAX_COMPATIBLE_GUNS_COUNT = 2
_HANDLERS_MAP = {GUI_ITEM_TYPE.OPTIONALDEVICE: (CONTEXT_MENU_HANDLER_TYPE.STORAGE_OPTIONAL_DEVICE_ITEM,),
 GUI_ITEM_TYPE.EQUIPMENT: (CONTEXT_MENU_HANDLER_TYPE.STORAGE_EQUIPMENT_ITEM,),
 GUI_ITEM_TYPE.BATTLE_BOOSTER: (CONTEXT_MENU_HANDLER_TYPE.STORAGE_BONS_ITEM,),
 GUI_ITEM_TYPE.TURRET: (CONTEXT_MENU_HANDLER_TYPE.STORAGE_MODULES_SHELLS_ITEM,),
 GUI_ITEM_TYPE.ENGINE: (CONTEXT_MENU_HANDLER_TYPE.STORAGE_MODULES_SHELLS_ITEM,),
 GUI_ITEM_TYPE.GUN: (CONTEXT_MENU_HANDLER_TYPE.STORAGE_MODULES_SHELLS_ITEM,),
 GUI_ITEM_TYPE.RADIO: (CONTEXT_MENU_HANDLER_TYPE.STORAGE_MODULES_SHELLS_ITEM,),
 GUI_ITEM_TYPE.CHASSIS: (CONTEXT_MENU_HANDLER_TYPE.STORAGE_MODULES_SHELLS_ITEM,),
 GUI_ITEM_TYPE.SHELL: (CONTEXT_MENU_HANDLER_TYPE.STORAGE_MODULES_SHELLS_ITEM,),
 GUI_ITEM_TYPE.CREW_BOOKS: (CONTEXT_MENU_HANDLER_TYPE.STORAGE_CREW_BOOKS_NO_SALE_ITEM, CONTEXT_MENU_HANDLER_TYPE.STORAGE_MODULES_SHELLS_ITEM),
 GUI_ITEM_TYPE.DEMOUNT_KIT: (CONTEXT_MENU_HANDLER_TYPE.STORAGE_DEMOUNT_KIT_ITEM,)}
OPT_DEVICE_CATEGORIES_ORDER = {category:idx for idx, category in enumerate(SlotCategories.ORDER)}
CATEGORIES_COUNT = len(OPT_DEVICE_CATEGORIES_ORDER)

def getTopVehicleByNation(nationName):
    customizationCache = vehicles.g_cache.customization20()
    topVehicles = customizationCache.topVehiclesByNation
    return topVehicles.get(nationName, '')


def _getContextMenuHandlerID(item):
    itemTypeID = item.itemTypeID
    if itemTypeID not in _HANDLERS_MAP:
        return ''
    handlers = _HANDLERS_MAP[item.itemTypeID]
    return handlers[item.isForSale] if len(handlers) > 1 else handlers[0]


_CUSTOMIZATION_VEHICLE_CRITERIA = ~REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR | ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE | ~REQ_CRITERIA.VEHICLE.IS_BOT

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
    elif itemType == GUI_ITEM_TYPE.OPTIONALDEVICE:
        return OptDeviceBonusesDescriptionBuilder().getEffectDescription(item)
    else:
        template = g_htmlTemplates['html_templates:lobby/popovers']['equipment']
        desc = item.formattedShortDescription(template.source)
        return text_styles.main(desc)


def createStorageDefVO(itemID, title, description, count, price, image, imageAlt, itemType='', nationFlagIcon='', enabled=True, available=True, contextMenuId='', additionalInfo='', active=GOODIE_STATE.INACTIVE, upgradable=False, upgradeButtonTooltip='', extraParams=(), specializations=()):
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
     'available': available,
     'additionalInfo': additionalInfo,
     'active': active == GOODIE_STATE.ACTIVE,
     'upgradable': upgradable,
     'upgradeButtonTooltip': upgradeButtonTooltip,
     'extraParams': extraParams,
     'specializations': specializations,
     'contextMenuId': contextMenuId}


def getStorageVehicleVo(vehicle):
    name = getVehicleName(vehicle)
    description = _getVehicleDescription(vehicle)
    imageSmall = func_utils.makeFlashPath(vehicle.getShopIcon(STORE_CONSTANTS.ICON_SIZE_SMALL))
    stateIcon, stateText = _getVehicleInfo(vehicle)
    if not imageSmall and not stateText:
        stateText = text_styles.vehicleStatusInfoText(_ms(STORAGE.INHANGAR_NOIMAGE))
    vo = createStorageDefVO(vehicle.intCD, name, description, vehicle.inventoryCount, getItemPricesVO(vehicle.getSellPrice())[0], imageSmall, RES_SHOP.getVehicleIcon(STORE_CONSTANTS.ICON_SIZE_SMALL, 'empty_tank'), itemType=vehicle.getHighlightType(), nationFlagIcon=RES_SHOP.getNationFlagIcon(nations.NAMES[vehicle.nationID]), contextMenuId=CONTEXT_MENU_HANDLER_TYPE.STORAGE_VEHICLES_REGULAR_ITEM)
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
    items = vehicle.consumables.installed.getItems() + vehicle.optDevices.installed.getItems() + vehicle.shells.installed.getItems()
    return sum((item.getSellPrice().price.get(Currency.CREDITS, 0) * getattr(item, 'count', 1) for item in items))


def getStorageItemName(item):
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
    serverSettings = dependency.instance(ILobbyContext).getServerSettings()
    upgradable = item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and item.isUpgradable and serverSettings.isTrophyDevicesEnabled()
    vo = createStorageDefVO(item.intCD, getStorageItemName(item), getStorageItemDescr(item), item.inventoryCount, priceVO, getStorageItemIcon(item, STORE_CONSTANTS.ICON_SIZE_SMALL), 'altimage', itemType=item.getOverlayType(), nationFlagIcon=nationFlagIcon, enabled=item.isForSale, contextMenuId=_getContextMenuHandlerID(item), upgradable=upgradable, upgradeButtonTooltip=makeTooltip(body=backport.text(R.strings.storage.buttonUpgrade.tooltip.body())), extraParams=getItemExtraParams(item), specializations=getCategoriesIcons(item) if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE else ())
    return vo


def isStorageSessionTimeout():
    lastVisitTime = AccountSettings.getSessionSettings(LAST_STORAGE_VISITED_TIMESTAMP)
    return getCurrentTimestamp() - lastVisitTime > STORAGE_CONSTANTS.SESSION_TIMEOUT


def isCustomizationAvailableForSell(item, vehicleCD=None):
    return False if item.getSellPrice() == ITEM_PRICE_EMPTY or item.isRentable or item.isHidden else getAvailableForSellCustomizationCount(item, vehicleCD) > 0


def getAvailableForSellCustomizationCount(item, vehicleCD=None):
    if not item.isVehicleBound or vehicleCD is None:
        inventoryCount = item.inventoryCount
    else:
        inventoryCount = item.fullInventoryCount(vehicleCD)
        if item.isProgressive:
            availableForSell = inventoryCount - item.descriptor.progression.autoGrantCount
            inventoryCount = min(inventoryCount, availableForSell)
    return inventoryCount


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getVehicleCDForStyle(item, itemsCache=None):
    suitableVehicles = []
    itemFilter = item.descriptor.filter
    nationsFilter = []
    if itemFilter is not None and itemFilter.include:
        for node in itemFilter.include:
            if node.nations:
                nationsFilter += node.nations
            if node.vehicles:
                suitableVehicles += node.vehicles

        if not suitableVehicles and nationsFilter:
            nationName = nations.NAMES[nationsFilter[0]]
            topVehicle = getTopVehicleByNation(nationName)
            if topVehicle:
                try:
                    vehicleCD = makeVehicleTypeCompDescrByName(topVehicle)
                    vehicle = itemsCache.items.getItemByCD(vehicleCD)
                    if item.mayInstall(vehicle):
                        suitableVehicles.append(vehicleCD)
                except SoftException as e:
                    _logger.warning(e)

    if not suitableVehicles:
        req = _CUSTOMIZATION_VEHICLE_CRITERIA | ~REQ_CRITERIA.SECRET
        for vehCD, vehicle in itemsCache.items.getVehicles(req).iteritems():
            if not vehicle.isOutfitLocked and item.mayInstall(vehicle):
                suitableVehicles.append(vehCD)

    if not suitableVehicles:
        secretReq = _CUSTOMIZATION_VEHICLE_CRITERIA | REQ_CRITERIA.SECRET
        for vehCD, vehicle in itemsCache.items.getVehicles(secretReq).iteritems():
            if not vehicle.isOutfitLocked and item.mayInstall(vehicle):
                suitableVehicles.append(vehCD)

    return random.choice(suitableVehicles)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def customizationPreview(itemCD, itemsCache=None, vehicleCD=None):
    item = itemsCache.items.getItemByCD(itemCD)
    if vehicleCD is None:
        vehicleCD = getVehicleCDForStyle(item, itemsCache=itemsCache)
    showStylePreviewFunc = showStylePreview
    if item.isProgression:
        showStylePreviewFunc = showProgressionStylesStylePreview
    showStylePreviewFunc(vehicleCD, item, item.getDescription(), partial(showStorage, defaultSection=STORAGE_CONSTANTS.CUSTOMIZATION), backport.text(R.strings.vehicle_preview.header.backBtn.descrLabel.storage()))
    return


class OptDeviceBonusesDescriptionBuilder(object):
    KPI_VALUE_TEMPLATE = '{{colorTagOpen}}{}{{colorTagClose}}'
    KPI_HTML_TEMPLATE = g_htmlTemplates['html_templates:lobby/popovers']['equipment']

    def getDescription(self, item):
        return '\n'.join(chain((self.getEffectDescription(item),), self.getDescriptionByKpiStrings(item)))

    def getDescriptionByKpiStrings(self, item):
        if any((kpi.type == KPI.Type.AGGREGATE_MUL for kpi in item.getKpi())):
            return [item.shortDescriptionSpecial]
        return [ self.__createKpiString(kpi) for kpi in item.getKpi() ]

    def getEffectDescription(self, item):
        return self.__createEffectString(item)

    def __createEffectString(self, item):
        itemR = R.strings.artefacts.dyn(item.descriptor.groupName)
        effectR = itemR.dyn('effect') if itemR else None
        effectsList = [ backport.text(effect()) for effect in effectR.values() ] if effectR else []
        return text_styles.concatStylesToSingleLine(icons.lightning(), backport.text(R.strings.storage.optDevice.hover.effect()), effectsList[0]).format(**self.KPI_HTML_TEMPLATE.source) if effectsList else ''

    def __createKpiString(self, kpi):
        value = self.__kpiFormat(kpi, kpi.value)
        specValue = self.__kpiFormat(kpi, kpi.specValue) if kpi.specValue else None
        generalValue = ' / '.join((value, specValue)) if specValue is not None else value
        bonus = kpi.getDescriptionR()
        description = ' '.join((generalValue, backport.text(bonus) if bonus else ''))
        return description.format(**self.KPI_HTML_TEMPLATE.source)

    def __kpiFormat(self, kpi, value):
        return self.KPI_VALUE_TEMPLATE.format(getKpiValueString(kpi, value))


def getItemExtraParams(item):
    return OptDeviceBonusesDescriptionBuilder().getDescriptionByKpiStrings(item) if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE else ()


def getCategoriesIcons(device):
    return [ backport.image(R.images.gui.maps.icons.specialization.dyn('medium_{}_off'.format(category))()) for category in SlotCategories.ORDER if category in device.descriptor.categories ]
