# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/hangar_loading_controller.py
import Event
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior
from gui.shared.account_settings_helper import AccountSettingsHelper
from gui.shared.event_dispatcher import showCrew5075Welcome
from helpers import dependency
from skeletons.gui.game_control import IHangarLoadingController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
CREW_WELCOME_SCREEN_BATTLES_COUNT = 100

class HangarLoadingController(IHangarLoadingController):
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(HangarLoadingController, self).__init__()
        self.onHangarLoadedAfterLogin = Event.Event()
        self.__isConnectedAsAccount = False

    def fini(self):
        self.__isConnectedAsAccount = False
        self.__hangarSpace.onSpaceCreate -= self.__hangarLoadedAfterLoginNotify

    def onAvatarBecomePlayer(self):
        self.__isConnectedAsAccount = False

    def onConnected(self):
        self.__isConnectedAsAccount = True

    def onAccountBecomeNonPlayer(self):
        self.__isConnectedAsAccount = False
        self.__hangarSpace.onSpaceCreate -= self.__hangarLoadedAfterLoginNotify

    def onDisconnected(self):
        self.__isConnectedAsAccount = False
        self.__hangarSpace.onSpaceCreate -= self.__hangarLoadedAfterLoginNotify

    def onLobbyInited(self, event):
        if self.isHangarLoadedAfterLogin():
            if self.__hangarSpace.spaceInited:
                self.__hangarLoadedAfterLoginNotify()
            else:
                self.__hangarSpace.onSpaceCreate += self.__hangarLoadedAfterLoginNotify

    def __processCrewWelcomeScreen(self):
        if AccountSettingsHelper.isWelcomeScreenShown(GuiSettingsBehavior.CREW_5075_WELCOME_SHOWN):
            return
        if self.__itemsCache.items.getAccountDossier().getTotalStats().getBattlesCount() > CREW_WELCOME_SCREEN_BATTLES_COUNT:
            showCrew5075Welcome()
        else:
            AccountSettingsHelper.welcomeScreenShown(GuiSettingsBehavior.CREW_5075_WELCOME_SHOWN)

    def __hangarLoadedAfterLoginNotify(self):
        self.__hangarSpace.onSpaceCreate -= self.__hangarLoadedAfterLoginNotify
        self.__processCrewWelcomeScreen()
        self.onHangarLoadedAfterLogin()

    def isHangarLoadedAfterLogin(self):
        return self.__isConnectedAsAccount
