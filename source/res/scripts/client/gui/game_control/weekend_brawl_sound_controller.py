# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/weekend_brawl_sound_controller.py
import WWISE
from constants import QUEUE_TYPE, PREBATTLE_TYPE
from skeletons.gui.game_control import IWeekendBrawlSoundController
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.dispatcher import g_prbLoader
_BRAWL_GAME_MODE_STATE = 'STATE_gamemode'
_BRAWL_GAME_MODE_STATE_ON = 'STATE_gamemode_weekend_brawl'
_BRAWL_GAME_MODE_STATE_OFF = 'STATE_gamemode_default'
_BRAWL_GAME_MODE_EVENT_ENTER = 'gui_weekend_brawl_Entrance'
_BRAWL_GAME_MODE_EVENT_EXIT = 'gui_weekend_brawl_Exit'

class WeekendBrawlSoundController(IWeekendBrawlSoundController, IGlobalListener):

    def __init__(self):
        super(WeekendBrawlSoundController, self).init()
        self.__isWeekendBrawl = False

    def onLobbyInited(self, event):
        self.__startListening()
        self.__updatePrb()

    def onAvatarBecomePlayer(self):
        self.__stopListening()

    def onDisconnected(self):
        self.__stopListening()

    def onPrbEntitySwitched(self):
        self.__updatePrb()

    def __startListening(self):
        self.startGlobalListening()

    def __stopListening(self):
        self.stopGlobalListening()
        self.__isWeekendBrawl = False

    def __updatePrb(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is None:
            return
        else:
            state = dispatcher.getFunctionalState()
            isWeekendBrawl = state.isInPreQueue(queueType=QUEUE_TYPE.WEEKEND_BRAWL) or state.isInUnit(PREBATTLE_TYPE.WEEKEND_BRAWL)
            if isWeekendBrawl != self.__isWeekendBrawl:
                self.__playSound(isWeekendBrawl)
                self.__isWeekendBrawl = isWeekendBrawl
            return

    def __playSound(self, isWeekendBrawl):
        WWISE.WW_setState(_BRAWL_GAME_MODE_STATE, _BRAWL_GAME_MODE_STATE_ON if isWeekendBrawl else _BRAWL_GAME_MODE_STATE_OFF)
        WWISE.WW_eventGlobal(_BRAWL_GAME_MODE_EVENT_ENTER if isWeekendBrawl else _BRAWL_GAME_MODE_EVENT_EXIT)
