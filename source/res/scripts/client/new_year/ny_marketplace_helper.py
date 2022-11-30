# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_marketplace_helper.py
import typing
from gui.impl.lobby.new_year.marketplace import getMarketItemBonusesFromItem
from helpers import dependency
from ny_common.settings import MarketplaceConsts
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from ny_common.MarketplaceConfig import MarketplaceConfig

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


def isCollectionItemReceived(item):
    condition = None
    if isItemCollection(item):
        condition = any
    elif isItemGift(item):
        condition = all
    if condition is not None:
        receivedStatuses = []
        bonuses = getMarketItemBonusesFromItem(item)
        for bonus in bonuses:
            for bonusItem in bonus.getCustomizations():
                customization = bonus.getC11nItem(bonusItem)
                receivedStatuses.append(customization.isInInventory or customization.installedCount())

        if condition(receivedStatuses):
            return True
    return False


def isItemCollection(item):
    actions = item.getActions()
    return bool(actions.get(MarketplaceConsts.FILL_COLLECTION))


def isItemGift(item):
    actions = item.getActions()
    return bool(actions.get(MarketplaceConsts.BUY_REWARDS))
