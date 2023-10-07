# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/damage_log_panel.py
from gui.Scaleform.daapi.view.battle.shared.damage_log_panel import DamageLogPanel, _LogViewComponent
from account_helpers.settings_core.options import DamageLogDetailsSetting as _VIEW_MODE
from gui.battle_control.controllers.personal_efficiency_ctrl import _FEEDBACK_EVENT_TYPE_TO_PERSONAL_EFFICIENCY_TYPE
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _FET

class _HalloweenLogViewComponent(_LogViewComponent):

    def updateViewMode(self, viewMode):
        if viewMode != self._logViewMode:
            self._logViewMode = viewMode
            self.invalidate()


class HalloweenDamageLogPanel(DamageLogPanel):

    def __init__(self):
        super(HalloweenDamageLogPanel, self).__init__()
        self._topLog = _HalloweenLogViewComponent()
        self._bottomLog = _HalloweenLogViewComponent()

    def _hideLogs(self):
        self._topLog.updateViewMode(_VIEW_MODE.HIDE)
        self._bottomLog.updateViewMode(_VIEW_MODE.HIDE)

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        super(HalloweenDamageLogPanel, self)._onPostMortemSwitched(noRespawnPossible, respawnAvailable)
        self._hideLogs()

    def _onVehicleControlling(self, vehicle):
        self._invalidateLogs()
        super(HalloweenDamageLogPanel, self)._onVehicleControlling(vehicle)
