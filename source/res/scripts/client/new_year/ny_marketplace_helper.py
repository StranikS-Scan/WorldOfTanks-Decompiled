# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_marketplace_helper.py
import typing
from gui.impl.lobby.new_year.marketplace import bonusChecker
from gui.shared.gui_items import GUI_ITEM_TYPE_INDICES, GUI_ITEM_TYPE
from helpers import dependency
from ny_common.settings import MarketplaceConsts
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from ny_common.MarketplaceConfig import MarketplaceConfig, CategoryItem

def _getItemTypeID(itemTypeName):
    if itemTypeName == 'projection_decal':
        itemTypeID = GUI_ITEM_TYPE.PROJECTION_DECAL
    elif itemTypeName == 'personal_number':
        itemTypeID = GUI_ITEM_TYPE.PERSONAL_NUMBER
    else:
        itemTypeID = GUI_ITEM_TYPE_INDICES.get(itemTypeName)
    return itemTypeID


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getNYMarketplaceConfig(lobbyCtx=None):
    return lobbyCtx.getServerSettings().getNewYearMarketplaceConfig()


def isCollectionReceived(yearName):
    config = getNYMarketplaceConfig()
    items = config.getCategoryItems(yearName)
    for item in items:
        if not isCollectionItemReceived(item):
            return False

    return True


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def isCollectionItemReceived(item, itemsCache=None):
    collectionDistributions = itemsCache.items.festivity.getCollectionDistributions()
    prevNYLevel = itemsCache.items.festivity.getPrevNYLevel()
    return item.calculateDiscount(collectionDistributions, bonusChecker, prevNYLevel) >= 100


@dependency.replace_none_kwargs(service=ICustomizationService)
def getCollectionCompleteInfo(item, service=None):
    completed, total = (0, 0)
    actions = item.getActions()
    actionData = actions.get(MarketplaceConsts.BUY_REWARDS)
    if actionData:
        for _, _, rewardsData in actionData:
            for rewardType, rewards in rewardsData.iteritems():
                if rewardType != 'customizations':
                    continue
                for reward in rewards:
                    guiType = _getItemTypeID(reward.get('custType'))
                    item = service.getItemByID(guiType, reward.get('id'))
                    if item.isInInventory or item.installedCount():
                        completed += 1
                    total += 1

    return (completed, total)
