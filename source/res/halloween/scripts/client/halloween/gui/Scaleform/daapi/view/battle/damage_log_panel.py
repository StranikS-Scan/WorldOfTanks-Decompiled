# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/damage_log_panel.py
from gui.Scaleform.daapi.view.battle.shared.damage_log_panel import DamageLogPanel, _LogViewComponent, _LogRecordVOBuilder, _ReceivedHitVehicleVOBuilder, _ActionImgVOBuilder, _CritsShellVOBuilder, _CriticalHitValueVOBuilder
from account_helpers.settings_core.options import DamageLogDetailsSetting as _VIEW_MODE
from gui.battle_control.controllers.personal_efficiency_ctrl import _FEEDBACK_EVENT_TYPE_TO_PERSONAL_EFFICIENCY_TYPE, _CriticalHitsEfficiencyInfo
from gui.battle_control.battle_constants import PERSONAL_EFFICIENCY_TYPE as _ETYPE
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _FET
from gui.Scaleform.genConsts.BATTLEDAMAGELOG_IMAGES import BATTLEDAMAGELOG_IMAGES as _IMAGES
HALLOWEEN_SUPER_SHELL_FLAG = 16777216
HW_EFFICIENCY_SUPER_SHELL_CRITS = _ETYPE.RECEIVED_CRITICAL_HITS | HALLOWEEN_SUPER_SHELL_FLAG
_FEEDBACK_EVENT_TYPE_TO_PERSONAL_EFFICIENCY_TYPE.update({_FET.PLAYER_DAMAGED_DEVICE_ENEMY: (HW_EFFICIENCY_SUPER_SHELL_CRITS, _CriticalHitsEfficiencyInfo)})

class _HWSuperShellCritsRecordVOBuilder(_LogRecordVOBuilder):

    def buildVO(self, info, arenaDP):
        return None if not info.isSuperShell(primary=False) else super(_HWSuperShellCritsRecordVOBuilder, self).buildVO(info, arenaDP)


_ETYPE_TO_RECORD_VO_BUILDER = {HW_EFFICIENCY_SUPER_SHELL_CRITS: _HWSuperShellCritsRecordVOBuilder(_ReceivedHitVehicleVOBuilder(), _CritsShellVOBuilder(), _CriticalHitValueVOBuilder(), _ActionImgVOBuilder(image=_IMAGES.DAMAGELOG_CRITICAL_16X16))}

class _HalloweenLogViewComponent(_LogViewComponent):

    def updateViewMode(self, viewMode):
        if viewMode != self._logViewMode:
            self._logViewMode = viewMode
            self.invalidate()

    def _buildLogMessageVO(self, info):
        builder = _ETYPE_TO_RECORD_VO_BUILDER.get(info.getType(), None)
        return builder.buildVO(info, self._LogViewComponent__arenaDP) if builder is not None else super(_HalloweenLogViewComponent, self)._buildLogMessageVO(info)


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
