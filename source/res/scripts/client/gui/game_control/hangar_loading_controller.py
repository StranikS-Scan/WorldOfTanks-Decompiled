# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/hangar_loading_controller.py
import Event
from helpers import dependency
from skeletons.gui.game_control import IHangarLoadingController, IBootcampController
from skeletons.gui.shared.utils import IHangarSpace

class HangarLoadingController(IHangarLoadingController):
    __bootcamp = dependency.descriptor(IBootcampController)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(HangarLoadingController, self).__init__()
        self.onHangarLoadedAfterLogin = Event.Event()
        self.__isConnectedAsAccount = False
        self.__wasInBootcamp = False

    def fini(self):
        self.__isConnectedAsAccount = False
        self.__wasInBootcamp = False
        self.__hangarSpace.onSpaceCreate -= self.__hangarLoadedAfterLoginNotify

    def onAvatarBecomePlayer(self):
        if not self.__bootcamp.isInBootcamp():
            if self.__wasInBootcamp:
                self.__isConnectedAsAccount = True
                self.__wasInBootcamp = False
            else:
                self.__isConnectedAsAccount = False
        else:
            self.__wasInBootcamp = True

    def getWasInBootcamp(self):
        return self.__wasInBootcamp

    def getConnectedAsACcount(self):
        return self.__isConnectedAsAccount

    def onConnected(self):
        self.__isConnectedAsAccount = True

    def onDisconnected(self):
        self.__isConnectedAsAccount = False
        self.__hangarSpace.onSpaceCreate -= self.__hangarLoadedAfterLoginNotify

    def onLobbyInited(self, event):
        if self.__isHangarLoadedAfterLogin():
            if self.__hangarSpace.spaceInited:
                self.__hangarLoadedAfterLoginNotify()
            else:
                self.__hangarSpace.onSpaceCreate += self.__hangarLoadedAfterLoginNotify

    def __hangarLoadedAfterLoginNotify(self):
        self.__hangarSpace.onSpaceCreate -= self.__hangarLoadedAfterLoginNotify
        self.onHangarLoadedAfterLogin()

    def __isHangarLoadedAfterLogin(self):
        return self.__isConnectedAsAccount and not self.__bootcamp.isInBootcamp() and not self.__bootcamp.isInBootcampAccount()
