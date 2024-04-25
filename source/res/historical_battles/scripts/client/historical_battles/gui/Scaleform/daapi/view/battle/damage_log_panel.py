# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/damage_log_panel.py
from typing import TYPE_CHECKING, Any
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.damage_log_panel import DamageLogPanel, _LogViewComponent, _EMPTY_SHELL_VO_BUILDER, _LogRecordVOBuilder, _DamageActionImgVOBuilder, _DAMAGE_VALUE_VO_BUILDER, _DamageShellVOBuilder, _VehicleVOBuilder, _ShellVOBuilder, _ActionImgVOBuilder, _AssistActionImgVOBuilder, _CritsShellVOBuilder, _CriticalHitValueVOBuilder
from gui.battle_control.battle_constants import PERSONAL_EFFICIENCY_TYPE as _ETYPE
from gui.Scaleform.genConsts.HBBATTLEDAMAGELOG_IMAGES import HBBATTLEDAMAGELOG_IMAGES as _HB_IMAGES
from gui.Scaleform.genConsts.BATTLEDAMAGELOG_IMAGES import BATTLEDAMAGELOG_IMAGES as _IMAGES
if TYPE_CHECKING:
    from gui.battle_control.controllers.personal_efficiency_ctrl import _DamageEfficiencyInfo, _EfficiencyInfo

class _HistoricalBattlesDamageActionImgVOBuilder(_DamageActionImgVOBuilder):

    def _getImage(self, info):
        if info.isDeathZone():
            return _HB_IMAGES.DAMAGELOG_BY_ARTILLERY_FIELD_16X16
        if info.isPersonalDeathZone():
            return _HB_IMAGES.DAMAGELOG_BY_ARTILLERY_FIELD_16X16
        if info.isBomberEqDamage():
            return _HB_IMAGES.DAMAGELOG_AIRSTRIKE_TEAM_16X16
        if info.isArtilleryEqDamage():
            return _HB_IMAGES.DAMAGELOG_ARTILLERY_TEAM_16X16
        if info.isArtilleryRocketDamage():
            return _HB_IMAGES.DAMAGELOG_ARTILLERY_TEAM_16X16
        if info.isArtilleryMortarDamage():
            return _HB_IMAGES.DAMAGELOG_ARTILLERY_TEAM_16X16
        return _HB_IMAGES.DAMAGELOG_BOMBERCAS_TEAM_16X16 if info.isBombercasDamage() else super(_HistoricalBattlesDamageActionImgVOBuilder, self)._getImage(info)


class _HistoricalBattlesLogViewComponent(_LogViewComponent):

    def _buildLogMessageVO(self, info):
        builder = _ETYPE_TO_RECORD_VO_BUILDER.get(info.getType(), None)
        return builder.buildVO(info, self._LogViewComponent__arenaDP) if builder is not None else super(_HistoricalBattlesLogViewComponent, self)._buildLogMessageVO(info)


class _HistoricalBattlesVehicleVOBuilder(_VehicleVOBuilder):

    def _populateVO(self, vehicleVO, info, arenaDP):
        super(_HistoricalBattlesVehicleVOBuilder, self)._populateVO(vehicleVO, info, arenaDP)
        vehicleId = info.getArenaVehicleID()
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            role = arena.arenaInfo.vehicleRoleArenaComponent.getRole(vehicleId)
            if role:
                vehicleVO.vehicleTypeImg = arena.arenaInfo.vehicleRoleArenaComponent.getDamageLogIcon(vehicleId)
        return


class _HistoricalBattlesReceivedHitVehicleVOBuilder(_HistoricalBattlesVehicleVOBuilder):

    def _populateVO(self, vehicleVO, info, arenaDP):
        super(_HistoricalBattlesReceivedHitVehicleVOBuilder, self)._populateVO(vehicleVO, info, arenaDP)
        if info.getArenaVehicleID() == arenaDP.getPlayerVehicleID() and info.isRam():
            vehicleVO.vehicleName = ''
            vehicleVO.vehicleTypeImg = ''
        if info.isDeathZone():
            vehicleVO.vehicleName = ''
            vehicleVO.vehicleTypeImg = ''
        if info.isDamagingSmoke():
            vehicleVO.vehicleName = ''
            vehicleVO.vehicleTypeImg = ''
        if info.isProtectionZoneDamage() or info.isProtectionZoneDamage(primary=False) or info.isArtilleryEqDamage() or info.isArtilleryEqDamage(primary=False):
            vehicleVO.vehicleName = ''
            vehicleVO.vehicleTypeImg = _IMAGES.DAMAGELOG_ARTILLERY_16X16
        elif info.isBombersDamage() or info.isBombersDamage(primary=False) or info.isBomberEqDamage() or info.isBomberEqDamage(primary=False):
            vehicleVO.vehicleName = ''
            vehicleVO.vehicleTypeImg = _IMAGES.DAMAGELOG_AIRSTRIKE_ENEMY_16X16


_DEFAULT_HB_VEHICLE_VO_BUILDER = _HistoricalBattlesVehicleVOBuilder()

class HBDamageShellVOBuilder(_DamageShellVOBuilder):

    def buildVO(self, info, arenaDP):
        if info.isShot() or info.isFire():
            shellVOBuilder = _ShellVOBuilder()
        else:
            shellVOBuilder = _EMPTY_SHELL_VO_BUILDER
        return shellVOBuilder.buildVO(info, arenaDP)


_ETYPE_TO_RECORD_VO_BUILDER = {_ETYPE.DAMAGE: _LogRecordVOBuilder(_DEFAULT_HB_VEHICLE_VO_BUILDER, _EMPTY_SHELL_VO_BUILDER, _DAMAGE_VALUE_VO_BUILDER, _HistoricalBattlesDamageActionImgVOBuilder(shotIcon=_IMAGES.DAMAGELOG_DAMAGE_16X16, fireIcon=_IMAGES.DAMAGELOG_FIRE_16X16, ramIcon=_IMAGES.DAMAGELOG_RAM_16X16, wcIcon=_IMAGES.DAMAGELOG_ICON_WORLD_COLLISION, mineFieldIcon=_IMAGES.DAMAGELOG_MINE_FIELD_16X16, spawnBotDmgIcon=_IMAGES.DAMAGELOG_YOUR_SPAWNED_BOT_DMG_16X16, airstrikeIcon=_IMAGES.DAMAGELOG_AIRSTRIKE_ENEMY_16X16, artilleryIcon=_IMAGES.DAMAGELOG_ARTILLERY_ENEMY_16X16)),
 _ETYPE.RECEIVED_DAMAGE: _LogRecordVOBuilder(_HistoricalBattlesReceivedHitVehicleVOBuilder(), HBDamageShellVOBuilder(), _DAMAGE_VALUE_VO_BUILDER, _HistoricalBattlesDamageActionImgVOBuilder(shotIcon=_IMAGES.DAMAGELOG_DAMAGE_ENEMY_16X16, fireIcon=_IMAGES.DAMAGELOG_BURN_ENEMY_16X16, ramIcon=_IMAGES.DAMAGELOG_RAM_ENEMY_16X16, wcIcon=_IMAGES.DAMAGELOG_DAMAGE_ENEMY_16X16, mineFieldIcon=_IMAGES.DAMAGELOG_BY_MINE_FIELD_16X16, berserkerIcon=_IMAGES.DAMAGELOG_BERSERKER_16X16, spawnBotDmgIcon=_IMAGES.DAMAGELOG_DMG_BY_SPAWNED_BOT_16X16, smokeDmgIcon=_IMAGES.DAMAGELOG_DMG_BY_SMOKE_16X16, airstrikeIcon=_IMAGES.DAMAGELOG_AIRSTRIKE_ENEMY_16X16, artilleryIcon=_IMAGES.DAMAGELOG_ARTILLERY_ENEMY_16X16)),
 _ETYPE.BLOCKED_DAMAGE: _LogRecordVOBuilder(_DEFAULT_HB_VEHICLE_VO_BUILDER, _ShellVOBuilder(), _DAMAGE_VALUE_VO_BUILDER, _ActionImgVOBuilder(image=_IMAGES.DAMAGELOG_REFLECT_16X16)),
 _ETYPE.ASSIST_DAMAGE: _LogRecordVOBuilder(_DEFAULT_HB_VEHICLE_VO_BUILDER, _EMPTY_SHELL_VO_BUILDER, _DAMAGE_VALUE_VO_BUILDER, _AssistActionImgVOBuilder()),
 _ETYPE.RECEIVED_CRITICAL_HITS: _LogRecordVOBuilder(_HistoricalBattlesReceivedHitVehicleVOBuilder(), _CritsShellVOBuilder(), _CriticalHitValueVOBuilder(), _ActionImgVOBuilder(image=_IMAGES.DAMAGELOG_CRITICAL_ENEMY_16X16)),
 _ETYPE.STUN: _LogRecordVOBuilder(_DEFAULT_HB_VEHICLE_VO_BUILDER, _EMPTY_SHELL_VO_BUILDER, _DAMAGE_VALUE_VO_BUILDER, _ActionImgVOBuilder(image=_IMAGES.DAMAGELOG_STUN_16X16))}

class HistoricalBattlesDamageLogPanel(DamageLogPanel):

    def __init__(self):
        super(HistoricalBattlesDamageLogPanel, self).__init__()
        self._topLog = _HistoricalBattlesLogViewComponent()
        self._bottomLog = _HistoricalBattlesLogViewComponent()
