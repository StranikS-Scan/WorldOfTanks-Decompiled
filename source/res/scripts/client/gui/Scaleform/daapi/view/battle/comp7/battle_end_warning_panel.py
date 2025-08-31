# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/comp7/battle_end_warning_panel.py
import WWISE
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.meta.BattleEndWarningPanelMeta import BattleEndWarningPanelMeta
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from helpers.time_utils import ONE_MINUTE
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class _WWISE_EVENTS(object):
    APPEAR = 'time_buzzer_01'


_SWF_FILE_NAME = 'BattleEndWarningPanel.swf'

class Comp7BattleEndWarningPanel(BattleEndWarningPanelMeta, IAbstractPeriodView):
    __slots__ = ('__duration', '__appearTime', '__extraAppearTime', '__roundLength', '__isShown', '__warningIsValid', '__extraWarningIsValid')
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(Comp7BattleEndWarningPanel, self).__init__()
        arenaVisitor = self.sessionProvider.arenaVisitor
        self.__duration = arenaVisitor.type.getBattleEndWarningDuration()
        self.__appearTime = arenaVisitor.type.getBattleEndWarningAppearTime()
        self.__extraAppearTime = arenaVisitor.type.getBattleEndWarningExtraAppearTime()
        self.__roundLength = arenaVisitor.getRoundLength()
        self.__isShown = False
        self.__warningIsValid = self.__validateWarningTime()
        self.__extraWarningIsValid = self.__validateExtraWarningTime()

    def isLoaded(self):
        return True

    def setTotalTime(self, totalTime):
        if not self.isLoaded():
            return
        minutes, seconds = divmod(int(totalTime), ONE_MINUTE)
        minutesStr = '{:02d}'.format(minutes)
        secondsStr = '{:02d}'.format(seconds)
        if self.__isShown:
            self.as_setTotalTimeS(minutesStr, secondsStr)
        isAppearTime = totalTime == self.__appearTime
        isExtraAppearTime = totalTime == self.__extraAppearTime
        if isAppearTime and self.__warningIsValid or isExtraAppearTime and self.__extraWarningIsValid:
            WWISE.WW_eventGlobal(_WWISE_EVENTS.APPEAR)
            self.as_setTotalTimeS(minutesStr, secondsStr)
            self.as_setTextInfoS(self.__getWarningText())
            self.as_setStateS(True)
            self.__isShown = True
        isBeforeWarning = totalTime <= self.__appearTime - self.__duration
        isAfterWarning = totalTime > self.__appearTime
        isBeforeExtraWarning = totalTime <= self.__extraAppearTime - self.__duration
        isAfterExtraWarning = totalTime > self.__extraAppearTime
        if (isBeforeWarning or isAfterWarning) and (isBeforeExtraWarning or isAfterExtraWarning) and self.__isShown:
            self.as_setStateS(False)
            self.__isShown = False

    def __getWarningText(self):
        arenaDescription = self.sessionProvider.getArenaDP().getPersonalDescription()
        hasControlPoint = arenaDescription.isControlPointExists()
        hasBase = arenaDescription.isBaseExists()
        return backport.text(R.strings.ingame_gui.battleEndWarning.text()) if hasControlPoint else backport.text(R.strings.ingame_gui.battleEndWarning.dyn('comp7_{}'.format(1 if hasBase else 2)).dyn('text')())

    def __validateWarningTime(self):
        return False if self.__appearTime < self.__duration or self.__appearTime <= 0 or self.__duration <= 0 or self.__appearTime > self.__roundLength or self.__duration > self.__roundLength and self.sessionProvider.arenaVisitor.isBattleEndWarningEnabled() else True

    def __validateExtraWarningTime(self):
        return False if self.__extraAppearTime < self.__duration or self.__extraAppearTime <= 0 or self.__duration <= 0 or self.__extraAppearTime > self.__roundLength or self.__duration > self.__roundLength and self.sessionProvider.arenaVisitor.isBattleEndWarningEnabled() else True
