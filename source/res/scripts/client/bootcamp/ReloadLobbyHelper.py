# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/ReloadLobbyHelper.py
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.shared import EVENT_BUS_SCOPE
from gui.app_loader import g_appLoader
from gui.shared.events import AppLifeCycleEvent
from BootcampTransition import BootcampTransition
from helpers import aop

class _PointcutGameSessionControllerFix(aop.Pointcut):
    """ Sending onAvatarBecomePlayer from ReloadLobbyHelper.reload interferes with GameSessionController logic.
        This pointcut fixes it by preventing an extra notification on switching to/from bootcamp
        (as if on exiting battle).
    
        NOTE: this is not in bootcamp/aop/common.py,
              because ReloadLobbyHelper is used slightly outside the bootcamp scope.
    """

    def __init__(self):
        super(_PointcutGameSessionControllerFix, self).__init__('gui.game_control.GameSessionController', 'GameSessionController', '_stop', aspects=(_AspectGameSessionControllerFix,))


class _AspectGameSessionControllerFix(aop.Aspect):

    def atCall(self, cd):
        return cd.changeArgs((0, 'doNotifyInStart', False))


class ReloadLobbyHelper(EventSystemEntity):

    def __init__(self, finishCallback=None):
        super(ReloadLobbyHelper, self).__init__()
        self.__callback = finishCallback

    def reload(self):
        from gui.prb_control.dispatcher import g_prbLoader
        from gui.shared.personality import ServicesLocator
        pc = _PointcutGameSessionControllerFix()
        self.addListener(AppLifeCycleEvent.INITIALIZED, self.__appInitialized, EVENT_BUS_SCOPE.GLOBAL)
        g_prbLoader.onAccountBecomeNonPlayer()
        ServicesLocator.gameState.onAvatarBecomePlayer()
        g_appLoader.switchAccountEntity()
        g_prbLoader.onAccountShowGUI({})
        BootcampTransition.start()
        pc.clear()

    def __onViewLoaded(self, view, loadParams):
        view.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        BootcampTransition.stop()
        if self.__callback is not None:
            self.__callback()
        self.destroy()
        return

    def __appInitialized(self, event):
        self.app = g_appLoader.getApp(event.ns)
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded
        self.removeListener(AppLifeCycleEvent.INITIALIZED, self.__appInitialized, EVENT_BUS_SCOPE.GLOBAL)
