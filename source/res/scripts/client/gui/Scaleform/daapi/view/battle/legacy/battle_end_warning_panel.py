# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/legacy/battle_end_warning_panel.py
from helpers.i18n import makeString as _ms
from helpers.time_utils import ONE_MINUTE

class _SOUNDS:
    APPEAR = 'time_buzzer_01'


_WARNING_TEXT_KEY = '#ingame_gui:battleEndWarning/text'
_SWF_FILE_NAME = 'BattleEndWarningPanel.swf'
_CALLBACK_NAME = 'battle.onLoadEndWarningPanel'

class BattleEndWarningEmptyObject(object):

    def __init__(self, battleUI, arenaType, soundEngine):
        self._swfIsLoaded = False
        self._battleUI = battleUI

    def isLoaded(self):
        return self._swfIsLoaded

    def setCurrentTimeLeft(self, totalTime):
        pass

    def destroy(self):
        self._battleUI = None
        return


class BattleEndWarningPanel(BattleEndWarningEmptyObject):

    def __init__(self, battleUI, arenaType, soundEngine):
        BattleEndWarningEmptyObject.__init__(self, battleUI, arenaType, soundEngine)
        self.__flashObject = None
        self.__isShown = False
        self.__soundEngine = soundEngine
        self.__roundLength = arenaType.getRoundLength()
        self.__appearTime = arenaType.getBattleEndWarningAppearTime()
        self.__duration = arenaType.getBattleEndWarningDuration()
        self.__warningIsValid = self.__validateWarningTime()
        self._battleUI.addExternalCallback(_CALLBACK_NAME, self.__onLoad)
        self._battleUI.movie.loadEndWarningPanel(_SWF_FILE_NAME)
        return

    def destroy(self):
        self._battleUI.removeExternalCallback(_CALLBACK_NAME)

    def setCurrentTimeLeft(self, totalTime):
        minutes, seconds = divmod(int(totalTime), ONE_MINUTE)
        minutesStr = '{:02d}'.format(minutes)
        secondsStr = '{:02d}'.format(seconds)
        if self.__isShown:
            self.__flashObject.as_setTotalTime(minutesStr, secondsStr)
        if totalTime == self.__appearTime and self.__warningIsValid:
            self.__soundEngine.playSound2D(_SOUNDS.APPEAR)
            self.__flashObject.as_setTotalTime(minutesStr, secondsStr)
            self.__flashObject.as_setTextInfo(_ms(_WARNING_TEXT_KEY))
            self.__flashObject.as_setState(True)
            self.__isShown = True
        if totalTime <= self.__appearTime - self.__duration and self.__isShown:
            self.__flashObject.as_setState(False)
            self.__isShown = False

    def __onLoad(self, _):
        self._swfIsLoaded = True
        self.__flashObject = self._battleUI.movie.endWarningPanel.instance

    def __validateWarningTime(self):
        return False if self.__appearTime < self.__duration or self.__appearTime <= 0 or self.__duration <= 0 or self.__appearTime > self.__roundLength or self.__duration > self.__roundLength else True
