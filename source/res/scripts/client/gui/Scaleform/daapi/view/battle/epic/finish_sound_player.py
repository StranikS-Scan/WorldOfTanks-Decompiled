# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/finish_sound_player.py
from functools import partial
import BigWorld
from PlayerEvents import g_playerEvents
from gui.Scaleform.daapi.view.battle.shared.finish_sound_player import FinishSoundPlayer
from gui.battle_control.view_components import IViewComponentsCtrlListener
from constants import FINISH_REASON
from gui.battle_control import avatar_getter
from gui.sounds.epic_sound_constants import EPIC_SOUND
_EPIC_SOUND_EVENTS = {FINISH_REASON.DESTROYED_OBJECTS: 'end_battle_last_kill',
 FINISH_REASON.EXTERMINATION: 'end_battle_last_kill'}
_EPIC_SOUND_NOTIFICATIONS = {FINISH_REASON.EXTERMINATION: EPIC_SOUND.BF_EB_ALL_ENEMIES_DESTROYED,
 FINISH_REASON.TIMEOUT: EPIC_SOUND.BF_EB_TIME_OUT}
_EPIC_SOUND_NOTIFICATION_DELAY = {FINISH_REASON.EXTERMINATION: 3,
 FINISH_REASON.DESTROYED_OBJECTS: 3}

class EpicFinishSoundPlayer(FinishSoundPlayer, IViewComponentsCtrlListener):

    def __init__(self):
        super(EpicFinishSoundPlayer, self).__init__()
        self.__soundID = None
        self.__notificationDelayCB = None
        g_playerEvents.onRoundFinished += self.__onEpicRoundFinished
        return

    def detachedFromCtrl(self, ctrlID):
        g_playerEvents.onRoundFinished -= self.__onEpicRoundFinished

    def setTeamBaseCaptured(self, clientID, playerTeam):
        pass

    def addCapturedTeamBase(self, clientID, playerTeam, timeLeft, invadersCnt):
        pass

    def _playSoundNotification(self, winnerTeam, reason):
        playerTeam = avatar_getter.getPlayerTeam()
        notification = _EPIC_SOUND_NOTIFICATIONS.get(reason, None)
        if notification is None:
            return
        else:
            victory = True if winnerTeam == playerTeam else False
            notification = notification.get(victory, None)
            soundNotifications = avatar_getter.getSoundNotifications()
            if soundNotifications and hasattr(soundNotifications, 'play'):
                soundNotifications.play(notification)
            return

    def __onEpicRoundFinished(self, winnerTeam, reason):
        delay = _EPIC_SOUND_NOTIFICATION_DELAY.get(reason, 0)
        self.__notificationDelayCB = BigWorld.callback(delay, partial(self._playSoundNotification, winnerTeam, reason))
        self.__soundID = _EPIC_SOUND_EVENTS.get(reason, None)
        if self.__soundID is not None:
            self._playSound(self.__soundID)
        return
