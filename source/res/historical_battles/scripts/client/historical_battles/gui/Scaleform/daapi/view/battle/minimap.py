# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/minimap.py
import typing
import enum
import logging
from collections import namedtuple
from functools import partial
import BigWorld
import GUI
import Math
import math_utils
from helpers import CallbackDelayer
from gui.Scaleform.daapi.view.battle.epic.minimap import MINIMAP_SCALE_TYPES, CenteredPersonalEntriesPlugin, makeMousePositionToEpicWorldPosition
from gui.Scaleform.daapi.view.battle.shared.minimap import settings
from gui.Scaleform.daapi.view.battle.shared.minimap.common import EntriesPlugin
from gui.Scaleform.daapi.view.battle.shared.minimap.entries import VehicleEntry
from gui.Scaleform.daapi.view.battle.shared.minimap.plugins import ArenaVehiclesPlugin, MinimapPingPlugin, EquipmentsPlugin
from gui.Scaleform.daapi.view.battle.classic.minimap import GlobalSettingsPlugin
from gui.Scaleform.genConsts.LAYER_NAMES import LAYER_NAMES
from gui.battle_control import minimap_utils, matrix_factory, avatar_getter
from gui.battle_control.battle_constants import VEHICLE_LOCATION
from battle_royale.gui.battle_control.controllers.radar_ctrl import IRadarListener
from chat_commands_consts import MarkerType, INVALID_TARGET_ID, LocationMarkerSubType
from HBAttackDirectionMarkerComponent import HBAttackDirectionMarkerComponent
from HBVehicleRoleComponent import HBVehicleRoleComponent
from historical_battles.gui.Scaleform.daapi.view.battle.mini_map_background import MiniMapBackground
from historical_battles.gui.battle_control.hb_battle_constants import FEEDBACK_EVENT_ID
from historical_battles.gui.Scaleform.daapi.view.battle.markers import HBObjectivesMinimapEntry
from historical_battles.gui.Scaleform.daapi.view.meta.HBMinimapMeta import HBMinimapMeta
from historical_battles.gui.Scaleform.daapi.view.battle.components import HBStaticObjectivesMarkerComponent, HBVehicleObjectivesMarkerComponent, sendPlayerReplyForMarker
if typing.TYPE_CHECKING:
    from typing import Dict, List
    from gui.battle_control.controllers.feedback_adaptor import BattleFeedbackAdaptor
    from HBVehiclePositionsComponent import HBVehiclePositionsComponent
_C_NAME = settings.CONTAINER_NAME
_S_NAME = settings.ENTRY_SYMBOL_NAME
_LOOT_AMMO_SYMBOL_NAME = 'TutorialTargetMinimapEntryUI'
_HB_ARTILLERY_MARKER = 'HbArtilleryMinimapEntryUI'
_HB_AOE_ARTILLERY_MARKER = 'HbAOEArtilleryMinimapEntryUI'
_HB_ATTACK_PLANE_MARKER = 'HbAttackPlaneMinimapEntryUI'
_HB_MINEFIELD_MARKER = 'HbMineMinimapEntryUI'
_HB_RECON_PLANE_MARKER = 'HbReconMinimapEntryUI'
_HB_ARTILLERY_ON_YOURSELF_MARKER = 'HbArtilleryOnYourselfMinimapEntryUI'
_HB_BOMBER_MARKER = 'HbBomberMinimapEntryUI'
_HISTORICAL_BATTLE_BASE_ID = 8
_FULLMAP_ZOOM = 1.0
_MINIMAP_ZOOM = 0.666
_FULL_MAP_PATH = '_level0.root.{}.main.fullMap.mapContainer.entriesContainer'.format(LAYER_NAMES.VIEWS)
_logger = logging.getLogger(__name__)

class _MinimapScaleTypes(MINIMAP_SCALE_TYPES):
    FULLMAP_SCALE = 3


class _MarkerBlinkingParams(enum.Enum):
    BLINKING_DURATION_CUSTOM_MARKER = 10
    BLINKING_DURATION_ARROW_MARKER = 5
    BLINKING_SPEED_CUSTOM_MARKER_MS = 600
    BLINKING_SPEED_ARROW_MARKER_MS = 1000


class EventScalableEntriesPlugin(EntriesPlugin):

    def _addEntry(self, symbol, container, matrix=None, active=False, transformProps=settings.TRANSFORM_FLAG.DEFAULT):
        entryID = super(EventScalableEntriesPlugin, self)._addEntry(symbol, container, matrix, active, transformProps)
        self._parentObj.setEntryParameters(entryID)
        return entryID


class BotAppearNotificationPlugin(EntriesPlugin):
    _ANIMATION_NAME = 'firstEnemy'
    _ENEMY_MARKER = 'enemy'
    _MARKER_CLEAR_EVENTS = {FEEDBACK_EVENT_ID.VEHICLE_DEAD, FEEDBACK_EVENT_ID.MINIMAP_SHOW_MARKER, FEEDBACK_EVENT_ID.PLAYER_KILLED_ENEMY}

    def __init__(self, parent):
        super(BotAppearNotificationPlugin, self).__init__(parent, clazz=VehicleEntry)

    @classmethod
    def getHBVehiclePositions(cls):
        return BigWorld.player().arena.arenaInfo.hbVehiclePositionsComponent

    @classmethod
    def getBattleFeedback(cls):
        return cls.sessionProvider.shared.feedback

    def stop(self):
        ctrl = self.getBattleFeedback()
        if ctrl is not None:
            ctrl.onMinimapVehicleAdded -= self.__onMinimapVehicleAdded
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        if BigWorld.player() is not None:
            arena = BigWorld.player().arena
            if arena is not None:
                arena.arenaInfo.hbVehiclePositionsComponent.onReceive -= self.__onVehicleSpawnNotification
        super(BotAppearNotificationPlugin, self).stop()
        return

    def start(self):
        super(BotAppearNotificationPlugin, self).start()
        self.getHBVehiclePositions().onReceive += self.__onVehicleSpawnNotification
        ctrl = self.getBattleFeedback()
        if ctrl is not None:
            ctrl.onMinimapVehicleAdded += self.__onMinimapVehicleAdded
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        return

    def __onVehicleSpawnNotification(self, positions):
        for item in positions:
            entityID, position = item['vehicleID'], item['position']
            if self.getBattleFeedback().getVehicleProxy(entityID) is not None:
                continue
            matrix = minimap_utils.makePositionMatrix(position)
            model = self._addEntryEx(entityID, _S_NAME.VEHICLE, _C_NAME.ALIVE_VEHICLES, matrix=matrix, active=True)
            self._invoke(model.getID(), 'setVehicleInfo', '', '', '', self._ENEMY_MARKER, self._ANIMATION_NAME)

        return

    def __onMinimapVehicleAdded(self, vProxy, vInfo, guiProps):
        self._delEntryEx(vInfo.vehicleID)

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if eventID in self._MARKER_CLEAR_EVENTS:
            self._delEntryEx(vehicleID)


class LootObjectsEntriesPlugin(EntriesPlugin):
    __slots__ = ('_lootDict',)

    def __init__(self, parentObj):
        super(LootObjectsEntriesPlugin, self).__init__(parentObj)
        self._lootDict = {}

    def start(self):
        super(LootObjectsEntriesPlugin, self).start()
        self._updateCurrentOpacity()
        lootComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'loot', None)
        if lootComp is not None:
            lootComp.onLootAdded += self.__onLootAdded
            lootComp.onLootRemoved += self.__onLootRemoved
            lootEntities = lootComp.getLootEntities()
            for loot in lootEntities.values():
                self.__onLootAdded(loot)

        return

    def fini(self):
        lootComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'loot', None)
        if lootComp is not None:
            lootComp.onLootAdded -= self.__onLootAdded
            lootComp.onLootRemoved -= self.__onLootRemoved
        super(LootObjectsEntriesPlugin, self).fini()
        return

    def _updateCurrentOpacity(self):
        pass

    def _setLootHighlight(self, lootEntryID):
        self._invoke(lootEntryID, 'setHighlight', False)

    def __onLootRemoved(self, loot):
        if loot.id in self._lootDict:
            self._delEntry(self._lootDict[loot.id])
            del self._lootDict[loot.id]

    def __onLootAdded(self, loot):
        minimapSymbol = loot.gameObject.minimapSymbol
        if minimapSymbol is not None:
            matrix = Math.Matrix()
            matrix.setTranslate(loot.position)
            lootEntryID = self._addEntry(minimapSymbol, _C_NAME.ICONS, matrix=matrix, active=True)
            self._lootDict[loot.id] = lootEntryID
            if minimapSymbol == _LOOT_AMMO_SYMBOL_NAME:
                self._setLootHighlight(lootEntryID)
        return


RadarEntryParams = namedtuple('RadarEntryParams', 'symbol container')
RadarPluginParams = namedtuple('RadarPluginParams', 'fadeIn fadeOut lifetime vehicleEntryParams')

class _RadarEntryData(object):

    def __init__(self, entryId, destroyMeCallback, lifeTime, typeId=None):
        super(_RadarEntryData, self).__init__()
        self.__entryId = entryId
        self.__lifeTime = lifeTime
        self.__destroyMeCallback = destroyMeCallback
        self.__typeId = typeId
        self.__timerId = None
        return

    @property
    def entryId(self):
        return self.__entryId

    def getTypeId(self):
        return self.__typeId

    def destroy(self):
        self.stopTimer()
        self.__timerId = None
        self.__destroyMeCallback = None
        return

    def upTimer(self):
        self.stopTimer()
        self.__timerId = BigWorld.callback(self.__lifeTime, partial(self.__destroyMeCallback, self.__entryId))

    def stopTimer(self):
        if self.__timerId is not None:
            BigWorld.cancelCallback(self.__timerId)
        return


class RadarPlugin(EntriesPlugin, IRadarListener):
    _NOTIFICATION_DURATION = 3
    _ANIMATION_NAME = 'firstEnemy'

    def __init__(self, parent):
        super(RadarPlugin, self).__init__(parent)
        self._vehicleEntries = {}
        self._params = RadarPluginParams(fadeIn=0.0, fadeOut=0.0, lifetime=0.0, vehicleEntryParams=RadarEntryParams(container='', symbol=''))
        self._callbackIDs = {}

    def init(self, arenaVisitor, arenaDP):
        super(RadarPlugin, self).init(arenaVisitor, arenaDP)
        if self.sessionProvider.dynamic.radar:
            self.sessionProvider.dynamic.radar.addRuntimeView(self)

    def fini(self):
        self._clearAllCallbacks()
        if self.sessionProvider.dynamic.radar:
            self.sessionProvider.dynamic.radar.removeRuntimeView(self)
        super(RadarPlugin, self).fini()

    def radarInfoReceived(self, duration, positions):
        for _id, _pos in positions:
            self._addVehicleEntry(_id, _pos, duration)

        self._playSound2D(settings.MINIMAP_ATTENTION_SOUND_ID)

    def _addVehicleEntry(self, vehicleID, position, duration):
        matrix = minimap_utils.makePositionMatrix(position)
        model = self._addEntryEx(vehicleID, _S_NAME.VEHICLE, _C_NAME.ALIVE_VEHICLES, matrix=matrix, active=True)
        self._invoke(model.getID(), 'setVehicleInfo', vehicleID, '', '', '', self._ANIMATION_NAME)
        self._scheduleCleanup(vehicleID, duration)

    def _scheduleCleanup(self, vehicleID, interval):
        self._clearCallback(vehicleID)
        self._callbackIDs[vehicleID] = BigWorld.callback(interval, partial(self._clearCallback, vehicleID))

    def _clearCallback(self, vehicleID):
        callbackID = self._callbackIDs.pop(vehicleID, None)
        if callbackID is not None:
            self._delEntryEx(vehicleID)
            BigWorld.cancelCallback(callbackID)
        return

    def _clearAllCallbacks(self):
        for uniqueID, callbackID in self._callbackIDs.iteritems():
            self._delEntryEx(uniqueID)
            BigWorld.cancelCallback(callbackID)

        self._callbackIDs.clear()


class EventArenaVehiclesPlugin(ArenaVehiclesPlugin):

    def start(self):
        super(EventArenaVehiclesPlugin, self).start()
        HBVehicleRoleComponent.onRoleUpdated += self._onRoleUpdated

    def stop(self):
        HBVehicleRoleComponent.onRoleUpdated -= self._onRoleUpdated
        super(EventArenaVehiclesPlugin, self).stop()

    def updateControlMode(self, mode, vehicleID):
        prevCtrlID = self._ctrlVehicleID
        super(EventArenaVehiclesPlugin, self).updateControlMode(mode, vehicleID)
        if self._isInRespawnDeath():
            self.eventSwitchToVehicle(prevCtrlID)

    def _getClassTag(self, vInfo):
        vehicle = BigWorld.entities.get(vInfo.vehicleID)
        if vehicle:
            if 'roleComponent' in vehicle.dynamicComponents and vehicle.roleComponent.vehicleRole:
                return vehicle.roleComponent.getRoleIconName()
        return super(EventArenaVehiclesPlugin, self)._getClassTag(vInfo)

    def _onRoleUpdated(self, component):
        vInfo = self._arenaDP.getVehicleInfo(component.entity.id)
        self.updateVehiclesInfo(((0, vInfo),), self._arenaDP)

    def updateVehiclePosition(self, vehicleID, position):
        entry = self._entries.get(vehicleID)
        self._setInAoI(entry, True)
        self._setActive(entry.getID(), True)
        matrix = entry.getMatrix()
        if matrix is None:
            matrix = matrix_factory.makePositionMP(position)
            entry.setMatrix(matrix)
            self._setMatrix(entry.getID(), matrix)
        else:
            matrix.source.setTranslate(position)
        entry.setLocation(VEHICLE_LOCATION.AOI)
        return


class HistoricalBattlesMinimapPingPlugin(MinimapPingPlugin):
    _LOCATION_PING_RANGE = 30

    def _getClickPosition(self, x, y):
        return makeMousePositionToEpicWorldPosition(x, y, self._parentObj.getVisualBounds())

    def _getIdByBaseNumber(self, team, number):
        pass

    def _processCommandByPosition(self, commands, locationCommand, position, minimapScaleIndex):
        if avatar_getter.isVehicleAlive():
            selfVehicleID = avatar_getter.getPlayerVehicleID()
            vehicleID = self._getNearestVehicleIDForPosition(position, self._LOCATION_PING_RANGE)
            if vehicleID is not None and vehicleID != selfVehicleID:
                sendPlayerReplyForMarker(self.sessionProvider, vehicleID, MarkerType.VEHICLE_MARKER_TYPE)
                return
            locationID = self._getNearestLocationIDForPosition(position, self._LOCATION_PING_RANGE)
            if locationID is not None:
                self._replyPing3DMarker(commands, locationID)
                return
        commands.sendAttentionToPosition3D(position, locationCommand)
        return

    def _getNearestVehicleIDForPosition(self, position, pRange):
        vehiclesIterator = (BigWorld.entities.get(vInfo.vehicleID) for vInfo in self.sessionProvider.getArenaDP().getVehiclesInfoIterator())
        closestVehicle = min((vehicle for vehicle in vehiclesIterator if vehicle is not None and vehicle.isStarted), key=lambda entity: Math.Vector3(entity.position).flatDistTo(Math.Vector3(position)))
        return closestVehicle.id if Math.Vector3(closestVehicle.position).flatDistTo(Math.Vector3(position)) < pRange else None


class HBDeathZonesMinimapPlugin(EntriesPlugin):
    __slots__ = ('_activeDeathZones', '_scaleCoefX', '_scaleCoefY')
    _SYMBOL_NAME = 'EventDeathZoneMinimapEntryUI'

    def __init__(self, parentObj):
        super(HBDeathZonesMinimapPlugin, self).__init__(parentObj)
        self._activeDeathZones = {}
        self._updateScaleCoefs()

    def _updateScaleCoefs(self):
        arenaSize = BigWorld.player().arena.arenaType.boundingBox[1]
        self._scaleCoefX = minimap_utils.MINIMAP_SIZE[0] / arenaSize[0]
        self._scaleCoefY = minimap_utils.MINIMAP_SIZE[1] / arenaSize[1]


class HBCenteredPersonalEntriesPlugin(CenteredPersonalEntriesPlugin):
    __slots__ = ('__zoneCenterEntryID',)
    _EMPTY_SYMBOL = 'HBEmptyMinimapEntryUI'

    def __init__(self, parentObj):
        super(HBCenteredPersonalEntriesPlugin, self).__init__(parentObj)
        self.__zoneCenterEntryID = None
        return

    def start(self):
        super(HBCenteredPersonalEntriesPlugin, self).start()
        bb = BigWorld.player().arena.arenaType.boundingBox
        center = Math.Vector3((bb[0][0] + bb[1][0]) / 2.0, 0, (bb[0][1] + bb[1][1]) / 2.0)
        matrix = Math.Matrix()
        matrix.setTranslate(center)
        self.__zoneCenterEntryID = self._addEntry(self._EMPTY_SYMBOL, _C_NAME.PERSONAL, matrix=matrix, active=True)

    def getZoneCenterEntryID(self):
        return self.__zoneCenterEntryID


class HistoricalMinimapComponent(HBMinimapMeta):

    class _MapParams(object):

        def __init__(self, sizeIndex, zoom, centerEntryID=None):
            self.sizeIndex = sizeIndex
            self.zoom = zoom
            self.centerEntryID = centerEntryID

    def __init__(self):
        super(HistoricalMinimapComponent, self).__init__()
        self.__isFullSize = False
        self.__miniMapParams = self._MapParams(float(settings.MINIMAP_MIN_SIZE_INDEX), _MINIMAP_ZOOM)
        self.__fullMapParams = self._MapParams(float(settings.MINIMAP_MAX_SIZE_INDEX), _FULLMAP_ZOOM)

    def applyNewSize(self, sizeIndex):
        super(HistoricalMinimapComponent, self).applyNewSize(sizeIndex)
        if not self.__isFullSize:
            self.__miniMapParams.sizeIndex = sizeIndex

    def isFullViewMode(self):
        return self.__isFullSize

    def setMiniMapViewMode(self):
        self.__setViewMode(False)

    def setFullMapViewMode(self):
        self.__setViewMode(True)

    def isModalViewShown(self):
        return self.isFullViewMode()

    def changeMinimapZoom(self, mode):
        self.getComponent().changeMinimapZoom(mode)

    def setEntryParameters(self, entryId, doClip=True, scaleType=_MinimapScaleTypes.ADAPTED_SCALE):
        self.getComponent().setEntryParameters(entryId, doClip, scaleType)

    def setMinimapCenterEntry(self, entryID):
        if not self.__isFullSize:
            self.__miniMapParams.centerEntryID = entryID
            self.getComponent().setMinimapCenterEntry(entryID)

    def onZoomModeChanged(self, change):
        pass

    def getVisualBounds(self):
        return self.getComponent().getVisualBound()

    def _createFlashComponent(self):
        return GUI.ScrollingMinimapGUIComponentAS3(self.app.movie, settings.MINIMAP_COMPONENT_PATH)

    def _processMinimapSize(self, minSize, maxSize):
        mapWidthPx, mapHeightPx = minimap_utils.metersToMinimapPixels(minSize, maxSize)
        self.as_setMapDimensionsS(mapWidthPx, mapHeightPx)
        size = self._getMinimapSize()
        self.__fullMapParams.zoom = min(mapWidthPx / size[0], mapHeightPx / size[1])

    def _setupPlugins(self, arenaVisitor):
        setup = super(HistoricalMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['bot_appear_notification'] = BotAppearNotificationPlugin
        setup['loot_objects'] = LootObjectsEntriesPlugin
        setup['vehicles'] = EventArenaVehiclesPlugin
        setup['personal'] = HBCenteredPersonalEntriesPlugin
        setup['pinging'] = HistoricalBattlesMinimapPingPlugin
        setup['equipments'] = HistoricalEquipmentsPlugin
        setup['minimap_background'] = MiniMapBackground
        setup['attack_direction'] = HistoricalAttackDirectionPlugin
        setup['objectives'] = HBObjectivesPointMarkerPlugin
        setup['settings'] = HBGlobalSettingsPlugin
        setup['deathzones'] = HBDeathZonesMinimapPlugin
        return setup

    def _populate(self):
        super(HistoricalMinimapComponent, self)._populate()
        personalPlugin = self.getPlugin('personal')
        if personalPlugin is not None:
            self.__fullMapParams.centerEntryID = personalPlugin.getZoneCenterEntryID()
        self.changeMinimapZoom(self._getZoom())
        return

    def _getZoom(self):
        return self.__mapParams.zoom

    @property
    def __mapParams(self):
        return self.__fullMapParams if self.__isFullSize else self.__miniMapParams

    def __setViewMode(self, toFullSize):
        if self.isFullViewMode() == toFullSize:
            return
        else:
            self.__isFullSize = toFullSize
            centerEntryID = self.__mapParams.centerEntryID
            if centerEntryID is not None:
                self.getComponent().setMinimapCenterEntry(centerEntryID)
            zoom = self.__mapParams.zoom
            sizeIndex = self.__mapParams.sizeIndex
            self.changeMinimapZoom(zoom)
            self.as_setTabModeS(self.__isFullSize)
            self.as_setSizeS(int(sizeIndex))
            super(HistoricalMinimapComponent, self).applyNewSize(sizeIndex)
            return


class HBObjectivesPointMarkerPlugin(EntriesPlugin, HBStaticObjectivesMarkerComponent, HBVehicleObjectivesMarkerComponent):
    __slots__ = ('__delayer',)

    def __init__(self, parent):
        super(HBObjectivesPointMarkerPlugin, self).__init__(parent, clazz=HBObjectivesMinimapEntry)
        self.__delayer = CallbackDelayer.CallbacksSetByID()

    def stop(self):
        self.__delayer.clear()
        HBStaticObjectivesMarkerComponent.stop(self)
        HBVehicleObjectivesMarkerComponent.stop(self)
        super(HBObjectivesPointMarkerPlugin, self).stop()

    def start(self):
        super(HBObjectivesPointMarkerPlugin, self).start()
        HBStaticObjectivesMarkerComponent.start(self)
        HBVehicleObjectivesMarkerComponent.start(self)

    def getMarkerType(self):
        return MarkerType.LOCATION_MARKER_TYPE

    def getMarkerSubType(self):
        return LocationMarkerSubType.OBJECTIVES_POINT_SUBTYPE

    def getTargetIDFromMarkerID(self, markerID):
        return next((tID for tID, marker in self._entries.iteritems() if marker.getID() == markerID), INVALID_TARGET_ID)

    def _getTargetIDFromVehicleID(self, vehicleID):
        return next((tID for tID, marker in self._entries.iteritems() if marker.ownVehicleID == vehicleID), INVALID_TARGET_ID)

    def _getMarker(self, markerID, markerType, defaultMarker=None):
        return self._entries.get(markerID, defaultMarker) if markerType == self.getMarkerType() else defaultMarker

    def _getMarkerFromTargetID(self, targetID, markerType):
        return self._getMarker(targetID, markerType)

    def _playAnimation(self, targetID, animationName):
        marker = self._getMarkerFromTargetID(targetID, self.getMarkerType())
        if marker is not None:
            self._invoke(marker.getID(), 'setBlinking', True, self._clazz.ANIMATION_SPEED)
            marker.animationID = self._parentObj.addEntry(animationName, _C_NAME.EQUIPMENTS, matrix=marker.getMatrix(), active=True)
            self.__delayer.delayCallback(targetID, self._clazz.ANIMATION_LIFETIME, self._stopAnimation, targetID)
        return

    def _stopAnimation(self, targetID):
        if self.__delayer.hasDelayedCallbackID(targetID):
            self.__delayer.stopCallback(targetID)
            marker = self._getMarkerFromTargetID(targetID, self.getMarkerType())
            if marker is not None:
                self._invoke(marker.getID(), 'setBlinking', False, 0)
                if marker.animationID:
                    self._parentObj.delEntry(marker.animationID)
        return

    def _addMarker(self, targetID, position, featureID):
        matrix = matrix_factory.makePositionMP(position)
        isAlly = self.sessionProvider.getArenaDP().isAlly(featureID) if featureID else False
        marker = self._addEntryEx(targetID, self._clazz.FLASH_SYMBOL_NAME, _C_NAME.EQUIPMENTS, matrix=matrix, active=not isAlly)
        marker.setMatrix(matrix)
        marker.ownVehicleID = featureID
        marker.isAlly = isAlly
        marker.isGoalForPlayer = False
        self._parentObj.setEntryParameters(marker.getID(), doClip=True, scaleType=_MinimapScaleTypes.ADAPTED_SCALE)
        self._invoke(marker.getID(), 'setIcon', self._clazz.GOAL_ICON)
        self._playAnimation(targetID, self._clazz.SPOTTED_ANIMATION)

    def _removeMarker(self, targetID, markerType):
        marker = self._getMarkerFromTargetID(targetID, markerType)
        if marker is not None:
            self._stopAnimation(targetID)
            self._delEntryEx(targetID)
        return

    def _setMarkerMatrix(self, markerID, matrix):
        marker = self._getMarkerFromTargetID(self.getTargetIDFromMarkerID(markerID), self.getMarkerType())
        if marker is not None:
            marker.setMatrix(matrix)
            self._setMatrix(marker.getID(), matrix)
        return

    def _updateMarker(self, targetID, isReplied, replierVehicleID):
        marker = self._getMarkerFromTargetID(targetID, self.getMarkerType())
        if marker is not None:
            if replierVehicleID == self.sessionProvider.arenaVisitor.getArenaUniqueID():
                if marker.isGoalForPlayer:
                    self._playAnimation(targetID, self._clazz.ONCALL_ANIMATION)
            else:
                self._invoke(marker.getID(), 'setIcon', self._clazz.GOAL_REPLIED_ICON if isReplied else self._clazz.GOAL_ICON)
        return

    def _setMarkerActive(self, markerID, shouldNotHide):
        pass

    def invokeMarker(self, markerID, function, *args):
        pass

    def _setMarkerSticky(self, markerID, isSticky):
        pass

    def _setMarkerBoundEnabled(self, markerID, isEnabled):
        pass


class HistoricalEquipmentsPlugin(EquipmentsPlugin):
    _HB_EQ_MARKER_TO_SYMBOL = {'death': _HB_AOE_ARTILLERY_MARKER,
     'hb_artillery': _HB_ARTILLERY_MARKER,
     'hb_attack_plane': _HB_ATTACK_PLANE_MARKER,
     'hb_minefield': _HB_MINEFIELD_MARKER,
     'hb_recon': _HB_RECON_PLANE_MARKER,
     'hb_artillery_on_yourself': _HB_ARTILLERY_ON_YOURSELF_MARKER,
     'hb_bomber': _HB_BOMBER_MARKER}

    def _getMarkerSymbol(self, marker):
        symbol = self._HB_EQ_MARKER_TO_SYMBOL.get(marker)
        return symbol or super(HistoricalEquipmentsPlugin, self)._getMarkerSymbol(marker)


class HistoricalAttackDirectionPlugin(EventScalableEntriesPlugin):
    _SYMBOL = 'HBArrowMinimapEntryUI'

    def __init__(self, *args, **kwargs):
        super(HistoricalAttackDirectionPlugin, self).__init__(*args, **kwargs)
        self._displayedMarkers = {}
        self._blinkingCallbacks = {}

    def start(self):
        super(HistoricalAttackDirectionPlugin, self).start()
        HBAttackDirectionMarkerComponent.onMarkersUpdated += self.__onMarkersUpdated

    def fini(self):
        for callbackId in self._blinkingCallbacks.itervalues():
            BigWorld.cancelCallback(callbackId)

        self._blinkingCallbacks.clear()
        self._displayedMarkers.clear()
        HBAttackDirectionMarkerComponent.onMarkersUpdated -= self.__onMarkersUpdated
        super(HistoricalAttackDirectionPlugin, self).fini()

    def __onMarkersUpdated(self, currentMarkers):
        currentMarkersIds = [ marker['markerID'] for marker in currentMarkers ]
        addedMarkers = [ marker for marker in currentMarkers if marker['markerID'] not in self._displayedMarkers ]
        for marker in addedMarkers:
            self.__addMarker(**marker)

        removedMarkers = [ markerID for markerID in self._displayedMarkers if markerID not in currentMarkersIds ]
        for markerID in removedMarkers:
            self.__removeMarker(markerID)

    def __addMarker(self, markerID, markerType, position, yaw):
        matrix = math_utils.createRTMatrix(Math.Vector3(yaw, 0.0, 0.0), position)
        markerEntryID = self._addEntry(self._SYMBOL, _C_NAME.ICONS, matrix=matrix, active=True)
        self._parentObj.setEntryParameters(markerEntryID, doClip=False, scaleType=_MinimapScaleTypes.REAL_SCALE)
        self._invoke(markerEntryID, 'setIcon', markerType)
        self._invoke(markerEntryID, 'setBlinking', True, _MarkerBlinkingParams.BLINKING_SPEED_ARROW_MARKER_MS.value)
        self._blinkingCallbacks[markerID] = BigWorld.callback(_MarkerBlinkingParams.BLINKING_DURATION_ARROW_MARKER.value, partial(self.__stopBlinking, markerID))
        self._displayedMarkers[markerID] = markerEntryID

    def __removeMarker(self, markerID):
        if markerID in self._blinkingCallbacks:
            BigWorld.cancelCallback(self._blinkingCallbacks[markerID])
            del self._blinkingCallbacks[markerID]
        self._delEntry(self._displayedMarkers[markerID])
        del self._displayedMarkers[markerID]

    def __stopBlinking(self, markerId):
        if markerId in self._blinkingCallbacks:
            self._invoke(self._displayedMarkers[markerId], 'setBlinking', False, 0)
            del self._blinkingCallbacks[markerId]


class HBGlobalSettingsPlugin(GlobalSettingsPlugin):

    def _toogleVisible(self):
        pass
