# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/damage_log_panel.py
from collections import defaultdict
from BattleFeedbackCommon import BATTLE_EVENT_TYPE as _BET
from account_helpers.settings_core.options import DamageLogDetailsSetting as _VIEW_MODE, DamageLogEventPositionsSetting as _EVENT_POSITIONS, DamageLogEventTypesSetting as _DISPLAYED_EVENT_TYPES
from account_helpers.settings_core.settings_constants import DAMAGE_LOG, GRAPHICS
from constants import BATTLE_LOG_SHELL_TYPES, BOT_DISPLAY_CLASS_NAMES, VEHICLE_BUNKER_TURRET_TAG
from gui.Scaleform.daapi.view.meta.BattleDamageLogPanelMeta import BattleDamageLogPanelMeta
from gui.Scaleform.genConsts.BATTLEDAMAGELOG_IMAGES import BATTLEDAMAGELOG_IMAGES as _IMAGES
from gui.Scaleform.genConsts.DAMAGE_LOG_SHELL_BG_TYPES import DAMAGE_LOG_SHELL_BG_TYPES
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control.battle_constants import PERSONAL_EFFICIENCY_TYPE as _ETYPE
from gui.battle_control.controllers.personal_efficiency_ctrl import _DamageEfficiencyInfo
from gui.impl import backport
from gui.shared import events as gui_events, EVENT_BUS_SCOPE
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from helpers import dependency
from helpers import i18n
from shared_utils import BitmaskHelper
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
_POSITIVE_EVENTS_MASK = _ETYPE.DAMAGE | _ETYPE.ASSIST_DAMAGE | _ETYPE.STUN
_NEGATIVE_EVENTS_MASK = _ETYPE.BLOCKED_DAMAGE | _ETYPE.RECEIVED_DAMAGE | _ETYPE.RECEIVED_CRITICAL_HITS
_ALL_EVENTS_MASK = _POSITIVE_EVENTS_MASK | _NEGATIVE_EVENTS_MASK
_EVENT_POSITIONS_TO_CONTENT_MASK = {_EVENT_POSITIONS.ALL_BOTTOM: (0, _ALL_EVENTS_MASK),
 _EVENT_POSITIONS.NEGATIVE_AT_TOP: (_NEGATIVE_EVENTS_MASK, _POSITIVE_EVENTS_MASK)}

class _RECORD_STYLE(object):
    FULL = 0
    SHORT = 1


_EVENT_POSITIONS_TO_RECORD_STYLE = {_EVENT_POSITIONS.ALL_BOTTOM: {_DISPLAYED_EVENT_TYPES.ALL: (_RECORD_STYLE.FULL, _RECORD_STYLE.FULL),
                               _DISPLAYED_EVENT_TYPES.ONLY_NEGATIVE: (_RECORD_STYLE.FULL, _RECORD_STYLE.FULL),
                               _DISPLAYED_EVENT_TYPES.ONLY_POSITIVE: (_RECORD_STYLE.FULL, _RECORD_STYLE.SHORT)},
 _EVENT_POSITIONS.NEGATIVE_AT_TOP: {_DISPLAYED_EVENT_TYPES.ALL: (_RECORD_STYLE.FULL, _RECORD_STYLE.SHORT),
                                    _DISPLAYED_EVENT_TYPES.ONLY_NEGATIVE: (_RECORD_STYLE.FULL, _RECORD_STYLE.SHORT),
                                    _DISPLAYED_EVENT_TYPES.ONLY_POSITIVE: (_RECORD_STYLE.FULL, _RECORD_STYLE.SHORT)}}
_DISPLAYED_EVENT_TYPES_TO_CONTENT_MASK = {_DISPLAYED_EVENT_TYPES.ALL: _ALL_EVENTS_MASK,
 _DISPLAYED_EVENT_TYPES.ONLY_NEGATIVE: _NEGATIVE_EVENTS_MASK,
 _DISPLAYED_EVENT_TYPES.ONLY_POSITIVE: _POSITIVE_EVENTS_MASK}
_TOTAL_DAMAGE_SETTINGS_TO_CONTENT_MASK = {DAMAGE_LOG.TOTAL_DAMAGE: _ETYPE.DAMAGE,
 DAMAGE_LOG.ASSIST_DAMAGE: _ETYPE.ASSIST_DAMAGE,
 DAMAGE_LOG.BLOCKED_DAMAGE: _ETYPE.BLOCKED_DAMAGE,
 DAMAGE_LOG.ASSIST_STUN: _ETYPE.STUN}
_LOGS_SETTINGS = (DAMAGE_LOG.SHOW_DETAILS, DAMAGE_LOG.EVENT_POSITIONS, DAMAGE_LOG.SHOW_EVENT_TYPES)
_VEHICLE_CLASS_TAGS_ICONS = {VEHICLE_CLASS_NAME.LIGHT_TANK: _IMAGES.WHITE_ICON_LIGHTTANK_16X16,
 VEHICLE_CLASS_NAME.MEDIUM_TANK: _IMAGES.WHITE_ICON_MEDIUM_TANK_16X16,
 VEHICLE_CLASS_NAME.HEAVY_TANK: _IMAGES.WHITE_ICON_HEAVYTANK_16X16,
 VEHICLE_CLASS_NAME.SPG: _IMAGES.WHITE_ICON_SPG_16X16,
 VEHICLE_CLASS_NAME.AT_SPG: _IMAGES.WHITE_ICON_AT_SPG_16X16,
 BOT_DISPLAY_CLASS_NAMES.LIGHT_TANK_ELITE.value: _IMAGES.WHITE_ICON_LIGHTTANK_ELITE_16X16,
 BOT_DISPLAY_CLASS_NAMES.MEDIUM_TANK_ELITE.value: _IMAGES.WHITE_ICON_MEDIUM_TANK_ELITE_16X16,
 BOT_DISPLAY_CLASS_NAMES.HEAVY_TANK_ELITE.value: _IMAGES.WHITE_ICON_HEAVYTANK_ELITE_16X16,
 BOT_DISPLAY_CLASS_NAMES.SPG_ELITE.value: _IMAGES.WHITE_ICON_SPG_ELITE_16X16,
 BOT_DISPLAY_CLASS_NAMES.AT_SPG_ELITE.value: _IMAGES.WHITE_ICON_AT_SPG_ELITE_16X16,
 BOT_DISPLAY_CLASS_NAMES.BOSS.value: _IMAGES.WHITE_ICON_BOSS_16X16}
_SHELL_TYPES_TO_STR = {BATTLE_LOG_SHELL_TYPES.ARMOR_PIERCING: INGAME_GUI.DAMAGELOG_SHELLTYPE_ARMOR_PIERCING,
 BATTLE_LOG_SHELL_TYPES.ARMOR_PIERCING_HE: INGAME_GUI.DAMAGELOG_SHELLTYPE_ARMOR_PIERCING_HE,
 BATTLE_LOG_SHELL_TYPES.ARMOR_PIERCING_CR: INGAME_GUI.DAMAGELOG_SHELLTYPE_ARMOR_PIERCING_CR,
 BATTLE_LOG_SHELL_TYPES.HOLLOW_CHARGE: INGAME_GUI.DAMAGELOG_SHELLTYPE_HOLLOW_CHARGE,
 BATTLE_LOG_SHELL_TYPES.HE_MODERN: INGAME_GUI.DAMAGELOG_SHELLTYPE_HIGH_EXPLOSIVE,
 BATTLE_LOG_SHELL_TYPES.HE_LEGACY_STUN: INGAME_GUI.DAMAGELOG_SHELLTYPE_HIGH_EXPLOSIVE,
 BATTLE_LOG_SHELL_TYPES.HE_LEGACY_NO_STUN: INGAME_GUI.DAMAGELOG_SHELLTYPE_HIGH_EXPLOSIVE}
HIDDEN_SHELL = ''

def _formatTotalValue(value):
    return backport.getIntegralFormat(value)


class _VOModel(dict):
    pass


class _VOModelProperty(object):
    __slots__ = ('name',)

    def __init__(self, name):
        self.name = name

    def __get__(self, model, objtype):
        return model[self.name]

    def __set__(self, model, val):
        model[self.name] = val


class _IVOBuilder(object):

    def buildVO(self, info, arenaDP):
        raise NotImplementedError


class _LogRecordVOBuilder(_IVOBuilder):

    def __init__(self, *builders):
        super(_LogRecordVOBuilder, self).__init__()
        self.__builders = builders

    def buildVO(self, info, arenaDP):
        if isinstance(info, _DamageEfficiencyInfo) and info.isHidden():
            return None
        else:
            vo = {}
            for b in self.__builders:
                vo.update(b.buildVO(info, arenaDP))

            return vo


class _VehicleVOModel(_VOModel):
    vehicleTypeImg = _VOModelProperty(name='vehicleTypeImg')
    vehicleName = _VOModelProperty(name='vehicleName')

    def __init__(self, vehicleTypeImg='', vehicleName=''):
        super(_VehicleVOModel, self).__init__()
        self.vehicleTypeImg = vehicleTypeImg
        self.vehicleName = vehicleName


class _VehicleVOBuilder(_IVOBuilder):

    def buildVO(self, info, arenaDP):
        vo = _VehicleVOModel()
        if arenaDP is not None:
            self._populateVO(vo, info, arenaDP)
        return vo

    def _populateVO(self, vehicleVO, info, arenaDP):
        vInfoVO = arenaDP.getVehicleInfo(info.getArenaVehicleID())
        if VEHICLE_BUNKER_TURRET_TAG in vInfoVO.vehicleType.tags:
            vehicleVO.vehicleTypeImg = _IMAGES.WHITE_ICON_BUNKER_16X16
        else:
            vehicleVO.vehicleTypeImg = _VEHICLE_CLASS_TAGS_ICONS.get(vInfoVO.getDisplayedClassTag(), '')
        vehicleVO.vehicleName = vInfoVO.getDisplayedName()


class _ReceivedHitVehicleVOBuilder(_VehicleVOBuilder):

    def _populateVO(self, vehicleVO, info, arenaDP):
        super(_ReceivedHitVehicleVOBuilder, self)._populateVO(vehicleVO, info, arenaDP)
        if info.getArenaVehicleID() == arenaDP.getPlayerVehicleID() and info.isRam():
            vehicleVO.vehicleName = ''
            vehicleVO.vehicleTypeImg = ''
        if info.isDeathZone() or info.isStaticDeathZone() or info.isMinefieldZone():
            vehicleVO.vehicleName = ''
            vehicleVO.vehicleTypeImg = ''
        if info.isDamagingSmoke():
            vehicleVO.vehicleName = ''
            vehicleVO.vehicleTypeImg = ''
        if info.isProtectionZoneDamage() or info.isProtectionZoneDamage(primary=False):
            vehicleVO.vehicleName = ''
            vehicleVO.vehicleTypeImg = ''
        elif info.isBombersDamage() or info.isBombersDamage(primary=False):
            vehicleVO.vehicleName = ''
            vehicleVO.vehicleTypeImg = ''
        elif info.isFortArtilleryEqDamage() or info.isFortArtilleryEqDamage(primary=False):
            vehicleVO.vehicleName = ''
            vehicleVO.vehicleTypeImg = _IMAGES.DAMAGELOG_FORT_ARTILLERY_16X16


class _ShellVOModel(_VOModel):
    shellTypeStr = _VOModelProperty(name='shellTypeStr')
    shellTypeBG = _VOModelProperty(name='shellTypeBG')

    def __init__(self, shellTypeStr='', shellTypeBG=''):
        super(_ShellVOModel, self).__init__()
        self.shellTypeStr = shellTypeStr
        self.shellTypeBG = shellTypeBG


class _ShellVOBuilder(_IVOBuilder):

    def buildVO(self, info, arenaDP):
        return _ShellVOModel(self._getShellTypeStr(info), self._getShellTypeBg(info, arenaDP))

    def _getShellTypeStr(self, info):
        shType = info.getShellType()
        return _SHELL_TYPES_TO_STR[shType] if shType is not None and shType in _SHELL_TYPES_TO_STR else ''

    def _getShellTypeBg(self, info, arenaDP=None):
        shellType = info.getShellType()
        if shellType is None or arenaDP is None:
            return DAMAGE_LOG_SHELL_BG_TYPES.EMPTY
        elif arenaDP.getVehicleInfo(info.getArenaVehicleID()).isSPG():
            if shellType in (BATTLE_LOG_SHELL_TYPES.HE_MODERN, BATTLE_LOG_SHELL_TYPES.HE_LEGACY_NO_STUN):
                return DAMAGE_LOG_SHELL_BG_TYPES.SPG_HE_NO_STUN
            return DAMAGE_LOG_SHELL_BG_TYPES.SPG
        else:
            return DAMAGE_LOG_SHELL_BG_TYPES.GOLD if info.isShellGold() else DAMAGE_LOG_SHELL_BG_TYPES.DEFAULT


class _EmptyShellVOBuilder(_ShellVOBuilder):

    def _getShellTypeStr(self, info):
        pass

    def _getShellTypeBg(self, info, arenaDP=None):
        return DAMAGE_LOG_SHELL_BG_TYPES.EMPTY


class _StaticDeathZoneVOBuilder(_ShellVOBuilder):

    def _getShellTypeStr(self, info):
        return HIDDEN_SHELL

    def _getShellTypeBg(self, info, arenaDP=None):
        return DAMAGE_LOG_SHELL_BG_TYPES.EMPTY


class _MinefieldZoneVOBuilder(_ShellVOBuilder):

    def _getShellTypeStr(self, info):
        return HIDDEN_SHELL

    def _getShellTypeBg(self, info, arenaDP=None):
        return DAMAGE_LOG_SHELL_BG_TYPES.EMPTY


class _EpicDeathZoneVOBuilder(_ShellVOBuilder):

    def _getShellTypeStr(self, info):
        return HIDDEN_SHELL

    def _getShellTypeBg(self, info, arenaDP=None):
        return HIDDEN_SHELL


class _DamageShellVOBuilder(_ShellVOBuilder):

    def buildVO(self, info, arenaDP):
        if info.isShot() or info.isFire():
            shellVOBuilder = _ShellVOBuilder()
        elif info.isStaticDeathZone():
            shellVOBuilder = _StaticDeathZoneVOBuilder()
        elif info.isMinefieldZone():
            shellVOBuilder = _MinefieldZoneVOBuilder()
        elif info.isProtectionZoneDamage() or info.isBombersDamage():
            shellVOBuilder = _EpicDeathZoneVOBuilder()
        else:
            shellVOBuilder = _EmptyShellVOBuilder()
        return shellVOBuilder.buildVO(info, arenaDP)


class _CritsShellVOBuilder(_ShellVOBuilder):

    def buildVO(self, info, arenaDP):
        if info.isShot() or info.isFire():
            shellVOBuilder = _ShellVOBuilder()
        elif info.isStaticDeathZone():
            shellVOBuilder = _StaticDeathZoneVOBuilder()
        elif info.isMinefieldZone():
            shellVOBuilder = _MinefieldZoneVOBuilder()
        elif info.isProtectionZoneDamage() or info.isBombersDamage():
            shellVOBuilder = _EpicDeathZoneVOBuilder()
        else:
            shellVOBuilder = _EmptyShellVOBuilder()
        return shellVOBuilder.buildVO(info, arenaDP)


class _ValueVOModel(_VOModel):
    value = _VOModelProperty(name='value')

    def __init__(self, value=0):
        super(_ValueVOModel, self).__init__()
        self.value = value


class _ValueVOBuilder(_IVOBuilder):

    def buildVO(self, info, arenaDP):
        return _ValueVOModel(self._getValue(info))

    def _getValue(self, info):
        pass


class _CriticalHitValueVOBuilder(_ValueVOBuilder):

    def _getValue(self, info):
        return i18n.makeString(INGAME_GUI.DAMAGELOG_MULTIPLIER, multiplier=str(info.getCritsCount()))


class _DamageValueVOBuilder(_ValueVOBuilder):

    def _getValue(self, info):
        return backport.getIntegralFormat(info.getDamage())


class _ActionImgVOModel(_VOModel):
    actionTypeImg = _VOModelProperty(name='actionTypeImg')

    def __init__(self, image=''):
        super(_ActionImgVOModel, self).__init__()
        self.actionTypeImg = image


class _ActionImgVOBuilder(_IVOBuilder):

    def __init__(self, image):
        super(_ActionImgVOBuilder, self).__init__()
        self._image = image

    def buildVO(self, info, arenaDP):
        return _ActionImgVOModel(self._getImage(info))

    def _getImage(self, info):
        return self._image


class _DamageActionImgVOBuilder(_ActionImgVOBuilder):
    __slots__ = ('__shotIcon', '__fireIcon', '__ramIcon', '__wcIcon', '__berserkerIcon', '__spawnBotDmgIcon', '__mineFieldIcon', '__smokeDmgIcon', '__corrodingShotDmgIcon', '__fireCircleDmgIcon', '__clingBranderDmgIcon', '__thunderStrikeIcon', '__airstrikeIcon', '__artilleryIcon', '__airstrikeZoneIcon', '__deathZoneIcon', '__battleshipIcon', '__destroyerIcon')

    def __init__(self, shotIcon, fireIcon, ramIcon, wcIcon, mineFieldIcon, airstrikeIcon, artilleryIcon, airstrikeZoneIcon=None, deathZoneIcon=None, berserkerIcon=None, spawnBotDmgIcon=None, smokeDmgIcon=None, corrodingShotIcon=None, fireCircleDmgIcon=None, clingBranderDmgIcon=None, thunderStrikeIcon=None, battleshipIcon=None, destroyerIcon=None):
        super(_DamageActionImgVOBuilder, self).__init__('')
        self.__shotIcon = shotIcon
        self.__fireIcon = fireIcon
        self.__ramIcon = ramIcon
        self.__wcIcon = wcIcon
        self.__berserkerIcon = berserkerIcon
        self.__spawnBotDmgIcon = spawnBotDmgIcon
        self.__mineFieldIcon = mineFieldIcon
        self.__smokeDmgIcon = smokeDmgIcon
        self.__corrodingShotDmgIcon = corrodingShotIcon
        self.__fireCircleDmgIcon = fireCircleDmgIcon
        self.__clingBranderDmgIcon = clingBranderDmgIcon
        self.__thunderStrikeIcon = thunderStrikeIcon
        self.__airstrikeIcon = airstrikeIcon
        self.__artilleryIcon = artilleryIcon
        self.__airstrikeZoneIcon = airstrikeZoneIcon
        self.__deathZoneIcon = deathZoneIcon
        self.__battleshipIcon = battleshipIcon
        self.__destroyerIcon = destroyerIcon

    def _getImage(self, info):
        if info.isClingBrander():
            return self.__clingBranderDmgIcon
        if info.isShot() or info.isDeathZone() or info.isFortArtilleryEqDamage() or info.isStaticDeathZone() or info.isMinefieldZone():
            return self.__shotIcon
        if info.isProtectionZoneDamage():
            return self.__deathZoneIcon
        if info.isBombersDamage():
            return self.__airstrikeZoneIcon
        if info.isFire():
            return self.__fireIcon
        if info.isBerserker():
            return self.__berserkerIcon
        if info.isSpawnedBotExplosion():
            return self.__spawnBotDmgIcon
        if info.isWorldCollision():
            return self.__wcIcon
        if info.isMinefield():
            return self.__mineFieldIcon
        if info.isArtilleryEqDamage():
            return self.__artilleryIcon
        if info.isBomberEqDamage():
            return self.__airstrikeIcon
        if info.isDamagingSmoke():
            return self.__smokeDmgIcon
        if info.isCorrodingShot():
            return self.__corrodingShotDmgIcon
        if info.isFireCircle():
            return self.__fireCircleDmgIcon
        if info.isThunderStrike():
            return self.__thunderStrikeIcon
        if info.isBattleshipStrike():
            return self.__battleshipIcon
        return self.__destroyerIcon if info.isDestroyerStrike() else self.__ramIcon


class _AssistActionImgVOBuilder(_ActionImgVOBuilder):

    def __init__(self):
        super(_AssistActionImgVOBuilder, self).__init__('')

    def _getImage(self, info):
        if info.getBattleEventType() == _BET.TRACK_ASSIST:
            return _IMAGES.DAMAGELOG_IMMOBILIZED_16X16
        return _IMAGES.DAMAGELOG_COORDINATE_16X16 if info.getBattleEventType() == _BET.RADIO_ASSIST else super(_AssistActionImgVOBuilder, self)._getImage(info)


_DEFAULT_VEHICLE_VO_BUILDER = _VehicleVOBuilder()
_EMPTY_SHELL_VO_BUILDER = _EmptyShellVOBuilder()
_DAMAGE_VALUE_VO_BUILDER = _DamageValueVOBuilder()
_ETYPE_TO_RECORD_VO_BUILDER = {_ETYPE.DAMAGE: _LogRecordVOBuilder(_DEFAULT_VEHICLE_VO_BUILDER, _EMPTY_SHELL_VO_BUILDER, _DAMAGE_VALUE_VO_BUILDER, _DamageActionImgVOBuilder(shotIcon=_IMAGES.DAMAGELOG_DAMAGE_16X16, fireIcon=_IMAGES.DAMAGELOG_FIRE_16X16, ramIcon=_IMAGES.DAMAGELOG_RAM_16X16, wcIcon=_IMAGES.DAMAGELOG_ICON_WORLD_COLLISION, mineFieldIcon=_IMAGES.DAMAGELOG_MINE_FIELD_16X16, spawnBotDmgIcon=_IMAGES.DAMAGELOG_YOUR_SPAWNED_BOT_DMG_16X16, corrodingShotIcon=_IMAGES.DAMAGELOG_CORRODING_SHOT_16X16, fireCircleDmgIcon=_IMAGES.DAMAGELOG_FIRE_CIRCLE_16X16, clingBranderDmgIcon=_IMAGES.DAMAGELOG_CLING_BRANDER_16X16, thunderStrikeIcon=_IMAGES.DAMAGELOG_THUNDER_STRIKE_16X16, airstrikeIcon=_IMAGES.DAMAGELOG_AIRSTRIKE_EQ_16X16, artilleryIcon=_IMAGES.DAMAGELOG_ARTILLERY_EQ_16X16, battleshipIcon=_IMAGES.DAMAGELOG_ARTILLERY_16X16, destroyerIcon=_IMAGES.DAMAGELOG_ARTILLERY_16X16)),
 _ETYPE.RECEIVED_DAMAGE: _LogRecordVOBuilder(_ReceivedHitVehicleVOBuilder(), _DamageShellVOBuilder(), _DAMAGE_VALUE_VO_BUILDER, _DamageActionImgVOBuilder(shotIcon=_IMAGES.DAMAGELOG_DAMAGE_ENEMY_16X16, fireIcon=_IMAGES.DAMAGELOG_BURN_ENEMY_16X16, ramIcon=_IMAGES.DAMAGELOG_RAM_ENEMY_16X16, wcIcon=_IMAGES.DAMAGELOG_DAMAGE_ENEMY_16X16, mineFieldIcon=_IMAGES.DAMAGELOG_BY_MINE_FIELD_16X16, berserkerIcon=_IMAGES.DAMAGELOG_BERSERKER_16X16, spawnBotDmgIcon=_IMAGES.DAMAGELOG_DMG_BY_SPAWNED_BOT_16X16, smokeDmgIcon=_IMAGES.DAMAGELOG_DMG_BY_SMOKE_16X16, corrodingShotIcon=_IMAGES.DAMAGELOG_CORRODING_SHOT_ENEMY_16X16, fireCircleDmgIcon=_IMAGES.DAMAGELOG_FIRE_CIRCLE_ENEMY_16X16, clingBranderDmgIcon=_IMAGES.DAMAGELOG_CLING_BRANDER_ENEMY_16X16, thunderStrikeIcon=_IMAGES.DAMAGELOG_THUNDER_STRIKE_ENEMY_16X16, airstrikeIcon=_IMAGES.DAMAGELOG_AIRSTRIKE_EQ_ENEMY_16X16, artilleryIcon=_IMAGES.DAMAGELOG_ARTILLERY_EQ_ENEMY_16X16, airstrikeZoneIcon=_IMAGES.DAMAGELOG_AIRSTRIKE_ENEMY_16X16, deathZoneIcon=_IMAGES.DAMAGELOG_ARTILLERY_ENEMY_16X16, battleshipIcon=_IMAGES.DAMAGELOG_ARTILLERY_ENEMY_16X16, destroyerIcon=_IMAGES.DAMAGELOG_ARTILLERY_ENEMY_16X16)),
 _ETYPE.BLOCKED_DAMAGE: _LogRecordVOBuilder(_DEFAULT_VEHICLE_VO_BUILDER, _ShellVOBuilder(), _DAMAGE_VALUE_VO_BUILDER, _ActionImgVOBuilder(image=_IMAGES.DAMAGELOG_REFLECT_16X16)),
 _ETYPE.ASSIST_DAMAGE: _LogRecordVOBuilder(_DEFAULT_VEHICLE_VO_BUILDER, _EMPTY_SHELL_VO_BUILDER, _DAMAGE_VALUE_VO_BUILDER, _AssistActionImgVOBuilder()),
 _ETYPE.RECEIVED_CRITICAL_HITS: _LogRecordVOBuilder(_ReceivedHitVehicleVOBuilder(), _CritsShellVOBuilder(), _CriticalHitValueVOBuilder(), _ActionImgVOBuilder(image=_IMAGES.DAMAGELOG_CRITICAL_ENEMY_16X16)),
 _ETYPE.STUN: _LogRecordVOBuilder(_DEFAULT_VEHICLE_VO_BUILDER, _EMPTY_SHELL_VO_BUILDER, _DAMAGE_VALUE_VO_BUILDER, _ActionImgVOBuilder(image=_IMAGES.DAMAGELOG_STUN_16X16))}

class _LogViewComponent(object):

    def __init__(self):
        super(_LogViewComponent, self).__init__()
        self.__setListProxy = None
        self.__addToListProxy = None
        self.__efficiencyCtrl = None
        self.__arenaDP = None
        self._logViewMode = _VIEW_MODE.SHOW_ALWAYS
        self.__isVisible = True
        self.__contentMask = 0
        self.__recordStyle = _RECORD_STYLE.FULL
        return

    def initialize(self, setListProxyMethod, addToListProxyMethod, efficiencyCtrl, arenaDP):
        self.__setListProxy = setListProxyMethod
        self.__addToListProxy = addToListProxyMethod
        self.__efficiencyCtrl = efficiencyCtrl
        self.__arenaDP = arenaDP

    def dispose(self):
        self.__setListProxy = None
        self.__addToListProxy = None
        self.__efficiencyCtrl = None
        self.__arenaDP = None
        return

    def clear(self):
        self.__setListProxy(self.__isVisible, bool(self.__recordStyle == _RECORD_STYLE.SHORT), [])

    def invalidate(self):
        if self._logViewMode == _VIEW_MODE.SHOW_ALWAYS:
            self.__isVisible = True
            messages = self._getLogMessages(self.__contentMask)
        elif self._logViewMode == _VIEW_MODE.SHOW_BY_ALT_PRESS:
            self.__isVisible = False
            messages = self._getLogMessages(self.__contentMask)
        else:
            self.__isVisible = False
            messages = []
        self.__setListProxy(self.__isVisible, bool(self.__recordStyle == _RECORD_STYLE.SHORT), messages)

    def updateLog(self, contentMask=None, viewMode=None, recordStyle=_RECORD_STYLE.FULL):
        needUpdate = False
        if viewMode != self._logViewMode:
            self._logViewMode = viewMode
            needUpdate = True
        if contentMask != self.__contentMask:
            self.__contentMask = contentMask
            needUpdate = True
        if recordStyle != self.__recordStyle:
            self.__recordStyle = recordStyle
            needUpdate = True
        if needUpdate:
            self.invalidate()

    def addToLog(self, events):
        if self._logViewMode == _VIEW_MODE.HIDE:
            return
        else:
            for e in events:
                if BitmaskHelper.hasAnyBitSet(self.__contentMask, e.getType()):
                    vo = self._buildLogMessageVO(e)
                    if vo is not None:
                        self.__addToListProxy(**vo)

            return

    def _getLogMessages(self, contentMask):
        if self.__efficiencyCtrl is not None:
            records = self.__efficiencyCtrl.getLoogedEfficiency(contentMask)
            return [ res for res in map(self._buildLogMessageVO, records) if res is not None ]
        else:
            return []

    def _buildLogMessageVO(self, info):
        builder = _ETYPE_TO_RECORD_VO_BUILDER[info.getType()]
        return builder.buildVO(info, self.__arenaDP)


class DamageLogPanel(BattleDamageLogPanelMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(DamageLogPanel, self).__init__()
        self.__efficiencyCtrl = None
        self.__arenaDP = self.sessionProvider.getArenaDP()
        self.__vehStateCtrl = self.sessionProvider.shared.vehicleState
        self._isVisible = False
        self._isFullStatsShown = False
        self._isWinnerScreenShown = False
        self._logViewMode = _VIEW_MODE.SHOW_ALWAYS
        self.__totalDamageContentMask = 0
        self.__totalValues = defaultdict(int)
        self._totalEvents = None
        self._topLog = _LogViewComponent()
        self._bottomLog = _LogViewComponent()
        return

    def isSwitchToVehicle(self):
        observedVehID = self.__vehStateCtrl.getControllingVehicleID()
        playerVehicleID = self.__arenaDP.getPlayerVehicleID()
        return playerVehicleID == observedVehID

    def _populate(self):
        super(DamageLogPanel, self)._populate()
        self.__efficiencyCtrl = self.sessionProvider.shared.personalEfficiencyCtrl
        self._topLog.initialize(setListProxyMethod=self._updateTopLog, addToListProxyMethod=self._addToTopLog, efficiencyCtrl=self.__efficiencyCtrl, arenaDP=self.__arenaDP)
        self._bottomLog.initialize(setListProxyMethod=self._updateBottomLog, addToListProxyMethod=self._addToBottomLog, efficiencyCtrl=self.__efficiencyCtrl, arenaDP=self.__arenaDP)
        self._totalEvents = ((_ETYPE.DAMAGE, self._updateTotalDamageValue),
         (_ETYPE.BLOCKED_DAMAGE, self._updateTotalBlockedDamageValue),
         (_ETYPE.ASSIST_DAMAGE, self._updateTotalAssistValue),
         (_ETYPE.STUN, self._updateTotalStunValue))
        self._invalidatePanelVisibility()
        if self.__efficiencyCtrl is not None:
            self._invalidateContent()
            self.__efficiencyCtrl.onTotalEfficiencyUpdated += self._onTotalEfficiencyUpdated
            self.__efficiencyCtrl.onPersonalEfficiencyReceived += self._onEfficiencyReceived
            self.__efficiencyCtrl.onPersonalEfficiencyLogSynced += self._onPersonalEfficiencyLogSynced
        self.settingsCore.onSettingsChanged += self._onSettingsChanged
        if self.__vehStateCtrl is not None:
            self.__vehStateCtrl.onPostMortemSwitched += self._onPostMortemSwitched
            self.__vehStateCtrl.onVehicleControlling += self._onVehicleControlling
        deathScreenCtrl = self.sessionProvider.dynamic.deathScreen
        if deathScreenCtrl:
            deathScreenCtrl.onWinnerScreen += self.__onWinnerScreen
        self.addListener(gui_events.GameEvent.SHOW_EXTENDED_INFO, self._handleShowExtendedInfo, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(gui_events.GameEvent.SHOW_CURSOR, self._handleShowCursor, EVENT_BUS_SCOPE.GLOBAL)
        self.addListener(gui_events.GameEvent.HIDE_CURSOR, self._handleHideCursor, EVENT_BUS_SCOPE.GLOBAL)
        self.addListener(gui_events.GameEvent.FULL_STATS, self.__handleShowFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
        return

    def _dispose(self):
        self.removeListener(gui_events.GameEvent.SHOW_EXTENDED_INFO, self._handleShowExtendedInfo, EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(gui_events.GameEvent.SHOW_CURSOR, self._handleShowCursor, EVENT_BUS_SCOPE.GLOBAL)
        self.removeListener(gui_events.GameEvent.HIDE_CURSOR, self._handleHideCursor, EVENT_BUS_SCOPE.GLOBAL)
        self.removeListener(gui_events.GameEvent.FULL_STATS, self.__handleShowFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
        if self.__vehStateCtrl is not None:
            self.__vehStateCtrl.onPostMortemSwitched -= self._onPostMortemSwitched
            self.__vehStateCtrl.onVehicleControlling -= self._onVehicleControlling
        deathScreenCtrl = self.sessionProvider.dynamic.deathScreen
        if deathScreenCtrl:
            deathScreenCtrl.onWinnerScreen -= self.__onWinnerScreen
        self.settingsCore.onSettingsChanged -= self._onSettingsChanged
        if self.__efficiencyCtrl is not None:
            self.__efficiencyCtrl.onTotalEfficiencyUpdated -= self._onTotalEfficiencyUpdated
            self.__efficiencyCtrl.onPersonalEfficiencyReceived -= self._onEfficiencyReceived
            self.__efficiencyCtrl.onPersonalEfficiencyLogSynced -= self._onPersonalEfficiencyLogSynced
            self.__efficiencyCtrl = None
        self.__vehStateCtrl = None
        self.__arenaDP = None
        self._topLog.dispose()
        self._bottomLog.dispose()
        self._totalEvents = None
        super(DamageLogPanel, self)._dispose()
        return

    def _invalidateContent(self):
        self._invalidateTotalDamages()
        self._invalidateLogs()

    def _invalidateLogs(self):
        settingGetter = self.settingsCore.getSetting
        self._logViewMode = settingGetter(DAMAGE_LOG.SHOW_DETAILS)
        epos = settingGetter(DAMAGE_LOG.EVENT_POSITIONS)
        etype = settingGetter(DAMAGE_LOG.SHOW_EVENT_TYPES)
        topLogContentMask, bottomLogContentMask = _EVENT_POSITIONS_TO_CONTENT_MASK[epos]
        topLogRecStyle, bottomLogRecStyle = _EVENT_POSITIONS_TO_RECORD_STYLE[epos][etype]
        displayedEventsContentMask = _DISPLAYED_EVENT_TYPES_TO_CONTENT_MASK[etype]
        topLogContentMask &= displayedEventsContentMask
        bottomLogContentMask &= displayedEventsContentMask
        self._topLog.updateLog(topLogContentMask, self._logViewMode, topLogRecStyle)
        self._bottomLog.updateLog(bottomLogContentMask, self._logViewMode, bottomLogRecStyle)

    def _invalidateTotalDamages(self):
        contentMask = 0
        isDamageSettingEnabled = self.__isDamageSettingEnabled
        for settingName, bit in _TOTAL_DAMAGE_SETTINGS_TO_CONTENT_MASK.iteritems():
            if isDamageSettingEnabled(settingName):
                contentMask |= bit

        if contentMask != self.__totalDamageContentMask:
            self.__totalDamageContentMask = contentMask
            getter = self.__efficiencyCtrl.getTotalEfficiency
            args = [ self._setTotalValue(e, getter(e))[1] for e, _ in self._totalEvents ]
            self.as_summaryStatsS(*args)

    def _onTotalEfficiencyUpdated(self, diff):
        if self.isSwitchToVehicle():
            for e, updateMethod in self._totalEvents:
                if e in diff:
                    isUpdated, value = self._setTotalValue(e, diff[e])
                    if isUpdated:
                        updateMethod(value)

    def _onPersonalEfficiencyLogSynced(self):
        if self.isSwitchToVehicle():
            self._topLog.invalidate()
            self._bottomLog.invalidate()

    def _onEfficiencyReceived(self, events):
        if self.isSwitchToVehicle():
            self._topLog.addToLog(events)
            self._bottomLog.addToLog(events)

    def _invalidatePanelVisibility(self):
        if self._isFullStatsShown or self._isWinnerScreenShown:
            return
        else:
            isVisible = True
            if self.sessionProvider.getCtx().isPlayerObserver():
                isVisible = True
            elif self.__vehStateCtrl is None:
                isVisible = self._isVisible
            elif self.__vehStateCtrl.isInPostmortem:
                if self.__arenaDP is None:
                    isVisible = self._isVisible
                else:
                    isVisible = self.isSwitchToVehicle()
            if self._isVisible != isVisible:
                self._isVisible = isVisible
                self._setSettings(self._isVisible, bool(self.settingsCore.getSetting(GRAPHICS.COLOR_BLIND)))
            return

    def _onSettingsChanged(self, diff):
        for key in _TOTAL_DAMAGE_SETTINGS_TO_CONTENT_MASK.iterkeys():
            if key in diff:
                self._invalidateTotalDamages()

        for key in _LOGS_SETTINGS:
            if key in diff:
                self._invalidateLogs()

        if GRAPHICS.COLOR_BLIND in diff:
            self._setSettings(self._isVisible, bool(diff[GRAPHICS.COLOR_BLIND]))

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self._invalidatePanelVisibility()

    def _onVehicleControlling(self, vehicle):
        self._invalidatePanelVisibility()
        self._invalidateTotalDamages()

    def _handleShowExtendedInfo(self, event):
        if self._logViewMode == _VIEW_MODE.SHOW_BY_ALT_PRESS:
            self.as_isDownAltButtonS(event.ctx['isDown'])

    def _handleShowCursor(self, _):
        self.as_isDownCtrlButtonS(True)

    def _handleHideCursor(self, _):
        self.as_isDownCtrlButtonS(False)

    def __handleShowFullStats(self, event):
        self._isFullStatsShown = event.ctx['isDown']
        if not self._isFullStatsShown:
            self._invalidatePanelVisibility()

    def __onWinnerScreen(self):
        self._isWinnerScreenShown = True

    def _setTotalValue(self, etype, value):
        if BitmaskHelper.hasAnyBitSet(self.__totalDamageContentMask, etype):
            value = _formatTotalValue(value)
        else:
            value = None
        if value != self.__totalValues[etype]:
            self.__totalValues[etype] = value
            return (True, value)
        else:
            return (False, value)

    def _updateTopLog(self, isVisible, isShortMode, records):
        self.as_detailStatsTopS(isVisible, isShortMode, records)

    def _addToTopLog(self, value, actionTypeImg, vehicleTypeImg, vehicleName, shellTypeStr, shellTypeBG):
        self.as_addDetailMessageTopS(value, actionTypeImg, vehicleTypeImg, vehicleName, shellTypeStr, shellTypeBG)

    def _updateBottomLog(self, isVisible, isShortMode, records):
        self.as_detailStatsBottomS(isVisible, isShortMode, records)

    def _addToBottomLog(self, value, actionTypeImg, vehicleTypeImg, vehicleName, shellTypeStr, shellTypeBG):
        self.as_addDetailMessageBottomS(value, actionTypeImg, vehicleTypeImg, vehicleName, shellTypeStr, shellTypeBG)

    def _updateTotalDamageValue(self, value):
        self.as_updateSummaryDamageValueS(value)

    def _updateTotalBlockedDamageValue(self, value):
        self.as_updateSummaryBlockedValueS(value)

    def _updateTotalAssistValue(self, value):
        self.as_updateSummaryAssistValueS(value)

    def _updateTotalStunValue(self, value):
        self.as_updateSummaryStunValueS(value)

    def _setSettings(self, isVisible, isColorBlind):
        self.as_setSettingsDamageLogComponentS(isVisible, isColorBlind)

    def __isDamageSettingEnabled(self, settingName):
        result = self.settingsCore.getSetting(settingName)
        if settingName == DAMAGE_LOG.ASSIST_STUN and result:
            isSPG = self.__arenaDP.getVehicleInfo(self.__vehStateCtrl.getControllingVehicleID()).isSPG()
            arenaVisitor = self.sessionProvider.arenaVisitor
            isComp7Battle = arenaVisitor.gui.isComp7Battle()
            result = (isSPG or isComp7Battle) and self.lobbyContext.getServerSettings().spgRedesignFeatures.isStunEnabled()
        return result
