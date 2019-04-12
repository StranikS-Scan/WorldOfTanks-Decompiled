# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/states/StateInGarage.py
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from bootcamp.states import STATE
from bootcamp.states.AbstractState import AbstractState
from bootcamp.aop.in_garage import weave
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import g_eventBus
from gui.shared.events import AppLifeCycleEvent
from gui.app_loader.settings import APP_NAME_SPACE
from helpers import dependency, aop
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.lobby_context import ILobbyContext
from PlayerEvents import g_playerEvents
from skeletons.gui.shared.utils import IHangarSpace

class StateInGarage(AbstractState):
    lobbyContext = dependency.descriptor(ILobbyContext)
    hangarSpace = dependency.descriptor(IHangarSpace)
    appLoader = dependency.descriptor(IAppLoader)

    def __init__(self):
        super(StateInGarage, self).__init__(STATE.IN_GARAGE)
        self.__weaver = aop.Weaver()

    def _doActivate(self):
        LOG_DEBUG_DEV_BOOTCAMP('Activating StateInGarage')
        weave(self.__weaver, self)
        from bootcamp.Bootcamp import g_bootcamp
        g_bootcamp.setBootcampHangarSpace()
        app = self.appLoader.getApp(APP_NAME_SPACE.SF_LOBBY)
        if app is not None and app.initialized:
            self.__onSfAppInited()
        else:
            g_eventBus.addListener(AppLifeCycleEvent.INITIALIZED, self.__onSfAppInited, EVENT_BUS_SCOPE.GLOBAL)
        return

    def _doDeactivate(self):
        g_eventBus.removeListener(AppLifeCycleEvent.INITIALIZED, self.__onSfAppInited, EVENT_BUS_SCOPE.GLOBAL)
        self.__weaver.clear()
        g_currentVehicle.destroy()
        g_currentPreviewVehicle.destroy()
        self.hangarSpace.destroy()

    def __onSfAppInited(self, event=None):
        LOG_DEBUG_DEV_BOOTCAMP('StateInGarage.__onSfAppInited')
        g_eventBus.removeListener(AppLifeCycleEvent.INITIALIZED, self.__onSfAppInited, EVENT_BUS_SCOPE.GLOBAL)
        g_playerEvents.onAccountShowGUI(self.lobbyContext.getGuiCtx())
