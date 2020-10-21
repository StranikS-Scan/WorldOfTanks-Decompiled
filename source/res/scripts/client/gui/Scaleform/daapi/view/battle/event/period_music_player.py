# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/period_music_player.py
import WWISE
import SoundGroups
from constants import ARENA_PERIOD
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.battle_control.view_components import IViewComponentsCtrlListener
from gui.battle_control.avatar_getter import getSoundNotifications
from gui.Scaleform.daapi.view.battle.event.game_event_getter import GameEventGetterMixin
from shared_utils import CONST_CONTAINER

class PeriodMusicHalloweenPlayer(IAbstractPeriodView):

    def __init__(self):
        super(PeriodMusicHalloweenPlayer, self).__init__()
        self.__isStartPlayed = False

    def setPeriod(self, period):
        if (period == ARENA_PERIOD.PREBATTLE or period == ARENA_PERIOD.BATTLE) and not self.__isStartPlayed:
            SoundGroups.g_instance.playSound2D('ev_halloween_2019_gameplay_start')
            self.__isStartPlayed = True
        elif period == ARENA_PERIOD.AFTERBATTLE:
            SoundGroups.g_instance.playSound2D('ev_halloween_2019_gameplay_stop')


class _ConstWorldSound(CONST_CONTAINER):
    RTPC_NAME = 'RTPC_ext_hw19_world'
    STATE_NAME = 'STATE_ev_halloween_2019_world'
    BATTLE_STATE = 'STATE_ev_halloween_2019_world_m{}'
    NOTIFICATION_WORLD_SWITCH = 'hw19_vo_notification_world_{}'
    NOTIFICATION_WORLD_WIN = 'hw19_vo_notification_world_after_win'
    WIN_SOUND_ENV_NUM = 5


class EnvironmentMusicHalloweenPlayer(IAbstractPeriodView, IViewComponentsCtrlListener, GameEventGetterMixin):

    def __init__(self):
        super(EnvironmentMusicHalloweenPlayer, self).__init__()
        self.__initialized = False
        self.__currentEventEnvID = None
        return

    def detachedFromCtrl(self, ctrlID):
        self.__removeListeners()

    def setPeriod(self, period):
        if period == ARENA_PERIOD.BATTLE and not self.__initialized:
            self.__initialized = True
            self.__environmentIDWasUpdated(self.__getEventEnvID())
            self.__addListeners()

    def __addListeners(self):
        if self.environmentData is not None:
            self.environmentData.onEnvironmentEventIDUpdate += self.__environmentIDWasUpdated
        return

    def __removeListeners(self):
        if self.environmentData is not None:
            self.environmentData.onEnvironmentEventIDUpdate -= self.__environmentIDWasUpdated
        return

    def __getEventEnvID(self):
        return self.environmentData.getCurrentEnvironmentID() if self.environmentData is not None else None

    def __environmentIDWasUpdated(self, eventEnvID):
        if self.__currentEventEnvID != eventEnvID:
            self.__currentEventEnvID = eventEnvID
            self.__updateSoundEnvironment(eventEnvID + 1)

    def __updateSoundEnvironment(self, soundEnvID):
        if soundEnvID == _ConstWorldSound.WIN_SOUND_ENV_NUM:
            notification = _ConstWorldSound.NOTIFICATION_WORLD_WIN
        else:
            rtcpArenaWorldParam = WWISE.WW_getRTPCValue(_ConstWorldSound.RTPC_NAME)
            rtcpArenaWorldParam.set(soundEnvID)
            WWISE.WW_setState(_ConstWorldSound.STATE_NAME, _ConstWorldSound.BATTLE_STATE.format(soundEnvID))
            notification = _ConstWorldSound.NOTIFICATION_WORLD_SWITCH.format(soundEnvID)
        soundNotifications = getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'play'):
            soundNotifications.play(notification)
