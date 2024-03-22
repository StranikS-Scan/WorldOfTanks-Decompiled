# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/minimap/plugins.py
import logging
from collections import namedtuple
from functools import partial
import BigWorld
import Math
import typing
from death_zones_helpers import ZONES_SIZE, idxFrom
import ArenaInfo
import Placement
import math_utils
from Avatar import PlayerAvatar
from account_helpers.settings_core import settings_constants
from battle_royale.gui.Scaleform.daapi.view.battle.minimap.settings import DeathZonesAs3Descr, ViewRangeSectorAs3Descr, BattleRoyaleEntries, MarkersAs3Descr
from battle_royale.gui.shared.events import DeathZoneEvent
from battleground.location_point_manager import g_locationPointManager
from chat_commands_consts import LocationMarkerSubType
from constants import LOOT_TYPE, ARENA_BONUS_TYPE
from gui.Scaleform.daapi.view.battle.epic.minimap import CenteredPersonalEntriesPlugin, MINIMAP_SCALE_TYPES, makeMousePositionToEpicWorldPosition
from gui.Scaleform.daapi.view.battle.shared.minimap import settings
from gui.Scaleform.daapi.view.battle.shared.minimap.common import SimplePlugin, EntriesPlugin, IntervalPlugin
from gui.Scaleform.daapi.view.battle.shared.minimap.plugins import RadarPlugin, RadarEntryParams, RadarPluginParams, ArenaVehiclesPlugin, _RadarEntryData, MinimapPingPlugin, _LOCATION_PING_RANGE
from gui.Scaleform.daapi.view.common.battle_royale.br_helpers import getCircularVisionAngle
from gui.battle_control import matrix_factory, minimap_utils, avatar_getter
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from gui.doc_loaders.battle_royale_settings_loader import getBattleRoyaleSettings
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import AirDropEvent
from helpers import dependency
from items.battle_royale import isSpawnedBot
from skeletons.gui.battle_session import IBattleSessionProvider
_C_NAME = settings.CONTAINER_NAME
_S_NAME = settings.ENTRY_SYMBOL_NAME
_FIRTS_CELL_INDEX = 0
_ARENA_SIZE_DEATH_ZONE_MULTIPLIER = 0.5
_MARKER_SIZE_INDEX_BREAKPOINT = 3
_SQUAD_COLOR_MAP = [1,
 2,
 4,
 5,
 7,
 8,
 9,
 11,
 13,
 14]
_MINIMAP_MIN_SCALE_INDEX = 0
_MINIMAP_MAX_SCALE_INDEX = 5
_MINIMAP_LOCATION_MARKER_MIN_SCALE = 1.0
_MINIMAP_LOCATION_MARKER_MAX_SCALE = 2.33
RADAR_PLUGIN = 'radar'
VEHICLES_PLUGIN = 'vehicles'
_logger = logging.getLogger(__name__)

class BattleRoyalePersonalEntriesPlugin(CenteredPersonalEntriesPlugin):
    __slots__ = ('__viewRangeEntityID', '__restoreMatrixCbkID')
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, parentObj):
        super(BattleRoyalePersonalEntriesPlugin, self).__init__(parentObj)
        self.__viewRangeEntityID = None
        self.__restoreMatrixCbkID = None
        return

    def init(self, arenaVisitor, arenaDP):
        super(BattleRoyalePersonalEntriesPlugin, self).init(arenaVisitor, arenaDP)
        progressionCtrl = self.__guiSessionProvider.dynamic.progression
        if progressionCtrl is not None:
            progressionCtrl.onVehicleUpgradeStarted += self.__onUpgradeStarted
            progressionCtrl.onVehicleUpgradeFinished += self.__onUpgradeFinished
        return

    def initControlMode(self, mode, available):
        super(BattleRoyalePersonalEntriesPlugin, self).initControlMode(mode, available)
        bottomLeft, upperRight = self._arenaVisitor.type.getBoundingBox()
        arenaWidth, _ = upperRight - bottomLeft
        if self._isInArcadeMode():
            matrix = matrix_factory.makeVehicleTurretMatrixMP()
            entryID = self._addEntry(BattleRoyaleEntries.VIEW_RANGE_SECTOR, _C_NAME.FLAGS, matrix=matrix, active=True)
            self.__viewRangeEntityID = entryID
            self._parentObj.setEntryParameters(self.__viewRangeEntityID, doClip=False, scaleType=MINIMAP_SCALE_TYPES.REAL_SCALE)
            self._invoke(entryID, ViewRangeSectorAs3Descr.AS_INIT_ARENA_SIZE, arenaWidth)
            playerAvatar = BigWorld.player()
            vehicle = playerAvatar.getVehicleAttached()
            if vehicle is not None:
                sector = getCircularVisionAngle(vehicle)
                if sector is not None:
                    self.__addSectorEntity(sector)
            else:
                _logger.info('Initialize sector when vehicle will be created.')
                playerAvatar.onVehicleEnterWorld += self.__onVehicleEnterWorld
        return

    def fini(self):
        self.__clearVehicleHandler()
        progressionCtrl = self.__guiSessionProvider.dynamic.progression
        if progressionCtrl is not None:
            progressionCtrl.onVehicleUpgradeStarted -= self.__onUpgradeStarted
            progressionCtrl.onVehicleUpgradeFinished -= self.__onUpgradeFinished
        if self.__restoreMatrixCbkID is not None:
            BigWorld.cancelCallback(self.__restoreMatrixCbkID)
            self.__restoreMatrixCbkID = None
        super(BattleRoyalePersonalEntriesPlugin, self).fini()
        return

    def updateControlMode(self, mode, vehicleID):
        super(BattleRoyalePersonalEntriesPlugin, self).updateControlMode(mode, vehicleID)
        self.__updateViewSector()

    def _invalidateMarkup(self, forceInvalidate=False):
        super(BattleRoyalePersonalEntriesPlugin, self)._invalidateMarkup(forceInvalidate)
        self.__updateViewSector()

    def _onVehicleFeedbackReceived(self, eventID, _, __):
        vInfo = self._arenaDP.getVehicleInfo()
        if not vInfo.isObserver() and eventID == FEEDBACK_EVENT_ID.VEHICLE_ATTRS_CHANGED:
            self.__updateViewSectorRadius()

    def _updateDeadPointEntry(self, active=True):
        super(BattleRoyalePersonalEntriesPlugin, self)._updateDeadPointEntry(active)
        self.__updateViewSector()

    def _canShowMaxViewRangeCircle(self):
        return False

    def _canShowDrawRangeCircle(self):
        return False

    def _canShowViewRangeCircle(self):
        return self._isAlive()

    def _canShowMinSpottingRangeCircle(self):
        return False

    def _canShowDirectionLine(self):
        return self._isAlive()

    def _getViewRangeRadius(self):
        return self.__guiSessionProvider.arenaVisitor.getVisibilityMinRadius()

    def _getPostmortemCenterEntry(self):
        if self._isInPostmortemMode() and self._ctrlVehicleID and self._ctrlVehicleID != self._getPlayerVehicleID():
            newEntryID = self._getViewPointID()
        else:
            newEntryID = super(BattleRoyalePersonalEntriesPlugin, self)._getPostmortemCenterEntry()
        return newEntryID

    def __onVehicleEnterWorld(self, vehicle):
        playerVehId = avatar_getter.getPlayerVehicleID()
        if vehicle.id == playerVehId:
            sector = getCircularVisionAngle(vehicle)
            _logger.info('Vehicle is created and sector can be initialized now! value=%s', str(sector))
            if sector is not None:
                self.__addSectorEntity(sector)
            else:
                _logger.warning('Vehicle has no "circularVisionAngle" property. Sector could not been initialized!')
            self.__clearVehicleHandler()
        return

    def __updateViewSectorRadius(self):
        if self.__viewRangeEntityID:
            self._invoke(self.__viewRangeEntityID, ViewRangeSectorAs3Descr.AS_UPDATE_SECTOR_RADIUS, self._calcCircularVisionRadius())

    def __updateViewSector(self):
        if self.__viewRangeEntityID:
            isVisible = self._isAlive() and self._getSelectedCameraID() == self._getCameraIDs().get(_S_NAME.ARCADE_CAMERA)
            self._setActive(self.__viewRangeEntityID, isVisible)

    def __addSectorEntity(self, sector):
        self._invoke(self.__viewRangeEntityID, ViewRangeSectorAs3Descr.AS_ADD_SECTOR, self._calcCircularVisionRadius(), sector)
        self.__updateViewSectorRadius()
        self.__updateViewSector()

    def __clearVehicleHandler(self):
        playerAvatar = BigWorld.player()
        if playerAvatar and isinstance(playerAvatar, PlayerAvatar):
            playerAvatar.onVehicleEnterWorld -= self.__onVehicleEnterWorld

    def __onUpgradeStarted(self, vehicleId):
        if self.__viewRangeEntityID:
            provider = matrix_factory.makeVehicleTurretMatrixMP()
            self._setMatrix(self.__viewRangeEntityID, Math.Matrix(provider))
        lineEntryID = self.__getDirectionLineEntryID()
        if lineEntryID:
            if self._ctrlVehicleID and avatar_getter.getPlayerVehicleID() != self._ctrlVehicleID:
                provider = matrix_factory.makePostmortemCameraMatrix()
            else:
                provider = matrix_factory.makeArcadeCameraMatrix()
            self._setMatrix(lineEntryID, Math.Matrix(provider))

    def __onUpgradeFinished(self, vehicleId):
        if self.__restoreMatrixCbkID is not None:
            BigWorld.cancelCallback(self.__restoreMatrixCbkID)
        self.__restoreMatrixCbkID = BigWorld.callback(0.0, self.__restoreMatrixProviders)
        return

    def __restoreMatrixProviders(self):
        self.__restoreMatrixCbkID = None
        if self.__viewRangeEntityID:
            self._setMatrix(self.__viewRangeEntityID, matrix_factory.makeVehicleTurretMatrixMP())
        lineEntryID = self.__getDirectionLineEntryID()
        if lineEntryID:
            if self._ctrlVehicleID and avatar_getter.getPlayerVehicleID() != self._ctrlVehicleID:
                provider = matrix_factory.makePostmortemCameraMatrix()
            else:
                provider = matrix_factory.makeArcadeCameraMatrix()
            self._setMatrix(lineEntryID, provider)
        return

    def __getDirectionLineEntryID(self):
        cameraIDs = self._getCameraIDs()
        return cameraIDs[_S_NAME.ARCADE_CAMERA] if _S_NAME.ARCADE_CAMERA in cameraIDs else None


class DeathZonesPlugin(SimplePlugin):

    def __init__(self, parent):
        super(DeathZonesPlugin, self).__init__(parent)
        self.__deathZonesEntryID = None
        return

    def initControlMode(self, mode, available):
        super(DeathZonesPlugin, self).initControlMode(mode, available)
        bottomLeft, upperRight = self._arenaVisitor.type.getBoundingBox()
        arenaWidth, arenaHeight = upperRight - bottomLeft
        deathZoneMatrix = minimap_utils.makePointInBBoxMatrix((-arenaWidth * _ARENA_SIZE_DEATH_ZONE_MULTIPLIER, 0, arenaHeight * _ARENA_SIZE_DEATH_ZONE_MULTIPLIER), bottomLeft, upperRight)
        self.__deathZonesEntryID = self._addEntry(BattleRoyaleEntries.BATTLE_ROYALE_DEATH_ZONE, _C_NAME.PERSONAL, matrix=deathZoneMatrix, active=True)
        self._parentObj.setEntryParameters(self.__deathZonesEntryID, doClip=False, scaleType=MINIMAP_SCALE_TYPES.REAL_SCALE)
        self.__initDeathZones(bottomLeft, upperRight)

    def fini(self):
        super(DeathZonesPlugin, self).fini()
        self.__clearDeathZones()

    def __initDeathZones(self, bottomLeft, upperRight):
        mapWidthPx, _ = minimap_utils.metersToMinimapPixels(bottomLeft, upperRight)
        self._invoke(self.__deathZonesEntryID, DeathZonesAs3Descr.AS_INIT_DEATH_ZONE_SIZE, mapWidthPx / ZONES_SIZE)
        g_eventBus.addListener(DeathZoneEvent.UPDATE_DEATH_ZONE, self.__onDeathZoneUpdated, scope=EVENT_BUS_SCOPE.BATTLE)

    def __clearDeathZones(self):
        g_eventBus.removeListener(DeathZoneEvent.UPDATE_DEATH_ZONE, self.__onDeathZoneUpdated, scope=EVENT_BUS_SCOPE.BATTLE)

    def __onDeathZoneUpdated(self, event):
        targetList = []
        deathZones = event.ctx['deathZones']
        for zoneID in deathZones.updatedZones:
            x, y = idxFrom(zoneID)
            self.__updateZonesData(x, y, deathZones.activeZones[zoneID], targetList)

        self.__sendDeathZonesUpdate(targetList)

    def __sendDeathZonesUpdate(self, targetList):
        if targetList:
            self._invoke(self.__deathZonesEntryID, DeathZonesAs3Descr.AS_UPDATE_DEATH_ZONES, targetList)

    def __updateZonesData(self, x, y, state, targetList):
        targetList.extend([x, ZONES_SIZE - 1 - y, state])


_TimeParamsForAs = namedtuple('_TimeParamsForAs', 'fadeIn fadeOut lifetime')

class _BattleRoyaleRadarEntryData(_RadarEntryData):

    def __init__(self, entryId, hideMeCallback, destroyMeCallback, params, typeId=None):
        super(_BattleRoyaleRadarEntryData, self).__init__(entryId, destroyMeCallback, params, typeId)
        self.__entryId = entryId
        self.__hideTime = params.lifetime - params.fadeOut - params.fadeIn
        self.__hideMeCallback = hideMeCallback

    def destroy(self):
        super(_BattleRoyaleRadarEntryData, self).destroy()
        self.__hideMeCallback = None
        return

    def upTimer(self):
        super(_BattleRoyaleRadarEntryData, self).upTimer()
        self._callbackDelayer.delayCallback(self.__hideTime, partial(self.__hideMeCallback, self.__entryId))


class BattleRoyaleRadarPlugin(RadarPlugin):

    def __init__(self, parent):
        super(BattleRoyaleRadarPlugin, self).__init__(parent)
        radarSettings = getBattleRoyaleSettings().radar.marker
        self._params = RadarPluginParams(fadeIn=radarSettings.fadeIn, fadeOut=radarSettings.fadeOut, lifetime=radarSettings.lifeTime, vehicleEntryParams=RadarEntryParams(container=_C_NAME.ALIVE_VEHICLES, symbol=_S_NAME.DISCOVERED_ITEM_MARKER), lootEntryParams=RadarEntryParams(container=_C_NAME.EQUIPMENTS, symbol=_S_NAME.DISCOVERED_ITEM_MARKER))
        self.__timeParamsForAS = _TimeParamsForAs(fadeIn=self.__sToMs(self._params.fadeIn), fadeOut=self.__sToMs(self._params.fadeOut), lifetime=self.__sToMs(self._params.lifetime - self._params.fadeIn - self._params.fadeOut))
        self.__radarRadius = 0
        self.__radarAnimationEntry = None
        self.__isColorBlind = False
        self.__isMinimapSmall = None
        self.__visibilitySystemSpottedVehicles = set()
        return

    def start(self):
        super(BattleRoyaleRadarPlugin, self).start()
        self.__radarAnimationEntry = self._addEntry(_S_NAME.RADAR_ANIM, _C_NAME.PERSONAL, matrix=matrix_factory.makeAttachedVehicleMatrix(), active=True)

    def setSettings(self):
        super(BattleRoyaleRadarPlugin, self).setSettings()
        self.__isColorBlind = self.settingsCore.getSetting(settings_constants.GRAPHICS.COLOR_BLIND)

    def updateSettings(self, diff):
        super(BattleRoyaleRadarPlugin, self).updateSettings(diff)
        if settings_constants.GRAPHICS.COLOR_BLIND in diff:
            self.__isColorBlind = diff[settings_constants.GRAPHICS.COLOR_BLIND]
            self.__updateVehicleEntries()

    def applyNewSize(self, sizeIndex):
        super(BattleRoyaleRadarPlugin, self).applyNewSize(sizeIndex)
        newValue = sizeIndex < _MARKER_SIZE_INDEX_BREAKPOINT
        if self.__isMinimapSmall is None or newValue != self.__isMinimapSmall:
            self.__isMinimapSmall = newValue
            self.__updateVehicleEntries()
            self.__updateLootEntries()
        return

    def radarActivated(self, radarRadius):
        if self.__radarAnimationEntry is not None:
            if radarRadius != self.__radarRadius:
                self._invoke(self.__radarAnimationEntry, MarkersAs3Descr.AS_UPDATE_RADAR_RADIUS, radarRadius)
                self.__radarRadius = radarRadius
            self._invoke(self.__radarAnimationEntry, MarkersAs3Descr.AS_PLAY_RADAR_ANIMATION)
        return

    def addVisibilitySysSpottedVeh(self, vehId):
        self.__visibilitySystemSpottedVehicles.add(vehId)
        self.__destroyVehicleEntryByVehId(vehId)

    def removeVisibilitySysSpottedVeh(self, vehId):
        self.__visibilitySystemSpottedVehicles.remove(vehId)

    def _createEntryData(self, entryId, destroyMeCallback, params, typeId=None):
        return _BattleRoyaleRadarEntryData(entryId, self.__hideEntryByEntryID, destroyMeCallback, params, typeId)

    def _addVehicleEntry(self, vehicleId, xzPosition):
        if vehicleId in self.__visibilitySystemSpottedVehicles:
            _logger.debug('Vehicle marker spotted by radar is not displayeddue to vehicle marker spotted by visibility system is still visible!')
            return
        else:
            vEntryId = super(BattleRoyaleRadarPlugin, self)._addVehicleEntry(vehicleId, xzPosition)
            if vEntryId is not None:
                entryName = 'enemy'
                vInfo = self._arenaDP.getVehicleInfo(vehicleId)
                isBot = vInfo.team == 21
                if avatar_getter.isVehiclesColorized():
                    entryName = 'team{}'.format(vInfo.team)
                elif isBot:
                    entryName = 'br_enemy_bot'
                self._parentObj.setEntryParameters(vEntryId, doClip=False, scaleType=MINIMAP_SCALE_TYPES.NO_SCALE)
                self._invoke(vEntryId, MarkersAs3Descr.AS_ADD_MARKER, self.__getVehicleMarker(vInfo), self.__timeParamsForAS.fadeIn, entryName)
            return vEntryId

    def _addLootEntry(self, typeId, xzPosition):
        lEntryId = super(BattleRoyaleRadarPlugin, self)._addLootEntry(typeId, xzPosition)
        if lEntryId is not None:
            lootTypeParam = self.__getLootMarkerByTypeId(typeId)
            if lootTypeParam is None:
                _logger.warning('Error in loot entry creation, typeId = %s', str(typeId))
            else:
                self._parentObj.setEntryParameters(lEntryId, doClip=False, scaleType=MINIMAP_SCALE_TYPES.NO_SCALE)
                self._invoke(lEntryId, MarkersAs3Descr.AS_ADD_MARKER, lootTypeParam, self.__timeParamsForAS.fadeIn)
        return lEntryId

    def __hideEntryByEntryID(self, entryId):
        self._invoke(entryId, MarkersAs3Descr.AS_REMOVE_MARKER, self.__timeParamsForAS.fadeOut)

    def __destroyVehicleEntryByVehId(self, vehId):
        if vehId in self._vehicleEntries:
            self._destroyVehicleEntry(self._vehicleEntries[vehId].entryId, vehId)

    def __updateVehicleEntries(self):
        for vehicleId, entry in self._vehicleEntries.iteritems():
            vInfo = self._arenaDP.getVehicleInfo(vehicleId)
            markerType = self.__getVehicleMarker(vInfo)
            self._invoke(entry.entryId, MarkersAs3Descr.AS_UPDATE_MARKER, markerType)

    def __updateLootEntries(self):
        for entry in self._lootEntries:
            markerType = self.__getLootMarkerByTypeId(entry.getTypeId())
            self._invoke(entry.entryId, MarkersAs3Descr.AS_UPDATE_MARKER, markerType)

    def __getVehicleMarker(self, vInfo=None):
        if vInfo and isSpawnedBot(vInfo.vehicleType.tags):
            return MarkersAs3Descr.AS_ADD_MARKER_BOT_VEHICLE
        if vInfo and vInfo.team == 21:
            if self.__isMinimapSmall:
                return MarkersAs3Descr.AS_ADD_MARKER_ENEMY_BOT_VEHICLE
            return MarkersAs3Descr.AS_ADD_MARKER_ENEMY_BOT_VEHICLE_BIG
        return MarkersAs3Descr.AS_ADD_MARKER_ENEMY_VEHICLE if self.__isMinimapSmall else MarkersAs3Descr.AS_ADD_MARKER_ENEMY_VEHICLE_BIG

    def __getLootMarkerByTypeId(self, typeId):
        return MarkersAs3Descr.AS_ADD_MARKER_LOOT_BY_TYPE_ID.get(typeId) if self.__isMinimapSmall else MarkersAs3Descr.AS_ADD_MARKER_LOOT_BIG_BY_TYPE_ID.get(typeId)

    @staticmethod
    def __sToMs(seconds):
        return seconds * 1000


class AirDropPlugin(EntriesPlugin):

    def __init__(self, parent):
        super(AirDropPlugin, self).__init__(parent)
        self.__isMinimapSmall = None
        return

    def applyNewSize(self, sizeIndex):
        super(AirDropPlugin, self).applyNewSize(sizeIndex)
        newValue = sizeIndex < _MARKER_SIZE_INDEX_BREAKPOINT
        if self.__isMinimapSmall is None or newValue != self.__isMinimapSmall:
            self.__isMinimapSmall = newValue
            self.__updateMarkers()
        return

    def initControlMode(self, mode, available):
        super(AirDropPlugin, self).initControlMode(mode, available)
        self.__initMarkers()
        g_eventBus.addListener(AirDropEvent.AIR_DROP_SPAWNED, self.__onAirDropSpawned, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(AirDropEvent.AIR_DROP_LANDED, self.__removeMarker, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(AirDropEvent.AIR_DROP_LOOP_ENTERED, self.__onAirDropLootEntered, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(AirDropEvent.AIR_DROP_LOOP_LEFT, self.__removeMarker, scope=EVENT_BUS_SCOPE.BATTLE)

    def fini(self):
        super(AirDropPlugin, self).fini()
        g_eventBus.removeListener(AirDropEvent.AIR_DROP_SPAWNED, self.__onAirDropSpawned, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.removeListener(AirDropEvent.AIR_DROP_LANDED, self.__removeMarker, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.removeListener(AirDropEvent.AIR_DROP_LOOP_ENTERED, self.__onAirDropLootEntered, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.removeListener(AirDropEvent.AIR_DROP_LOOP_LEFT, self.__removeMarker, scope=EVENT_BUS_SCOPE.BATTLE)

    def __initMarkers(self):
        for v in BigWorld.entities.values():
            if isinstance(v, Placement.Placement):
                self.__showMarker(v.id, v.position)
            if isinstance(v, ArenaInfo.ArenaInfo):
                for item in v.lootArenaInfo.lootPositions:
                    self.__showMarker(item.id, item.position)

    def __onAirDropSpawned(self, event):
        self.__showMarker(event.ctx['id'], event.ctx['position'])

    def __onAirDropLootEntered(self, event):
        self.__showMarker(event.ctx['id'], event.ctx['position'])

    def __removeMarker(self, event):
        self._delEntryEx(event.ctx['id'])

    def __showMarker(self, lootID, position):
        self._addEntryEx(lootID, BattleRoyaleEntries.BATTLE_ROYALE_MARKER, _C_NAME.EQUIPMENTS, active=True, matrix=math_utils.createTranslationMatrix(position))
        entryId = self._entries[lootID].getID()
        self._parentObj.setEntryParameters(entryId, doClip=False, scaleType=MINIMAP_SCALE_TYPES.NO_SCALE)
        self._invoke(entryId, MarkersAs3Descr.AS_ADD_MARKER, self.__getMarkerType())

    def __updateMarkers(self):
        for entry in self._entries.itervalues():
            self._invoke(entry.getID(), MarkersAs3Descr.AS_ADD_MARKER, self.__getMarkerType())

    def __getMarkerType(self):
        return MarkersAs3Descr.AS_ADD_MARKER_LOOT_BY_TYPE_ID.get(LOOT_TYPE.AIRDROP) if self.__isMinimapSmall else MarkersAs3Descr.AS_ADD_MARKER_LOOT_BIG_BY_TYPE_ID.get(LOOT_TYPE.AIRDROP)


class BattleRoyalStaticMarkerPlugin(IntervalPlugin):
    _CELL_BLINKING_DURATION = 3.0

    def start(self):
        super(BattleRoyalStaticMarkerPlugin, self).start()
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onStaticMarkerAdded += self.__addStaticMarker
            ctrl.onStaticMarkerRemoved += self._delEntryEx
        self.__checkMarkers()
        return

    def stop(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onStaticMarkerAdded -= self.__addStaticMarker
            ctrl.onStaticMarkerRemoved -= self._delEntryEx
        super(BattleRoyalStaticMarkerPlugin, self).stop()
        return

    def __checkMarkers(self):
        _logger.debug('minimap __checkMarkers')
        for key in g_locationPointManager.markedAreas:
            _logger.debug('minimap marker created')
            locationPoint = g_locationPointManager.markedAreas[key]
            if locationPoint.markerSubType != LocationMarkerSubType.ATTENTION_TO_MARKER_SUBTYPE:
                continue
            self.__addStaticMarker(locationPoint.targetID, locationPoint.creatorID, locationPoint.position, locationPoint.markerSubType, locationPoint.markerText, locationPoint.replyCount, False)

    def __addStaticMarker(self, areaID, creatorID, position, locationMarkerSubtype, markerText='', numberOfReplies=0, isTargetForPlayer=False):
        if locationMarkerSubtype != LocationMarkerSubType.ATTENTION_TO_MARKER_SUBTYPE:
            return
        model = self._addEntryEx(areaID, _S_NAME.MARK_POSITION, _C_NAME.EQUIPMENTS, matrix=minimap_utils.makePositionMatrix(position), active=True)
        if model:
            self._invoke(model.getID(), 'playAnimation')
            self._setCallback(areaID, BattleRoyalStaticMarkerPlugin._CELL_BLINKING_DURATION)
            self._playSound2D(settings.MINIMAP_ATTENTION_SOUND_ID)


class BattleRoyalMinimapPingPlugin(MinimapPingPlugin):

    def __init__(self, parentObj):
        super(BattleRoyalMinimapPingPlugin, self).__init__(parentObj)
        self._hitAreaSize = minimap_utils.EPIC_MINIMAP_HIT_AREA

    def _getClickPosition(self, x, y):
        return makeMousePositionToEpicWorldPosition(x, y, self._parentObj.getVisualBounds(), self._hitAreaSize)

    def _processCommandByPosition(self, commands, locationCommand, position, minimapScaleIndex):
        locationID = self._getNearestLocationIDForPosition(position, _LOCATION_PING_RANGE)
        if locationID is not None:
            self._replyPing3DMarker(commands, locationID)
            return
        else:
            commands.sendAttentionToPosition3D(position, locationCommand)
            return


class BattleRoyaleVehiclePlugin(ArenaVehiclesPlugin):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, parent):
        super(BattleRoyaleVehiclePlugin, self).__init__(parent)
        self.__isColorBlind = False
        self.__isMinimapSmall = None
        self.__radarSpottedVehiclesPlugin = None
        return

    def init(self, arenaVisitor, arenaDP):
        super(BattleRoyaleVehiclePlugin, self).init(arenaVisitor, arenaDP)
        radarPlugin = self.parentObj.getPlugin(RADAR_PLUGIN)
        if radarPlugin:
            self.__radarSpottedVehiclesPlugin = radarPlugin
        else:
            _logger.error('Radar plugin has not been found!')

    def fini(self):
        self.__radarSpottedVehiclesPlugin = None
        super(BattleRoyaleVehiclePlugin, self).fini()
        return

    def setSettings(self):
        isColorBlind = self.settingsCore.getSetting(settings_constants.GRAPHICS.COLOR_BLIND)
        if isColorBlind != self.__isColorBlind:
            self.__isColorBlind = isColorBlind
            self.invalidateVehiclesInfo(self._arenaDP)

    def updateSettings(self, diff):
        if settings_constants.GRAPHICS.COLOR_BLIND in diff:
            newColorBlind = diff[settings_constants.GRAPHICS.COLOR_BLIND]
            if self.__isColorBlind != newColorBlind:
                self.__isColorBlind = newColorBlind
                self.invalidateVehiclesInfo(self._arenaDP)

    def applyNewSize(self, sizeIndex):
        super(BattleRoyaleVehiclePlugin, self).applyNewSize(sizeIndex)
        newValue = sizeIndex < _MARKER_SIZE_INDEX_BREAKPOINT
        curScale = self.__calculateMarkerScale(sizeIndex)
        for entryID in self._entries:
            self.parentObj.invoke(self._entries[entryID].getID(), 'setTopAnimationScale', curScale)

        if self.__isMinimapSmall is None or newValue != self.__isMinimapSmall:
            self.__isMinimapSmall = newValue
            self.invalidateVehiclesInfo(self._arenaDP)
        return

    def _notifyVehicleAdded(self, vehicleID):
        super(BattleRoyaleVehiclePlugin, self)._notifyVehicleAdded(vehicleID)
        if self.__radarSpottedVehiclesPlugin is not None:
            if self._entries[vehicleID].isActive():
                self.__radarSpottedVehiclesPlugin.addVisibilitySysSpottedVeh(vehicleID)
        else:
            _logger.warning("Couldn't update radar plugin. The reference is None!")
        return

    def _notifyVehicleRemoved(self, vehicleID):
        super(BattleRoyaleVehiclePlugin, self)._notifyVehicleRemoved(vehicleID)
        if self.__radarSpottedVehiclesPlugin is not None:
            self.__radarSpottedVehiclesPlugin.removeVisibilitySysSpottedVeh(vehicleID)
        else:
            _logger.warning("Couldn't update radar plugin. The reference is None!")
        return

    def _onMinimapFeedbackReceived(self, eventID, entityID, value):
        if eventID == FEEDBACK_EVENT_ID.MINIMAP_SHOW_MARKER and entityID != self._getPlayerVehicleID():
            if entityID in self._entries:
                entry = self._entries[entityID]
                if (self._getIsObserver() or not avatar_getter.isVehicleAlive()) and avatar_getter.getVehicleIDAttached() == entityID:
                    return
                marker, _ = entry.isInAoI() and value
                self._parentObj.invoke(entry.getID(), 'setAnimation', marker)

    def _addEntry(self, symbol, container, matrix=None, active=False, transformProps=settings.TRANSFORM_FLAG.DEFAULT):
        entryId = super(BattleRoyaleVehiclePlugin, self)._addEntry(BattleRoyaleEntries.BATTLE_ROYALE_MARKER, container, matrix, active, transformProps)
        self._parentObj.setEntryParameters(entryId, doClip=False, scaleType=MINIMAP_SCALE_TYPES.NO_SCALE)
        return entryId

    def _setVehicleInfo(self, vehicleID, entry, vInfo, guiProps, isSpotted=False):
        super(BattleRoyaleVehiclePlugin, self)._setVehicleInfo(vehicleID, entry, vInfo, guiProps, isSpotted)
        playerName = ''
        playerFakeName = ''
        playerClan = ''
        playerInfoVO = vInfo.player
        isSpawnedBotVehicle = isSpawnedBot(vInfo.vehicleType.tags)
        isBot = vInfo.team == 21
        if guiProps.isFriend:
            if isSpawnedBotVehicle:
                marker = self.__getSpawnedBotVehMarker()
            elif isBot:
                marker = self.__getBotVehMarker()
            else:
                marker = self.__getSquadVehMarker()
                playerName = playerInfoVO.name
                playerFakeName = playerInfoVO.fakeName
                playerClan = playerInfoVO.clanAbbrev
            entryName = 'squadman'
        else:
            entryName = 'enemy'
            if isSpawnedBotVehicle:
                marker = self.__getSpawnedBotVehMarker()
            elif isBot:
                marker = self.__getBotVehMarker()
                entryName = 'br_enemy_bot'
            else:
                marker = self.__getEnemyVehMarker()
        if not self.__isMinimapSmall and not isSpawnedBotVehicle:
            marker = '_'.join((marker, 'big'))
        if avatar_getter.isVehiclesColorized():
            arenaBonusType = self.__sessionProvider.arenaVisitor.getArenaBonusType()
            if arenaBonusType == ARENA_BONUS_TYPE.BATTLE_ROYALE_TRN_SOLO:
                playerName = ''
            if not isBot:
                isSquadMode = arenaBonusType == ARENA_BONUS_TYPE.BATTLE_ROYALE_TRN_SQUAD
                team = _SQUAD_COLOR_MAP[vInfo.team - 1] if isSquadMode and len(_SQUAD_COLOR_MAP) >= vInfo.team else vInfo.team
                entryName = 'team{}'.format(team)
        self.parentObj.invoke(entry.getID(), 'show', marker, playerName, playerFakeName, playerClan, entryName)

    def _hideVehicle(self, entry):
        super(BattleRoyaleVehiclePlugin, self)._hideVehicle(entry)
        if entry.setActive(False):
            self._setActive(entry.getID(), False)

    def __getEnemyVehMarker(self):
        return MarkersAs3Descr.AS_ADD_MARKER_ENEMY_VEHICLE

    def __getSquadVehMarker(self):
        return MarkersAs3Descr.AS_ADD_MARKER_SQUAD_VEHICLE

    def __getSpawnedBotVehMarker(self):
        return MarkersAs3Descr.AS_ADD_MARKER_BOT_VEHICLE

    def __getBotVehMarker(self):
        return MarkersAs3Descr.AS_ADD_MARKER_ENEMY_BOT_VEHICLE

    def __calculateMarkerScale(self, minimapSizeIndex):
        p = float(minimapSizeIndex - _MINIMAP_MIN_SCALE_INDEX) / float(_MINIMAP_MAX_SCALE_INDEX - _MINIMAP_MIN_SCALE_INDEX)
        return (1 - p) * _MINIMAP_LOCATION_MARKER_MIN_SCALE + p * _MINIMAP_LOCATION_MARKER_MAX_SCALE
