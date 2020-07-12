# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/start_countdown_sound_player.py
import logging
from helpers import dependency
import BattleReplay
import SoundGroups
from gui.battle_control.battle_constants import COUNTDOWN_STATE
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.battle_control.view_components import IViewComponentsCtrlListener
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class _SoundWrapper(object):

    def __init__(self):
        super(_SoundWrapper, self).__init__()
        self.__sound = None
        return

    def play(self):
        sound = self.__getSound2D()
        if sound and not sound.isPlaying:
            sound.play()

    def stop(self):
        sound = self.__getSound2D()
        if sound and sound.isPlaying:
            sound.stop()

    def dispose(self):
        self.__sound = None
        return

    def __getSound2D(self):
        if not self.__sound:
            sessionProvider = dependency.instance(IBattleSessionProvider)
            sound2DID = sessionProvider.arenaVisitor.type.getCountdownTimerSound()
            if sound2DID:
                self.__sound = SoundGroups.g_instance.getSound2D(sound2DID)
            else:
                _logger.warning('Countdown sound for this game mode is not defined! ' + 'Please define one ' + 'otherwise remove this player from the list in the corresponded page.py')
                self.__sound = None
        return self.__sound


class StartCountdownSoundPlayer(IAbstractPeriodView, IViewComponentsCtrlListener):

    def __init__(self):
        super(StartCountdownSoundPlayer, self).__init__()
        self.__sound = _SoundWrapper()

    def setCountdown(self, state, timeLeft):
        if state == COUNTDOWN_STATE.START:
            self.__updateSound(timeLeft)

    def hideCountdown(self, state, speed):
        if state == COUNTDOWN_STATE.STOP:
            self.__stopSound()

    def detachedFromCtrl(self, ctrlID):
        self.__stopSound()
        self.__sound.dispose()
        self.__sound = None
        return

    def __updateSound(self, timeLeft):
        if timeLeft and self.__checkReplay():
            self.__playSound()
        else:
            self.__stopSound()

    def __checkReplay(self):
        replay = BattleReplay.g_replayCtrl
        return not replay.playbackSpeed == 0 if replay.isPlaying else True

    def __playSound(self):
        self.__sound.play()

    def __stopSound(self):
        self.__sound.stop()
