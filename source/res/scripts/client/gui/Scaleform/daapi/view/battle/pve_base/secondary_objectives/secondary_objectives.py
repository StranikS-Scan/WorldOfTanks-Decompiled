# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/secondary_objectives/secondary_objectives.py
import typing
from helpers.time_utils import ONE_MINUTE
import BattleReplay
import BigWorld
from gui.Scaleform.daapi.view.battle.pve_base.base.pve_hud_widget import SeveralItemsPveHudWidget
from gui.Scaleform.daapi.view.battle.pve_base.secondary_objectives.settings_model import SecondaryObjectiveServerModel
from gui.Scaleform.daapi.view.battle.pve_base.secondary_objectives.state_machine.machine import SecondaryObjectiveStateMachine
from gui.Scaleform.daapi.view.meta.PveSecondaryObjectivesMeta import PveSecondaryObjectivesMeta
from pve_battle_hud import WidgetType, SecondaryObjectiveState

class PveSecondaryObjectives(SeveralItemsPveHudWidget, PveSecondaryObjectivesMeta):
    MAX_ITEMS_COUNT = 3

    def __init__(self):
        super(PveSecondaryObjectives, self).__init__(widgetType=WidgetType.SECONDARY_OBJECTIVE, stateMachineClass=SecondaryObjectiveStateMachine, serverSettingsModel=SecondaryObjectiveServerModel)

    def addObjective(self, serverSettings, clientSettings):
        hasProgressBar = serverSettings.progress is not None
        newObjective = {'id': serverSettings.id,
         'icon': clientSettings.icon,
         'isTimerEnable': bool(serverSettings.timer),
         'title': clientSettings.getHeader(serverSettings.params),
         'description': clientSettings.getSubheader(),
         'isVisibleProgressBar': hasProgressBar,
         'progressBarValue': serverSettings.progress * 100 if hasProgressBar else 0}
        self.as_addObjectS(newObjective)
        self.updateProgress(serverSettings.id, serverSettings.progress)
        return

    def removeObjective(self, objectiveId, hideType):
        self.as_removeObjectS(objectiveId, hideType)

    def updateTimer(self, objectiveId, timerValue, isWarning=False):
        timerValue = max(timerValue, 0)
        minutes, seconds = divmod(int(timerValue), ONE_MINUTE)
        formattedTime = '{:02d}:{:02d}'.format(minutes, seconds)
        self.as_updateTimeS(objectiveId, formattedTime, isWarning)

    def updateProgress(self, objectiveId, progress):
        if progress is not None:
            self.as_setProgressBarValueS(objectiveId, progress * 100)
        return

    def updateTitle(self, objectiveId, title):
        self.as_setTitleS(objectiveId, title)

    def _onPrebattlePeriod(self):
        if BattleReplay.isPlaying():
            self.as_clearS()

    def _getStateToRestore(self, serverSettings):
        serverState = serverSettings.state
        timeLeft = serverSettings.finishTime - BigWorld.serverTime()
        completeStates = [SecondaryObjectiveState.SUCCESS,
         SecondaryObjectiveState.FAILURE,
         SecondaryObjectiveState.DISAPPEARANCE,
         SecondaryObjectiveState.HIDDEN]
        if serverState in completeStates or serverSettings.finishTime and timeLeft <= 0:
            return None
        else:
            return SecondaryObjectiveState.RESTORED if serverState in [SecondaryObjectiveState.APPEARANCE, SecondaryObjectiveState.REGULAR, SecondaryObjectiveState.RESTORED] else serverState
