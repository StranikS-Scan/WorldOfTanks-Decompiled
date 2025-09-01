# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/damage_log_panel.py
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.battle.shared.damage_log_panel import DamageLogPanel, _LogViewComponent, _DamageActionImgVOBuilder, _LogRecordVOBuilder, _VehicleVOBuilder, _EMPTY_SHELL_VO_BUILDER, _DAMAGE_VALUE_VO_BUILDER, _ReceivedHitVehicleVOBuilder, _DamageShellVOBuilder, _ShellVOBuilder, _CritsShellVOBuilder, _CriticalHitValueVOBuilder, _ActionImgVOBuilder, _AssistActionImgVOBuilder
from gui.battle_control.battle_constants import PERSONAL_EFFICIENCY_TYPE as _ETYPE
from gui.Scaleform.genConsts.BATTLEDAMAGELOG_IMAGES import BATTLEDAMAGELOG_IMAGES as _IMAGES
from last_stand.gui.scaleform.genConsts.LS_BATTLEDAMAGELOG_IMAGES import LS_BATTLEDAMAGELOG_IMAGES as _LS_IMAGES
from last_stand_common.last_stand_constants import ATTACK_REASON
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from last_stand.gui.ls_vehicle_role_helper import getVehicleRole
_LS_VEHICLE_CLASS_TAGS_ICONS = {'sentry': _LS_IMAGES.LS_DAMAGELOG_SENTRY_16X16,
 'hunter': _LS_IMAGES.LS_DAMAGELOG_HUNTER_16X16,
 'runner': _LS_IMAGES.LS_DAMAGELOG_RUNNER_16X16,
 'alpha': _LS_IMAGES.LS_DAMAGELOG_ALPHA_16X16,
 'turret': _LS_IMAGES.LS_DAMAGELOG_TURRET_16X16,
 'bomber': _LS_IMAGES.LS_DAMAGELOG_BOMBER_16X16,
 'bomber_alpha': _LS_IMAGES.LS_DAMAGELOG_BOMBER_ALPHA_16X16,
 'catcher': _LS_IMAGES.LS_DAMAGELOG_CATCHER_16X16,
 'charger': _LS_IMAGES.LS_DAMAGELOG_CHARGER_16X16,
 'ripper': _LS_IMAGES.LS_DAMAGELOG_RIPPER_16X16,
 'detonator': _LS_IMAGES.LS_DAMAGELOG_DETONATOR_16X16,
 'boss': _LS_IMAGES.LS_DAMAGELOG_BOSS_16X16}

class LSReceivedHitVehicleVOBuilder(_ReceivedHitVehicleVOBuilder):

    def _populateVO(self, vehicleVO, info, arenaDP):
        super(LSReceivedHitVehicleVOBuilder, self)._populateVO(vehicleVO, info, arenaDP)
        if info.isStaticDeathZone():
            vehicleVO.vehicleName = backport.text(R.strings.last_stand_battle.damageLog.static_death_zone())
            vehicleVO.vehicleTypeImg = _IMAGES.DAMAGELOG_STATIC_DEATH_ZONE_16X16
            return
        elif info.isDeathZone():
            vehicleVO.vehicleName = backport.text(R.strings.last_stand_battle.damageLog.personal_death_zone())
            vehicleVO.vehicleTypeImg = _IMAGES.DAMAGELOG_STATIC_DEATH_ZONE_16X16
            return
        else:
            vInfo = arenaDP.getVehicleInfo(info.getArenaVehicleID())
            vehicleType = vInfo.vehicleType
            role = getVehicleRole(vehicleType)
            if role is not None:
                vehicleVO.vehicleTypeImg = _LS_VEHICLE_CLASS_TAGS_ICONS[role]
            if vInfo.isEnemy():
                vehicleVO.vehicleName = vehicleType.name
            return


class LSExtendedDamageActionVOBuilder(_DamageActionImgVOBuilder):
    DEFAULT_DAMAGE_ICON = _IMAGES.DAMAGELOG_DAMAGE_16X16
    LS_ATTACK_REASON_TO_ICON = {ATTACK_REASON.LS_ABILITY_VAMPIRE: _IMAGES.DAMAGELOG_DAMAGE_16X16,
     ATTACK_REASON.LS_ABILITY_AOE_DAMAGE: _IMAGES.DAMAGELOG_DAMAGE_16X16}

    def _getImage(self, info):
        img = self._getIcon(info.getAttackReasonID())
        return img or super(LSExtendedDamageActionVOBuilder, self)._getImage(info)

    @classmethod
    def _getIcon(cls, reasonID):
        attackReason = ATTACK_REASON.getValue(reasonID)
        res = cls.LS_ATTACK_REASON_TO_ICON.get(attackReason)
        if not res and attackReason in ATTACK_REASON.getExtraAttrs().itervalues():
            res = cls.DEFAULT_DAMAGE_ICON
        return res


class LSExtendedReceivedDamageActionVOBuilder(LSExtendedDamageActionVOBuilder):
    DEFAULT_DAMAGE_ICON = _IMAGES.DAMAGELOG_DAMAGE_ENEMY_16X16
    LS_ATTACK_REASON_TO_ICON = {ATTACK_REASON.LS_BOMBER_EXPLOSION: _IMAGES.DAMAGELOG_DAMAGE_ENEMY_16X16,
     ATTACK_REASON.LS_ABILITY_VAMPIRE: _IMAGES.DAMAGELOG_DAMAGE_ENEMY_16X16,
     ATTACK_REASON.LS_ABILITY_AOE_DAMAGE: _IMAGES.DAMAGELOG_DAMAGE_ENEMY_16X16}


class LSVehicleVOBuilder(_VehicleVOBuilder):

    def _populateVO(self, vehicleVO, info, arenaDP):
        super(LSVehicleVOBuilder, self)._populateVO(vehicleVO, info, arenaDP)
        vInfo = arenaDP.getVehicleInfo(info.getArenaVehicleID())
        vehicleType = vInfo.vehicleType
        role = getVehicleRole(vehicleType)
        if role is not None:
            vehicleVO.vehicleTypeImg = _LS_VEHICLE_CLASS_TAGS_ICONS[role]
        if vInfo.isEnemy():
            vehicleVO.vehicleName = vehicleType.name
        return


_LS_ETYPE_TO_RECORD_VO_BUILDER = {_ETYPE.DAMAGE: _LogRecordVOBuilder(LSVehicleVOBuilder(), _EMPTY_SHELL_VO_BUILDER, _DAMAGE_VALUE_VO_BUILDER, LSExtendedDamageActionVOBuilder(shotIcon=_IMAGES.DAMAGELOG_DAMAGE_16X16, fireIcon=_IMAGES.DAMAGELOG_FIRE_16X16, ramIcon=_IMAGES.DAMAGELOG_RAM_16X16, wcIcon=_IMAGES.DAMAGELOG_ICON_WORLD_COLLISION, mineFieldIcon=_IMAGES.DAMAGELOG_MINE_FIELD_16X16, spawnBotDmgIcon=_IMAGES.DAMAGELOG_YOUR_SPAWNED_BOT_DMG_16X16, corrodingShotIcon=_IMAGES.DAMAGELOG_CORRODING_SHOT_16X16, fireCircleDmgIcon=_IMAGES.DAMAGELOG_FIRE_CIRCLE_16X16, clingBranderDmgIcon=_IMAGES.DAMAGELOG_CLING_BRANDER_16X16, thunderStrikeIcon=_IMAGES.DAMAGELOG_THUNDER_STRIKE_16X16, airstrikeIcon=_IMAGES.DAMAGELOG_AIRSTRIKE_EQ_16X16, artilleryIcon=_IMAGES.DAMAGELOG_ARTILLERY_EQ_16X16)),
 _ETYPE.RECEIVED_DAMAGE: _LogRecordVOBuilder(LSReceivedHitVehicleVOBuilder(), _DamageShellVOBuilder(), _DAMAGE_VALUE_VO_BUILDER, LSExtendedReceivedDamageActionVOBuilder(shotIcon=_IMAGES.DAMAGELOG_DAMAGE_ENEMY_16X16, fireIcon=_IMAGES.DAMAGELOG_BURN_ENEMY_16X16, ramIcon=_IMAGES.DAMAGELOG_RAM_ENEMY_16X16, wcIcon=_IMAGES.DAMAGELOG_DAMAGE_ENEMY_16X16, mineFieldIcon=_IMAGES.DAMAGELOG_BY_MINE_FIELD_16X16, berserkerIcon=_IMAGES.DAMAGELOG_BERSERKER_16X16, spawnBotDmgIcon=_IMAGES.DAMAGELOG_DMG_BY_SPAWNED_BOT_16X16, smokeDmgIcon=_IMAGES.DAMAGELOG_DMG_BY_SMOKE_16X16, corrodingShotIcon=_IMAGES.DAMAGELOG_CORRODING_SHOT_ENEMY_16X16, fireCircleDmgIcon=_IMAGES.DAMAGELOG_FIRE_CIRCLE_ENEMY_16X16, clingBranderDmgIcon=_IMAGES.DAMAGELOG_CLING_BRANDER_ENEMY_16X16, thunderStrikeIcon=_IMAGES.DAMAGELOG_THUNDER_STRIKE_ENEMY_16X16, airstrikeIcon=_IMAGES.DAMAGELOG_AIRSTRIKE_EQ_ENEMY_16X16, artilleryIcon=_IMAGES.DAMAGELOG_ARTILLERY_EQ_ENEMY_16X16, airstrikeZoneIcon=_IMAGES.DAMAGELOG_AIRSTRIKE_ENEMY_16X16, deathZoneIcon=_IMAGES.DAMAGELOG_ARTILLERY_ENEMY_16X16)),
 _ETYPE.BLOCKED_DAMAGE: _LogRecordVOBuilder(LSVehicleVOBuilder(), _ShellVOBuilder(), _DAMAGE_VALUE_VO_BUILDER, _ActionImgVOBuilder(image=_IMAGES.DAMAGELOG_REFLECT_16X16)),
 _ETYPE.ASSIST_DAMAGE: _LogRecordVOBuilder(LSVehicleVOBuilder(), _EMPTY_SHELL_VO_BUILDER, _DAMAGE_VALUE_VO_BUILDER, _AssistActionImgVOBuilder()),
 _ETYPE.RECEIVED_CRITICAL_HITS: _LogRecordVOBuilder(LSReceivedHitVehicleVOBuilder(), _CritsShellVOBuilder(), _CriticalHitValueVOBuilder(), _ActionImgVOBuilder(image=_IMAGES.DAMAGELOG_CRITICAL_ENEMY_16X16))}

class _LSLogViewComponent(_LogViewComponent):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def updateViewMode(self, viewMode):
        if viewMode != self._logViewMode:
            self._logViewMode = viewMode
            self.invalidate()

    def _buildLogMessageVO(self, info):
        builder = _LS_ETYPE_TO_RECORD_VO_BUILDER.get(info.getType(), None)
        return builder.buildVO(info, self.sessionProvider.getArenaDP()) if builder is not None else super(_LSLogViewComponent, self)._buildLogMessageVO(info)


class LSDamageLogPanel(DamageLogPanel):

    def __init__(self):
        super(LSDamageLogPanel, self).__init__()
        self._topLog = _LSLogViewComponent()
        self._bottomLog = _LSLogViewComponent()
        self.__vehStateCtrl = self.sessionProvider.shared.vehicleState

    def _onVehicleControlling(self, vehicle):
        if not self.__vehStateCtrl.isInPostmortem:
            self._invalidatePanelVisibility()
        self._invalidateTotalDamages()
