# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/bob_sound_controller.py
from skeletons.gui.game_control import IBobSoundController
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.dispatcher import g_prbLoader
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.marathon.bob_event import BobEvent
from gui.shared import g_eventBus, events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from constants import QUEUE_TYPE, PREBATTLE_TYPE
import WWISE
_BOB_GAME_MODE_STATE = 'STATE_gamemode'
_BOB_GAME_MODE_STATE_ON = 'STATE_gamemode_battle_of_bloggers'
_BOB_GAME_MODE_STATE_OFF = 'STATE_gamemode_default'
_BOB_GAME_MODE_EVENT_ENTER = 'gui_bb_bloggers_Entrance'
_BOB_GAME_MODE_EVENT_EXIT = 'gui_bb_bloggers_Exit'
_BOB_PAGE_STATE = 'STATE_gamemode_progress_page'
_BOB_PAGE_STATE_ON = 'STATE_gamemode_progress_page_on'
_BOB_PAGE_STATE_OFF = 'STATE_gamemode_progress_page_off'
_BOB_PAGE_EVENT_ENTER = 'gui_bb_bloggers_progress_page_ambient_Entrance'
_BOB_PAGE_EVENT_EXIT = 'gui_bb_bloggers_progress_page_ambient_Exit'
BOB_TEAM_REWARD_OPEN = 'gui_bb_bloggers_team_award'

class BobSoundController(IBobSoundController, IGlobalListener):

    def __init__(self):
        super(BobSoundController, self).init()
        self.__isBobPrb = False
        self.__isBobPageVisible = False
        self.__isBobGameMode = False
        self.__isInPreview = False

    def setState(self, stateName, stateValue):
        WWISE.WW_setState(stateName, stateValue)

    def playSound(self, eventName):
        WWISE.WW_eventGlobal(eventName)

    def onLobbyInited(self, event):
        self.setState(_BOB_PAGE_STATE, _BOB_PAGE_STATE_ON if self.__isBobPageVisible else _BOB_PAGE_STATE_OFF)
        self.setState(_BOB_GAME_MODE_STATE, _BOB_GAME_MODE_STATE_ON if self.__isBobGameMode else _BOB_GAME_MODE_STATE_OFF)
        if self.__isBobGameMode:
            self.playSound(_BOB_GAME_MODE_EVENT_ENTER)
        self.__startListening()
        self.__updatePrb()

    def onAvatarBecomePlayer(self):
        self.__stopListening()

    def onDisconnected(self):
        self.__stopListening()

    def onPrbEntitySwitched(self):
        self.__updatePrb()

    def onStylePreviewOpen(self):
        self.__isInPreview = True
        self.__updateGameMode()

    def onStylePreviewClose(self):
        self.__isInPreview = False
        self.__updateGameMode()

    def __startListening(self):
        self.startGlobalListening()
        g_eventBus.addListener(events.MissionsEvent.ON_TAB_CHANGED, self.__onMissionsTabUpdated, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.MissionsEvent.ON_DEACTIVATE, self.__onMissionsTabUpdated, EVENT_BUS_SCOPE.LOBBY)

    def __stopListening(self):
        self.stopGlobalListening()
        g_eventBus.removeListener(events.MissionsEvent.ON_TAB_CHANGED, self.__onMissionsTabUpdated, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.MissionsEvent.ON_DEACTIVATE, self.__onMissionsTabUpdated, EVENT_BUS_SCOPE.LOBBY)

    def __onMissionsTabUpdated(self, event):
        isBobPageVisible = event.ctx and event.ctx.get('alias') == QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_PY_ALIAS and event.ctx.get('marathonPrefix') == BobEvent.BOB_EVENT_PREFIX
        if isBobPageVisible != self.__isBobPageVisible:
            self.setState(_BOB_PAGE_STATE, _BOB_PAGE_STATE_ON if isBobPageVisible else _BOB_PAGE_STATE_OFF)
            self.playSound(_BOB_PAGE_EVENT_ENTER if isBobPageVisible else _BOB_PAGE_EVENT_EXIT)
            self.__isBobPageVisible = isBobPageVisible
            self.__updateGameMode()

    def __updatePrb(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is None:
            return
        else:
            state = dispatcher.getFunctionalState()
            self.__isBobPrb = state.isInPreQueue(queueType=QUEUE_TYPE.BOB) or state.isInUnit(PREBATTLE_TYPE.BOB)
            self.__updateGameMode()
            return

    def __updateGameMode(self):
        isBobGameMode = self.__isBobPrb or self.__isBobPageVisible or self.__isInPreview
        if isBobGameMode != self.__isBobGameMode:
            self.setState(_BOB_GAME_MODE_STATE, _BOB_GAME_MODE_STATE_ON if isBobGameMode else _BOB_GAME_MODE_STATE_OFF)
            self.playSound(_BOB_GAME_MODE_EVENT_ENTER if isBobGameMode else _BOB_GAME_MODE_EVENT_EXIT)
            self.__isBobGameMode = isBobGameMode
