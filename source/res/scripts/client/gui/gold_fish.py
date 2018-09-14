# Embedded file name: scripts/client/gui/gold_fish.py
from account_helpers.AccountSettings import AccountSettings, GOLD_FISH_LAST_SHOW_TIME
import constants
from gui import GUI_SETTINGS
from helpers.time_utils import getCurrentTimestamp

def isGoldFishActionActive():
    from gui.LobbyContext import g_lobbyContext
    from gui.shared.ItemsCache import g_itemsCache
    outOfSessionWallet = constants.ACCOUNT_ATTR.OUT_OF_SESSION_WALLET
    return not g_itemsCache.items.stats.isGoldFishBonusApplied and g_lobbyContext.getServerSettings().isGoldFishEnabled() and not g_itemsCache.items.stats.attributes & outOfSessionWallet != 0


def isTimeToShowGoldFishPromo():
    return getCurrentTimestamp() - AccountSettings.getFilter(GOLD_FISH_LAST_SHOW_TIME) >= GUI_SETTINGS.goldFishActionShowCooldown
