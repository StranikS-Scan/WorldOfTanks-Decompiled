# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/storage_helpers.py
from gui import g_htmlTemplates
from gui.Scaleform.daapi.settings import BUTTON_LINKAGES
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.STORAGE import STORAGE
from gui.shared import g_eventBus, events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from helpers.i18n import makeString as _ms
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_parameters import params_helper
from gui.shared.utils.functions import getViewName
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import i18n, dependency, int2roman
from skeletons.gui.shared import IItemsCache
_MAX_COMPATIBLE_VEHS_COUNT = 5
_MAX_COMPATIBLE_GUNS_COUNT = 2

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


def createStorageDefVO(itemID, title, description, count, price, imageSmall, imageMedium, imageAlt, itemType='', nationFlagIcon='', level='', enabled=True, infoImgSrc='', infoText='', timerText='', timerIcon=''):
    return {'id': itemID,
     'title': title,
     'description': description,
     'count': count,
     'price': price,
     'imageMedium': imageMedium,
     'imageSmall': imageSmall,
     'imageAlt': imageAlt,
     'type': itemType,
     'nationFlagIcon': nationFlagIcon,
     'enabled': enabled,
     'level': level,
     'timerText': timerText,
     'timerIcon': timerIcon,
     'infoImgSrc': infoImgSrc,
     'infoText': infoText}


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


def showStorageModuleInfo(intCD):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.MODULE_INFO_WINDOW, getViewName(VIEW_ALIAS.MODULE_INFO_WINDOW, intCD), {'moduleCompactDescr': intCD,
     'isAdditionalInfoShow': i18n.makeString(MENU.MODULEINFO_ADDITIONALINFO)}), EVENT_BUS_SCOPE.LOBBY)


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


def getBoosterType(item):
    if item.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER:
        if item.isCrewBooster():
            return SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER_CREW_REPLACE
        return SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER
    return SLOT_HIGHLIGHT_TYPES.EQUIPMENT_PLUS if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and item.isDeluxe() else SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT


def getStorageItemIcon(item, size=STORE_CONSTANTS.ICON_SIZE_MEDIUM):
    if item.itemTypeID in GUI_ITEM_TYPE.VEHICLE_COMPONENTS:
        icon = item.getShopIcon(size)
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
