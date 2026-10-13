# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/damage_log_panel.py
from gui.Scaleform.daapi.view.battle.shared.damage_log_panel import DamageLogPanel, LogViewComponent, _ReceivedHitVehicleVOBuilder, makeReceivedDamageBuilder
from gui.battle_control.battle_constants import PERSONAL_EFFICIENCY_TYPE as _ETYPE

class _PortalReceivedHitVehicleVOBuilder(_ReceivedHitVehicleVOBuilder):

    def _populateVO(self, vehicleVO, info, arenaDP):
        super(_PortalReceivedHitVehicleVOBuilder, self)._populateVO(vehicleVO, info, arenaDP)
        if info.isDeathZone():
            vehicleType = arenaDP.getVehicleInfo(info.getArenaVehicleID()).vehicleType
            vehicleVO.vehicleTypeImg = self._getVehicleTypeIcon(vehicleType)
            vehicleVO.vehicleName = vehicleType.shortNameWithPrefix


_PORTAL_ETYPE_TO_RECORD_VO_BUILDER = {_ETYPE.RECEIVED_DAMAGE: makeReceivedDamageBuilder(vehicleBuilder=_PortalReceivedHitVehicleVOBuilder())}

class PortalLogViewComponent(LogViewComponent):

    def _buildLogMessageVO(self, info):
        builder = _PORTAL_ETYPE_TO_RECORD_VO_BUILDER.get(info.getType())
        return builder.buildVO(info, self._arenaDP) if builder is not None else super(PortalLogViewComponent, self)._buildLogMessageVO(info)


class PortalDamageLogPanel(DamageLogPanel):

    def _isDamageSettingEnabled(self, settingName):
        return True

    def _getLogViewComponentClass(self):
        return PortalLogViewComponent()
