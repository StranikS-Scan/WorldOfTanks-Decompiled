# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/Scaleform/daapi/view/battle/start_countdown_sound_player.py
from constants import VEHICLE_SELECTION_BLOCK_DELAY
from gui.Scaleform.daapi.view.battle.shared.start_countdown_sound_player import StartCountdownSoundPlayer
from gui.battle_control.battle_constants import COUNTDOWN_STATE

class Comp7StartTimerSoundPlayer(StartCountdownSoundPlayer):

    def setCountdown(self, state, timeLeft):
        correctedTimeLeft = timeLeft - VEHICLE_SELECTION_BLOCK_DELAY if timeLeft is not None else timeLeft
        if correctedTimeLeft < 0:
            state = COUNTDOWN_STATE.STOP
        super(Comp7StartTimerSoundPlayer, self).setCountdown(state, correctedTimeLeft)
        return
