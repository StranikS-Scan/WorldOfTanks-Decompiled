# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/comp7_helpers/comp7_c11n_helpers.py
import logging
import typing
from random import shuffle
from CurrentVehicle import g_currentVehicle
from comp7.gui.shared.gui_items.dossier.stats import getComp7DossierStats
from comp7.gui.impl.lobby.comp7_helpers.comp7_shared import getComp7Criteria
from comp7_common_const import qualificationQuestIDBySeasonNumber
from customization_quests_common import serializeToken
from gui.Scaleform.daapi.view.lobby.customization.context.editable_style_mode import EditableStyleMode
from gui.Scaleform.daapi.view.lobby.customization.shared import CustomizationTabs
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from items.components.c11n_constants import CustomizationType
from shared_utils import first
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
if typing.TYPE_CHECKING:
    from typing import Optional, Union, Dict, Tuple, Callable, List
    from gui.shared.gui_items.customization.c11n_items import Style, Customization
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.shared.utils.requesters import RequestCriteria
    from skeletons.gui.shared import IItemsRequester
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(c11nService=ICustomizationService)
def getComp7ProgressionStyleCamouflage(styleID, branch, level, c11nService=None):
    style = c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, styleID)
    tokenID = serializeToken(styleID, branch)
    c11nQuestProgress = style.descriptor.questsProgression
    groupItems = c11nQuestProgress.getItemsForGroup(tokenID)
    if level >= len(groupItems):
        _logger.error('Wrong progress level [%s] for customization progress group [%s]', level, tokenID)
        return
    levelItems = groupItems[level]
    camoID = first(levelItems.get(CustomizationType.CAMOUFLAGE, ()))
    if camoID is None:
        _logger.error('Missing camouflage for level [%s] in customization progress group [%s]', level, tokenID)
        return
    else:
        return c11nService.getItemByID(GUI_ITEM_TYPE.CAMOUFLAGE, camoID)


@dependency.replace_none_kwargs(comp7Ctrl=IComp7Controller, eventsCache=IEventsCache, c11n=ICustomizationService)
def getComp7ProgressionStyle(seasonNum=None, comp7Ctrl=None, eventsCache=None, c11n=None):
    seasonNum = seasonNum or comp7Ctrl.getActualSeasonNumber()
    if seasonNum is None:
        return
    else:
        qID = qualificationQuestIDBySeasonNumber(seasonNum)
        qualQuest = eventsCache.getUngroupedBasicQuestByID(qID)
        if qualQuest is None:
            return
        styleID = None
        bonuses = qualQuest.getRawBonuses()
        custs = bonuses.get('customizations', ())
        for cust in custs:
            if cust.get('custType') == 'style':
                styleID = cust.get('id')
                break

        return None if styleID is None else c11n.getItemByID(GUI_ITEM_TYPE.STYLE, styleID)


@dependency.replace_none_kwargs(itemsCache=IItemsCache, comp7Controller=IComp7Controller)
def getStylePreviewVehicle(style, defaultVehicle=None, itemsCache=None, comp7Controller=None):
    if g_currentVehicle.isPresent() and style.mayInstall(g_currentVehicle.item):
        return g_currentVehicle.item.intCD
    else:
        comp7Season = comp7Controller.getActualSeasonNumber()
        if comp7Season is not None:
            accDossier = itemsCache.items.getAccountDossier()
            stats = getComp7DossierStats(accDossier, season=comp7Season)
            vehicles = stats.getVehicles() or accDossier.getRandomStats().getVehicles()
            if vehicles:
                sortedVehicles = sorted(vehicles.items(), key=lambda vStat: vStat[1].battlesCount, reverse=True)
                for vehicleCD, _ in sortedVehicles:
                    vehicle = itemsCache.items.getItemByCD(vehicleCD)
                    if style.mayInstall(vehicle):
                        return vehicleCD

        styleCriteria = REQ_CRITERIA.CUSTOM(style.mayInstall)
        invVehicles = itemsCache.items.getVehicles(getComp7Criteria() | styleCriteria).values()
        vehicles = sorted([ v for v in invVehicles ], key=lambda v: v.level, reverse=True)
        if vehicles:
            return first(vehicles).intCD
        if defaultVehicle is not None:
            return defaultVehicle
        allSuitableVehicles = itemsCache.items.getVehicles(styleCriteria)
        vehicle = first(sorted(allSuitableVehicles.values(), key=lambda v: v.level, reverse=True))
        if vehicle is not None:
            return vehicle.intCD
        _logger.warning('Could not find suitable vehicle for style %s', style.id)
        return


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def hasVehicleForCustomization(customization, itemsCache=None):
    inventorySuitableVehicles = itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.CUSTOM(customization.mayInstall))
    return bool(inventorySuitableVehicles)


@dependency.replace_none_kwargs(itemsFactory=IGuiItemsFactory)
def getPreviewOutfit(style, branchID, progressLevel, vehicleCD, itemsFactory=None):
    camo = getComp7ProgressionStyleCamouflage(style.id, branchID, progressLevel)
    season = first(style.seasons)
    outfit = style.getOutfit(season, vehicleCD=vehicleCD)
    outfitComponent = outfit.pack()
    if camo:
        for camoComponent in outfitComponent.camouflages:
            camoComponent.id = camo.id

    outfitComponent = style.descriptor.addPartsToOutfit(season, outfitComponent, outfit.vehicleCD)
    return itemsFactory.createOutfit(component=outfitComponent, vehicleCD=outfit.vehicleCD)


def isC11nItemTokenAttainable(allTokens, item, supportedTypes=(GUI_ITEM_TYPE.EMBLEM, GUI_ITEM_TYPE.INSCRIPTION)):
    if item.itemTypeID not in supportedTypes or item.isUnlockingExpired():
        return False
    requiredToken = item.requiredToken
    return False if not requiredToken or requiredToken in allTokens and allTokens[requiredToken][1] >= item.descriptor.requiredTokenCount else True


def getVehicleForStyle(items, criteria, sortKey, style, preferredVeh=None):
    styleID = style.id
    styleIsInInventory = style.isInInventory
    if preferredVeh and criteria(preferredVeh) and (styleIsInInventory or preferredVeh.hasStyle(styleID)):
        return (preferredVeh, '')
    validVehs = list(items.getVehicles(criteria).values())
    if not validVehs:
        return (None, 'noValidVehicles')
    shuffle(validVehs)
    styledVehs = [ veh for veh in validVehs if veh.hasStyle(styleID) ]
    if styledVehs:
        return (max(styledVehs, key=sortKey), '')
    else:
        return (None, 'allStylesInstalledOnInvalids') if not styleIsInInventory else (max(validVehs, key=sortKey), '')


def getMaxLevelAndBattlesVehicleSortKey(items):
    vehRndStats = items.getAccountDossier().getRandomStats().getVehicles()

    def maxLevelAndBattlesVehicleSortKey(vehicle):
        battlesCount = vehRndStats.get(vehicle.intCD, (0,))[0]
        return (vehicle.level, battlesCount)

    return maxLevelAndBattlesVehicleSortKey


def selectStyleAndDecalInC11nHangar(c11n, items, styleCD, decalCD):
    ctx = c11n.getCtx()
    if ctx is None:
        _logger.error('c11n context is None')
        return
    else:
        ctx.editStyle(styleCD)
        mode = ctx.mode
        if not isinstance(mode, EditableStyleMode):
            _logger.error('Should be EditableStyleMode!')
            return
        if decalCD:
            item = items.getItemByCD(decalCD)
            if item.itemTypeID == GUI_ITEM_TYPE.EMBLEM:
                mode.changeTab(CustomizationTabs.EMBLEMS, decalCD)
                return
            if item.itemTypeID == GUI_ITEM_TYPE.INSCRIPTION:
                mode.changeTab(CustomizationTabs.INSCRIPTIONS, decalCD)
                return
        mode.changeTab(CustomizationTabs.DEFAULT)
        return
