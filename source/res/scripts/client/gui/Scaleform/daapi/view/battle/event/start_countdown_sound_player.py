# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/start_countdown_sound_player.py
import logging
import WWISE
from helpers import dependency
import BattleReplay
from gui.battle_control.battle_constants import COUNTDOWN_STATE
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.battle_control.view_components import IViewComponentsCtrlListener
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)
_RTPC = 'RTPC_ext_battle_countdown_timer'

class StartCountdownSoundPlayer(IAbstractPeriodView, IViewComponentsCtrlListener):

    def __init__(self):
        super(StartCountdownSoundPlayer, self).__init__()
        self.__soundID = dependency.instance(IBattleSessionProvider).arenaVisitor.type.getCountdownTimerSound()
        if not self.__soundID:
            _logger.warning('Countdown sound for this game mode is not defined! ' + 'Please define one ' + 'otherwise remove this player from the list in the corresponded page.py')

    def setCountdown(self, state, timeLeft):
        if state == COUNTDOWN_STATE.START:
            self.__updateSound(timeLeft)

    def __updateSound(self, timeLeft):
        if self.__checkNotReplay():
            self.__playSound(timeLeft)

    def __checkNotReplay(self):
        replay = BattleReplay.g_replayCtrl
        return not replay.playbackSpeed == 0 if replay.isPlaying else True

    def __playSound(self, timeLeft):
        if self.__soundID:
            WWISE.WW_setRTCPGlobal(_RTPC, timeLeft)
            WWISE.WW_eventGlobal(self.__soundID)
