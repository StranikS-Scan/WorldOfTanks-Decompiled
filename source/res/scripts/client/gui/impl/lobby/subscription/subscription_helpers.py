# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/subscription/subscription_helpers.py
from helpers import dependency
from account_helpers import AccountSettings
from account_helpers.AccountSettings import SUBSCRIPTION_DAILY_QUESTS_INTRO_SHOWN
from gui.shared.event_dispatcher import showSubscriptionDailyQuestsIntroWindow
from skeletons.gui.lobby_context import ILobbyContext

def isSubscriptionDailyQuestsIntroShown():
    return AccountSettings.getSettings(SUBSCRIPTION_DAILY_QUESTS_INTRO_SHOWN)


def showSubscriptionDailyQuestsIntro():
    _lobbyContext = dependency.instance(ILobbyContext)
    if not _lobbyContext.getServerSettings().isDailyQuestsExtraRewardsEnabled():
        return None
    else:
        if not isSubscriptionDailyQuestsIntroShown():
            showSubscriptionDailyQuestsIntroWindow()
            AccountSettings.setSettings(SUBSCRIPTION_DAILY_QUESTS_INTRO_SHOWN, True)
        return None
