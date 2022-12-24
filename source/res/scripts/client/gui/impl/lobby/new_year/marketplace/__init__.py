# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/marketplace/__init__.py
from adisp import adisp_process
from gui.Scaleform.daapi.view.lobby.customization.context.styled_mode import StyledMode
from gui.customization.constants import CustomizationModes
from gui.impl.gen.view_models.views.lobby.new_year.ny_constants import CollectionName
from gui.impl.lobby.new_year.ny_views_helpers import marketPlaceKeySortOrder
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.new_year_bonus_packer import getNYMarketplaceRewardBonuses
from gui.server_events.bonuses import getNonQuestBonuses
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_INDICES
from helpers import dependency
from ny_common.settings import MarketplaceConsts
from shared_utils import awaitNextFrame
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_COLLECTIONS_UI_IDS_MAP = {'ny22:gift': CollectionName.GIFTSYSTEM}

def _getItemTypeID(itemTypeName):
    if itemTypeName == 'projection_decal':
        itemTypeID = GUI_ITEM_TYPE.PROJECTION_DECAL
    elif itemTypeName == 'personal_number':
        itemTypeID = GUI_ITEM_TYPE.PERSONAL_NUMBER
    else:
        itemTypeID = GUI_ITEM_TYPE_INDICES.get(itemTypeName)
    return itemTypeID


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getMarketItemBonusesFromItem(item, eventsCache=None):
    actions = item.getActions()
    rewards = actions.get(MarketplaceConsts.BUY_REWARDS)
    if rewards:
        bonuses = []
        for _, _, bonusData in rewards:
            bonuses.extend(createBonuses(bonusData))

        return bonuses
    if actions.get(MarketplaceConsts.FILL_COLLECTION):
        questID = item.getID()
        quest = eventsCache.getQuestByID(questID)
        if quest:
            return quest.getBonuses()
    return []


def getMarketRewards(item, isMerge=False):
    bonuses = getMarketItemBonusesFromItem(item)
    return getNYMarketplaceRewardBonuses(bonuses, isMerge, sortKey=lambda b: marketPlaceKeySortOrder(*b))


def createBonuses(bonusData):
    bonuses = []
    for name, value in bonusData.iteritems():
        for bonus in getNonQuestBonuses(name, value):
            bonuses.append(bonus)

    return bonuses


@dependency.replace_none_kwargs(service=ICustomizationService)
def bonusChecker(rewardsData, service=None):
    for rewardType, rewards in rewardsData.iteritems():
        if rewardType != 'customizations':
            continue
        for reward in rewards:
            guiType = _getItemTypeID(reward.get('custType'))
            item = service.getItemByID(guiType, reward.get('id'))
            if item.isInInventory or item.installedCount():
                return True

    return False


def getSettingsName(item):
    actions = item.getActions()
    collectionAction = actions.get(MarketplaceConsts.FILL_COLLECTION)
    return collectionAction.get(MarketplaceConsts.FILL_COLLECTION_SETTING) if collectionAction is not None else _COLLECTIONS_UI_IDS_MAP.get(item.getID(), CollectionName.UNDEFINED).value


@adisp_process
@dependency.replace_none_kwargs(service=ICustomizationService, itemsCache=IItemsCache)
def showStyleFromMarketPlace(styleID, vehInvID, service=None, itemsCache=None):
    yield awaitNextFrame()
    NewYearNavigation.closeMainView(switchCamera=True, toHangar=False)

    def styleCallback():
        if styleID is not None:
            style = service.getItemByID(GUI_ITEM_TYPE.STYLE, styleID)
            vehicle = itemsCache.items.getVehicle(vehInvID)
            installedOn = style.getInstalledVehicles()
            if vehicle.intCD not in installedOn:
                ctx = service.getCtx()
                ctx.changeMode(CustomizationModes.STYLED)
                ctx.mode.installItem(style.intCD, StyledMode.STYLE_SLOT)
        return

    service.showCustomization(vehInvID, callback=styleCallback)
