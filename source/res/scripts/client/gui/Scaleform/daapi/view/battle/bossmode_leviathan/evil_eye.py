# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/bossmode_leviathan/evil_eye.py
import BigWorld
import SoundGroups
from gui.battle_control import avatar_getter
from gui.Scaleform.daapi.view.meta.EvilEyeMeta import EvilEyeMeta
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.account_helpers.settings_core import ISettingsCore
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from account_helpers.settings_core.settings_constants import SOUND
from constants import HALLOWEEN_BOSS_RAGE_HEALTH_RATIO, LEVIATHAN_HALFWAY_PROGRESS, LEVIATHAN_PROGRESS_CLOSE
from helpers import dependency, i18n
import BattleReplay
from ReplayEvents import g_replayEvents
_UPDATE_INTERVAL = 0.2
_LEVIATHAN_RAGE_SOUND = 'ev_halloween_ui_leviathan_health'
_LEVIATHAN_EVIL_EYE_SOUND = 'ev_halloween_ui_targeting'

class EvilEye(EvilEyeMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(EvilEye, self).__init__()
        self.__detectionSoundEventName = None
        self.__detectionSoundEvent = None
        self.__callbackID = None
        self.__timerCallbackID = None
        self.__mainEyeShowing = False
        self.__secondaryEyeShowing = False
        self.__secondaryEyeCount = 0
        self.__rageNotified = False
        self.__halfwayNotified = False
        self.__closeNotified = False
        self.__captureNotified = False
        self.__leviathanMaxHealth = 1
        return

    def __del__(self):
        self._stop()

    def _stop(self):
        pass

    def _dispose(self):
        self.__cancelCallback()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        BigWorld.player().onLeviathanProgressUpdate -= self.__avatar_onLeviathanHealthAndProgressUpdated
        BigWorld.player().arena.onTeamBasePointsUpdate -= self.__arena_onTeamBasePointsUpdated
        self.__stopUpdateTimer()
        super(EvilEye, self)._dispose()
        g_replayEvents.onTimeWarpFinish -= self.__onReplayRewindComplete
        return

    def _populate(self):
        super(EvilEye, self)._populate()
        BigWorld.player().onLeviathanProgressUpdate += self.__avatar_onLeviathanHealthAndProgressUpdated
        BigWorld.player().arena.onTeamBasePointsUpdate += self.__arena_onTeamBasePointsUpdated
        self.__setDetectionSoundEvent(_LEVIATHAN_EVIL_EYE_SOUND)
        self.__startUpdateTimer()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        self.__getLeviathanMaxHealth()
        vo = {'mainEyeVO': i18n.makeString(INGAME_GUI.HALLOWEEN_EYE_MAINLABEL),
         'secondaryEyeVO': i18n.makeString(INGAME_GUI.HALLOWEEN_EYE_SECONDARYLABEL)}
        self.as_setEyeLabelsS(vo)
        g_replayEvents.onTimeWarpFinish += self.__onReplayRewindComplete
        return

    def __getLeviathanMaxHealth(self):
        arenaDP = self.sessionProvider.getArenaDP()
        for vInfo in arenaDP.getVehiclesInfoIterator():
            vTypeInfoVO = vInfo.vehicleType
            if vTypeInfoVO.isLeviathan:
                self.__leviathanMaxHealth = vTypeInfoVO.maxHealth

    def __arena_showMainEye(self):
        self.as_showMainS()
        self.__setSoundToPlay()
        self.__mainEyeShowing = True

    def __arena_showSecondaryEye(self, val):
        self.as_showSecondaryS()
        self.__setSoundToPlay()
        self.__secondaryEyeShowing = True
        self.__secondaryEyeCount = val

    def __arena_updateSecondaryCount(self, val):
        self.__secondaryEyeCount = val

    def __arena_showNotification(self, msg):
        self.as_showNotificationS(msg)

    def __hideMainEye(self):
        self.as_hideMainS()
        self.__mainEyeShowing = False

    def __hideSecondaryEye(self):
        self.as_hideSecondaryS()
        self.__secondaryEyeShowing = False

    def __startUpdateTimer(self):
        self.__stopUpdateTimer()
        BigWorld.callback(_UPDATE_INTERVAL, self.__updateTimerCallback)

    def __stopUpdateTimer(self):
        if self.__timerCallbackID is not None:
            BigWorld.cancelCallback(self.__timerCallbackID)
        return

    def __updateTimerCallback(self):
        if avatar_getter.getArena():
            self.__arena_onEvilEyeStatusUpdated()
            self.__startUpdateTimer()

    def __arena_onEvilEyeStatusUpdated(self):
        evilEyePrimaryStatus = avatar_getter.getEvilEyePrimaryStatus()
        evilEyeSecondaryStatus = avatar_getter.getEvilEyeSecondaryStatus()
        if evilEyePrimaryStatus and not self.__mainEyeShowing:
            self.__arena_showMainEye()
        elif not evilEyePrimaryStatus and self.__mainEyeShowing:
            self.__hideMainEye()
        if evilEyeSecondaryStatus > 0:
            if not self.__secondaryEyeShowing:
                self.__arena_showSecondaryEye(evilEyeSecondaryStatus)
            elif evilEyeSecondaryStatus != self.__secondaryEyeCount:
                self.__arena_updateSecondaryCount(evilEyeSecondaryStatus)
        elif evilEyeSecondaryStatus <= 0 and self.__secondaryEyeShowing:
            self.__hideSecondaryEye()

    def __avatar_onLeviathanHealthAndProgressUpdated(self, leviathanHealth, leviathanProgressPercent):
        healthRatio = float(leviathanHealth) / float(self.__leviathanMaxHealth)
        if BattleReplay.isPlaying():
            if leviathanProgressPercent < LEVIATHAN_PROGRESS_CLOSE:
                self.__closeNotified = False
            if leviathanProgressPercent < LEVIATHAN_HALFWAY_PROGRESS:
                self.__halfwayNotified = False
            if healthRatio < HALLOWEEN_BOSS_RAGE_HEALTH_RATIO:
                self.__rageNotified = False
        if leviathanProgressPercent > LEVIATHAN_HALFWAY_PROGRESS and not self.__halfwayNotified:
            self.__halfwayNotified = True
            self.__arena_showNotification(INGAME_GUI.HALLOWEEN_PVE_GOAL_HINT_HALFWAYLEVIATHANMSG)
        elif leviathanProgressPercent > LEVIATHAN_PROGRESS_CLOSE and not self.__closeNotified:
            self.__closeNotified = True
            self.__arena_showNotification(INGAME_GUI.HALLOWEEN_PVE_GOAL_HINT_LEVIATHANCLOSEMSG)
        if healthRatio < HALLOWEEN_BOSS_RAGE_HEALTH_RATIO and not self.__rageNotified:
            SoundGroups.g_instance.playSound2D(_LEVIATHAN_RAGE_SOUND)
            self.__rageNotified = True
            self.__arena_showNotification(INGAME_GUI.HALLOWEEN_PVE_GOAL_HINT_ENGRAGEDLEVIATHANMSG)

    def __cancelCallback(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.DESTROYED:
            self.as_hideAllNowS()

    def __setSoundToPlay(self):
        if self.__detectionSoundEvent is not None:
            if not self.__detectionSoundEvent.isPlaying:
                self.__detectionSoundEvent.play()
        return

    def __setDetectionSoundEvent(self, soundEventName):
        if self.__detectionSoundEventName != soundEventName:
            self.__detectionSoundEventName = soundEventName
            self.__detectionSoundEvent = SoundGroups.g_instance.getSound2D(self.__detectionSoundEventName)

    def __arena_onTeamBasePointsUpdated(self, team, baseID, points, timeLeft, invadersCnt, capturingStopped):
        if points > 0 and not self.__captureNotified:
            self.__arena_showNotification(INGAME_GUI.HALLOWEEN_PVE_GOAL_HINT_ENTERSCAPTUREMSG)
            self.__captureNotified = True

    def __onReplayRewindComplete(self):
        self.__hideMainEye()
        self.__hideSecondaryEye()
        self.__arena_onEvilEyeStatusUpdated()
