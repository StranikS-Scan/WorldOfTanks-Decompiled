# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/primary_objective/primary_objective.py
import typing
from helpers.time_utils import ONE_MINUTE
import BattleReplay
import BigWorld
from gui.Scaleform.daapi.view.battle.pve_base.base.pve_hud_widget import SingleItemPveHudWidget
from gui.Scaleform.daapi.view.battle.pve_base.primary_objective.settings_model import PrimaryObjectiveServerModel
from gui.Scaleform.daapi.view.battle.pve_base.primary_objective.state_machine.machine import PrimaryObjectiveStateMachine
from gui.Scaleform.daapi.view.meta.PvePrimaryObjectiveMeta import PvePrimaryObjectiveMeta
from pve_battle_hud import WidgetType, PrimaryObjectiveState, getPveHudLogger
_logger = getPveHudLogger()

class PvePrimaryObjective(SingleItemPveHudWidget, PvePrimaryObjectiveMeta):

    def __init__(self):
        super(PvePrimaryObjective, self).__init__(widgetType=WidgetType.PRIMARY_OBJECTIVE, stateMachineClass=PrimaryObjectiveStateMachine, serverSettingsModel=PrimaryObjectiveServerModel)

    def updateTimer(self, timerValue):
        if timerValue is None:
            formattedTime = ''
        else:
            timerValue = max(timerValue, 0)
            minutes, seconds = divmod(int(timerValue), ONE_MINUTE)
            formattedTime = '{:02d}:{:02d}'.format(minutes, seconds)
        self.as_updateTimeS(formattedTime)
        return

    def updateHeaderWithSubheader(self, header, subheader):
        self.as_setDataS(self._createVo(header=header, objective=subheader))
        self.as_setHintStateS(True)

    def updateSubheader(self, subheader):
        self.as_setDataS(self._createVo(title=subheader))
        self.as_setHintStateS(False)

    def updateProgress(self, progresses=None, isVisible=True):
        progress, isVisible = (0, False) if not progresses or not isVisible else (int(progresses[0] * 100), True)
        self.as_updateProgressBarS(progress, isVisible)

    def showMessage(self, isBackgroundVisible, icon, text):
        self.as_showResultS(isBackgroundVisible, icon, text)

    def hideMessage(self):
        self.as_hideResultS()

    def hideObjective(self):
        self.updateTimer(None)
        self.updateProgress(isVisible=False)
        self.as_setDataS(self._createVo())
        self.as_playFxS(False, False)
        self.as_setTimerBackgroundS(False)
        self.as_setHintStateS(False)
        return

    def _onPrebattlePeriod(self):
        if BattleReplay.isPlaying():
            self.hideObjective()

    def _getStateToRestore(self, serverSettings):
        widgetKey = (serverSettings.type, serverSettings.id)
        _, clientSettings = self.getSettings(widgetKey)
        serverState = serverSettings.state
        finishTime = serverSettings.finishTime
        timeLeft = finishTime - BigWorld.serverTime() if finishTime is not None else None
        countdownTimer = clientSettings.countdownTimer
        completeStates = [PrimaryObjectiveState.SUCCESS, PrimaryObjectiveState.FAILURE, PrimaryObjectiveState.HIDDEN]
        if serverState in completeStates or timeLeft is not None and timeLeft <= 0:
            return
        elif serverState == PrimaryObjectiveState.COUNTDOWN or timeLeft is not None and countdownTimer:
            if 0 < timeLeft <= countdownTimer:
                return PrimaryObjectiveState.COUNTDOWN
            return serverState in [PrimaryObjectiveState.LARGE_TIMER, PrimaryObjectiveState.LAST_REMIND] and PrimaryObjectiveState.LARGE_TIMER
        else:
            return PrimaryObjectiveState.REGULAR if serverState in [PrimaryObjectiveState.APPEARANCE, PrimaryObjectiveState.REMIND] else serverState

    @staticmethod
    def _createVo(header='', objective='', title=''):
        return {'header': header,
         'objective': objective,
         'title': title}
