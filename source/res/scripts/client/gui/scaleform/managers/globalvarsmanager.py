# Embedded file name: scripts/client/gui/Scaleform/managers/GlobalVarsManager.py
import constants
from gui.shared.ItemsCache import g_itemsCache
from helpers import getClientOverride
from gui import GUI_SETTINGS, game_control
from gui.shared.fortifications import isFortificationEnabled, isFortificationBattlesEnabled
from gui.Scaleform.framework.entities.abstract.GlobalVarsMgrMeta import GlobalVarsMgrMeta

class GlobalVarsManager(GlobalVarsMgrMeta):

    def __init__(self):
        super(GlobalVarsManager, self).__init__()
        self.__isTutorialDisabled = False
        self.__isTutorialRunning = False

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

    def isTutorialDisabled(self):
        return self.__isTutorialDisabled

    def setTutorialDisabled(self, isDisabled):
        self.__isTutorialDisabled = isDisabled

    def isTutorialRunning(self):
        return self.__isTutorialRunning

    def setTutorialRunning(self, isRunning):
        self.__isTutorialRunning = isRunning

    def isFreeXpToTankman(self):
        return GUI_SETTINGS.freeXpToTankman

    def getLocaleOverride(self):
        return getClientOverride()

    def isRoamingEnabled(self):
        return game_control.g_instance.roaming.isEnabled()

    def isInRoaming(self):
        return game_control.g_instance.roaming.isInRoaming()

    def isFortificationAvailable(self):
        return isFortificationEnabled()

    def isFortificationBattleAvailable(self):
        return isFortificationBattlesEnabled()

    def isWalletAvailable(self):
        return game_control.g_instance.wallet.isAvailable

    def isShowLoginRssFeed(self):
        return GUI_SETTINGS.loginRssFeed.show

    def isShowTicker(self):
        return constants.IS_CHINA and GUI_SETTINGS.movingText.show

    def isRentalsEnabled(self):
        return constants.IS_RENTALS_ENABLED
