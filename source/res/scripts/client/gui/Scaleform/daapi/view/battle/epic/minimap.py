# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/minimap.py
import logging
import os
import BigWorld
import GUI
import Math
from account_helpers import AccountSettings
from aih_constants import CTRL_MODE_NAME
from arena_component_system.sector_base_arena_component import ID_TO_BASENAME
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES, MarkerType, ReplyState
from constants import IS_DEVELOPMENT
from coordinate_system import AXIS_ALIGNED_DIRECTION as AAD
from epic_constants import EPIC_BATTLE_TEAM_ID
from gui.Scaleform.daapi.view.battle.classic.minimap import GlobalSettingsPlugin
from gui.Scaleform.daapi.view.battle.shared.minimap import settings, plugins, common
from gui.Scaleform.daapi.view.battle.shared.minimap.common import SimplePlugin
from gui.Scaleform.daapi.view.battle.shared.minimap.plugins import PersonalEntriesPlugin, ArenaVehiclesPlugin, _LOCATION_PING_RANGE, _EMinimapMouseKey
from gui.Scaleform.daapi.view.meta.EpicMinimapMeta import EpicMinimapMeta
from gui.Scaleform.genConsts.BATTLE_MINIMAP_CONSTS import BATTLE_MINIMAP_CONSTS
from gui.Scaleform.genConsts.LAYER_NAMES import LAYER_NAMES
from gui.battle_control import minimap_utils, avatar_getter
from gui.battle_control.battle_constants import PROGRESS_CIRCLE_TYPE, SECTOR_STATE_ID, FEEDBACK_EVENT_ID
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS
_C_NAME = settings.CONTAINER_NAME
_S_NAME = settings.ENTRY_SYMBOL_NAME
_EPIC_TEAM_POINTS = settings.CONTAINER_NAME.TEAM_POINTS
_EPIC_ZONES = settings.CONTAINER_NAME.ZONES
_EPIC_HQS = settings.CONTAINER_NAME.HQS
_EPIC_PROTECTION_ZONE = settings.CONTAINER_NAME.PROTECTION_ZONE
_EPIC_ICONS = settings.CONTAINER_NAME.ICONS
_RESPAWN_VISUALIZATION_ENTRY_1 = 0
_RESPAWN_VISUALIZATION_ENTRY_2 = 1
_RESPAWN_VISUALIZATION_ENTRY_3 = 2
_IS_COORDINATOR = bool(os.getenv('WOT_COORDINATOR', False))
_FRONT_LINE_DEV_VISUALIZATION_SUPPORTED = IS_DEVELOPMENT
_MINI_MINIMAP_HIGHLIGHT_PATH = '_level0.root.{}.main.minimap.mapShortcutLabel.sectorOverview.mmapAreaHighlight'.format(LAYER_NAMES.VIEWS)
_MINI_MINIMAP_SIZE = 46
_ZOOM_MODE_MIN = 1
_ZOOM_MODE_STEP = 0.5
_ZOOM_MULTIPLIER_TEXT = 'x'
_METERS_IN_1X_ZOOM = 1000
EPIC_MINIMAP_HIT_AREA = 210
_EPIC_BASE_PING_RANGE = 145
_DOWN_SCALE = 0.45
_UP_SCALE = 1.0
_MIN_RANGE_SCALE = 1.0
_MIN_BASE_SCALE = 1.0
_MAX_BASE_SCALE = 2.0
_logger = logging.getLogger(__name__)

def makeMousePositionToEpicWorldPosition(clickedX, clickedY, bounds, hitArea=EPIC_MINIMAP_HIT_AREA):
    upperLeftX, upperLeftZ, lowerRightX, lowerRightZ = bounds
    upperLeft = Math.Vector3(upperLeftX, 0, upperLeftZ)
    lowerRight = Math.Vector3(lowerRightX, 0, lowerRightZ)
    dis = lowerRight - upperLeft
    pos = upperLeft + Math.Vector3(clickedX / hitArea * dis.x, 0, clickedY / hitArea * dis.z)
    return pos


class MINIMAP_SCALE_TYPES(object):
    NO_SCALE = 0
    REAL_SCALE = 1
    ADAPTED_SCALE = 2


class EpicMinimapComponent(EpicMinimapMeta):

    def __init__(self):
        super(EpicMinimapComponent, self).__init__()
        self.__mode = None
        self.__minimapCenterPos = (-1, -1)
        self.__maxZoomMode = None
        self.__rangeScale = 1.0
        return

    def _populate(self):
        super(EpicMinimapComponent, self)._populate()
        mode = AccountSettings.getSettings('epicMinimapZoom')
        if mode > self.__maxZoomMode:
            mode = self.__maxZoomMode
        self.updateZoomMode(mode)
        self.__rangeScale = self.__calculateRangeScale(_ZOOM_MODE_MIN, self.__maxZoomMode, mode)

    def setMinimapCenterEntry(self, entryID):
        component = self.getComponent()
        if component is not None:
            component.setMinimapCenterEntry(entryID)
        return

    def changeMinimapZoom(self, mode):
        component = self.getComponent()
        if component is not None:
            self.getComponent().changeMinimapZoom(mode)
        AccountSettings.setSettings('epicMinimapZoom', mode)
        return

    def getRangeScale(self):
        return self.__rangeScale

    def setEntryParameters(self, entryId, doClip=True, scaleType=MINIMAP_SCALE_TYPES.ADAPTED_SCALE):
        self.getComponent().setEntryParameters(entryId, doClip, scaleType)

    def getPositionOfEntry(self, vID):
        plugin = self.getPlugin('vehicles')
        return plugin.getVehiclePosition(vID)

    def updateZoomMode(self, mode):
        if mode != self.__mode:
            self.__mode = mode
            self.changeMinimapZoom(self.__mode)
            self.as_setZoomModeS(self.__mode, self.__zoomText())

    def onZoomModeChanged(self, change):
        mode = self.__mode + change * _ZOOM_MODE_STEP
        if mode > self.__maxZoomMode:
            mode = self.__maxZoomMode
        elif mode < _ZOOM_MODE_MIN:
            mode = _ZOOM_MODE_MIN
        self.__rangeScale = self.__calculateRangeScale(_ZOOM_MODE_MIN, self.__maxZoomMode, mode)
        self.updateZoomMode(mode)

    def getZoomMode(self):
        return self.__mode

    def getCenterPosition(self):
        return self.getComponent().getCenterPosition()

    def getVisualBounds(self):
        return self.getComponent().getVisualBound()

    def updateSectorStates(self, states):
        self.as_updateSectorStateStatsS(states)

    def _setupPlugins(self, visitor):
        setup = super(EpicMinimapComponent, self)._setupPlugins(visitor)
        setup['settings'] = EpicGlobalSettingsPlugin
        setup['personal'] = CenteredPersonalEntriesPlugin
        setup['pinging'] = EpicMinimapPingPlugin
        if IS_DEVELOPMENT:
            setup['teleport'] = EpicTeleportPlugin
        if visitor.hasSectors():
            setup['epic_bases'] = SectorBaseEntriesPlugin
            setup['epic_sector_overlay'] = SectorOverlayEntriesPlugin
        if visitor.hasRespawns() and visitor.hasSectors():
            setup['epic_sectorstates'] = SectorStatusEntriesPlugin
            setup['protection_zones'] = ProtectionZoneEntriesPlugin
            setup['vehicles'] = RecoveringVehiclesPlugin
        if visitor.hasDestructibleEntities():
            setup['epic_hqs'] = HeadquartersStatusEntriesPlugin
        if visitor.hasStepRepairPoints():
            setup['repairs'] = StepRepairPointEntriesPlugin
        if _FRONT_LINE_DEV_VISUALIZATION_SUPPORTED:
            setup['epic_frontline'] = DevelopmentRespawnEntriesPlugin
            if _IS_COORDINATOR:
                BigWorld.player().enableFrontLineDevInfo(True)
        return setup

    def _processMinimapSize(self, minSize, maxSize):
        self.__maxZoomMode = self._getMaxZoomMode(minSize, maxSize)
        mapWidthPx, mapHeightPx = minimap_utils.metersToMinimapPixels(minSize, maxSize)
        self.as_setMapDimensionsS(mapWidthPx, mapHeightPx)

    def _createFlashComponent(self):
        comp = GUI.WGScrollingMinimapGUIComponentAS3(self.app.movie, settings.MINIMAP_COMPONENT_PATH)
        comp.setMiniMinimapHighlightProps(_MINI_MINIMAP_HIGHLIGHT_PATH, _MINI_MINIMAP_SIZE)
        return comp

    def _getMaxZoomMode(self, bl, tr):
        topRightX, topRightY = tr
        bottomLeftX, bottomLeftY = bl
        d1 = abs(topRightX - bottomLeftX)
        d2 = abs(topRightY - bottomLeftY)
        return max(d1, d2) / _METERS_IN_1X_ZOOM

    def __zoomText(self):
        return str(round(self.__mode, 1)) + _ZOOM_MULTIPLIER_TEXT

    def __calculateRangeScale(self, minScale, maxScale, current):
        if minScale == maxScale:
            return _MIN_RANGE_SCALE
        p = (current - minScale) / (maxScale - minScale)
        return (1 - p) * _DOWN_SCALE + p * _UP_SCALE


class RecoveringVehiclesPlugin(ArenaVehiclesPlugin):

    def start(self):
        super(RecoveringVehiclesPlugin, self).start()
        arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onVehicleRecovered += self.__arena_onVehicleRecovered
        return

    def stop(self):
        super(RecoveringVehiclesPlugin, self).stop()
        arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onVehicleRecovered -= self.__arena_onVehicleRecovered
        return

    def __arena_onVehicleRecovered(self, vehicleID):
        if vehicleID in self._entries:
            entry = self._entries[vehicleID]
            if entry.setActive(False):
                self._setActive(entry.getID(), False)


class RespawningPersonalEntriesPlugin(PersonalEntriesPlugin):
    __slots__ = ('__lastCtrlMode',)
    RESPAWN_MODES = (CTRL_MODE_NAME.DEATH_FREE_CAM, CTRL_MODE_NAME.RESPAWN_DEATH)

    def __init__(self, parentObj):
        super(RespawningPersonalEntriesPlugin, self).__init__(parentObj)
        self.setDefaultViewRangeCircleSize(1000.0)
        self.__lastCtrlMode = None
        return

    def initControlMode(self, mode, available):
        super(RespawningPersonalEntriesPlugin, self).initControlMode(mode, available)
        if self._getViewRangeCirclesID() >= 0:
            self._parentObj.setEntryParameters(self._getViewRangeCirclesID(), doClip=False, scaleType=MINIMAP_SCALE_TYPES.REAL_SCALE)
        if self._getViewPointID() >= 0:
            self._parentObj.setEntryParameters(self._getViewPointID(), doClip=False, scaleType=MINIMAP_SCALE_TYPES.ADAPTED_SCALE)
        if self._getAnimationID() >= 0:
            self._parentObj.setEntryParameters(self._getAnimationID(), doClip=False)
        for cam in self._getCameraIDs():
            if self._getCameraIDs()[cam] >= 0:
                if cam not in [_S_NAME.STRATEGIC_CAMERA]:
                    self._parentObj.setEntryParameters(self._getCameraIDs()[cam], doClip=False)
                else:
                    self._parentObj.setEntryParameters(self._getCameraIDs()[cam], doClip=False, scaleType=MINIMAP_SCALE_TYPES.REAL_SCALE)

    def updateControlMode(self, mode, vehicleID):
        super(RespawningPersonalEntriesPlugin, self).updateControlMode(mode, vehicleID)
        if mode in self.RESPAWN_MODES:
            self._hideMarkup()
            if not self._isInVideoMode():
                self.clearCamera()
        elif self.__lastCtrlMode in self.RESPAWN_MODES:
            super(RespawningPersonalEntriesPlugin, self)._invalidateMarkup(True)
        self.__lastCtrlMode = mode

    def updateSettings(self, diff):
        if self._ctrlMode not in self.RESPAWN_MODES:
            super(RespawningPersonalEntriesPlugin, self).updateSettings(diff)

    def _invalidateMarkup(self, forceInvalidate=False):
        if self._ctrlMode not in self.RESPAWN_MODES:
            super(RespawningPersonalEntriesPlugin, self)._invalidateMarkup(forceInvalidate)

    def _enableCameraEntryInCtrlMode(self, ctrlMode):
        return False if ctrlMode == CTRL_MODE_NAME.RESPAWN_DEATH else True

    def _updateCirlcesState(self):
        if not self._isInPostmortemMode() and not self._isInRespawnDeath():
            super(RespawningPersonalEntriesPlugin, self)._updateCirlcesState()


class CenteredPersonalEntriesPlugin(RespawningPersonalEntriesPlugin):
    __slots__ = ('__savedEntry', '__mode')

    def __init__(self, parentObj):
        super(CenteredPersonalEntriesPlugin, self).__init__(parentObj)
        self.__savedEntry = -1
        self.__mode = None
        return

    def initControlMode(self, mode, available):
        super(CenteredPersonalEntriesPlugin, self).initControlMode(mode, available)
        self.__centerMapBasedOnMode()

    def updateControlMode(self, mode, vehicleID):
        super(CenteredPersonalEntriesPlugin, self).updateControlMode(mode, vehicleID)
        self.__centerMapBasedOnMode()

    def _getPostmortemCenterEntry(self):
        iah = avatar_getter.getInputHandler()
        if iah and iah.ctrls[CTRL_MODE_NAME.POSTMORTEM].altTargetMode == CTRL_MODE_NAME.DEATH_FREE_CAM:
            newEntryID = self._getViewPointID()
        else:
            newEntryID = self._getDeadPointID()
        return newEntryID

    def __centerMapBasedOnMode(self):
        if self._isInPostmortemMode():
            newEntryID = self._getPostmortemCenterEntry()
            self.__mode = CTRL_MODE_NAME.POSTMORTEM
        elif self._isInStrategicMode():
            newEntryID = self._getCameraIDs()[_S_NAME.STRATEGIC_CAMERA]
            self.__mode = CTRL_MODE_NAME.STRATEGIC
        elif self._isInArcadeMode():
            newEntryID = self._getViewPointID()
            self.__mode = CTRL_MODE_NAME.ARCADE
        elif self._isInVideoMode():
            newEntryID = self._getCameraIDs()[_S_NAME.VIDEO_CAMERA]
            self.__mode = CTRL_MODE_NAME.DEATH_FREE_CAM
        else:
            newEntryID = self._getViewPointID()
            self.__mode = None
        if self.__savedEntry != newEntryID:
            self._parentObj.setMinimapCenterEntry(newEntryID)
            self.__savedEntry = newEntryID
        return


class SectorBaseEntriesPlugin(common.EntriesPlugin):
    __slots__ = ('__personalTeam', '__markerIDs', '__symbolAlly', '__symbolEnemy', '__hasActiveCommit')

    def __init__(self, parentObj, symbolAlly=_S_NAME.EPIC_SECTOR_ALLY_BASE, symbolEnemy=_S_NAME.EPIC_SECTOR_ENEMY_BASE):
        super(SectorBaseEntriesPlugin, self).__init__(parentObj)
        self.__markerIDs = {}
        self.__personalTeam = -1
        self.__symbolAlly = symbolAlly
        self.__symbolEnemy = symbolEnemy
        self.__hasActiveCommit = False

    def start(self):
        super(SectorBaseEntriesPlugin, self).start()
        self.__personalTeam = self._arenaDP.getNumberOfTeam()
        sectorBaseComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'sectorBaseComponent', None)
        if sectorBaseComp is not None:
            sectorBaseComp.onSectorBaseAdded += self.__onSectorBaseAdded
            sectorBaseComp.onSectorBaseCaptured += self.__onSectorBaseCaptured
            sectorBaseComp.onSectorBasePointsUpdate += self.__onSectorBasePointsUpdate
            for base in sectorBaseComp.sectorBases:
                self.__onSectorBaseAdded(base)
                if 0 < base.capturePercentage < 1:
                    self.__onSectorBasePointsUpdate(base.baseID, base.isPlayerTeam(), base.capturePercentage, base.capturingStopped, 0, '')

        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onActionAddedToMarkerReceived += self.__onActionAddedToObjectiveMarkerReceived
            ctrl.onReplyFeedbackReceived += self.__onReplyFeedbackReceived
            ctrl.onRemoveCommandReceived += self.__onRemoveCommandReceived
        else:
            _logger.error('Seesion Provider Feedback present - Could not set marker receiver events!')
        return

    def fini(self):
        super(SectorBaseEntriesPlugin, self).fini()
        sectorBaseComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'sectorBaseComponent', None)
        if sectorBaseComp is not None:
            sectorBaseComp.onSectorBaseAdded -= self.__onSectorBaseAdded
            sectorBaseComp.onSectorBaseCaptured -= self.__onSectorBaseCaptured
            sectorBaseComp.onSectorBasePointsUpdate -= self.__onSectorBasePointsUpdate
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onActionAddedToMarkerReceived -= self.__onActionAddedToObjectiveMarkerReceived
            ctrl.onReplyFeedbackReceived -= self.__onReplyFeedbackReceived
            ctrl.onRemoveCommandReceived -= self.__onRemoveCommandReceived
        return

    def __onSectorBaseAdded(self, sectorBase):
        symbol = self.__symbolEnemy
        if sectorBase.isPlayerTeam():
            symbol = self.__symbolAlly
        model = self.__markerIDs[sectorBase.baseID] = self.__addPointEntry(symbol, sectorBase)
        if model is not None:
            self._invoke(model.getID(), 'setOwningTeam', sectorBase.isPlayerTeam())
            self._invoke(model.getID(), 'setIdentifier', sectorBase.baseID)
            self._invoke(model.getID(), BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_DEFAULT)
        return

    def __onSectorBaseCaptured(self, baseId, isPlayerTeam):
        model = self.__markerIDs[baseId]
        if model is None:
            _logger.error('[ZoneBaseEntriesPlugins:__onSectorBaseCaptured] NO ENTRY WITH ID: %d', baseId)
            return
        else:
            self._invoke(model.getID(), 'setCapturePoints', 1)
            self._invoke(model.getID(), 'setOwningTeam', isPlayerTeam)
            self._invoke(model.getID(), BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_DEFAULT)
            return

    def __onSectorBasePointsUpdate(self, baseId, isPlayerTeam, points, capturingStopped, invadersCount, expectedCaptureTime):
        model = self.__markerIDs[baseId]
        if model is None:
            _logger.error('[ZoneBaseEntriesPlugins:__onSectorBasePointsUpdate] NO ENTRY WITH ID: %d', baseId)
            return
        else:
            self._invoke(model.getID(), 'setCapturePoints', points)
            return

    def __addPointEntry(self, symbol, sectorBase):
        matrix = Math.Matrix()
        matrix.setTranslate(sectorBase.position)
        return self._addEntryEx(sectorBase.baseID, symbol, _EPIC_TEAM_POINTS, matrix, True)

    def __onActionAddedToObjectiveMarkerReceived(self, senderID, commandID, markerType, objectID):
        if markerType != MarkerType.BASE_MARKER_TYPE or objectID not in self.__markerIDs:
            return
        else:
            model = self.__markerIDs[objectID]
            if model is None:
                return
            if _ACTIONS.battleChatCommandFromActionID(commandID).name in (BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE, BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE):
                self.__onReplyFeedbackReceived(objectID, senderID, MarkerType.BASE_MARKER_TYPE, 0, 1)
                return
            self._invoke(model.getID(), BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_ATTACK)
            return

    def __onReplyFeedbackReceived(self, ucmdID, replierID, markerType, oldReplyCount, newReplyCount):
        if markerType != MarkerType.BASE_MARKER_TYPE or ucmdID not in self.__markerIDs:
            return
        playerHasReplied = replierID == avatar_getter.getPlayerVehicleID()
        if newReplyCount > oldReplyCount:
            if playerHasReplied:
                self._invoke(self.__markerIDs[ucmdID].getID(), BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_REPLY)
                self.__hasActiveCommit = True
            elif not self.__hasActiveCommit:
                self._invoke(self.__markerIDs[ucmdID].getID(), BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_IDLE)
            return
        if newReplyCount < oldReplyCount and playerHasReplied or newReplyCount <= 0:
            self._invoke(self.__markerIDs[ucmdID].getID(), BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_IDLE)
            if playerHasReplied:
                self.__hasActiveCommit = False

    def __onRemoveCommandReceived(self, removeID, markerType):
        if not self.__markerIDs or markerType != MarkerType.BASE_MARKER_TYPE or removeID not in self.__markerIDs:
            return
        self._invoke(self.__markerIDs[removeID].getID(), BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_DEFAULT)


class SectorStatusEntriesPlugin(SimplePlugin):
    __slots__ = ('__personalTeam', '_zonesDict', '_symbol', '_posDict')

    def __init__(self, parentObj):
        super(SectorStatusEntriesPlugin, self).__init__(parentObj)
        self._zonesDict = {}
        self._posDict = {}
        self.__personalTeam = -1
        self._symbol = _S_NAME.EPIC_SECTOR

    def start(self):
        super(SectorStatusEntriesPlugin, self).start()
        self.__personalTeam = self._arenaDP.getNumberOfTeam()
        sectorComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'sectorComponent', None)
        if sectorComp is not None:
            sectorComp.onSectorGroupUpdated += self.__onSectorGroupUpdated
            sectorComp.onPlayerSectorGroupChanged += self._onPlayerSectorGroupChanged
            sectorGroups = sectorComp.sectorGroups
            for groupID in sectorGroups:
                group = sectorGroups[groupID]
                self.__onSectorGroupUpdated(group.id, group.state, group.center, group.getBound())

        else:
            _logger.error('Expected SectorComponent not present!')
        return

    def fini(self):
        super(SectorStatusEntriesPlugin, self).fini()
        sectorComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'sectorComponent', None)
        if sectorComp is not None:
            sectorComp.onSectorGroupUpdated -= self.__onSectorGroupUpdated
            sectorComp.onPlayerSectorGroupChanged -= self._onPlayerSectorGroupChanged
        return

    def _onPlayerSectorGroupChanged(self, newSectorGroupID, isAllowed, oldSectorGroupID, wasAllowed):
        if oldSectorGroupID is not None and not wasAllowed and oldSectorGroupID in self._zonesDict:
            oldEntryID = self._zonesDict[oldSectorGroupID]
            self._invoke(oldEntryID, 'setWarning', False)
        if not isAllowed and newSectorGroupID in self._zonesDict:
            newEntryID = self._zonesDict[newSectorGroupID]
            self._invoke(newEntryID, 'setWarning', True)
        return

    def __onSectorGroupUpdated(self, sectorGroupId, state, center, bounds):
        sectorComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'sectorComponent', None)
        if sectorGroupId not in self._zonesDict:
            self._zonesDict[sectorGroupId] = self.__addZoneEntry(self._symbol, center)
            self._posDict[sectorGroupId] = center
        elif self._posDict[sectorGroupId] != center:
            matrix = Math.Matrix()
            matrix.setTranslate(center)
            sectorGroup = self._zonesDict[sectorGroupId]
            self._setMatrix(sectorGroup, matrix)
            self._posDict[sectorGroupId] = center
        entryID = self._zonesDict[sectorGroupId]
        if entryID is not None:
            sectorStateID = SECTOR_STATE_ID[state]
            if sectorComponent is not None and sectorGroupId in sectorComponent.sectorGroups:
                group = sectorComponent.sectorGroups[sectorGroupId]
                self._invoke(entryID, 'changeSectorState', sectorStateID, self.__personalTeam == EPIC_BATTLE_TEAM_ID.TEAM_ATTACKER, group.numSubSectors > 1)
            else:
                _logger.error('Expected SectorComponent not present!')
        sectors = []
        for groupID in sectorComponent.sectorGroups:
            group = sectorComponent.sectorGroups[groupID]
            sectors.append(SECTOR_STATE_ID[group.state])

        data = dict()
        data['amount'] = len(sectorComponent.sectorGroups)
        data['sectors'] = sectors
        self.parentObj.updateSectorStates(data)
        return

    def __addZoneEntry(self, symbol, position):
        matrix = Math.Matrix()
        matrix.setTranslate(position)
        entryID = self._addEntry(symbol, _EPIC_ZONES, matrix=matrix, active=True)
        self._parentObj.setEntryParameters(entryID, doClip=False, scaleType=MINIMAP_SCALE_TYPES.REAL_SCALE)
        return entryID


class HeadquartersStatusEntriesPlugin(SimplePlugin):
    __slots__ = ('__hqsDict', '__symbolAlly', '__symbolEnemy', '__hasActiveCommit')

    def __init__(self, parentObj, symbolAlly=_S_NAME.EPIC_HQ_ALLY, symbolEnemy=_S_NAME.EPIC_HQ_ENEMY):
        super(HeadquartersStatusEntriesPlugin, self).__init__(parentObj)
        self.__hqsDict = {}
        self.__symbolAlly = symbolAlly
        self.__symbolEnemy = symbolEnemy
        self.__hasActiveCommit = False

    def start(self):
        super(HeadquartersStatusEntriesPlugin, self).start()
        destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
        if destructibleComponent is not None:
            destructibleComponent.onDestructibleEntityAdded += self.__onDestructibleEntityAdded
            destructibleComponent.onDestructibleEntityHealthChanged += self.__onDestructibleEntityHealthChanged
            hqs = destructibleComponent.destructibleEntities
            for hq in (hq for _, hq in hqs.iteritems() if hq.destructibleEntityID != 0):
                self.__onDestructibleEntityAdded(hq)

        else:
            _logger.error('Expected DestructibleEntityComponent not present!')
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onReplyFeedbackReceived += self.__onReplyFeedbackReceived
            ctrl.onRemoveCommandReceived += self.__onRemoveCommandReceived
            ctrl.onMinimapFeedbackReceived += self.__onMinimapFeedbackReceived
        return

    def fini(self):
        super(HeadquartersStatusEntriesPlugin, self).fini()
        destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
        if destructibleComponent is not None:
            destructibleComponent.onDestructibleEntityAdded -= self.__onDestructibleEntityAdded
            destructibleComponent.onDestructibleEntityHealthChanged -= self.__onDestructibleEntityHealthChanged
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onReplyFeedbackReceived -= self.__onReplyFeedbackReceived
            ctrl.onRemoveCommandReceived -= self.__onRemoveCommandReceived
            ctrl.onMinimapFeedbackReceived -= self.__onMinimapFeedbackReceived
        return

    def __onDestructibleEntityAdded(self, entity):
        symbol = self.__symbolEnemy
        if entity.isPlayerTeam:
            symbol = self.__symbolAlly
        entryID = self.__hqsDict[entity.destructibleEntityID] = self.__addHQEntry(symbol, entity.position)
        isDead = entity.health == 0
        if entryID is not None:
            self._invoke(entryID, 'setOwningTeam', entity.isPlayerTeam)
            self._invoke(entryID, 'setIdentifier', entity.destructibleEntityID)
            self._invoke(entryID, 'setDead', isDead)
            self._invoke(entryID, BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_DEFAULT)
        return

    def __onDestructibleEntityHealthChanged(self, destructibleEntityID, newHealth, maxHealth, atkID, atkReason, hitFlags):
        if newHealth != 0:
            return
        else:
            entryID = self.__hqsDict[destructibleEntityID]
            if entryID is not None:
                self._invoke(entryID, 'setDead', True)
            return

    def __addHQEntry(self, symbol, position):
        matrix = Math.Matrix()
        matrix.setTranslate(position)
        entryID = self._addEntry(symbol, _EPIC_HQS, matrix=matrix, active=True)
        return entryID

    def __onMinimapFeedbackReceived(self, eventID, entityID, value):
        if eventID == FEEDBACK_EVENT_ID.MINIMAP_MARK_OBJECTIVE:
            self.__onActionAddedToMarkerReceived(entityID, *value)

    def __onActionAddedToMarkerReceived(self, senderID, hqId, duration, cmdName):
        if hqId not in self.__hqsDict:
            return
        modelID = self.__hqsDict[hqId]
        if modelID == 0:
            return
        if cmdName in (BATTLE_CHAT_COMMAND_NAMES.ATTACKING_OBJECTIVE, BATTLE_CHAT_COMMAND_NAMES.DEFENDING_OBJECTIVE):
            self.__onReplyFeedbackReceived(hqId, senderID, MarkerType.HEADQUARTER_MARKER_TYPE, 0, 1)
            return
        self._invoke(modelID, BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_ATTACK)

    def __onReplyFeedbackReceived(self, ucmdID, replierID, markerType, oldReplyCount, newReplyCount):
        if markerType != MarkerType.HEADQUARTER_MARKER_TYPE or ucmdID not in self.__hqsDict:
            return
        playerHasReplied = replierID == avatar_getter.getPlayerVehicleID()
        if newReplyCount > oldReplyCount:
            if playerHasReplied:
                self._invoke(self.__hqsDict[ucmdID], BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_REPLY)
                self.__hasActiveCommit = True
            elif not self.__hasActiveCommit:
                self._invoke(self.__hqsDict[ucmdID], BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_IDLE)
        elif newReplyCount < oldReplyCount and replierID == avatar_getter.getPlayerVehicleID() or newReplyCount <= 0:
            self._invoke(self.__hqsDict[ucmdID], BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_IDLE)
            if playerHasReplied:
                self.__hasActiveCommit = False

    def __onRemoveCommandReceived(self, removeID, markerType):
        if not self.__hqsDict or markerType != MarkerType.HEADQUARTER_MARKER_TYPE or removeID not in self.__hqsDict:
            return
        self._invoke(self.__hqsDict[removeID], BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_DEFAULT)


class DevelopmentRespawnEntriesPlugin(SimplePlugin):
    __slots__ = ('__markers',)

    def __init__(self, parentObj):
        super(DevelopmentRespawnEntriesPlugin, self).__init__(parentObj)
        self.__markers = []

    def start(self):
        super(DevelopmentRespawnEntriesPlugin, self).start()
        player = BigWorld.player()
        if player is not None:
            player.onFrontLineInfoUpdated += self.__onFrontLineInfoUpdated
        return

    def fini(self):
        super(DevelopmentRespawnEntriesPlugin, self).fini()
        player = BigWorld.player()
        if player is not None and hasattr(player, 'onFrontLineInfoUpdated'):
            player.onFrontLineInfoUpdated -= self.__onFrontLineInfoUpdated
        return

    def __onFrontLineInfoUpdated(self, frontlinePoints, attackerIntruder, defenderIntruder):
        symbol = _S_NAME.EPIC_FLP
        while self.__markers:
            self._delEntry(self.__markers.pop())

        for flp in frontlinePoints:
            entryID = self.__addRPEntry(symbol, flp)
            self.__markers.append(entryID)
            if entryID is not None:
                self._invoke(entryID, 'setMarkerType', _RESPAWN_VISUALIZATION_ENTRY_1)

        for flp in attackerIntruder:
            entryID = self.__addRPEntry(symbol, flp)
            self.__markers.append(entryID)
            if entryID is not None:
                self._invoke(entryID, 'setMarkerType', _RESPAWN_VISUALIZATION_ENTRY_2)

        for flp in defenderIntruder:
            entryID = self.__addRPEntry(symbol, flp)
            self.__markers.append(entryID)
            if entryID is not None:
                self._invoke(entryID, 'setMarkerType', _RESPAWN_VISUALIZATION_ENTRY_3)

        return

    def __addRPEntry(self, symbol, pos):
        position = (pos.x, 0, pos.y)
        matrix = Math.Matrix()
        matrix.setTranslate(position)
        return self._addEntry(symbol, _EPIC_TEAM_POINTS, matrix=matrix, active=True)


class EpicGlobalSettingsPlugin(GlobalSettingsPlugin):

    def _toogleVisible(self):
        pass


class StepRepairPointEntriesPlugin(SimplePlugin):
    __slots__ = ('__ptDict',)

    def __init__(self, parentObj):
        super(StepRepairPointEntriesPlugin, self).__init__(parentObj)
        self.__ptDict = {}

    def start(self):
        super(StepRepairPointEntriesPlugin, self).start()
        stepRepairPointComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'stepRepairPointComponent', None)
        if stepRepairPointComponent is not None:
            stepRepairPointComponent.onStepRepairPointAdded += self.__onStepRepairPointAdded
            stepRepairPointComponent.onStepRepairPointActiveStateChanged += self.__onStepRepairPointActiveStateChanged
            repairPts = stepRepairPointComponent.stepRepairPoints
            for pt in repairPts:
                self.__onStepRepairPointAdded(pt)

        else:
            _logger.error('Expected StepRepairPointComponent not present!')
        ctrl = self.sessionProvider.dynamic.progressTimer
        ctrl.onCircleStatusChanged += self.__onCircleStatusChanged
        return

    def fini(self):
        super(StepRepairPointEntriesPlugin, self).fini()
        stepRepairPointComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'stepRepairPointComponent', None)
        if stepRepairPointComponent is not None:
            stepRepairPointComponent.onStepRepairPointAdded -= self.__onStepRepairPointAdded
            stepRepairPointComponent.onStepRepairPointActiveStateChanged -= self.__onStepRepairPointActiveStateChanged
        ctrl = self.sessionProvider.dynamic.progressTimer
        if ctrl is not None:
            ctrl.onCircleStatusChanged -= self.__onCircleStatusChanged
        return

    def __onCircleStatusChanged(self, type_, pointId, state):
        if type_ is not PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        entryID = self.__ptDict[pointId]
        self._parentObj.invoke(entryID, BATTLE_MINIMAP_CONSTS.SET_STATE, state)

    def __onStepRepairPointAdded(self, stepRepairPoint):
        symbol = _S_NAME.EPIC_REPAIR
        entryID = self.__ptDict[stepRepairPoint.id] = self.__addRPEntry(symbol, stepRepairPoint.position)
        self._parentObj.invoke(entryID, 'setActive', stepRepairPoint.isActiveForPlayerTeam())

    def __onStepRepairPointActiveStateChanged(self, pointId, isActive):
        entryID = self.__ptDict[pointId]
        if entryID is not None:
            self._parentObj.invoke(entryID, 'setActive', isActive)
        return

    def __addRPEntry(self, symbol, position):
        matrix = Math.Matrix()
        matrix.setTranslate(position)
        entryID = self._addEntry(symbol, _EPIC_ICONS, matrix=matrix, active=True)
        return entryID


class ProtectionZoneEntriesPlugin(SimplePlugin):
    __slots__ = ('__personalTeam', '_zonesDict', '_symbol')

    def __init__(self, parentObj):
        super(ProtectionZoneEntriesPlugin, self).__init__(parentObj)
        self._zonesDict = {}
        self.__personalTeam = -1
        self._symbol = _S_NAME.EPIC_PROTECTION_ZONE

    def start(self):
        super(ProtectionZoneEntriesPlugin, self).start()
        self.__personalTeam = self._arenaDP.getNumberOfTeam()
        protZoneComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'protectionZoneComponent', None)
        if protZoneComp is not None:
            protZoneComp.onProtectionZoneAdded += self.__onProtZoneAdded
            protZones = protZoneComp.protectionZones
            for zone in protZones.values():
                self.__onProtZoneAdded(zone.zoneID, zone.position, zone.bound)

        else:
            _logger.error('Expected ProtectionZoneComponent not present!')
        return

    def fini(self):
        super(ProtectionZoneEntriesPlugin, self).fini()
        protZoneComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'protectionZoneComponent', None)
        if protZoneComp is not None:
            protZoneComp.onProtectionZoneAdded -= self.__onProtZoneAdded
        return

    def __onProtZoneAdded(self, protZone, center, bounds):
        lowerleft, upperright = bounds
        protZoneComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'protectionZoneComponent', None)
        if protZoneComp is None:
            _logger.error('Expected ProtectionZoneComponent not present!')
            return
        else:
            zone = protZoneComp.getProtectionZoneById(protZone)
            if zone is None:
                return
            isPlayerTeam = self.__personalTeam == zone.team
            isVertical = avatar_getter.getArena().arenaType.epicSectorGrid.mainDirection in (AAD.PLUS_Z, AAD.MINUS_Z)
            frontPosition = upperright if zone.team == EPIC_BATTLE_TEAM_ID.TEAM_ATTACKER else lowerleft
            frontPosition = (center.x if isVertical else center.y, 0, frontPosition.y if isVertical else frontPosition.x)
            if protZone not in self._zonesDict:
                self._zonesDict[protZone] = entryID = self.__addProtectionZoneEntry(self._symbol, frontPosition)
            else:
                entryID = self._zonesDict[protZone]
            if entryID is not None:
                self._invoke(entryID, 'setOwningTeam', isPlayerTeam)
            return

    def __addProtectionZoneEntry(self, symbol, position):
        matrix = Math.Matrix()
        matrix.setTranslate(position)
        entryID = self._addEntry(symbol, _EPIC_PROTECTION_ZONE, matrix=matrix, active=True)
        self._parentObj.setEntryParameters(entryID, doClip=False, scaleType=MINIMAP_SCALE_TYPES.REAL_SCALE)
        return entryID


class SectorOverlayEntriesPlugin(SectorStatusEntriesPlugin):

    def __init__(self, parentObj):
        super(SectorOverlayEntriesPlugin, self).__init__(parentObj)
        self._symbol = _S_NAME.EPIC_SECTOR_OVERLAY

    def start(self):
        super(SectorOverlayEntriesPlugin, self).start()
        ctrl = self.sessionProvider.dynamic.maps
        if ctrl:
            ctrl.onOverlayTriggered += self.__onOverlayTriggered
            self.__onOverlayTriggered(ctrl.overlayActive)
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnVisibilityChanged += self.__onRespawnVisibility
        return

    def fini(self):
        super(SectorOverlayEntriesPlugin, self).fini()
        ctrl = self.sessionProvider.dynamic.maps
        if ctrl:
            ctrl.onOverlayTriggered -= self.__onOverlayTriggered
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnVisibilityChanged -= self.__onRespawnVisibility
        return

    def _onPlayerSectorGroupChanged(self, newSectorGroupID, isAllowed, oldSectorGroupID, wasAllowed):
        pass

    def __onOverlayTriggered(self, isActive):
        for key in self._zonesDict:
            entryID = self._zonesDict[key]
            self._setActive(entryID, isActive)

    def __onRespawnVisibility(self, visible):
        if not visible:
            return
        self.__onOverlayTriggered(True)


class EpicMinimapPingPlugin(plugins.MinimapPingPlugin):

    def __init__(self, parentObj):
        super(EpicMinimapPingPlugin, self).__init__(parentObj)
        self.__baseInteractionList = {}
        self.__hqInteractionActive = False
        self._hitAreaSize = minimap_utils.EPIC_MINIMAP_HIT_AREA

    def start(self):
        super(EpicMinimapPingPlugin, self).start()
        sectorBaseComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'sectorBaseComponent', None)
        if sectorBaseComponent is not None:
            sectorBases = sectorBaseComponent.sectorBases
            for base in sectorBases:
                self.__onSectorBaseAdded(base)

        missionCtrl = self.sessionProvider.dynamic.missions
        if missionCtrl is not None:
            missionCtrl.onPlayerMissionUpdated += self._onPlayerMissionUpdated
        return

    def stop(self):
        super(EpicMinimapPingPlugin, self).stop()
        missionCtrl = self.sessionProvider.dynamic.missions
        if missionCtrl is not None:
            missionCtrl.onPlayerMissionUpdated -= self._onPlayerMissionUpdated
        return

    def _onPlayerMissionUpdated(self, mission, _):
        if mission.isBaseMission():
            if mission.id in self.__baseInteractionList:
                self.__baseInteractionList[mission.id] = True
        elif mission.isObjectivesMission():
            self.__hqInteractionActive = True

    def _getClickPosition(self, x, y):
        return makeMousePositionToEpicWorldPosition(x, y, self._parentObj.getVisualBounds(), self._hitAreaSize)

    def _getIdByBaseNumber(self, team, number):
        return number

    def _processCommandByPosition(self, commands, locationCommand, position, minimapScaleIndex):
        minimapScale = minimap_utils.getMinimapBasePingScale(minimapScaleIndex, _MIN_BASE_SCALE, _MAX_BASE_SCALE)
        scaledBaseRange = _EPIC_BASE_PING_RANGE / minimapScale * self.parentObj.getRangeScale()
        hqIdx, hqTeam = self.__getNearestHQForPosition(position, scaledBaseRange)
        if hqIdx:
            self.__make3DPingHQ(commands, (hqTeam, 0, hqIdx))
            return
        else:
            baseIdx, baseTeam, baseName = self.__getNearestBaseForPosition(position, scaledBaseRange)
            if baseIdx:
                self._make3DPingBases(commands, (baseTeam, 0, baseIdx), baseName)
                return
            locationID = self._getNearestLocationIDForPosition(position, _LOCATION_PING_RANGE)
            if locationID is not None:
                self._replyPing3DMarker(commands, locationID)
                return
            commands.sendAttentionToPosition3D(position, locationCommand)
            return

    def __make3DPingHQ(self, commands, bases):
        advChatCmp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'advancedChatComponent', None)
        if advChatCmp is None:
            return
        else:
            team, _, number = bases
            uniqueId = self._getIdByBaseNumber(team, number)
            replyState, commandKey = advChatCmp.getReplyStateForTargetIDAndMarkerType(uniqueId, MarkerType.HEADQUARTER_MARKER_TYPE)
            if replyState is ReplyState.NO_REPLY:
                commands.sendAttentionToObjective(number, self._arenaDP.getNumberOfTeam() != team)
                return
            self._processReplyCommand(replyState, commands, uniqueId, commandKey)
            return

    def __onSectorBaseAdded(self, sectorBase):
        self.__baseInteractionList[sectorBase.baseID] = False

    def __getNearestHQForPosition(self, clickPos, range_):
        destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
        if destructibleComponent is None:
            _logger.error('Expected DestructibleEntityComponent not present!')
            return (None, None)
        else:
            closestHqIdx, distance = destructibleComponent.getNearestDestructibleEntityID(clickPos)
            destEntity = destructibleComponent.getDestructibleEntity(closestHqIdx)
            return (closestHqIdx, destEntity.team) if distance <= range_ and (destEntity.isActive or self.__hqInteractionActive) else (None, None)

    def __getNearestBaseForPosition(self, clickPos, range_):
        sectorBaseComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'sectorBaseComponent', None)
        if sectorBaseComponent is None:
            _logger.error('Expected SectorBaseComponent not present!')
            return (None, None, None)
        else:
            openBases = [ base for base in sectorBaseComponent.sectorBases if not base.isCaptured and base.active() or self.__baseInteractionList[base.baseID] ]
            if not openBases:
                return (None, None, None)

            def getDistance(entity):
                return entity.position.flatDistTo(clickPos)

            closestBase = min(openBases, key=getDistance)
            return (closestBase.baseID, closestBase.team, ID_TO_BASENAME[closestBase.baseID]) if getDistance(closestBase) <= range_ else (None, None, None)


class EpicTeleportPlugin(EpicMinimapPingPlugin):

    def onMinimapClicked(self, x, y, buttonIdx, minimapScaleIndex):
        if buttonIdx != _EMinimapMouseKey.KEY_MBL.value:
            return
        else:
            player = BigWorld.player()
            if player is not None and player.isTeleport:
                position = self._getClickPosition(x, y)
                result = BigWorld.collide(player.spaceID, (position.x, 1000.0, position.z), (position.x, -1000.0, position.z))
                player.base.vehicle_teleport((position[0], result[0][1], position[2]), 0)
            return
