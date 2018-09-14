# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/managers/GlobalVarsManager.py
import constants
from gui import GUI_SETTINGS
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.framework.entities.abstract.GlobalVarsMgrMeta import GlobalVarsMgrMeta
from gui.shared import g_itemsCache
from helpers import getClientOverride, dependency
from skeletons.gui.game_control import IWalletController, ITradeInController

class GlobalVarsManager(GlobalVarsMgrMeta):
    _isLoginLoadInfoRequested = False
    wallet = dependency.descriptor(IWalletController)
    tradeIn = dependency.descriptor(ITradeInController)

    def __init__(self):
        super(GlobalVarsManager, self).__init__()

    def isDevelopment(self):
        return constants.IS_DEVELOPMENT

    def isShowLangaugeBar(self):
        return GUI_SETTINGS.isShowLanguageBar

    def isShowServerStats(self):
        return constants.IS_SHOW_SERVER_STATS

    def isChina(self):
        return constants.IS_CHINA

    def isKorea(self):
        return constants.IS_KOREA

    def isTutorialRunning(self, tutorialID):
        try:
            from tutorial.loader import isTutorialRunning
        except ImportError:

            def isTutorialRunning(_):
                return False

        return isTutorialRunning(tutorialID)

    def isFreeXpToTankman(self):
        return g_itemsCache.items.shop.freeXPToTManXPRate > 0

    def getLocaleOverride(self):
        return getClientOverride()

    def isRoamingEnabled(self):
        return g_lobbyContext.getServerSettings().roaming.isEnabled()

    def isInRoaming(self):
        return g_lobbyContext.getServerSettings().roaming.isInRoaming()

    def isFortificationAvailable(self):
        return g_lobbyContext.getServerSettings().isFortsEnabled()

    def isWalletAvailable(self):
        if self.wallet:
            return self.wallet.isAvailable
        else:
            return False

    def isShowLoginRssFeed(self):
        return GUI_SETTINGS.loginRssFeed.show

    def isShowTicker(self):
        return constants.IS_CHINA and GUI_SETTINGS.movingText.show

    def isRentalsEnabled(self):
        return constants.IS_RENTALS_ENABLED

    def isPotapovQuestEnabled(self):
        return g_lobbyContext.getServerSettings().isPotapovQuestEnabled()

    def isLoginLoadedAtFirstTime(self):
        if GlobalVarsManager._isLoginLoadInfoRequested:
            return False
        else:
            GlobalVarsManager._isLoginLoadInfoRequested = True
            return True

    def isVehicleRestoreEnabled(self):
        return g_lobbyContext.getServerSettings().isVehicleRestoreEnabled()

    def isTradeInEnabled(self):
        return self.tradeIn.isEnabled()
