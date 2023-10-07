# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/epic_battles_widget.py
from collections import namedtuple
import SoundGroups
from gui.Scaleform.daapi.view.lobby.epicBattle.after_battle_reward_view_helpers import getProgressionIconVODict
from gui.Scaleform.daapi.view.meta.EpicBattlesWidgetMeta import EpicBattlesWidgetMeta
from gui.shared.event_dispatcher import showFrontlineContainerWindow
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers import dependency, time_utils
from skeletons.gui.game_control import IEpicBattleMetaGameController
from gui.ClientUpdateManager import g_clientUpdateManager
from epic_constants import EPIC_CHOICE_REWARD_OFFER_GIFT_TOKENS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from uilogging.epic_battle.constants import EpicBattleLogKeys
from uilogging.epic_battle.loggers import EpicBattleTooltipLogger
EpicBattlesWidgetVO = namedtuple('EpicBattlesWidgetVO', ('epicMetaLevelIconData', 'points', 'counterValue'))

class EpicBattlesWidget(EpicBattlesWidgetMeta):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self):
        super(EpicBattlesWidget, self).__init__()
        self.__periodicNotifier = None
        self.__uiEpicBattleLogger = EpicBattleTooltipLogger()
        return

    def onWidgetClick(self):
        showFrontlineContainerWindow()

    def onSoundTrigger(self, triggerName):
        SoundGroups.g_instance.playSound2D(triggerName)

    def _populate(self):
        super(EpicBattlesWidget, self)._populate()
        if not self.__epicController.isEnabled():
            return
        else:
            if self.__periodicNotifier is None:
                self.__periodicNotifier = PeriodicNotifier(self.__epicController.getTimer, self.__update)
            self.__periodicNotifier.startNotification()
            g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
            self.__uiEpicBattleLogger.initialize(EpicBattleLogKeys.HANGAR.value, (TOOLTIPS_CONSTANTS.EPIC_BATTLE_WIDGET_INFO,))
            self.__epicController.onUpdated += self.__update
            self.__update()
            return

    def __update(self, *_):
        if not self.__epicController.isEnabled():
            return
        else:
            if self.__periodicNotifier is not None:
                self.__periodicNotifier.startNotification()
            self.as_setDataS(self.__buildVO()._asdict())
            return

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        if self.__periodicNotifier is not None:
            self.__periodicNotifier.stopNotification()
            self.__periodicNotifier.clear()
            self.__periodicNotifier = None
        self.__epicController.onUpdated -= self.__update
        super(EpicBattlesWidget, self)._dispose()
        self.__periodicNotifier = None
        self.__uiEpicBattleLogger.reset()
        return

    def __buildVO(self):
        season = self.__epicController.getCurrentSeason() or self.__epicController.getNextSeason()
        currentLevel, _ = self.__epicController.getPlayerLevelInfo()
        cycleNumber = 1
        if season is not None:
            cycleNumber = self.__epicController.getCurrentOrNextActiveCycleNumber(season)
        level = currentLevel if self.__epicController.isCurrentCycleActive() or currentLevel > 1 else None
        return EpicBattlesWidgetVO(epicMetaLevelIconData=getProgressionIconVODict(cycleNumber, level), points=str(self.__getSkillPoints()), counterValue=self.__epicController.getNotChosenRewardCount())

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

    def __onTokensUpdate(self, diff):
        if any((key.startswith(EPIC_CHOICE_REWARD_OFFER_GIFT_TOKENS) for key in diff.keys())):
            self.__update()
