# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/comp7_c11n_helpers.py
import logging
import typing
from shared_utils import first
from CurrentVehicle import g_currentVehicle
from customization_quests_common import serializeToken
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from items.components.c11n_constants import CustomizationType
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.customization.c11n_items import Style, Customization
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


@dependency.replace_none_kwargs(itemsCache=IItemsCache, comp7Controller=IComp7Controller)
def getStylePreviewVehicle(style, defaultVehicle=None, itemsCache=None, comp7Controller=None):
    if g_currentVehicle.isPresent() and style.mayInstall(g_currentVehicle.item):
        return g_currentVehicle.item.intCD
    else:
        accDossier = itemsCache.items.getAccountDossier()
        comp7Season = comp7Controller.getActualSeasonNumber()
        vehicles = accDossier.getComp7Stats(season=comp7Season).getVehicles() or accDossier.getRandomStats().getVehicles()
        if vehicles:
            sortedVehicles = sorted(vehicles.items(), key=lambda vStat: vStat[1].battlesCount, reverse=True)
            for vehicleCD, _ in sortedVehicles:
                vehicle = itemsCache.items.getItemByCD(vehicleCD)
                if style.mayInstall(vehicle):
                    return vehicleCD

        styleCriteria = REQ_CRITERIA.CUSTOM(style.mayInstall)
        inventorySuitableVehicles = itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | styleCriteria)
        vehicle = first(sorted(inventorySuitableVehicles.values(), key=lambda v: v.level, reverse=True))
        if vehicle is not None:
            return vehicle.intCD
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
def getPreviewOutfit(style, branchID, progressLevel, itemsFactory=None):
    camo = getComp7ProgressionStyleCamouflage(style.id, branchID, progressLevel)
    season = first(style.seasons)
    outfit = style.getOutfit(season)
    outfitComponent = outfit.pack()
    if camo:
        for camoComponent in outfitComponent.camouflages:
            camoComponent.id = camo.id

    outfitComponent = style.descriptor.addPartsToOutfit(season, outfitComponent, outfit.vehicleCD)
    return itemsFactory.createOutfit(component=outfitComponent, vehicleCD=outfit.vehicleCD)
