# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/progress_counter/progress_counter.py
import BattleReplay
from gui.Scaleform.daapi.view.battle.pve_base.base.pve_hud_widget import SingleItemPveHudWidget
from gui.Scaleform.daapi.view.battle.pve_base.progress_counter.settings_model import ProgressCounterServerModel
from gui.Scaleform.daapi.view.battle.pve_base.progress_counter.state_machine.machine import ProgressCounterStateMachine
from gui.Scaleform.daapi.view.meta.PveProgressCounterMeta import PveProgressCounterMeta
from pve_battle_hud import WidgetType, ProgressCounterState

class PveProgressCounter(SingleItemPveHudWidget, PveProgressCounterMeta):

    def __init__(self):
        super(PveProgressCounter, self).__init__(widgetType=WidgetType.PROGRESS_COUNTER, stateMachineClass=ProgressCounterStateMachine, serverSettingsModel=ProgressCounterServerModel)

    def _getStateToRestore(self, serverSettings):
        serverState = serverSettings.state
        if serverState == ProgressCounterState.HIDDEN:
            return None
        else:
            return ProgressCounterState.REGULAR if serverState in [ProgressCounterState.APPEARANCE, ProgressCounterState.REGULAR] else serverState

    def _onPrebattlePeriod(self):
        if BattleReplay.isPlaying():
            self.as_setDataS('', '', False)
