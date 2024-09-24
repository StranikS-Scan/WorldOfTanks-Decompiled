# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/lootbox_system/utils.py
import logging
import random
from typing import TYPE_CHECKING
import BigWorld
from CurrentVehicle import g_currentVehicle
from account_helpers.AccountSettings import LOOT_BOXES_OPEN_ANIMATION_ENABLED
from adisp import adisp_process
from constants import IS_CHINA
from gui import GUI_SETTINGS, SystemMessages
from gui.impl import backport
from gui.lootbox_system.awards_manager import AwardsManager
from gui.lootbox_system.common import COUNTRY_CODES_FOR_EXTERNAL_LOOT_LIST, getTextResource
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.gui_items.processors.loot_boxes import LootBoxSystemOpenProcessor
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from shared_utils import findFirst, first
from skeletons.gui.game_control import ILootBoxSystemController
from skeletons.gui.shared import IItemsCache
if TYPE_CHECKING:
    from typing import Callable, List, Optional
    from gui.shared.gui_items.customization.c11n_items import Customization, Style
    from gui.shared.gui_items.loot_box import LootBox
    from gui.server_events.bonuses import SimpleBonus
    from gui.shared.gui_items.Vehicle import Vehicle
_logger = logging.getLogger(__name__)

def areUsedExternalTransitions():
    return IS_CHINA


@adisp_process
@dependency.replace_none_kwargs(lootBoxes=ILootBoxSystemController)
def openBoxes(category, count, processResult=None, lootBoxes=None):

    def isCompatibleBox(b):
        return b.getType() == lootBoxes.eventName and b.getCategory() == category

    box = first(lootBoxes.getBoxes(isCompatibleBox))
    if box is None:
        _logger.error('No box with category %s found', category)
        return
    else:
        if box.isEnabled():
            result = yield LootBoxSystemOpenProcessor(box, count).request()
            if result and result.success:
                if callable(processResult):
                    processResult([ AwardsManager.composeBonuses([slot]) for slot in result.auxData['bonus'] ])
            else:
                _logger.error('Failed to open loot box')
        else:
            pathParts = 'serviceChannelMessages/server_error'.split('/')
            SystemMessages.pushMessage(text=backport.text(getTextResource(pathParts + ['DISABLED'])()), type=SystemMessages.SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': backport.text(getTextResource(pathParts)())})
            g_eventBus.handleEvent(events.LootBoxSystemEvent(events.LootBoxSystemEvent.OPENING_ERROR), scope=EVENT_BUS_SCOPE.LOBBY)
        return


@dependency.replace_none_kwargs(lootBoxes=ILootBoxSystemController)
def getPreferredBox(category='', lootBoxes=None):
    return first(lootBoxes.getBoxes(lambda b: b.getCategory() == category)) if category else first(lootBoxes.getActiveBoxes(lambda b: b.getInventoryCount())) or first(lootBoxes.getActiveBoxes())


@dependency.replace_none_kwargs(lootBoxes=ILootBoxSystemController)
def getInfoPageSettings(setting, lootBoxes=None):
    eventSetting = GUI_SETTINGS.lootboxSystem.get('infoPage').get(setting).get(lootBoxes.eventName)
    return eventSetting if eventSetting is not None else GUI_SETTINGS.lootboxSystem.get('infoPage').get(setting).get('default')


@dependency.replace_none_kwargs(lootBoxes=ILootBoxSystemController)
def getIntroVideoUrl(lootBoxes=None):
    urlPart = GUI_SETTINGS.lootboxSystem.get('intro').get(lootBoxes.eventName, '')
    return ''.join((GUI_SETTINGS.baseUrls['webBridgeRootURL'], urlPart)) if urlPart else ''


def isCountryForShowingExternalLootList():
    return BigWorld.player().spaFlags.getCountry() in COUNTRY_CODES_FOR_EXTERNAL_LOOT_LIST


def openExternalLootList():
    if isCountryForShowingExternalLootList():
        g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.LOOT_BOXES_LIST))


@dependency.replace_none_kwargs(lootBoxes=ILootBoxSystemController)
def getIsAnimationActive(lootBoxes=None):
    return lootBoxes.getSetting(LOOT_BOXES_OPEN_ANIMATION_ENABLED)


@dependency.replace_none_kwargs(lootBoxes=ILootBoxSystemController)
def setIsAnimationActive(value, lootBoxes=None):
    lootBoxes.setSetting(LOOT_BOXES_OPEN_ANIMATION_ENABLED, value)


def getSingleVehicleCDForCustomization(customization):
    itemFilter = customization.descriptor.filter
    if itemFilter is not None and itemFilter.include:
        vehicles = []
        for node in itemFilter.include:
            if node.nations or node.levels:
                return
            if node.vehicles:
                vehicles.extend(node.vehicles)

        if len(vehicles) == 1:
            return vehicles[0]
    return


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getLootboxStatisticsKey(boxID=None, itemsCache=None):
    box = findFirst(lambda b: b.getID() == boxID, itemsCache.items.tokens.getLootBoxes().itervalues())
    return box.getStatsName() or str(boxID) if box is not None else getPreferredBox().getStatsName()


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getVehicleForStyle(style, itemsCache=None):
    vehicle = g_currentVehicle.item if g_currentVehicle.isPresent() else None
    if vehicle is not None and not vehicle.descriptor.type.isCustomizationLocked and style.mayInstall(vehicle):
        return vehicle
    else:
        getVehicleByCD = itemsCache.items.getItemByCD
        getVehiclesStats = itemsCache.items.getAccountDossier().getRandomStats().getVehicles
        vehiclesStats = {vehicleCD:value for vehicleCD, value in getVehiclesStats() if not getVehicleByCD(vehicleCD).descriptor.type.isCustomizationLocked and style.mayInstall(getVehicleByCD(vehicleCD))}
        if vehiclesStats:
            sortedVehicles = sorted(vehiclesStats.items(), key=lambda vStat: vStat[1].battlesCount, reverse=True)
            if sortedVehicles:
                return getVehicleByCD(sortedVehicles[0][0])
        suitableVehicles = _getVehiclesForStylePreview(criteria=REQ_CRITERIA.INVENTORY | ~REQ_CRITERIA.VEHICLE.IS_OUTFIT_LOCKED | REQ_CRITERIA.VEHICLE.FOR_ITEM(style))
        if suitableVehicles:
            return first(suitableVehicles)
        suitableVehicles = _getVehiclesForStylePreview(criteria=~REQ_CRITERIA.INVENTORY | ~REQ_CRITERIA.VEHICLE.IS_OUTFIT_LOCKED | REQ_CRITERIA.VEHICLE.FOR_ITEM(style) | ~REQ_CRITERIA.VEHICLE.EVENT)
        return random.choice(suitableVehicles) if suitableVehicles else first(_getVehiclesForStylePreview(criteria=REQ_CRITERIA.VEHICLE.FOR_ITEM(style)))


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _getVehiclesForStylePreview(criteria=None, itemsCache=None):
    return sorted(itemsCache.items.getVehicles(criteria=criteria).values(), key=lambda item: item.level, reverse=True)
