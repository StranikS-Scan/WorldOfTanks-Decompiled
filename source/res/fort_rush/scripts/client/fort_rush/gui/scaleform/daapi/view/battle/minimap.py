# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/battle/minimap.py
from __future__ import absolute_import
from future.utils import viewitems
import logging
from typing import TYPE_CHECKING
import BattleReplay
from Math import Matrix
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES, MarkerType, ReplyState, getUniqueTeamOrControlPointID
from fort_rush_common.fort_rush_constants import CAPTURE_POINT_NO_TEAM, CaptureStates
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.Scaleform.daapi.view.battle.shared.minimap import settings
from gui.Scaleform.daapi.view.battle.shared.minimap.common import EntriesPlugin
from gui.Scaleform.daapi.view.battle.shared.minimap.plugins import ArenaVehiclesPlugin
from gui.Scaleform.daapi.view.battle.classic.minimap import GlobalSettingsPlugin, ClassicMinimapPingPlugin
from fort_rush.gui.fort_rush_gui_constants import MINIMAP_CONTAINER_NAME, BATTLE_CTRL_ID
from fort_rush.gui.shared.events import RespawnCtrlEvent, CapturePointEvent
from fort_rush.gui.scaleform.daapi.view.meta.FortRushMinimapMeta import FortRushMinimapMeta
from helpers import dependency
from messenger.proto.events import g_messengerEvents
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS
from skeletons.gui.battle_session import IBattleSessionProvider
from fort_rush.helpers.utils import getCurrentTeam, mapOwnerTeamToMarkerTeam
if TYPE_CHECKING:
    from fort_rush.gui.battle_control.controllers.respawn_ctrl import FortRushRespawnViewController
    from gui.battle_control.controllers.chat_cmd_ctrl import ChatCommandsController
    from messenger.proto.bw_chat2.battle_chat_cmd import _ReceivedCmdDecorator
_logger = logging.getLogger(__name__)
_PING_COMMANDS = frozenset([BATTLE_CHAT_COMMAND_NAMES.ATTACK_BASE, BATTLE_CHAT_COMMAND_NAMES.DEFEND_BASE])
_COMMIT_COMMANDS = frozenset([BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE, BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE])
_ZONE_NAME_A_ID = ord('A')
_ZONE_NAME_Z_ID = ord('Z')
_ZONE_TARGET_TEAM_ID = 0
_ZONE_TARGET_BASE_FALLBACK = 1

def _resolveCommandName(command):
    action = _ACTIONS.battleChatCommandFromActionID(command.getID())
    return action.name if action else ''


def _isProgressState(captureState):
    return captureState in (CaptureStates.CAPTURING, CaptureStates.DECREASING)


def _isNeutralizingOwner(ownerTeam, invadingTeam, captureState):
    if ownerTeam == CAPTURE_POINT_NO_TEAM:
        return False
    return False if captureState not in (CaptureStates.CAPTURING, CaptureStates.DECREASING, CaptureStates.CONTESTED) else invadingTeam != ownerTeam


def _getCaptureProgressValue(currentPoints, ownerTeam, invadingTeam, captureState):
    progress = int(currentPoints)
    return 100 - progress if _isNeutralizingOwner(ownerTeam, invadingTeam, captureState) else progress


def _getCaptureProgressTeam(ownerTeam, invadingTeam, captureState, lastKnownInvadingTeam=CAPTURE_POINT_NO_TEAM):
    if _isNeutralizingOwner(ownerTeam, invadingTeam, captureState):
        return ownerTeam
    return lastKnownInvadingTeam if captureState == CaptureStates.DECREASING and lastKnownInvadingTeam != CAPTURE_POINT_NO_TEAM else invadingTeam


class FortRushSettingsPlugin(GlobalSettingsPlugin):

    def __init__(self, parentObj):
        super(FortRushSettingsPlugin, self).__init__(parentObj)
        self._isMinimapCMDDisabled = False

    def start(self):
        super(FortRushSettingsPlugin, self).start()
        g_eventBus.addListener(RespawnCtrlEvent.SHOW_SPAWN_POINTS, self.__onShowSpawnPoints, EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.addListener(RespawnCtrlEvent.HIDE_SPAWN_POINTS, self.__onHideSpawnPoints, EVENT_BUS_SCOPE.GLOBAL)

    def stop(self):
        g_eventBus.removeListener(RespawnCtrlEvent.HIDE_SPAWN_POINTS, self.__onHideSpawnPoints, EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.removeListener(RespawnCtrlEvent.SHOW_SPAWN_POINTS, self.__onShowSpawnPoints, EVENT_BUS_SCOPE.GLOBAL)
        super(FortRushSettingsPlugin, self).stop()

    def __onShowSpawnPoints(self, _):
        self._isMinimapCMDDisabled = True
        if self._parentObj is not None:
            self._parentObj.as_setVisibleS(True)
        return

    def __onHideSpawnPoints(self, _):
        self._isMinimapCMDDisabled = False
        if self._parentObj is not None:
            self._parentObj.as_setVisibleS(self._isVisible)
        return

    def _handleMinimapCmd(self, event):
        if self._isMinimapCMDDisabled:
            return
        super(FortRushSettingsPlugin, self)._handleMinimapCmd(event)


class FortRushMinimapComponent(FortRushMinimapMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(FortRushMinimapComponent, self).__init__()
        self.__isActiveSpawnPoints = False

    def _setupPlugins(self, arenaVisitor):
        setup = super(FortRushMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['spawn_points'] = SpawnPointsPlugin
        setup['vehicles'] = FortRushArenaVehiclesPlugin
        setup['settings'] = FortRushSettingsPlugin
        setup['capture_state'] = FortRushMinimapCapturePlugin
        if not BattleReplay.g_replayCtrl.isPlaying:
            setup['pinging'] = FortRushMinimapPingPlugin
        return setup

    def onZoneClicked(self, zoneName):
        plugin = self.getPlugin('pinging')
        if plugin is not None:
            plugin.onZoneMarkerClicked(zoneName)
        return

    def _populate(self):
        super(FortRushMinimapComponent, self)._populate()
        g_eventBus.addListener(RespawnCtrlEvent.SHOW_SPAWN_POINTS, self.__onShowSpawnPoints, EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.addListener(RespawnCtrlEvent.HIDE_SPAWN_POINTS, self.__onHideSpawnPoints, EVENT_BUS_SCOPE.GLOBAL)

    def _dispose(self):
        g_eventBus.removeListener(RespawnCtrlEvent.HIDE_SPAWN_POINTS, self.__onHideSpawnPoints, EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.removeListener(RespawnCtrlEvent.SHOW_SPAWN_POINTS, self.__onShowSpawnPoints, EVENT_BUS_SCOPE.GLOBAL)
        super(FortRushMinimapComponent, self)._dispose()

    def isModalViewShown(self):
        return True if self.__isActiveSpawnPoints else super(FortRushMinimapComponent, self).isModalViewShown()

    def __onShowSpawnPoints(self, _):
        self.__isActiveSpawnPoints = True
        mpp = self.getPlugin('pinging')
        if mpp is not None:
            mpp.hideHintPanel(instantHide=True)
        avp = self.getPlugin('vehicles')
        avp.hideMinimapHP()
        return

    def __onHideSpawnPoints(self, _):
        self.__isActiveSpawnPoints = False


class SpawnPointsPlugin(EntriesPlugin):
    __slots__ = ('_points',)
    _SPAWN_POINT_ENTRY = 'FortRushRespawnPointMinimapEntryUI'

    def __init__(self, parent, clazz=None):
        super(SpawnPointsPlugin, self).__init__(parent, clazz)
        self._points = {}

    def start(self):
        super(SpawnPointsPlugin, self).start()
        spawnCtrl = self._spawnCtrl
        if spawnCtrl:
            spawnCtrl.onShowSpawnPoints += self._onShowSpawnPoints
            spawnCtrl.onCloseSpawnPoints += self._onCloseSpawnPoints
            spawnCtrl.onChooseSpawnPoint += self._onChooseSpawnPoint

    def stop(self):
        spawnCtrl = self._spawnCtrl
        if spawnCtrl:
            spawnCtrl.onShowSpawnPoints -= self._onShowSpawnPoints
            spawnCtrl.onCloseSpawnPoints -= self._onCloseSpawnPoints
            spawnCtrl.onChooseSpawnPoint -= self._onChooseSpawnPoint
        super(SpawnPointsPlugin, self).stop()

    @property
    def _spawnCtrl(self):
        return self.sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.FORT_RUSH_GUI_CTRL)

    def _onShowSpawnPoints(self, points):
        self._removeMarkers()
        self._setPoints(points)
        self._addMarkers()

    def _onCloseSpawnPoints(self):
        self._removeMarkers()

    def _onChooseSpawnPoint(self, pointGuid):
        self._choosePoint(pointGuid)

    def _setPoints(self, points):
        self._points = {point['guid']:(point['position'][0], 0, point['position'][1]) for point in points}

    def _addMarkers(self):
        for pointGuid, position in viewitems(self._points):
            matrix = Matrix()
            matrix.setTranslate(position)
            self._addEntryEx(pointGuid, self._SPAWN_POINT_ENTRY, MINIMAP_CONTAINER_NAME.FORT_RUSH_DEPLOY, matrix, active=True)
            self._invokeEx(pointGuid, 'setId', pointGuid)

    def _removeMarkers(self):
        for pointGuid in self._points:
            self._delEntryEx(pointGuid)

        self._points = {}

    def _choosePoint(self, chosenGuid):
        for pointGuid in self._points:
            self._invokeEx(pointGuid, 'setIsSelected', pointGuid == chosenGuid)


class FortRushArenaVehiclesPlugin(ArenaVehiclesPlugin):

    def hideMinimapHP(self):
        self.setShowMinimapHP(False)


class FortRushMinimapCapturePlugin(EntriesPlugin):
    _ZONE_ENTRY_SYMBOL = 'FortRushZoneMarkerUI'
    _ZONE_TRANSFORM_PROPS = settings.TRANSFORM_FLAG.DEFAULT ^ settings.TRANSFORM_FLAG.NO_ROTATION

    def __init__(self, parentObj):
        super(FortRushMinimapCapturePlugin, self).__init__(parentObj)
        self._lastKnownInvadingTeams = {}
        self._lastKnownProgressTeams = {}
        self._lastCaptureStates = {}
        self._playerTeam = CAPTURE_POINT_NO_TEAM

    def start(self):
        super(FortRushMinimapCapturePlugin, self).start()
        self._playerTeam = getCurrentTeam()
        g_eventBus.addListener(CapturePointEvent.INIT_CAPTURABLE_POINT, self._onCapturePointInit, EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(CapturePointEvent.CAPTURABLE_POINT_UPDATE, self._onCapturePointUpdate, EVENT_BUS_SCOPE.BATTLE)

    def stop(self):
        g_eventBus.removeListener(CapturePointEvent.CAPTURABLE_POINT_UPDATE, self._onCapturePointUpdate, EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.removeListener(CapturePointEvent.INIT_CAPTURABLE_POINT, self._onCapturePointInit, EVENT_BUS_SCOPE.BATTLE)
        self._lastKnownInvadingTeams.clear()
        self._lastKnownProgressTeams.clear()
        self._lastCaptureStates.clear()
        self._playerTeam = CAPTURE_POINT_NO_TEAM
        super(FortRushMinimapCapturePlugin, self).stop()

    def _onCapturePointInit(self, event):
        zoneName = (event.capturablePointName or '').upper()
        if not zoneName:
            _logger.error('[FORT_RUSH][MINIMAP] Empty capturablePointName in capture point init event!')
            return
        else:
            entry = self._addEntryEx(zoneName, self._ZONE_ENTRY_SYMBOL, MINIMAP_CONTAINER_NAME.FORT_RUSH_ZONES, event.transform, active=True, transformProps=self._ZONE_TRANSFORM_PROPS)
            if entry is None:
                _logger.error('[FORT_RUSH][MINIMAP] Failed to add minimap entry for zone %s', zoneName)
                return
            self._invokeEx(zoneName, 'setZoneName', zoneName)
            captureState = self._lastCaptureStates.get(zoneName)
            if captureState is not None:
                self._applyCaptureState(captureState)
            return

    def _onCapturePointUpdate(self, event):
        zoneName = (event.capturablePointName or '').upper()
        if not zoneName:
            _logger.error('[FORT_RUSH][MINIMAP] Empty capturablePointName in capture update event!')
            return
        invadingTeam = event.invadersTeam
        if invadingTeam != CAPTURE_POINT_NO_TEAM:
            self._lastKnownInvadingTeams[zoneName] = invadingTeam
        captureState = self._buildCaptureState(zoneName, event, invadingTeam)
        self._lastCaptureStates[zoneName] = captureState
        self._applyCaptureState(captureState)

    def _buildCaptureState(self, zoneName, event, invadingTeam):
        ownerTeam = event.ownersTeam
        rawProgress = int((event.captureProgressPercent or 0) * 100)
        captureState = event.state
        isContested = event.isContested
        lastKnownInvadingTeam = self._lastKnownInvadingTeams.get(zoneName, CAPTURE_POINT_NO_TEAM)
        progressTeam = _getCaptureProgressTeam(ownerTeam, invadingTeam, captureState, lastKnownInvadingTeam)
        progress = _getCaptureProgressValue(rawProgress, ownerTeam, invadingTeam, captureState)
        if progressTeam != CAPTURE_POINT_NO_TEAM:
            self._lastKnownProgressTeams[zoneName] = progressTeam
        elif progress > 0:
            progressTeam = self._lastKnownProgressTeams.get(zoneName, CAPTURE_POINT_NO_TEAM)
        isCaptureActive = _isProgressState(captureState)
        if progressTeam != CAPTURE_POINT_NO_TEAM:
            isCaptureActive = 0 < progress < 100 and True
        return {'zoneName': zoneName,
         'ownerTeam': mapOwnerTeamToMarkerTeam(ownerTeam, self._playerTeam),
         'progressTeam': mapOwnerTeamToMarkerTeam(progressTeam, self._playerTeam),
         'captureActive': isCaptureActive,
         'isContested': isContested,
         'progress': progress}

    def _applyCaptureState(self, captureState):
        self._invokeEx(captureState['zoneName'], 'updateCaptureState', captureState['ownerTeam'], captureState['progressTeam'], captureState['captureActive'], captureState['isContested'], captureState['progress'])


class FortRushMinimapPingPlugin(ClassicMinimapPingPlugin):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, parentObj):
        super(FortRushMinimapPingPlugin, self).__init__(parentObj)
        self._zoneOwners = {}
        self._zoneIds = {}
        self._zoneNamesById = {}
        self._playerTeam = CAPTURE_POINT_NO_TEAM

    def start(self):
        super(FortRushMinimapPingPlugin, self).start()
        self._playerTeam = getCurrentTeam()
        g_eventBus.addListener(CapturePointEvent.CAPTURABLE_POINT_UPDATE, self._onCapturePointUpdate, EVENT_BUS_SCOPE.BATTLE)
        g_messengerEvents.channels.onCommandReceived += self._onCommandReceived
        feedback = self.sessionProvider.shared.feedback
        if feedback is not None:
            feedback.onRemoveCommandReceived += self._onCommandRemoved
            feedback.onReplyFeedbackReceived += self._onReplyFeedbackReceived
        return

    def stop(self):
        feedback = self.sessionProvider.shared.feedback
        if feedback is not None:
            feedback.onRemoveCommandReceived -= self._onCommandRemoved
            feedback.onReplyFeedbackReceived -= self._onReplyFeedbackReceived
        g_messengerEvents.channels.onCommandReceived -= self._onCommandReceived
        g_eventBus.removeListener(CapturePointEvent.CAPTURABLE_POINT_UPDATE, self._onCapturePointUpdate, EVENT_BUS_SCOPE.BATTLE)
        self._zoneOwners = {}
        self._zoneIds = {}
        self._zoneNamesById = {}
        self._playerTeam = CAPTURE_POINT_NO_TEAM
        super(FortRushMinimapPingPlugin, self).stop()
        return

    def _onCapturePointUpdate(self, event):
        name = (event.capturablePointName or '').upper()
        if name:
            self._zoneOwners[name] = event.ownersTeam
            zoneId = self._getZoneTargetId(name)
            self._zoneIds[name] = zoneId
            self._zoneNamesById[zoneId] = name

    def _onCommandReceived(self, command):
        if not command.isBaseRelatedCommand():
            return
        zoneName = (command.getCommandData()['strArg1'] or '').upper()
        if not zoneName:
            return
        cmdName = _resolveCommandName(command)
        if cmdName in _PING_COMMANDS:
            self.parentObj.as_showZonePingS(zoneName)
        elif cmdName in _COMMIT_COMMANDS:
            self.parentObj.as_showZoneCommitS(zoneName)

    def _onCommandRemoved(self, targetID, markerType):
        if markerType != MarkerType.BASE_MARKER_TYPE:
            return
        zoneName = self._zoneNamesById.get(targetID)
        if zoneName:
            self.parentObj.as_clearZonePingS(zoneName)

    def _onReplyFeedbackReceived(self, targetID, replierID, markerType, oldReplyCount, newReplyCount):
        if markerType != MarkerType.BASE_MARKER_TYPE:
            return
        if newReplyCount <= oldReplyCount:
            return
        zoneName = self._zoneNamesById.get(targetID)
        if zoneName:
            self.parentObj.as_showZoneCommitS(zoneName)

    def hideHintPanel(self, instantHide=False):
        if instantHide:
            self.parentObj.as_disableHintPanelS()

    def _getZoneOwner(self, zoneName):
        return self._zoneOwners.get(zoneName.upper(), CAPTURE_POINT_NO_TEAM)

    def _getZoneId(self, zoneName):
        name = (zoneName or '').upper()
        zoneId = self._zoneIds.get(name)
        if zoneId is None and name:
            zoneId = self._getZoneTargetId(name)
            self._zoneIds[name] = zoneId
            self._zoneNamesById[zoneId] = name
        return zoneId

    @staticmethod
    def _getZoneTargetId(zoneName):
        zoneName = (zoneName or '').upper()
        if zoneName:
            chID = ord(zoneName[0])
            if _ZONE_NAME_A_ID <= chID <= _ZONE_NAME_Z_ID:
                return getUniqueTeamOrControlPointID(_ZONE_TARGET_TEAM_ID, chID - _ZONE_NAME_A_ID + 1)
        _logger.warning('[FORT_RUSH] [MINIMAP] Invalid zone name for chat target id: %s', zoneName)
        return getUniqueTeamOrControlPointID(_ZONE_TARGET_TEAM_ID, _ZONE_TARGET_BASE_FALLBACK)

    def _getZoneTeamNumber(self, zoneName):
        owner = self._getZoneOwner(zoneName)
        return mapOwnerTeamToMarkerTeam(owner, self._playerTeam)

    def _getZonePingCommand(self, zoneName):
        teamNumber = self._getZoneTeamNumber(zoneName)
        return BATTLE_CHAT_COMMAND_NAMES.DEFEND_BASE if teamNumber == 1 else BATTLE_CHAT_COMMAND_NAMES.ATTACK_BASE

    def _getZoneCommitCommand(self, zoneName):
        teamNumber = self._getZoneTeamNumber(zoneName)
        return BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE if teamNumber == 1 else BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE

    def _sendZoneCommand(self, zoneName):
        commands = self.sessionProvider.shared.chatCommands
        if commands is None:
            return
        else:
            uniqueId = self._getZoneId(zoneName)
            if uniqueId is None:
                _logger.warning('[FORT_RUSH] [MINIMAP] Missing zone id for zoneName=%s', zoneName)
                return
            componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
            advChatCmp = getattr(componentSystem, 'advancedChatComponent', None)
            if advChatCmp is None:
                commands.sendCommandToBase(uniqueId, self._getZonePingCommand(zoneName), zoneName)
                return
            replyState, _ = advChatCmp.getReplyStateForTargetIDAndMarkerType(uniqueId, MarkerType.BASE_MARKER_TYPE)
            if replyState is ReplyState.NO_REPLY:
                commands.sendCommandToBase(uniqueId, self._getZonePingCommand(zoneName), zoneName)
                return
            self._sendZoneCommitCommand(commands, uniqueId, zoneName)
            return

    def onZoneMarkerClicked(self, zoneName):
        self._sendZoneCommand(zoneName)

    def _sendZoneCommitCommand(self, commands, uniqueId, zoneName):
        commands.sendClearChatCommandsFromTarget(uniqueId, MarkerType.BASE_MARKER_TYPE.name)
        commands.sendCommandToBase(uniqueId, self._getZoneCommitCommand(zoneName), zoneName)
