# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/battle_timers.py
import logging
import CommandMapping
import SoundGroups
from constants import ARENA_GUI_TYPE
from PlayerEvents import g_playerEvents
from gui import makeHtmlString
from gui.Scaleform.daapi.view.meta.BattleTimerMeta import BattleTimerMeta
from gui.Scaleform.daapi.view.meta.PrebattleTimerMeta import PrebattleTimerMeta
from gui.Scaleform.genConsts.PREBATTLE_TIMER import PREBATTLE_TIMER
from gui.battle_control.battle_constants import COUNTDOWN_STATE
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.utils.key_mapping import getReadableKey
from skeletons.gui.battle_session import IBattleSessionProvider

class _WWISE_EVENTS(object):
    BATTLE_ENDING_SOON = 'time_buzzer_02'
    COUNTDOWN_TICKING = 'time_countdown'
    STOP_TICKING = 'time_countdown_stop'
    FLAG_APPEAR = 'pm_flag_appearance'
    FLAG_DISAPPEAR = 'pm_flag_disappearance'


_BATTLE_END_TIME = 0
_logger = logging.getLogger(__name__)

class PreBattleTimer(PrebattleTimerMeta):

    def __init__(self):
        self.__isPMBattleProgressEnabled = False
        self.__isRankedBattle = False
        self.__isEventBattle = False
        self.__sounds = dict()
        super(PreBattleTimer, self).__init__()

    def _populate(self):
        super(PreBattleTimer, self)._populate()
        self.addListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)
        self.__isRankedBattle = self.sessionProvider.arenaVisitor.getArenaGuiType() == ARENA_GUI_TYPE.RANKED
        self.__isEventBattle = self.sessionProvider.arenaVisitor.getArenaGuiType() == ARENA_GUI_TYPE.EVENT_BATTLES
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

    def _getMessage(self):
        if self.__isEventBattle:
            if self._state == COUNTDOWN_STATE.WAIT:
                return makeHtmlString('html_templates:battleTimer', 'waitingForOtherPlayers')
            return makeHtmlString('html_templates:battleTimer', 'arenaDescription')
        return super(PreBattleTimer, self)._getMessage()

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


class BattleTimer(BattleTimerMeta, IAbstractPeriodView):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BattleTimer, self).__init__()
        self.__isTicking = False
        self.__state = COUNTDOWN_STATE.UNDEFINED
        self.__roundLength = self.arenaVisitor.type.getRoundLength()
        self.__endingSoonTime = self.arenaVisitor.type.getBattleEndingSoonTime()
        self.__isDeathScreenShown = False
        self.__endWarningIsEnabled = self.__checkEndWarningStatus()
        self.__sounds = dict()

    def destroy(self):
        for sound in self.__sounds.values():
            sound.stop()

        self.__sounds.clear()
        super(BattleTimer, self).destroy()

    @property
    def arenaVisitor(self):
        return self.sessionProvider.arenaVisitor

    def setTotalTime(self, totalTime):
        minutes, seconds = divmod(int(totalTime), 60)
        if self.__endWarningIsEnabled and self.__state == COUNTDOWN_STATE.STOP:
            if _BATTLE_END_TIME < totalTime <= self.__endingSoonTime:
                if not self.__isTicking:
                    self._startTicking()
                if totalTime == self.__endingSoonTime:
                    self._callWWISE(_WWISE_EVENTS.BATTLE_ENDING_SOON)
            elif self.__isTicking:
                self.__stopTicking()
        self._sendTime(minutes, seconds)

    def setState(self, state):
        self.__state = state

    def hideTotalTime(self):
        self.as_showBattleTimerS(False)

    def showTotalTime(self):
        self.as_showBattleTimerS(True)

    def _populate(self):
        super(BattleTimer, self)._populate()
        ctrl = self.sessionProvider.dynamic.deathScreen
        if ctrl is not None:
            ctrl.onShowDeathScreen += self.__onShowDeathScreen
        g_playerEvents.onAvatarVehicleLeaveWorld += self.__onVehicleLeaveWorld
        return

    def _dispose(self):
        ctrl = self.sessionProvider.dynamic.deathScreen
        if ctrl is not None:
            ctrl.onShowDeathScreen -= self.__onShowDeathScreen
        g_playerEvents.onAvatarVehicleLeaveWorld -= self.__onVehicleLeaveWorld
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
        self.as_setColorS(self.__isTicking)

    def _startTicking(self):
        self._callWWISE(_WWISE_EVENTS.COUNTDOWN_TICKING)
        self.__isTicking = True
        self._setColor()

    def __stopTicking(self):
        self._callWWISE(_WWISE_EVENTS.STOP_TICKING)
        self.__isTicking = False
        self._setColor()

    def __validateEndingSoonTime(self):
        return 0 < self.__endingSoonTime < self.__roundLength

    def __checkEndWarningStatus(self):
        endingSoonTimeIsValid = self.__validateEndingSoonTime()
        return self.arenaVisitor.isBattleEndWarningEnabled() and endingSoonTimeIsValid and not self.__isDeathScreenShown

    def __onShowDeathScreen(self):
        self.__isDeathScreenShown = True
        self.__endWarningIsEnabled = self.__checkEndWarningStatus()
        self.__stopTicking()

    def __onVehicleLeaveWorld(self):
        self.__isDeathScreenShown = False
        self.__endWarningIsEnabled = self.__checkEndWarningStatus()
