# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/epic_battles_widget.py
from collections import namedtuple
import SoundGroups
from gui.Scaleform.daapi.view.lobby.epicBattle.after_battle_reward_view_helpers import getProgressionIconVODict
from gui.Scaleform.daapi.view.meta.EpicBattlesWidgetMeta import EpicBattlesWidgetMeta
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers import dependency, time_utils
from skeletons.gui.game_control import IEpicBattleMetaGameController
EpicBattlesWidgetVO = namedtuple('EpicBattlesWidgetVO', ('epicMetaLevelIconData', 'points'))

class EpicBattlesWidget(EpicBattlesWidgetMeta):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self):
        super(EpicBattlesWidget, self).__init__()
        self.__periodicNotifier = None
        return

    def onWidgetClick(self):
        self.__epicController.openURL()

    def onSoundTrigger(self, triggerName):
        SoundGroups.g_instance.playSound2D(triggerName)

    def update(self):
        if not self.__epicController.isEnabled():
            return
        else:
            if self.__periodicNotifier is not None:
                self.__periodicNotifier.startNotification()
            self.as_setDataS(self.__buildVO()._asdict())
            return

    def _populate(self):
        super(EpicBattlesWidget, self)._populate()
        if not self.__epicController.isEnabled():
            return
        else:
            if self.__periodicNotifier is None:
                self.__periodicNotifier = PeriodicNotifier(self.__epicController.getTimer, self.update)
            self.__periodicNotifier.startNotification()
            return

    def _dispose(self):
        if self.__periodicNotifier is not None:
            self.__periodicNotifier.stopNotification()
            self.__periodicNotifier.clear()
            self.__periodicNotifier = None
        super(EpicBattlesWidget, self)._dispose()
        self.__periodicNotifier = None
        return

    def __buildVO(self):
        season = self.__epicController.getCurrentSeason() or self.__epicController.getNextSeason()
        currentLevel, _ = self.__epicController.getPlayerLevelInfo()
        cycleNumber = 1
        if season is not None:
            cycleNumber = self.__epicController.getCurrentOrNextActiveCycleNumber(season)
        level = currentLevel if self.__epicController.isCurrentCycleActive() else None
        return EpicBattlesWidgetVO(epicMetaLevelIconData=getProgressionIconVODict(cycleNumber, level), points=str(self.__getSkillPoints()))

    def __getSkillPoints(self):
        season = self.__epicController.getCurrentSeason()
        if season is None:
            return ''
        else:
            noActiveCycles = not self.__epicController.isCurrentCycleActive()
            now = time_utils.getCurrentLocalServerTimestamp()
            allCyclesInFuture = True
            for cycle in season.getAllCycles().values():
                if cycle.startDate < now:
                    allCyclesInFuture = False
                    break

            if noActiveCycles and allCyclesInFuture:
                return ''
            noNextCycle = season.getNextByTimeCycle(now) is None
            return '' if noActiveCycles and noNextCycle else str(self.__epicController.getSkillPoints())
