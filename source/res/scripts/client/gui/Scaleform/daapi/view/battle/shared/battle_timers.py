# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/battle_timers.py
import SoundGroups
import BigWorld
import CommandMapping
from constants import ARENA_GUI_TYPE, ARENA_PERIOD
from gui.Scaleform.daapi.view.meta.EventBattleTimerMeta import EventBattleTimerMeta
from gui.Scaleform.daapi.view.meta.PrebattleTimerMeta import PrebattleTimerMeta
from gui.Scaleform.genConsts.PREBATTLE_TIMER import PREBATTLE_TIMER
from gui.impl import backport
from gui.impl.gen import R
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import COUNTDOWN_STATE, BATTLE_CTRL_ID
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import WtGameEvent
from gui.wt_event.wt_event_helpers import getHunterDescr
from helpers import dependency, isPlayerAvatar
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.shared.utils.key_mapping import getReadableKey
from PlayerEvents import g_playerEvents

class _WWISE_EVENTS(object):
    BATTLE_ENDING_SOON = 'time_buzzer_02'
    COUNTDOWN_TICKING = 'time_countdown'
    STOP_TICKING = 'time_countdown_stop'
    FLAG_APPEAR = 'pm_flag_appearance'
    FLAG_DISAPPEAR = 'pm_flag_disappearance'


_BATTLE_END_TIME = 0

class PreBattleTimer(PrebattleTimerMeta):

    def __init__(self):
        self.__isPMBattleProgressEnabled = False
        self.__isRankedBattle = False
        self.__sounds = dict()
        super(PreBattleTimer, self).__init__()

    def _populate(self):
        super(PreBattleTimer, self)._populate()
        self.addListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)
        self.__isRankedBattle = self.sessionProvider.arenaVisitor.getArenaGuiType() == ARENA_GUI_TYPE.RANKED
        if not self.__isRankedBattle:
            self.__isPMBattleProgressEnabled = self.lobbyContext.getServerSettings().isPMBattleProgressEnabled()
            qProgressCtrl = self.sessionProvider.shared.questProgress
            if qProgressCtrl is not None and self.__isPMBattleProgressEnabled:
                qProgressCtrl.onFullConditionsUpdate += self._onPersonalQuestConditionsUpdate
                qProgressCtrl.onQuestProgressInited += self._onPersonalQuestConditionsUpdate
                if qProgressCtrl.isInited():
                    self._onPersonalQuestConditionsUpdate()
        CommandMapping.g_instance.onMappingChanged += self.__onMappingChanged
        self.__onMappingChanged()
        return

    def onShowInfo(self):
        self.__callWWISE(_WWISE_EVENTS.FLAG_APPEAR)

    def onHideInfo(self):
        self.__callWWISE(_WWISE_EVENTS.FLAG_DISAPPEAR)

    def _onPersonalQuestConditionsUpdate(self, *args):
        questProgress = self.sessionProvider.shared.questProgress
        if questProgress.hasQuestsToPerform():
            self.as_addInfoS(PREBATTLE_TIMER.QP_ANIM_FLAG_LINKAGE, questProgress.getQuestShortInfoData())

    def __onMappingChanged(self, *args):
        msg = ''
        if self.__isPMBattleProgressEnabled and not self.__isRankedBattle:
            msg = backport.text(R.strings.prebattle.battleProgress.hint(), hintKey=getReadableKey(CommandMapping.CMD_QUEST_PROGRESS_SHOW))
        if msg:
            self.as_setInfoHintS(msg)

    def __callWWISE(self, wwiseEventName):
        sound = SoundGroups.g_instance.getSound2D(wwiseEventName)
        if sound is not None:
            sound.play()
            self.__sounds[wwiseEventName] = sound
        return

    def _dispose(self):
        for sound in self.__sounds.values():
            sound.stop()

        self.__sounds.clear()
        CommandMapping.g_instance.onMappingChanged -= self.__onMappingChanged
        qProgressCtrl = self.sessionProvider.shared.questProgress
        if qProgressCtrl is not None and self.__isPMBattleProgressEnabled:
            qProgressCtrl.onFullConditionsUpdate -= self._onPersonalQuestConditionsUpdate
            qProgressCtrl.onQuestProgressInited -= self._onPersonalQuestConditionsUpdate
        self.removeListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, scope=EVENT_BUS_SCOPE.BATTLE)
        super(PreBattleTimer, self)._dispose()
        return

    def __handleBattleLoading(self, event):
        if not event.ctx['isShown']:
            self.as_showInfoS()


class BattleTimer(EventBattleTimerMeta, IAbstractPeriodView):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BattleTimer, self).__init__()
        self.__isTicking = False
        self.__state = COUNTDOWN_STATE.UNDEFINED
        self.__roundLength = self.arenaVisitor.type.getRoundLength()
        self.__endingSoonTime = self.arenaVisitor.type.getBattleEndingSoonTime()
        self.__appearTime = self.arenaVisitor.type.getBattleEndWarningAppearTime()
        self.__endWarningIsEnabled = self.__checkEndWarningStatus()
        self.__sounds = dict()
        self.__isDeathScreenShown = False
        self.__finalCountDownEnabled = False
        self.__endEventMusicPlayed = False

    def destroy(self):
        for sound in self.__sounds.values():
            sound.stop()

        self.__sounds.clear()
        super(BattleTimer, self).destroy()

    @property
    def arenaVisitor(self):
        return self.sessionProvider.arenaVisitor

    def isEventBattle(self):
        return self.arenaVisitor.gui.isEventBattle()

    def setTotalTime(self, totalTime):
        if self.__isDeathScreenShown:
            return
        else:
            minutes, seconds = divmod(int(totalTime), 60)
            if self.__endWarningIsEnabled and self.__state == COUNTDOWN_STATE.STOP:
                if _BATTLE_END_TIME < totalTime <= self.__endingSoonTime:
                    if self.isEventBattle() and not self.__finalCountDownEnabled:
                        self.__finalCountDownEnabled = True
                        self.__setEnlarged(False)
                    if not self.__isTicking:
                        self._startTicking()
                    if totalTime == self.__endingSoonTime:
                        self._callWWISE(_WWISE_EVENTS.BATTLE_ENDING_SOON)
                elif self.__isTicking:
                    self.__stopTicking()
            if not self.__endEventMusicPlayed and self.isEventBattle() and totalTime <= self.__appearTime and self.__state == COUNTDOWN_STATE.STOP:
                eventSoundController = self.sessionProvider.dynamic.getController(BATTLE_CTRL_ID.EVENT_SOUND_CTRL)
                if eventSoundController is not None:
                    self.__endEventMusicPlayed = eventSoundController.playStartMusic()
            self._sendTime(minutes, seconds)
            return

    def setState(self, state):
        self.__state = state

    def hideTotalTime(self):
        self.as_showBattleTimerS(False)

    def showTotalTime(self):
        self.as_showBattleTimerS(True)

    def showAddExtraTime(self, timeDiff):
        if not self.isEventBattle():
            self.__showExtraTimerAnimation(timeDiff)

    def _populate(self):
        super(BattleTimer, self)._populate()
        ctrl = self.sessionProvider.dynamic.deathScreen
        if ctrl is not None:
            ctrl.onShowDeathScreen += self.__onShowDeathScreen
        player = BigWorld.player()
        if player is not None:
            player.onVehicleLeaveWorld += self.__onVehicleLeaveWorld
        g_eventBus.addListener(WtGameEvent.TIMER_ADDED_ANIMATION, self.__showExtraTimerAnimationEvent, scope=EVENT_BUS_SCOPE.BATTLE)
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        self.__setEnlarged(self.arenaVisitor.getArenaPeriod() == ARENA_PERIOD.BATTLE)
        return

    def _dispose(self):
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        g_eventBus.removeListener(WtGameEvent.TIMER_ADDED_ANIMATION, self.__showExtraTimerAnimationEvent, scope=EVENT_BUS_SCOPE.BATTLE)
        ctrl = self.sessionProvider.dynamic.deathScreen
        if ctrl is not None:
            ctrl.onShowDeathScreen -= self.__onShowDeathScreen
        player = BigWorld.player()
        if isPlayerAvatar() and player.onVehicleLeaveWorld is not None:
            player.onVehicleLeaveWorld -= self.__onVehicleLeaveWorld
        super(BattleTimer, self)._dispose()
        return

    def _sendTime(self, minutes, seconds):
        self.as_setTotalTimeS('{:02d}'.format(minutes), '{:02d}'.format(seconds))

    def _callWWISE(self, wwiseEventName):
        sound = SoundGroups.g_instance.getSound2D(wwiseEventName)
        if sound is not None:
            sound.play()
            self.__sounds[wwiseEventName] = sound
        return

    def _setColor(self):
        if not self.isEventBattle():
            self.as_setColorS(self.__isTicking)

    def _startTicking(self):
        self._callWWISE(_WWISE_EVENTS.COUNTDOWN_TICKING)
        self.__isTicking = True
        self._setColor()

    def __stopTicking(self):
        self._callWWISE(_WWISE_EVENTS.STOP_TICKING)
        self.__isTicking = False
        self._setColor()

    def __onArenaPeriodChange(self, period, *_):
        self.__setEnlarged(period == ARENA_PERIOD.BATTLE and not self.__finalCountDownEnabled)

    def __validateEndingSoonTime(self):
        return 0 < self.__endingSoonTime < self.__roundLength

    def __checkEndWarningStatus(self):
        endingSoonTimeIsValid = self.__validateEndingSoonTime()
        return self.arenaVisitor.isBattleEndWarningEnabled() and endingSoonTimeIsValid

    def __onShowDeathScreen(self):
        self.__isDeathScreenShown = True
        self.__stopTicking()

    def __onVehicleLeaveWorld(self, vehicle):
        if BigWorld.player().playerVehicleID == vehicle.id:
            self.__isDeathScreenShown = False

    def __showExtraTimerAnimationEvent(self, event):
        self.__showExtraTimerAnimation(event.ctx['diff'])

    def __showExtraTimerAnimation(self, diff):
        if self.__finalCountDownEnabled or not self.isEventBattle():
            return
        minutes, seconds = divmod(int(diff), 60)
        info = self.sessionProvider.getCtx().getVehicleInfo(avatar_getter.getPlayerVehicleID())
        isRed = getHunterDescr() != info.vehicleType.compactDescr
        self.as_showAddExtraTimeS('+{:02d}:{:02d}'.format(minutes, seconds), isRed)

    def __setEnlarged(self, isBig):
        if self.isEventBattle():
            self.as_setIsEnlargedS(isBig)
