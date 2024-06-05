# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/damage_log_panel.py
from gui.impl import backport
from helpers import dependency
from gui.Scaleform.daapi.view.battle.shared.damage_log_panel import DamageLogPanel, _LogViewComponent, _DamageActionImgVOBuilder, _LogRecordVOBuilder, _EMPTY_SHELL_VO_BUILDER, _DAMAGE_VALUE_VO_BUILDER, _VehicleVOBuilder, _DamageShellVOBuilder, _ReceivedHitVehicleVOBuilder
from gui.battle_control.battle_constants import PERSONAL_EFFICIENCY_TYPE as _ETYPE
from gui.impl.gen import R
from gui.Scaleform.genConsts.BATTLEDAMAGELOG_IMAGES import BATTLEDAMAGELOG_IMAGES as _IMAGES
from PlayerEvents import g_playerEvents
from skeletons.gui.battle_session import IBattleSessionProvider

class StoryModeExtendedDamageActionVOBuilder(_DamageActionImgVOBuilder):

    def _getImage(self, info):
        return _IMAGES.DAMAGELOG_ARTILLERY_16X16 if info.isBattleshipStrike() or info.isDestroyerStrike() else super(StoryModeExtendedDamageActionVOBuilder, self)._getImage(info)


class StoryModeExtendedReceivedDamageActionVOBuilder(_DamageActionImgVOBuilder):

    def _getImage(self, info):
        return _IMAGES.DAMAGELOG_BY_MINE_FIELD_16X16 if info.isMinefieldZone() else super(StoryModeExtendedReceivedDamageActionVOBuilder, self)._getImage(info)


class StoryModeVehicleVOBuilder(_VehicleVOBuilder):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _populateVO(self, vehicleVO, info, arenaDP):
        super(StoryModeVehicleVOBuilder, self)._populateVO(vehicleVO, info, arenaDP)
        destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
        if destructibleComponent and destructibleComponent.getDestructibleEntity(info.getArenaVehicleID()):
            vehicleVO.vehicleTypeImg = _IMAGES.WHITE_ICON_BUNKER_16X16
            vehicleVO.vehicleName = backport.text(R.strings.sm_battle.bunker())
        return


_STORY_MODE_ETYPE_TO_RECORD_VO_BUILDER = {_ETYPE.DAMAGE: _LogRecordVOBuilder(StoryModeVehicleVOBuilder(), _EMPTY_SHELL_VO_BUILDER, _DAMAGE_VALUE_VO_BUILDER, StoryModeExtendedDamageActionVOBuilder(shotIcon=_IMAGES.DAMAGELOG_DAMAGE_16X16, fireIcon=_IMAGES.DAMAGELOG_FIRE_16X16, ramIcon=_IMAGES.DAMAGELOG_RAM_16X16, wcIcon=_IMAGES.DAMAGELOG_ICON_WORLD_COLLISION, mineFieldIcon=_IMAGES.DAMAGELOG_MINE_FIELD_16X16, spawnBotDmgIcon=_IMAGES.DAMAGELOG_YOUR_SPAWNED_BOT_DMG_16X16, corrodingShotIcon=_IMAGES.DAMAGELOG_CORRODING_SHOT_16X16, fireCircleDmgIcon=_IMAGES.DAMAGELOG_FIRE_CIRCLE_16X16, clingBranderDmgIcon=_IMAGES.DAMAGELOG_CLING_BRANDER_16X16, thunderStrikeIcon=_IMAGES.DAMAGELOG_THUNDER_STRIKE_16X16, airstrikeIcon=_IMAGES.DAMAGELOG_AIRSTRIKE_EQ_16X16, artilleryIcon=_IMAGES.DAMAGELOG_ARTILLERY_EQ_16X16, battleshipIcon=_IMAGES.DAMAGELOG_ARTILLERY_16X16, destroyerIcon=_IMAGES.DAMAGELOG_ARTILLERY_16X16)),
 _ETYPE.RECEIVED_DAMAGE: _LogRecordVOBuilder(_ReceivedHitVehicleVOBuilder(), _DamageShellVOBuilder(), _DAMAGE_VALUE_VO_BUILDER, StoryModeExtendedReceivedDamageActionVOBuilder(shotIcon=_IMAGES.DAMAGELOG_DAMAGE_ENEMY_16X16, fireIcon=_IMAGES.DAMAGELOG_BURN_ENEMY_16X16, ramIcon=_IMAGES.DAMAGELOG_RAM_ENEMY_16X16, wcIcon=_IMAGES.DAMAGELOG_DAMAGE_ENEMY_16X16, mineFieldIcon=_IMAGES.DAMAGELOG_BY_MINE_FIELD_16X16, berserkerIcon=_IMAGES.DAMAGELOG_BERSERKER_16X16, spawnBotDmgIcon=_IMAGES.DAMAGELOG_DMG_BY_SPAWNED_BOT_16X16, smokeDmgIcon=_IMAGES.DAMAGELOG_DMG_BY_SMOKE_16X16, corrodingShotIcon=_IMAGES.DAMAGELOG_CORRODING_SHOT_ENEMY_16X16, fireCircleDmgIcon=_IMAGES.DAMAGELOG_FIRE_CIRCLE_ENEMY_16X16, clingBranderDmgIcon=_IMAGES.DAMAGELOG_CLING_BRANDER_ENEMY_16X16, thunderStrikeIcon=_IMAGES.DAMAGELOG_THUNDER_STRIKE_ENEMY_16X16, airstrikeIcon=_IMAGES.DAMAGELOG_AIRSTRIKE_EQ_ENEMY_16X16, artilleryIcon=_IMAGES.DAMAGELOG_ARTILLERY_EQ_ENEMY_16X16, airstrikeZoneIcon=_IMAGES.DAMAGELOG_AIRSTRIKE_ENEMY_16X16, deathZoneIcon=_IMAGES.DAMAGELOG_ARTILLERY_ENEMY_16X16, battleshipIcon=_IMAGES.DAMAGELOG_ARTILLERY_ENEMY_16X16, destroyerIcon=_IMAGES.DAMAGELOG_ARTILLERY_ENEMY_16X16))}

class _StoryModeLogViewComponent(_LogViewComponent):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def updateViewMode(self, viewMode):
        if viewMode != self._logViewMode:
            self._logViewMode = viewMode
            self.invalidate()

    def _buildLogMessageVO(self, info):
        builder = _STORY_MODE_ETYPE_TO_RECORD_VO_BUILDER.get(info.getType(), None)
        return builder.buildVO(info, self.sessionProvider.getArenaDP()) if builder is not None else super(_StoryModeLogViewComponent, self)._buildLogMessageVO(info)


class StoryModeDamageLogPanel(DamageLogPanel):

    def __init__(self):
        super(StoryModeDamageLogPanel, self).__init__()
        self._topLog = _StoryModeLogViewComponent()
        self._bottomLog = _StoryModeLogViewComponent()
        self.__vehStateCtrl = self.sessionProvider.shared.vehicleState

    def _populate(self):
        super(StoryModeDamageLogPanel, self)._populate()
        g_playerEvents.onRoundFinished += self.__onRoundFinished

    def _dispose(self):
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        super(StoryModeDamageLogPanel, self)._dispose()

    def __onRoundFinished(self, winnerTeam, reason):
        self._isWinnerScreenShown = True
