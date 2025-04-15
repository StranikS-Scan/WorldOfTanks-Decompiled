# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/classic/battle_end_warning_panel.py
import WWISE
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.view.meta.BattleEndWarningPanelMeta import BattleEndWarningPanelMeta
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from helpers import dependency
from helpers.i18n import makeString as _ms
from helpers.time_utils import ONE_MINUTE
from skeletons.gui.battle_session import IBattleSessionProvider

class _WWISE_EVENTS(object):
    APPEAR = 'time_buzzer_01'


_WARNING_TEXT_KEY = '#ingame_gui:battleEndWarning/text'
_SWF_FILE_NAME = 'BattleEndWarningPanel.swf'
_CALLBACK_NAME = 'battle.onLoadEndWarningPanel'

class BattleEndWarningPanel(BattleEndWarningPanelMeta, IAbstractPeriodView):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BattleEndWarningPanel, self).__init__()
        arenaVisitor = self.sessionProvider.arenaVisitor
        self.__duration = arenaVisitor.type.getBattleEndWarningDuration()
        self.__appearTime = arenaVisitor.type.getBattleEndWarningAppearTime()
        self.__roundLength = arenaVisitor.getRoundLength()
        self.__isShown = False
        self.__warningIsValid = self.__validateWarningTime()
        self.__currPeriod = None
        return

    def isLoaded(self):
        return self.__currPeriod == ARENA_PERIOD.BATTLE

    def setPeriod(self, period):
        self.__currPeriod = period

    def setTotalTime(self, totalTime):
        if not self.isLoaded() or not self._isDAAPIInited():
            return
        minutes, seconds = divmod(int(totalTime), ONE_MINUTE)
        minutesStr = '{:02d}'.format(minutes)
        secondsStr = '{:02d}'.format(seconds)
        if self.__isShown:
            self.as_setTotalTimeS(minutesStr, secondsStr)
        if self.__isAlertTimerInterval(totalTime) and not self.__isShown and self.__warningIsValid:
            self._callWWISE(_WWISE_EVENTS.APPEAR)
            self.as_setTotalTimeS(minutesStr, secondsStr)
            self.as_setTextInfoS(_ms(_WARNING_TEXT_KEY))
            self.as_setStateS(True)
            self.__isShown = True
        if not self.__isAlertTimerInterval(totalTime) and self.__isShown:
            self.as_setStateS(False)
            self.__isShown = False

    def _callWWISE(self, wwiseEventName):
        WWISE.WW_eventGlobal(wwiseEventName)

    def __isAlertTimerInterval(self, totalTime):
        return self.__appearTime - self.__duration < totalTime <= self.__appearTime

    def __validateWarningTime(self):
        return False if self.__appearTime < self.__duration or self.__appearTime <= 0 or self.__duration <= 0 or self.__appearTime > self.__roundLength or self.__duration > self.__roundLength and self.sessionProvider.arenaVisitor.isBattleEndWarningEnabled() else True
