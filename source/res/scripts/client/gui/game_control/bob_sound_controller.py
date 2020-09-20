# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/bob_sound_controller.py
import WWISE
from constants import QUEUE_TYPE, PREBATTLE_TYPE
from skeletons.gui.game_control import IBobSoundController
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.dispatcher import g_prbLoader
_BOB_GAME_MODE_STATE = 'STATE_gamemode'
_BOB_GAME_MODE_STATE_ON = 'STATE_gamemode_weekend_brawl'
_BOB_GAME_MODE_STATE_OFF = 'STATE_gamemode_default'
_BOB_GAME_MODE_EVENT_ENTER = 'gui_weekend_brawl_Entrance'
_BOB_GAME_MODE_EVENT_EXIT = 'gui_weekend_brawl_Exit'

class BobSoundController(IBobSoundController, IGlobalListener):

    def __init__(self):
        super(BobSoundController, self).init()
        self.__isBob = False

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
        self.__isBob = False

    def __updatePrb(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is None:
            return
        else:
            state = dispatcher.getFunctionalState()
            isBob = state.isInPreQueue(queueType=QUEUE_TYPE.BOB) or state.isInUnit(PREBATTLE_TYPE.BOB)
            if isBob != self.__isBob:
                self.__playSound(isBob)
                self.__isBob = isBob
            return

    def __playSound(self, isBob):
        WWISE.WW_setState(_BOB_GAME_MODE_STATE, _BOB_GAME_MODE_STATE_ON if isBob else _BOB_GAME_MODE_STATE_OFF)
        WWISE.WW_eventGlobal(_BOB_GAME_MODE_EVENT_ENTER if isBob else _BOB_GAME_MODE_EVENT_EXIT)
