# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/damage_log_panel.py
from collections import defaultdict
from BattleFeedbackCommon import BATTLE_EVENT_TYPE as _BET
from account_helpers.settings_core.options import DamageLogDetailsSetting as _VIEW_MODE, DamageLogEventPositionsSetting as _EVENT_POSITIONS, DamageLogEventTypesSetting as _DISPLAYED_EVENT_TYPES
from account_helpers.settings_core.settings_constants import DAMAGE_LOG, GRAPHICS
from constants import SHELL_TYPES
from gui.Scaleform.daapi.view.meta.BattleDamageLogPanelMeta import BattleDamageLogPanelMeta
from gui.Scaleform.genConsts.BATTLEDAMAGELOG_IMAGES import BATTLEDAMAGELOG_IMAGES as _IMAGES
from gui.Scaleform.genConsts.DAMAGE_LOG_SHELL_BG_TYPES import DAMAGE_LOG_SHELL_BG_TYPES
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control.battle_constants import PERSONAL_EFFICIENCY_TYPE as _ETYPE
from gui.impl import backport
from gui.shared import events as gui_events, EVENT_BUS_SCOPE
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
_VEHICLE_CLASS_TAGS_ICONS = {'lightTank': _IMAGES.WHITE_ICON_LIGHTTANK_16X16,
 'mediumTank': _IMAGES.WHITE_ICON_MEDIUM_TANK_16X16,
 'heavyTank': _IMAGES.WHITE_ICON_HEAVYTANK_16X16,
 'SPG': _IMAGES.WHITE_ICON_SPG_16X16,
 'AT-SPG': _IMAGES.WHITE_ICON_AT_SPG_16X16}
_SHELL_TYPES_TO_STR = {SHELL_TYPES.ARMOR_PIERCING: INGAME_GUI.DAMAGELOG_SHELLTYPE_ARMOR_PIERCING,
 SHELL_TYPES.HIGH_EXPLOSIVE: INGAME_GUI.DAMAGELOG_SHELLTYPE_HIGH_EXPLOSIVE,
 SHELL_TYPES.ARMOR_PIERCING_HE: INGAME_GUI.DAMAGELOG_SHELLTYPE_ARMOR_PIERCING_HE,
 SHELL_TYPES.ARMOR_PIERCING_CR: INGAME_GUI.DAMAGELOG_SHELLTYPE_ARMOR_PIERCING_CR,
 SHELL_TYPES.HOLLOW_CHARGE: INGAME_GUI.DAMAGELOG_SHELLTYPE_HOLLOW_CHARGE}

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
        vTypeInfoVO = arenaDP.getVehicleInfo(info.getArenaVehicleID()).vehicleType
        vehicleVO.vehicleTypeImg = _VEHICLE_CLASS_TAGS_ICONS.get(vTypeInfoVO.classTag, '')
        vehicleVO.vehicleName = vTypeInfoVO.shortNameWithPrefix


class _ReceivedHitVehicleVOBuilder(_VehicleVOBuilder):

    def _populateVO(self, vehicleVO, info, arenaDP):
        super(_ReceivedHitVehicleVOBuilder, self)._populateVO(vehicleVO, info, arenaDP)
        if info.getArenaVehicleID() == arenaDP.getPlayerVehicleID() and info.isRam():
            vehicleVO.vehicleName = ''
            vehicleVO.vehicleTypeImg = ''
        if info.isDeathZone():
            vehicleVO.vehicleName = ''
            vehicleVO.vehicleTypeImg = ''
        if info.isProtectionZoneDamage() or info.isProtectionZoneDamage(primary=False) or info.isArtilleryEqDamage() or info.isArtilleryEqDamage(primary=False):
            vehicleVO.vehicleName = ''
            vehicleVO.vehicleTypeImg = _IMAGES.DAMAGELOG_ARTILLERY_16X16
        elif info.isBombersDamage() or info.isBombersDamage(primary=False) or info.isBomberEqDamage() or info.isBomberEqDamage(primary=False):
            vehicleVO.vehicleName = ''
            vehicleVO.vehicleTypeImg = _IMAGES.DAMAGELOG_AIRSTRIKE_16X16


class _ShellVOModel(_VOModel):
    shellTypeStr = _VOModelProperty(name='shellTypeStr')
    shellTypeBG = _VOModelProperty(name='shellTypeBG')

    def __init__(self, shellTypeStr='', shellTypeBG=''):
        super(_ShellVOModel, self).__init__()
        self.shellTypeStr = shellTypeStr
        self.shellTypeBG = shellTypeBG


class _ShellVOBuilder(_IVOBuilder):

    def buildVO(self, info, arenaDP):
        return _ShellVOModel(self._getShellTypeStr(info), self._getShellTypeBg(info))

    def _getShellTypeStr(self, info):
        shType = info.getShellType()
        return _SHELL_TYPES_TO_STR[shType] if shType is not None and shType in _SHELL_TYPES_TO_STR else ''

    def _getShellTypeBg(self, info):
        if info.getShellType() is None:
            return DAMAGE_LOG_SHELL_BG_TYPES.EMPTY
        else:
            return DAMAGE_LOG_SHELL_BG_TYPES.GOLD if info.isShellGold() else DAMAGE_LOG_SHELL_BG_TYPES.WHITE


class _EmptyShellVOBuilder(_ShellVOBuilder):

    def _getShellTypeStr(self, info):
        pass

    def _getShellTypeBg(self, info):
        return DAMAGE_LOG_SHELL_BG_TYPES.EMPTY


class _DamageShellVOBuilder(_ShellVOBuilder):

    def buildVO(self, info, arenaDP):
        if info.isShot():
            shellVOBuilder = _ShellVOBuilder()
        else:
            shellVOBuilder = _EmptyShellVOBuilder()
        return shellVOBuilder.buildVO(info, arenaDP)


class _CritsShellVOBuilder(_ShellVOBuilder):

    def buildVO(self, info, arenaDP):
        if info.isShot():
            shellVOBuilder = _ShellVOBuilder()
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

    def __init__(self, shotIcon, fireIcon, ramIcon, wcIcon):
        super(_DamageActionImgVOBuilder, self).__init__('')
        self._shotIcon = shotIcon
        self._fireIcon = fireIcon
        self._ramIcon = ramIcon
        self._wcIcon = wcIcon

    def _getImage(self, info):
        if info.isShot() or info.isProtectionZoneDamage() or info.isBombersDamage() or info.isArtilleryEqDamage() or info.isBomberEqDamage() or info.isDeathZone():
            return self._shotIcon
        if info.isFire():
            return self._fireIcon
        return self._wcIcon if info.isWorldCollision() else self._ramIcon


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
_ETYPE_TO_RECORD_VO_BUILDER = {_ETYPE.DAMAGE: _LogRecordVOBuilder(_DEFAULT_VEHICLE_VO_BUILDER, _EMPTY_SHELL_VO_BUILDER, _DAMAGE_VALUE_VO_BUILDER, _DamageActionImgVOBuilder(shotIcon=_IMAGES.DAMAGELOG_DAMAGE_16X16, fireIcon=_IMAGES.DAMAGELOG_FIRE_16X16, ramIcon=_IMAGES.DAMAGELOG_RAM_16X16, wcIcon=_IMAGES.DAMAGELOG_ICON_WORLD_COLLISION)),
 _ETYPE.RECEIVED_DAMAGE: _LogRecordVOBuilder(_ReceivedHitVehicleVOBuilder(), _DamageShellVOBuilder(), _DAMAGE_VALUE_VO_BUILDER, _DamageActionImgVOBuilder(shotIcon=_IMAGES.DAMAGELOG_DAMAGE_ENEMY_16X16, fireIcon=_IMAGES.DAMAGELOG_BURN_ENEMY_16X16, ramIcon=_IMAGES.DAMAGELOG_RAM_ENEMY_16X16, wcIcon=_IMAGES.DAMAGELOG_DAMAGE_ENEMY_16X16)),
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
        self.__logViewMode = _VIEW_MODE.SHOW_ALWAYS
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
        if self.__logViewMode == _VIEW_MODE.SHOW_ALWAYS:
            self.__isVisible = True
            messages = self._getLogMessages(self.__contentMask)
        elif self.__logViewMode == _VIEW_MODE.SHOW_BY_ALT_PRESS:
            self.__isVisible = False
            messages = self._getLogMessages(self.__contentMask)
        else:
            self.__isVisible = False
            messages = []
        self.__setListProxy(self.__isVisible, bool(self.__recordStyle == _RECORD_STYLE.SHORT), messages)

    def updateLog(self, contentMask=None, viewMode=None, recordStyle=_RECORD_STYLE.FULL):
        needUpdate = False
        if viewMode != self.__logViewMode:
            self.__logViewMode = viewMode
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
        if self.__logViewMode == _VIEW_MODE.HIDE:
            return
        for e in events:
            if BitmaskHelper.hasAnyBitSet(self.__contentMask, e.getType()):
                vo = self._buildLogMessageVO(e)
                self.__addToListProxy(**vo)

    def _getLogMessages(self, contentMask):
        if self.__efficiencyCtrl is not None:
            records = self.__efficiencyCtrl.getLoogedEfficiency(contentMask)
            return [ self._buildLogMessageVO(r) for r in records ]
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
        self.__isVisible = False
        self.__isFullStatsShown = False
        self.__logViewMode = _VIEW_MODE.SHOW_ALWAYS
        self.__totalDamageContentMask = 0
        self.__totalValues = defaultdict(int)
        self._totalEvents = None
        self.__topLog = _LogViewComponent()
        self.__bottomLog = _LogViewComponent()
        return

    def isSwitchToVehicle(self):
        observedVehID = self.__vehStateCtrl.getControllingVehicleID()
        playerVehicleID = self.__arenaDP.getPlayerVehicleID()
        return playerVehicleID != observedVehID

    def _populate(self):
        super(DamageLogPanel, self)._populate()
        self.__efficiencyCtrl = self.sessionProvider.shared.personalEfficiencyCtrl
        self.__topLog.initialize(setListProxyMethod=self._updateTopLog, addToListProxyMethod=self._addToTopLog, efficiencyCtrl=self.__efficiencyCtrl, arenaDP=self.__arenaDP)
        self.__bottomLog.initialize(setListProxyMethod=self._updateBottomLog, addToListProxyMethod=self._addToBottomLog, efficiencyCtrl=self.__efficiencyCtrl, arenaDP=self.__arenaDP)
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
        self.settingsCore.onSettingsChanged -= self._onSettingsChanged
        if self.__efficiencyCtrl is not None:
            self.__efficiencyCtrl.onTotalEfficiencyUpdated -= self._onTotalEfficiencyUpdated
            self.__efficiencyCtrl.onPersonalEfficiencyReceived -= self._onEfficiencyReceived
            self.__efficiencyCtrl = None
        self.__vehStateCtrl = None
        self.__arenaDP = None
        self.__topLog.dispose()
        self.__bottomLog.dispose()
        self._totalEvents = None
        super(DamageLogPanel, self)._dispose()
        return

    def _invalidateContent(self):
        self._invalidateTotalDamages()
        self._invalidateLogs()

    def _invalidateLogs(self):
        settingGetter = self.settingsCore.getSetting
        self.__logViewMode = settingGetter(DAMAGE_LOG.SHOW_DETAILS)
        epos = settingGetter(DAMAGE_LOG.EVENT_POSITIONS)
        etype = settingGetter(DAMAGE_LOG.SHOW_EVENT_TYPES)
        topLogContentMask, bottomLogContentMask = _EVENT_POSITIONS_TO_CONTENT_MASK[epos]
        topLogRecStyle, bottomLogRecStyle = _EVENT_POSITIONS_TO_RECORD_STYLE[epos][etype]
        displayedEventsContentMask = _DISPLAYED_EVENT_TYPES_TO_CONTENT_MASK[etype]
        topLogContentMask &= displayedEventsContentMask
        bottomLogContentMask &= displayedEventsContentMask
        self.__topLog.updateLog(topLogContentMask, self.__logViewMode, topLogRecStyle)
        self.__bottomLog.updateLog(bottomLogContentMask, self.__logViewMode, bottomLogRecStyle)

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
        for e, updateMethod in self._totalEvents:
            if e in diff:
                isUpdated, value = self._setTotalValue(e, diff[e])
                if isUpdated:
                    updateMethod(value)

    def _onPersonalEfficiencyLogSynced(self):
        self.__topLog.invalidate()
        self.__bottomLog.invalidate()

    def _onEfficiencyReceived(self, events):
        self.__topLog.addToLog(events)
        self.__bottomLog.addToLog(events)

    def _invalidatePanelVisibility(self):
        arenaVisitor = self.sessionProvider.arenaVisitor
        isEpicBattle = arenaVisitor.gui.isInEpicRange()
        if isEpicBattle:
            return
        elif self.__isFullStatsShown:
            return
        else:
            isVisible = True
            if self.sessionProvider.getCtx().isPlayerObserver():
                isVisible = True
            elif self.__vehStateCtrl is None:
                isVisible = self.__isVisible
            elif self.__vehStateCtrl.isInPostmortem:
                if self.__arenaDP is None:
                    isVisible = self.__isVisible
                else:
                    isVisible = not self.isSwitchToVehicle()
            if self.__isVisible != isVisible:
                self.__isVisible = isVisible
                self._setSettings(self.__isVisible, bool(self.settingsCore.getSetting(GRAPHICS.COLOR_BLIND)))
            return

    def _onSettingsChanged(self, diff):
        for key in _TOTAL_DAMAGE_SETTINGS_TO_CONTENT_MASK.iterkeys():
            if key in diff:
                self._invalidateTotalDamages()

        for key in _LOGS_SETTINGS:
            if key in diff:
                self._invalidateLogs()

        if GRAPHICS.COLOR_BLIND in diff:
            self._setSettings(self.__isVisible, bool(diff[GRAPHICS.COLOR_BLIND]))

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self._invalidatePanelVisibility()

    def _onVehicleControlling(self, vehicle):
        self._invalidatePanelVisibility()
        self._invalidateTotalDamages()

    def _handleShowExtendedInfo(self, event):
        if self.__logViewMode == _VIEW_MODE.SHOW_BY_ALT_PRESS:
            self.as_isDownAltButtonS(event.ctx['isDown'])

    def _handleShowCursor(self, _):
        self.as_isDownCtrlButtonS(True)

    def _handleHideCursor(self, _):
        self.as_isDownCtrlButtonS(False)

    def __handleShowFullStats(self, event):
        self.__isFullStatsShown = event.ctx['isDown']
        if not self.__isFullStatsShown:
            self._invalidatePanelVisibility()

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
            result = isSPG and self.lobbyContext.getServerSettings().spgRedesignFeatures.isStunEnabled()
        return result
