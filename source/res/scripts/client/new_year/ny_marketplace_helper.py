# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_marketplace_helper.py
import typing
from gui.impl.lobby.new_year.marketplace import bonusChecker
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from ny_common.MarketplaceConfig import MarketplaceConfig, CategoryItem

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
    return item.calculateDiscount(collectionDistributions, bonusChecker) >= 100
