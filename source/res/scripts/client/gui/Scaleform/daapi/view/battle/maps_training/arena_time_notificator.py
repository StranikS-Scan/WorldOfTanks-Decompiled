# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/maps_training/arena_time_notificator.py
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_TIME_TO_NOTIFY_BATTLE_END = 120

class MapsTrainingArenaTimeNotificator(IAbstractPeriodView):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(MapsTrainingArenaTimeNotificator, self).__init__()
        self.__prevLength = None
        self.__period = None
        self.__lastNotifiedTime = None
        return

    def setTotalTime(self, totalTime):
        if self.__lastNotifiedTime is None:
            self.__lastNotifiedTime = totalTime
        if not totalTime == _TIME_TO_NOTIFY_BATTLE_END:
            totalTime < _TIME_TO_NOTIFY_BATTLE_END < self.__lastNotifiedTime and self.sessionProvider.dynamic.battleHints.showHint('timeRunsOut', {'param1': _TIME_TO_NOTIFY_BATTLE_END})
        self.__lastNotifiedTime = totalTime
        return
