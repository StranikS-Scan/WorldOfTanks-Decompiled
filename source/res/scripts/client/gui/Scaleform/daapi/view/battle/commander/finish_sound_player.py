# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/commander/finish_sound_player.py
from PlayerEvents import g_playerEvents
from gui.Scaleform.daapi.view.battle.shared.finish_sound_player import FinishSoundPlayer
from gui.battle_control.view_components import IViewComponentsCtrlListener
from gui.battle_control import avatar_getter
from gui.sounds.r4_sound_constants import R4_SOUND
from constants import FINISH_REASON
_WIN_RESULT_TO_NOTIFICATION = {0: R4_SOUND.R4_DEFEAT,
 0.5: R4_SOUND.R4_DRAW,
 1.0: R4_SOUND.R4_VICTORY}

class R4FinishSoundPlayer(FinishSoundPlayer, IViewComponentsCtrlListener):

    def __init__(self):
        super(R4FinishSoundPlayer, self).__init__()
        self.__isPlaying = False
        g_playerEvents.onRoundFinished += self._playSoundNotification

    def detachedFromCtrl(self, ctrlID):
        g_playerEvents.onRoundFinished -= self._playSoundNotification

    def setTeamBaseCaptured(self, clientID, playerTeam):
        pass

    def addCapturedTeamBase(self, clientID, playerTeam, timeLeft, invadersCnt):
        pass

    def _playSoundNotification(self, winnerTeam, reason):
        if self.__isPlaying:
            return
        self.__isPlaying = True
        playerTeam = avatar_getter.getPlayerTeam()
        winResult = 0.5 if winnerTeam == 0 else float(winnerTeam == playerTeam)
        if reason == FINISH_REASON.EXTERMINATION and winnerTeam != playerTeam:
            return
        notification = _WIN_RESULT_TO_NOTIFICATION[winResult]
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'playOnRandomVehicle'):
            soundNotifications.playOnRandomVehicle(notification)
