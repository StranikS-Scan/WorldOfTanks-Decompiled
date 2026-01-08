# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/damage_log_panel.py
from gui.Scaleform.daapi.view.battle.shared.damage_log_panel import DamageLogPanel, LogViewComponent, VehicleVOBuilder, makeDamageBuilder, makeReceivedDamageBuilder, EMPTY_SHELL_VO_BUILDER, makeBlockedDamageBuilder, makeAssistDamageBuilder, makeReceivedCriticalHitsBuilder, makeStunBuilder
from gui.battle_control.battle_constants import PERSONAL_EFFICIENCY_TYPE as _ETYPE
from gui.Scaleform.genConsts.BATTLEDAMAGELOG_IMAGES import BATTLEDAMAGELOG_IMAGES as _IMAGES
from supply_shared import Supply
SUPPLY_TYPE_ICONS = {Supply.PILLBOX: _IMAGES.WHITE_ICON_PILLBOX_16X16,
 Supply.MORTAR: _IMAGES.WHITE_ICON_MORTAR_16X16,
 Supply.FLAMER: _IMAGES.WHITE_ICON_FLAMER_16X16,
 Supply.AIRSHIP: _IMAGES.WHITE_ICON_AIRSHIP_16X16}

class EpicDamageLogPanel(DamageLogPanel):

    def _getLogViewComponentClass(self):
        return EpicLogViewComponent()


class EpicVehicleVOBuilder(VehicleVOBuilder):

    def _getVehicleTypeIcon(self, vehicleType):
        if Supply.isSupply(vehicleType.tags):
            supplyID = Supply.getID(vehicleType)
            return SUPPLY_TYPE_ICONS.get(supplyID, '')
        return super(EpicVehicleVOBuilder, self)._getVehicleTypeIcon(vehicleType)


_EPIC_VEHICLE_VO_BUILDER = EpicVehicleVOBuilder()
_SUPPLY_ETYPE_TO_RECORD_VO_BUILDER = {_ETYPE.DAMAGE: makeDamageBuilder(vehicleBuilder=_EPIC_VEHICLE_VO_BUILDER),
 _ETYPE.RECEIVED_DAMAGE: makeReceivedDamageBuilder(vehicleBuilder=_EPIC_VEHICLE_VO_BUILDER, shellBuilder=EMPTY_SHELL_VO_BUILDER),
 _ETYPE.BLOCKED_DAMAGE: makeBlockedDamageBuilder(vehicleBuilder=_EPIC_VEHICLE_VO_BUILDER, shellBuilder=EMPTY_SHELL_VO_BUILDER),
 _ETYPE.ASSIST_DAMAGE: makeAssistDamageBuilder(vehicleBuilder=_EPIC_VEHICLE_VO_BUILDER),
 _ETYPE.RECEIVED_CRITICAL_HITS: makeReceivedCriticalHitsBuilder(vehicleBuilder=_EPIC_VEHICLE_VO_BUILDER, shellBuilder=EMPTY_SHELL_VO_BUILDER),
 _ETYPE.STUN: makeStunBuilder(vehicleBuilder=_EPIC_VEHICLE_VO_BUILDER)}

class EpicLogViewComponent(LogViewComponent):

    def _buildLogMessageVO(self, info):
        vType = self._arenaDP.getVehicleInfo(info.getArenaVehicleID()).vehicleType
        if Supply.isSupply(vType.tags):
            builder = _SUPPLY_ETYPE_TO_RECORD_VO_BUILDER[info.getType()]
            return builder.buildVO(info, self._arenaDP)
        return super(EpicLogViewComponent, self)._buildLogMessageVO(info)
