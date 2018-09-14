# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/fallout/markers2d.py
from functools import partial
import math
import BigWorld
import GUI
import constants
from CTFManager import g_ctfManager
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager
from gui.Scaleform.daapi.view.battle.shared.markers2d import markers
from gui.Scaleform.daapi.view.battle.shared.markers2d import plugins
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import NEUTRAL_TEAM, GAS_ATTACK_STATE, REPAIR_STATE_ID
from helpers import i18n, time_utils

class FalloutVehicleMarker(markers.VehicleMarker):

    def __init__(self, markerID, vehicleID, vProxy, active=True):
        super(FalloutVehicleMarker, self).__init__(markerID, vehicleID, vProxy, active)
        self._flagBearer = False

    def isFlagBearer(self):
        return self._flagBearer

    def setFlagBearer(self, bearer):
        if self._flagBearer != bearer:
            self._flagBearer = bearer
            return True
        else:
            return False


class FlagMarker(markers.Marker):
    """
    Holds info for Flag Marker
    """

    def __init__(self, markerID, callbackID=None, active=True):
        super(FlagMarker, self).__init__(markerID, active)
        self._callbackID = callbackID

    def getCallbackID(self):
        return self._callbackID

    def setCallbackID(self, cbID):
        self._callbackID = cbID


class RespawnableVehicleMarkerPlugin(plugins.VehicleMarkerPlugin):

    def __init__(self, parentObj, clazz=FalloutVehicleMarker):
        super(RespawnableVehicleMarkerPlugin, self).__init__(parentObj, clazz)

    def start(self):
        super(RespawnableVehicleMarkerPlugin, self).start()
        self._isSquadIndicatorEnabled = self.sessionProvider.arenaVisitor.gui.isFalloutMultiTeam()

    def _setMarkerInitialState(self, marker, accountDBID=0):
        super(RespawnableVehicleMarkerPlugin, self)._setMarkerInitialState(marker, accountDBID=accountDBID)
        flagBearer = g_ctfManager.getVehicleCarriedFlagID(marker.getVehicleID()) is not None
        if marker.setFlagBearer(flagBearer):
            self._invokeMarker(marker.getMarkerID(), 'updateFlagBearerState', flagBearer)
        return

    def _hideVehicleMarker(self, vehicleID):
        self._destroyVehicleMarker(vehicleID)


class VehicleAndFlagsMarkerPlugin(RespawnableVehicleMarkerPlugin):
    """
    This plugin handles Flags on 3d scene, also it switches flagBearer state for the base (vehicles) class.
    The flags are created at start and then they can be only updated for the remain life cycle.
    """
    __slots__ = ('_markers', '__spawnPoints', '__playerTeam', '__isTeamPlayer')

    def __init__(self, parentObj):
        super(VehicleAndFlagsMarkerPlugin, self).__init__(parentObj)
        self._markers = {}
        self.__spawnPoints = []
        self.__playerTeam = NEUTRAL_TEAM
        self.__isTeamPlayer = False

    def init(self):
        super(VehicleAndFlagsMarkerPlugin, self).init()
        g_ctfManager.onFlagSpawning += self.__onFlagSpawning
        g_ctfManager.onFlagSpawnedAtBase += self.__onSpawnedAtBase
        g_ctfManager.onFlagCapturedByVehicle += self.__onCapturedByVehicle
        g_ctfManager.onFlagDroppedToGround += self.__onDroppedToGround
        g_ctfManager.onFlagAbsorbed += self.__onAbsorbed
        g_ctfManager.onFlagRemoved += self.__onRemoved

    def fini(self):
        g_ctfManager.onFlagSpawning -= self.__onFlagSpawning
        g_ctfManager.onFlagSpawnedAtBase -= self.__onSpawnedAtBase
        g_ctfManager.onFlagCapturedByVehicle -= self.__onCapturedByVehicle
        g_ctfManager.onFlagDroppedToGround -= self.__onDroppedToGround
        g_ctfManager.onFlagAbsorbed -= self.__onAbsorbed
        g_ctfManager.onFlagRemoved -= self.__onRemoved
        super(VehicleAndFlagsMarkerPlugin, self).fini()

    def start(self):
        visitor = self.sessionProvider.arenaVisitor
        self.__playerTeam = avatar_getter.getPlayerTeam()
        self.__isTeamPlayer = not visitor.isSoloTeam(self.__playerTeam)
        self.__spawnPoints = visitor.type.getFlagSpawnPoints()
        for flagID, flagInfo in g_ctfManager.getFlags():
            vehicleID = flagInfo['vehicle']
            if vehicleID is None:
                flagState = flagInfo['state']
                if flagState == constants.FLAG_STATE.WAITING_FIRST_SPAWN:
                    self.__onFlagSpawning(flagID, flagInfo['respawnTime'])
                elif flagState in (constants.FLAG_STATE.ON_GROUND, constants.FLAG_STATE.ON_SPAWN):
                    self.__onSpawnedAtBase(flagID, flagInfo['team'], flagInfo['minimapPos'])

        super(VehicleAndFlagsMarkerPlugin, self).start()
        return

    def stop(self):
        for flagMarker in self._markers.values():
            self.__cancelCallback(flagMarker)

        self.__spawnPoints = None
        super(VehicleAndFlagsMarkerPlugin, self).stop()
        return

    def __addOrUpdateFlagMarker(self, flagID, flagPos, marker):
        position = flagPos + settings.MARKER_POSITION_ADJUSTMENT
        if flagID in self._markers:
            flagMarker = self._markers[flagID]
            handle = flagMarker.getMarkerID()
            self._setMarkerPosition(handle, position)
            if flagMarker.setActive(True):
                self._setMarkerActive(handle, True)
            self.__cancelCallback(flagMarker)
        else:
            handle = self._createMarkerWithPosition(settings.MARKER_SYMBOL_NAME.FLAG_MARKER, position)
            self._markers[flagID] = FlagMarker(handle)
        self._invokeMarker(handle, 'setIcon', marker)

    def __cancelCallback(self, flagMarker):
        callbackID = flagMarker.getCallbackID()
        if callbackID is not None:
            BigWorld.cancelCallback(callbackID)
            flagMarker.setCallbackID(None)
        return

    def __hideFlagMarker(self, flagID):
        if flagID in self._markers:
            flagMarker = self._markers[flagID]
            if flagMarker.setActive(False):
                self._setMarkerActive(flagMarker.getMarkerID(), False)
            self.__cancelCallback(flagMarker)

    def __initTimer(self, timer, flagID):
        if flagID not in self._markers:
            LOG_ERROR('VehicleAndFlagsMarkerPlugin does not have marker with flag id: ', flagID)
            return
        else:
            timer -= 1
            flagMarker = self._markers[flagID]
            if timer < 0:
                flagMarker.setCallbackID(None)
                return
            self._invokeMarker(flagMarker.getMarkerID(), 'setLabel', i18n.makeString(INGAME_GUI.FLAGS_TIMER, time=str(timer)))
            callbackId = BigWorld.callback(1, partial(self.__initTimer, timer, flagID))
            flagMarker.setCallbackID(callbackId)
            return

    def __onFlagSpawning(self, flagID, respawnTime):
        flagType = settings.FLAG_TYPE.COOLDOWN
        flagPos = self.__spawnPoints[flagID]['position']
        self.__addOrUpdateFlagMarker(flagID, flagPos, flagType)
        timer = respawnTime - BigWorld.serverTime()
        self.__initTimer(int(math.ceil(timer)), flagID)

    def __onSpawnedAtBase(self, flagID, flagTeam, flagPos):
        flagType = self.__getFlagMarkerType(flagID, flagTeam)
        self.__addOrUpdateFlagMarker(flagID, flagPos, flagType)

    def __updateFlagbearerState(self, vehicleID, newState):
        if vehicleID in self._markers:
            marker = self._markers[vehicleID]
            if marker.isActive() and marker.setFlagBearer(newState):
                self._invokeMarker(marker.getMarkerID(), 'updateFlagBearerState', newState)

    def __onCapturedByVehicle(self, flagID, flagTeam, vehicleID):
        self.__updateFlagbearerState(vehicleID, True)
        self.__hideFlagMarker(flagID)

    def __onDroppedToGround(self, flagID, flagTeam, loserVehicleID, flagPos, respawnTime):
        flagType = self.__getFlagMarkerType(flagID, flagTeam)
        self.__updateFlagbearerState(loserVehicleID, False)
        self.__addOrUpdateFlagMarker(flagID, flagPos, flagType)
        timer = respawnTime - BigWorld.serverTime()
        self.__initTimer(int(math.ceil(timer)), flagID)

    def __onAbsorbed(self, flagID, flagTeam, vehicleID, respawnTime):
        self.__updateFlagbearerState(vehicleID, False)
        self.__hideFlagMarker(flagID)

    def __onRemoved(self, flagID, flagTeam, vehicleID):
        self.__hideFlagMarker(flagID)
        if vehicleID is not None:
            self.__updateFlagbearerState(vehicleID, False)
        return

    def __getFlagMarkerType(self, flagID, flagTeam=0):
        if flagTeam != NEUTRAL_TEAM:
            if flagTeam == self.__playerTeam:
                return settings.FLAG_TYPE.ALLY
            return settings.FLAG_TYPE.ENEMY
        return settings.FLAG_TYPE.NEUTRAL


class AbsorptionMarkersPlugin(plugins.MarkerPlugin):
    __slots__ = ('__captureMarkers', '__playerVehicleID', '__playerTeam', '__isTeamPlayer')

    def __init__(self, parentObj):
        super(AbsorptionMarkersPlugin, self).__init__(parentObj)
        self.__captureMarkers = []
        self.__playerVehicleID = 0
        self.__playerTeam = NEUTRAL_TEAM
        self.__isTeamPlayer = False

    def init(self):
        super(AbsorptionMarkersPlugin, self).init()
        g_ctfManager.onFlagCapturedByVehicle += self.__onCapturedByVehicle
        g_ctfManager.onFlagDroppedToGround += self.__onDroppedToGround
        g_ctfManager.onFlagAbsorbed += self.__onAbsorbed
        g_ctfManager.onFlagRemoved += self.__onRemoved

    def fini(self):
        g_ctfManager.onFlagCapturedByVehicle -= self.__onCapturedByVehicle
        g_ctfManager.onFlagDroppedToGround -= self.__onDroppedToGround
        g_ctfManager.onFlagAbsorbed -= self.__onAbsorbed
        g_ctfManager.onFlagRemoved -= self.__onRemoved
        super(AbsorptionMarkersPlugin, self).fini()

    def start(self):
        visitor = self.sessionProvider.arenaVisitor
        self.__playerVehicleID = avatar_getter.getPlayerVehicleID()
        self.__playerTeam = avatar_getter.getPlayerTeam()
        self.__isTeamPlayer = not visitor.isSoloTeam(self.__playerTeam)
        self.__addCaptureMarkers(visitor, g_ctfManager.getVehicleCarriedFlagID(self.__playerVehicleID) is not None)
        super(AbsorptionMarkersPlugin, self).start()
        return

    def stop(self):
        self.__captureMarkers = None
        super(AbsorptionMarkersPlugin, self).stop()
        return

    def __addCaptureMarkers(self, visitor, flagBearer):
        for point in visitor.type.getFlagAbsorptionPoints():
            if self.__isTeamPlayer and point['team'] in (NEUTRAL_TEAM, self.__playerTeam):
                position = point['position']
                handle = self._createMarkerWithPosition(settings.MARKER_SYMBOL_NAME.FLAG_CAPTURE_MARKER, position + settings.MARKER_POSITION_ADJUSTMENT, flagBearer)
                self.__captureMarkers.append(handle)

    def __setCaptureMarkersVisible(self, visible):
        for handle in self.__captureMarkers:
            self._setMarkerActive(handle, visible)

    def __onCapturedByVehicle(self, flagID, flagTeam, vehicleID):
        if vehicleID == self.__playerVehicleID:
            self.__setCaptureMarkersVisible(True)

    def __onDroppedToGround(self, flagID, flagTeam, loserVehicleID, flagPos, respawnTime):
        if loserVehicleID == self.__playerVehicleID:
            self.__setCaptureMarkersVisible(False)

    def __onAbsorbed(self, flagID, flagTeam, vehicleID, respawnTime):
        if vehicleID == self.__playerVehicleID:
            self.__setCaptureMarkersVisible(False)

    def __onRemoved(self, flagID, flagTeam, vehicleID):
        if vehicleID is not None and vehicleID == self.__playerVehicleID:
            self.__setCaptureMarkersVisible(False)
        return


class RepairsMarkerPlugin(plugins.MarkerPlugin):
    __slots__ = ('__markers',)

    def __init__(self, parentObj):
        super(RepairsMarkerPlugin, self).__init__(parentObj)
        self.__markers = {}

    def init(self):
        super(RepairsMarkerPlugin, self).init()
        ctrl = self.sessionProvider.dynamic.repair
        if ctrl is not None:
            ctrl.onStateCreated += self.__onRepairPointStateCreated
            ctrl.onTimerUpdated += self.__onRepairPointTimerUpdated
        return

    def fini(self):
        ctrl = self.sessionProvider.dynamic.repair
        if ctrl is not None:
            ctrl.onStateCreated -= self.__onRepairPointStateCreated
            ctrl.onTimerUpdated -= self.__onRepairPointTimerUpdated
        super(RepairsMarkerPlugin, self).fini()
        return

    def start(self):
        playerTeam = avatar_getter.getPlayerTeam()
        ctrl = self.sessionProvider.dynamic.repair
        if ctrl is not None:
            getPointStateID = ctrl.getPointStateID
        else:

            def getPointStateID(_):
                return REPAIR_STATE_ID.UNRESOLVED

        iterator = self.sessionProvider.arenaVisitor.type.getRepairPointIterator()
        for pointID, (team, repairPos) in iterator:
            isAlly = team in (NEUTRAL_TEAM, playerTeam)
            markerID = self._createMarkerWithPosition(settings.MARKER_SYMBOL_NAME.REPAIR_MARKER, repairPos + settings.MARKER_POSITION_ADJUSTMENT)
            if getPointStateID(pointID) == REPAIR_STATE_ID.COOLDOWN:
                icon = 'cooldown'
            else:
                icon = 'active'
            self._invokeMarker(markerID, 'setIcon', icon, isAlly)
            self.__markers[pointID] = (markerID, isAlly)

        super(RepairsMarkerPlugin, self).start()
        return

    def stop(self):
        for markerID, _ in self.__markers.values():
            self._destroyMarker(markerID)

        self.__markers.clear()
        super(RepairsMarkerPlugin, self).stop()

    def __onRepairPointStateCreated(self, pointIndex, stateID):
        if pointIndex not in self.__markers:
            LOG_ERROR('Got repair point state changed for not available repair point: ', pointIndex, stateID)
            return
        if stateID == REPAIR_STATE_ID.DISABLED:
            markerID, _ = self.__markers.pop(pointIndex)
            self._destroyMarker(markerID)
            return
        if stateID == REPAIR_STATE_ID.COOLDOWN:
            icon = 'cooldown'
        else:
            icon = 'active'
        markerID, isAlly = self.__markers[pointIndex]
        self._parentObj.invokeMarker(markerID, 'setIcon', icon, isAlly)
        self._parentObj.invokeMarker(markerID, 'setLabel', '')

    def __onRepairPointTimerUpdated(self, pointIndex, stateID, timeLeft):
        if stateID == REPAIR_STATE_ID.COOLDOWN and pointIndex in self.__markers:
            self._parentObj.invokeMarker(self.__markers[pointIndex][0], 'setLabel', time_utils.getTimeLeftFormat(timeLeft))


class ResourceMarkerPlugin(plugins.MarkerPlugin):
    __slots__ = ('__markers',)

    def __init__(self, parentObj):
        super(ResourceMarkerPlugin, self).__init__(parentObj)
        self.__markers = {}

    def init(self):
        super(ResourceMarkerPlugin, self).init()
        g_ctfManager.onResPointIsFree += self.__onIsFree
        g_ctfManager.onResPointCooldown += self.__onCooldown
        g_ctfManager.onResPointCaptured += self.__onCaptured
        g_ctfManager.onResPointCapturedLocked += self.__onCapturedLocked
        g_ctfManager.onResPointBlocked += self.__onBlocked
        g_ctfManager.onResPointAmountChanged += self.__onAmountChanged

    def fini(self):
        g_ctfManager.onResPointIsFree -= self.__onIsFree
        g_ctfManager.onResPointCooldown -= self.__onCooldown
        g_ctfManager.onResPointCaptured -= self.__onCaptured
        g_ctfManager.onResPointCapturedLocked -= self.__onCapturedLocked
        g_ctfManager.onResPointBlocked -= self.__onBlocked
        g_ctfManager.onResPointAmountChanged -= self.__onAmountChanged
        super(ResourceMarkerPlugin, self).fini()

    def start(self):
        super(ResourceMarkerPlugin, self).start()
        arenaDP = self.sessionProvider.getArenaDP()
        for pointID, point in g_ctfManager.getResourcePoints():
            resourcePos = point['minimapPos']
            amount = point['amount']
            pointState = point['state']
            progress = float(amount) / point['totalAmount'] * 100
            if pointState == constants.RESOURCE_POINT_STATE.FREE:
                state = settings.RESOURCE_STATE.READY
            elif pointState == constants.RESOURCE_POINT_STATE.COOLDOWN:
                state = settings.RESOURCE_STATE.COOLDOWN
            elif pointState == constants.RESOURCE_POINT_STATE.CAPTURED:
                state = settings.CAPTURE_STATE_BY_TEAMS[arenaDP.isAllyTeam(point['team'])]
            elif pointState == constants.RESOURCE_POINT_STATE.CAPTURED_LOCKED:
                state = settings.CAPTURE_FROZEN_STATE_BY_TEAMS[arenaDP.isAllyTeam(point['team'])]
            elif pointState == constants.RESOURCE_POINT_STATE.BLOCKED:
                state = settings.RESOURCE_STATE.CONFLICT
            else:
                state = settings.RESOURCE_STATE.FREEZE
            handle = self._createMarkerWithPosition(settings.MARKER_SYMBOL_NAME.RESOURCE_MARKER, resourcePos + settings.MARKER_POSITION_ADJUSTMENT)
            self._invokeMarker(handle, 'as_init', pointID, state, progress)
            self.__markers[pointID] = (handle,
             None,
             resourcePos,
             state)

        return

    def stop(self):
        for handle, callbackID, _, _ in self.__markers.values():
            self._destroyMarker(handle)
            if callbackID is not None:
                BigWorld.cancelCallback(callbackID)

        self.__markers = None
        super(ResourceMarkerPlugin, self).stop()
        return

    def update(self):
        super(ResourceMarkerPlugin, self).update()
        for point in self.__markers.itervalues():
            handle = point[0]
            self._invokeMarker(handle, 'as_onSettingsChanged')

    def __onIsFree(self, pointID):
        handle, _, _, _ = self.__markers[pointID]
        self._invokeMarker(handle, 'as_setState', settings.RESOURCE_STATE.READY)

    def __onCooldown(self, pointID, serverTime):
        handle, _, _, _ = self.__markers[pointID]
        self._invokeMarker(handle, 'as_setState', settings.RESOURCE_STATE.COOLDOWN)

    def __onCaptured(self, pointID, team):
        handle, _, _, _ = self.__markers[pointID]
        state = settings.CAPTURE_STATE_BY_TEAMS[self.sessionProvider.getArenaDP().isAllyTeam(team)]
        self._invokeMarker(handle, 'as_setState', state)

    def __onCapturedLocked(self, pointID, team):
        handle, _, _, _ = self.__markers[pointID]
        state = settings.CAPTURE_FROZEN_STATE_BY_TEAMS[self.sessionProvider.getArenaDP().isAllyTeam(team)]
        self._invokeMarker(handle, 'as_setState', state)

    def __onBlocked(self, pointID):
        handle, _, _, _ = self.__markers[pointID]
        self._invokeMarker(handle, 'as_setState', settings.RESOURCE_STATE.CONFLICT)

    def __onAmountChanged(self, pointID, amount, totalAmount):
        progress = float(amount) / totalAmount * 100
        handle, _, _, _ = self.__markers[pointID]
        self._invokeMarker(handle, 'as_setProgress', progress)


class GasAttackSafeZonePlugin(plugins.MarkerPlugin):

    def __init__(self, parentObj):
        super(GasAttackSafeZonePlugin, self).__init__(parentObj)
        self.__safeZoneMarkerHandle = None
        self.__isMarkerVisible = False
        self.__settings = self.sessionProvider.arenaVisitor.getGasAttackSettings()
        return

    def init(self):
        super(GasAttackSafeZonePlugin, self).init()
        ctrl = self.sessionProvider.dynamic.gasAttack
        if ctrl is not None:
            ctrl.onUpdated += self.__onGasAttackUpdate
        self.__initMarker(self.__settings.position)
        return

    def fini(self):
        self.__settings = None
        ctrl = self.sessionProvider.dynamic.gasAttack
        if ctrl is not None:
            ctrl.onUpdated -= self.__onGasAttackUpdate
        super(GasAttackSafeZonePlugin, self).fini()
        return

    def start(self):
        super(GasAttackSafeZonePlugin, self).start()

    def stop(self):
        self.__delSafeZoneMarker()
        super(GasAttackSafeZonePlugin, self).stop()

    def __updateSafeZoneMarker(self, isVisible):
        if not self.__isMarkerVisible == isVisible:
            self.__isMarkerVisible = isVisible
            self._invokeMarker(self.__safeZoneMarkerHandle, 'update', self.__isMarkerVisible)

    def __initMarker(self, center):
        if self.__safeZoneMarkerHandle is None:
            self.__safeZoneMarkerHandle = self._createMarkerWithPosition(settings.MARKER_SYMBOL_NAME.SAFE_ZONE_MARKER, center + settings.MARKER_POSITION_ADJUSTMENT)
        return

    def __delSafeZoneMarker(self):
        if self.__safeZoneMarkerHandle is not None:
            self._destroyMarker(self.__safeZoneMarkerHandle)
            self.__safeZoneMarkerHandle = None
        return

    def __onGasAttackUpdate(self, state):
        self.__updateSafeZoneMarker(state.state in GAS_ATTACK_STATE.VISIBLE)


class FalloutMarkersManager(MarkersManager):

    def _createCanvas(self, arenaVisitor):
        if arenaVisitor.hasFlags():
            return GUI.WGVehicleFalloutMarkersCanvasFlashAS3(self.movie)
        else:
            return super(FalloutMarkersManager, self)._createCanvas(arenaVisitor)

    def _setupPlugins(self, arenaVisitor):
        setup = super(FalloutMarkersManager, self)._setupPlugins(arenaVisitor)
        if arenaVisitor.hasFlags():
            setup['vehicles'] = VehicleAndFlagsMarkerPlugin
            setup['absorption'] = AbsorptionMarkersPlugin
        elif arenaVisitor.hasRespawns():
            setup['vehicles'] = RespawnableVehicleMarkerPlugin
        if arenaVisitor.hasRepairPoints():
            setup['repairs'] = RepairsMarkerPlugin
        if arenaVisitor.hasResourcePoints():
            setup['resources'] = ResourceMarkerPlugin
        if arenaVisitor.hasGasAttack():
            setup['safe_zone'] = GasAttackSafeZonePlugin
        return setup
