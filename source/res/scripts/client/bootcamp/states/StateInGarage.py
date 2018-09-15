# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/states/StateInGarage.py
from copy import deepcopy
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from bootcamp.BootCampEvents import g_bootcampEvents
from bootcamp.BootcampLobbyHintsConfig import g_bootcampHintsConfig
from bootcamp.BootcampSettings import getGarageDefaults
from bootcamp.states import STATE
from bootcamp.states.AbstractState import AbstractState
from bootcamp.aop.in_garage import weave
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events
from gui.shared import g_eventBus
from gui.shared.events import GUICommonEvent
from helpers import dependency, aop
from skeletons.gui.game_control import IBootcampController
from skeletons.gui.lobby_context import ILobbyContext
from PlayerEvents import g_playerEvents

class StateInGarage(AbstractState):
    lobbyContext = dependency.descriptor(ILobbyContext)
    bootcampCtrl = dependency.descriptor(IBootcampController)

    def __init__(self, lessonNum, account, checkpoint):
        super(StateInGarage, self).__init__(STATE.IN_GARAGE)
        self.__lessonId = lessonNum
        self.__account = account
        self.__checkpoint = checkpoint
        self.__weaver = aop.Weaver()

    def onLobbyLessonFinished(self):
        g_bootcampEvents.onBattleReady()

    def onLobbyInited(self, event):
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BOOTCAMP_LOBBY_HIGHLIGHTS, None, {'descriptors': g_bootcampHintsConfig.getItems()}), EVENT_BUS_SCOPE.LOBBY)
        return

    def handleKeyEvent(self, event):
        pass

    def _onBattleReady(self):
        pass

    def _doActivate(self):
        from bootcamp.Bootcamp import g_bootcamp
        from bootcamp.BootcampGarage import g_bootcampGarage
        weave(self.__weaver, self)
        g_bootcampGarage.init(self.__lessonId, self.__account)
        g_bootcampGarage.setCheckpoint(self.__checkpoint)
        self.bootcampCtrl.setLobbySettings(deepcopy(getGarageDefaults()['panels']))
        g_eventBus.addListener(GUICommonEvent.LOBBY_VIEW_LOADED, self.onLobbyInited)
        g_bootcampEvents.onBattleReady += self._onBattleReady
        g_bootcamp.setBootcampHangarSpace()
        g_playerEvents.onAccountShowGUI(self.lobbyContext.getGuiCtx())
        g_bootcampGarage.selectLessonVehicle()
        LOG_DEBUG_DEV_BOOTCAMP('Created tutorialGarage', self.__lessonId)

    def _doDeactivate(self):
        from bootcamp.BootcampGarage import g_bootcampGarage
        g_eventBus.removeListener(GUICommonEvent.LOBBY_VIEW_LOADED, self.onLobbyInited)
        g_bootcampEvents.onBattleReady -= self._onBattleReady
        g_bootcampGarage.stopLobbyAssistance()
        g_bootcampGarage.clear()
        self.__weaver.clear()
        from gui.shared.utils.HangarSpace import g_hangarSpace
        g_currentVehicle.destroy()
        g_currentPreviewVehicle.destroy()
        g_hangarSpace.destroy()
