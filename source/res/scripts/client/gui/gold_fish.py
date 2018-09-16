# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/gold_fish.py
from account_helpers.AccountSettings import AccountSettings, GOLD_FISH_LAST_SHOW_TIME
import constants
from gui import GUI_SETTINGS
from helpers import dependency
from helpers.time_utils import getCurrentTimestamp
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

@dependency.replace_none_kwargs(itemsCache=IItemsCache, lobbyContext=ILobbyContext)
def isGoldFishActionActive(itemsCache=None, lobbyContext=None):
    outOfSessionWallet = constants.ACCOUNT_ATTR.OUT_OF_SESSION_WALLET
    return False if itemsCache is None or lobbyContext is None else not itemsCache.items.stats.isGoldFishBonusApplied and lobbyContext.getServerSettings().isGoldFishEnabled() and not itemsCache.items.stats.attributes & outOfSessionWallet != 0


def isTimeToShowGoldFishPromo():
    return getCurrentTimestamp() - AccountSettings.getFilter(GOLD_FISH_LAST_SHOW_TIME) >= GUI_SETTINGS.goldFishActionShowCooldown
