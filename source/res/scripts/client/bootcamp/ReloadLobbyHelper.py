# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/ReloadLobbyHelper.py
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.app_loader import g_appLoader
from BootcampTransition import BootcampTransition
from helpers import aop

class _PointcutGameSessionControllerFix(aop.Pointcut):

    def __init__(self):
        super(_PointcutGameSessionControllerFix, self).__init__('gui.game_control.GameSessionController', 'GameSessionController', '_stop', aspects=(_AspectGameSessionControllerFix,))


class _AspectGameSessionControllerFix(aop.Aspect):

    def atCall(self, cd):
        return cd.changeArgs((0, 'doNotifyInStart', False))


class ReloadLobbyHelper(object):

    def __init__(self):
        super(ReloadLobbyHelper, self).__init__()
        self.__isReloading = False

    def cancel(self):
        if self.__isReloading:
            g_eventBus.removeListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__onLobbyViewLoaded, EVENT_BUS_SCOPE.DEFAULT)
            BootcampTransition.stop()
        self.__isReloading = False

    def reload(self):
        self.__isReloading = True
        g_eventBus.addListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__onLobbyViewLoaded, EVENT_BUS_SCOPE.DEFAULT)
        from gui.prb_control.dispatcher import g_prbLoader
        from gui.shared.personality import ServicesLocator
        pc = _PointcutGameSessionControllerFix()
        BootcampTransition.start()
        g_prbLoader.onAccountBecomeNonPlayer()
        ServicesLocator.gameState.onAvatarBecomePlayer()
        g_appLoader.switchAccountEntity()
        g_prbLoader.onAccountShowGUI({})
        pc.clear()

    def __onLobbyViewLoaded(self, _):
        self.cancel()
