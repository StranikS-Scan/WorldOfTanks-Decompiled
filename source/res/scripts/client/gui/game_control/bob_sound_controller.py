# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/bob_sound_controller.py
import WWISE
from constants import QUEUE_TYPE, PREBATTLE_TYPE
from frameworks.wulf import ViewStatus
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.impl.gen import R
from gui.marathon.bob_event import BobEvent
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IBobSoundController
from skeletons.gui.impl import IGuiLoader
_BOB_GAME_MODE_STATE = 'STATE_gamemode'
_BOB_GAME_MODE_STATE_ON = 'STATE_gamemode_battle_of_bloggers'
_BOB_GAME_MODE_STATE_OFF = 'STATE_gamemode_default'
_BOB_GAME_MODE_EVENT_ENTER = 'gui_bb_bloggers_Entrance'
_BOB_GAME_MODE_EVENT_EXIT = 'gui_bb_bloggers_Exit'
BOB_TEAM_REWARD_OPEN = 'gui_bb_bloggers_team_award'
BOB_HANGAR_SKILL_UP = 'gui_bb_bloggers_hangar_skills_up'

class BobSoundController(IBobSoundController, IGlobalListener):
    __gui = dependency.descriptor(IGuiLoader)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self):
        super(BobSoundController, self).init()
        self.__isBobPrb = False
        self.__isBobPageVisible = False
        self.__isBobGameMode = False
        self.__isInPreview = False
        self.__isInHangar = False

    def onLobbyInited(self, event):
        self.__startListening()
        self.__updatePrb()
        app = self.__appLoader.getApp()
        if app is not None:
            self.__isInHangar = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY_HANGAR)) is not None
        return

    def onAvatarBecomePlayer(self):
        self.__stopListening()

    def onDisconnected(self):
        self.__stopListening()

    def onPrbEntitySwitched(self):
        self.__updatePrb()

    def onStylePreviewOpen(self):
        self.__isInPreview = True
        self.__playSound()

    def onStylePreviewClose(self):
        self.__isInPreview = False
        self.__playSound()

    def __startListening(self):
        self.startGlobalListening()
        g_eventBus.addListener(events.MissionsEvent.ON_TAB_CHANGED, self.__onMissionsTabUpdated, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.MissionsEvent.ON_DEACTIVATE, self.__onMissionsTabUpdated, EVENT_BUS_SCOPE.LOBBY)
        self.__gui.windowsManager.onViewStatusChanged += self.__onViewStatusChanged

    def __stopListening(self):
        self.stopGlobalListening()
        g_eventBus.removeListener(events.MissionsEvent.ON_TAB_CHANGED, self.__onMissionsTabUpdated, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.MissionsEvent.ON_DEACTIVATE, self.__onMissionsTabUpdated, EVENT_BUS_SCOPE.LOBBY)
        self.__gui.windowsManager.onViewStatusChanged -= self.__onViewStatusChanged
        self.__isBobPrb = False

    def __onViewStatusChanged(self, uniqueID, newStatus):
        view = self.__gui.windowsManager.getView(uniqueID)
        if view is not None and view.layoutID == R.views.lobby.bob.BobWidgetView():
            if newStatus in (ViewStatus.DESTROYING, ViewStatus.DESTROYED):
                isInHangar = False
            else:
                isInHangar = True
            if self.__isInHangar != isInHangar:
                self.__isInHangar = isInHangar
                self.__playSound()
        return

    def __onMissionsTabUpdated(self, event):
        isBobPageVisible = event.ctx and event.ctx.get('alias') == QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_PY_ALIAS and event.ctx.get('marathonPrefix') == BobEvent.BOB_EVENT_PREFIX
        if isBobPageVisible != self.__isBobPageVisible:
            self.__isBobPageVisible = isBobPageVisible
            self.__playSound()

    def __updatePrb(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is None:
            return
        else:
            state = dispatcher.getFunctionalState()
            isBob = state.isInPreQueue(queueType=QUEUE_TYPE.BOB) or state.isInUnit(PREBATTLE_TYPE.BOB)
            if isBob != self.__isBobPrb:
                self.__isBobPrb = isBob
                self.__playSound()
            return

    def __playSound(self):
        isBob = self.__isBobPrb and self.__isInHangar or self.__isBobPageVisible or self.__isInPreview
        if isBob != self.__isBobGameMode:
            WWISE.WW_setState(_BOB_GAME_MODE_STATE, _BOB_GAME_MODE_STATE_ON if isBob else _BOB_GAME_MODE_STATE_OFF)
            WWISE.WW_eventGlobal(_BOB_GAME_MODE_EVENT_ENTER if isBob else _BOB_GAME_MODE_EVENT_EXIT)
            self.__isBobGameMode = isBob
