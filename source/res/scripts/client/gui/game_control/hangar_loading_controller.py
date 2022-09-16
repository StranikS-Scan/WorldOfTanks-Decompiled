# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/hangar_loading_controller.py
import Event
from gui.impl.lobby.crew.crew_welcome_screen import CrewWelcomeScreenWindow
from gui.shared.account_settings_helper import AccountSettingsHelper
from helpers import dependency
from skeletons.gui.game_control import IHangarLoadingController, IBootcampController, IUISpamController
from skeletons.gui.shared.utils import IHangarSpace
from gui.shared.event_dispatcher import showCrewWelcomeScreenView

class HangarLoadingController(IHangarLoadingController):
    __bootcamp = dependency.descriptor(IBootcampController)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __uiSpamController = dependency.descriptor(IUISpamController)

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
        if self.__isHangarLoadedAfterLogin():
            if self.__hangarSpace.spaceInited:
                self.__hangarLoadedAfterLoginNotify()
            else:
                self.__hangarSpace.onSpaceCreate += self.__hangarLoadedAfterLoginNotify

    def __processCrewWelcomeScreen(self):
        if not self.__uiSpamController.shouldBeHidden(CrewWelcomeScreenWindow.UI_SPAM_WINDOW_NAME):
            showCrewWelcomeScreenView()
        else:
            AccountSettingsHelper.welcomeScreenShown()

    def __hangarLoadedAfterLoginNotify(self):
        self.__hangarSpace.onSpaceCreate -= self.__hangarLoadedAfterLoginNotify
        self.__processCrewWelcomeScreen()
        self.onHangarLoadedAfterLogin()

    def __isHangarLoadedAfterLogin(self):
        return self.__isConnectedAsAccount and not self.__bootcamp.isInBootcamp() and not self.__bootcamp.isInBootcampAccount()
