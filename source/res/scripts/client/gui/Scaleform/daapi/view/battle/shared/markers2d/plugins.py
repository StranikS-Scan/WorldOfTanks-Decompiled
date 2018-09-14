# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/markers2d/plugins.py
import math
from functools import partial
import BattleReplay
import BigWorld
import constants
from CTFManager import g_ctfManager
from Math import Matrix
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control import g_sessionProvider, avatar_getter
from gui.battle_control.arena_info.arena_vos import VehicleActions
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _EVENT_ID
from gui.battle_control.battle_constants import NEUTRAL_TEAM, PLAYER_GUI_PROPS
from gui.battle_control.battle_constants import REPAIR_STATE_ID, GAS_ATTACK_STATE
from gui.shared.utils.plugins import IPlugin, PluginsCollection
from helpers import i18n, time_utils
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents

def createPlugins(manager):
    assert isinstance(manager, IMarkersManager), 'Class of manager must extends IMarkersManager'
    visitor = g_sessionProvider.arenaVisitor
    setup = {'equipments': EquipmentsMarkerPlugin}
    if visitor.hasFlags():
        setup['vehicles_flags'] = VehicleAndFlagsMarkerPlugin
        setup['absorption'] = AbsorptionMarkersPlugin
    elif visitor.hasRespawns():
        setup['vehicles'] = RespawnableVehicleMarkerPlugin
    else:
        setup['vehicles'] = VehicleMarkerPlugin
    if visitor.hasRepairPoints():
        setup['repairs'] = RepairsMarkerPlugin
    if visitor.hasResourcePoints():
        setup['resources'] = ResourceMarkerPlugin
    if visitor.hasGasAttack():
        setup['safe_zone'] = GasAttackSafeZonePlugin
    plugins = PluginsCollection(manager)
    plugins.addPlugins(setup)
    return plugins


class IMarkersManager(object):

    def createMarker(self, matrix, symbol, active=True):
        raise NotImplementedError

    def invokeMarker(self, handle, function, args=None):
        raise NotImplementedError

    def setMarkerMatrix(self, handle, matrix):
        raise NotImplementedError

    def setMarkerActive(self, handle, active):
        raise NotImplementedError

    def destroyMarker(self, handle):
        raise NotImplementedError


class MarkerPlugin(IPlugin):

    def _createMarker(self, pos, symbol, active=True):
        mProv = Matrix()
        mProv.translation = pos
        return self._parentObj.createMarker(mProv, symbol, active)

    def _createMarkerWithMatrix(self, matrix, symbol, active=True):
        return self._parentObj.createMarker(matrix, symbol, active)

    def _invokeMarker(self, handle, function, args=None):
        self._parentObj.invokeMarker(handle, function, args)

    def _setMarkerPos(self, handle, pos):
        matrix = Matrix()
        matrix.setTranslate(pos)
        self._parentObj.setMarkerMatrix(handle, matrix)

    def _setMarkerMatrix(self, handle, matrix):
        self._parentObj.setMarkerMatrix(handle, matrix)

    def _setMarkerActive(self, handle, active):
        self._parentObj.setMarkerActive(handle, active)

    def _destroyMarker(self, handle):
        self._parentObj.destroyMarker(handle)


class Marker(object):
    """
    Base class which holds info for a Marker
    """

    def __init__(self, markerID, active=True):
        super(Marker, self).__init__()
        self._markerID = markerID
        self._active = active

    def getMarkerID(self):
        return self._markerID

    def isActive(self):
        return self._active

    def setActive(self, active):
        """
        Sets marker is shown/hidden on the scene.
        :param active: bool.
        :return: True if property is changed, otherwise - False.
        """
        if self._active != active:
            self._active = active
            return True
        else:
            return False


class FlagMarker(Marker):
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


class VehicleMarker(Marker):

    def __init__(self, markerID, vProxy, uiProxy, active=True):
        super(VehicleMarker, self).__init__(markerID, active)
        self.vProxy = None
        self.uiProxy = uiProxy
        self._flagBearer = False
        self._speaking = False
        self.attach(vProxy)
        return

    def attach(self, vProxy):
        self.detach()
        self.vProxy = vProxy
        self.vProxy.appearance.onModelChanged += self.__onModelChanged

    def detach(self):
        if self.vProxy is not None:
            self.vProxy.appearance.onModelChanged -= self.__onModelChanged
            self.vProxy = None
        return

    def destroy(self):
        self.detach()
        self.uiProxy = None
        return

    def isFlagBearer(self):
        return self._flagBearer

    def setFlagBearer(self, bearer):
        if self._flagBearer != bearer:
            self._flagBearer = bearer
            return True
        else:
            return False

    def isSpeaking(self):
        return self._speaking

    def setSpeaking(self, speaking):
        if self._speaking != speaking:
            self._speaking = speaking
            return True
        else:
            return False

    def __onModelChanged(self):
        if self.uiProxy() is not None:
            self.uiProxy().markerSetMatrix(self._markerID, self.vProxy.model.node('HP_gui'))
        return


class VehicleMarkerPlugin(MarkerPlugin, IArenaVehiclesController):
    __slots__ = ('__vehiclesMarkers', '__playerVehicleID')

    def __init__(self, parentObj):
        super(VehicleMarkerPlugin, self).__init__(parentObj)
        self.__vehiclesMarkers = {}
        self.__playerVehicleID = 0

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    def init(self, *args):
        super(VehicleMarkerPlugin, self).init()
        ctrl = g_sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleMarkerAdded += self.__onVehicleMarkerAdded
            ctrl.onVehicleMarkerRemoved += self.__onVehicleMarkerRemoved
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        g_messengerEvents.voip.onPlayerSpeaking += self.__onPlayerSpeaking
        return

    def fini(self):
        ctrl = g_sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleMarkerAdded -= self.__onVehicleMarkerAdded
            ctrl.onVehicleMarkerRemoved -= self.__onVehicleMarkerRemoved
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        g_messengerEvents.voip.onPlayerSpeaking -= self.__onPlayerSpeaking
        super(VehicleMarkerPlugin, self).fini()
        return

    def start(self):
        super(VehicleMarkerPlugin, self).start()
        self.__playerVehicleID = avatar_getter.getPlayerVehicleID()
        g_sessionProvider.addArenaCtrl(self)

    def stop(self):
        self.__vehiclesMarkers = {}
        super(VehicleMarkerPlugin, self).stop()

    def setTeamKiller(self, vID):
        if vID not in self.__vehiclesMarkers:
            return
        handle = self.__vehiclesMarkers[vID].getMarkerID()
        ctx = g_sessionProvider.getCtx()
        if not ctx.isTeamKiller(vID=vID) or ctx.isSquadMan(vID=vID):
            return
        self._invokeMarker(handle, 'setEntityName', [PLAYER_GUI_PROPS.teamKiller.name()])

    def invalidateArenaInfo(self):
        self.invalidateVehiclesInfo(g_sessionProvider.getArenaDP())

    def invalidateVehiclesInfo(self, arenaDP):
        for vInfo in arenaDP.getVehiclesInfoIterator():
            self.addVehicleInfo(vInfo, arenaDP)

    def addVehicleInfo(self, vInfo, arenaDP):
        vehicleID = vInfo.vehicleID
        if vehicleID != self.__playerVehicleID:
            active = self.__isVehicleActive(vehicleID)
            vehicle = BigWorld.entity(vehicleID)
            if vehicle:
                guiProps = g_sessionProvider.getCtx().getPlayerGuiProps(vehicleID, vInfo.team)
                self.__addOrUpdateVehicleMarker(vehicle.proxy, vInfo, guiProps, active)

    def updateVehiclesInfo(self, updated, arenaDP):
        for _, vInfo in updated:
            self.__setEntityName(vInfo, arenaDP)

    def invalidatePlayerStatus(self, flags, vInfo, arenaDP):
        self.__setEntityName(vInfo, arenaDP)

    def _updateFlagbearerState(self, vehID, newState):
        if vehID in self.__vehiclesMarkers:
            marker = self.__vehiclesMarkers[vehID]
            if marker.isActive() and marker.setFlagBearer(newState):
                self._invokeMarker(marker.getMarkerID(), 'updateFlagBearerState', [newState])

    def _hideVehicleMarker(self, vehicleID):
        if vehicleID in self.__vehiclesMarkers:
            marker = self.__vehiclesMarkers[vehicleID]
            if marker.setActive(False):
                self._setMarkerActive(marker.getMarkerID(), False)
                self._setMarkerMatrix(marker.getMarkerID(), None)
                marker.detach()
        return

    def _destroyVehicleMarker(self, vehicleID):
        if vehicleID in self.__vehiclesMarkers:
            marker = self.__vehiclesMarkers.pop(vehicleID)
            self._destroyMarker(marker.getMarkerID())
            marker.destroy()

    def __isVehicleActive(self, vehicleID):
        active = False
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle is not None and vehicle.isStarted:
            active = True
        elif vehicleID in BigWorld.player().arena.positions:
            active = True
        return active

    def __addOrUpdateVehicleMarker(self, vProxy, vInfo, guiProps, active=True):
        speaking = self.bwProto.voipController.isPlayerSpeaking(vInfo.player.accountDBID)
        flagBearer = g_ctfManager.getVehicleCarriedFlagID(vInfo.vehicleID) is not None
        if active:
            mProv = vProxy.model.node('HP_gui')
        else:
            mProv = None
        if vInfo.vehicleID in self.__vehiclesMarkers:
            marker = self.__vehiclesMarkers[vInfo.vehicleID]
            if marker.setActive(active):
                self._setMarkerMatrix(marker.getMarkerID(), mProv)
                self._setMarkerActive(marker.getMarkerID(), active)
                self.__updateVehicleStates(marker, speaking, vProxy.health, flagBearer)
                marker.attach(vProxy)
        else:
            hunting = VehicleActions.isHunting(vInfo.events)
            markerID = self._createMarkerWithMatrix(mProv, 'VehicleMarker')
            self.__vehiclesMarkers[vInfo.vehicleID] = VehicleMarker(markerID, vProxy, self._parentObj.getCanvasProxy(), active)
            battleCtx = g_sessionProvider.getCtx()
            result = battleCtx.getPlayerFullNameParts(vProxy.id)
            vType = vInfo.vehicleType
            squadIndex = 0
            if g_sessionProvider.arenaVisitor.gui.isFalloutMultiTeam() and vInfo.squadIndex:
                squadIndex = vInfo.squadIndex
            self._invokeMarker(markerID, 'setVehicleInfo', [vType.classTag,
             vType.iconPath,
             result.vehicleName,
             vType.level,
             result.playerFullName,
             result.playerName,
             result.clanAbbrev,
             result.regionCode,
             vType.maxHealth,
             guiProps.name(),
             hunting,
             squadIndex])
            if not vProxy.isAlive():
                self.__updateMarkerState(markerID, 'dead', True)
            if active:
                self.__updateVehicleStates(self.__vehiclesMarkers[vInfo.vehicleID], speaking, vProxy.health, flagBearer)
        return

    def __updateVehicleStates(self, marker, speaking, health, flagBearer):
        handle = marker.getMarkerID()
        if marker.setSpeaking(speaking):
            self._invokeMarker(handle, 'setSpeaking', [speaking])
        if marker.setFlagBearer(flagBearer):
            self._invokeMarker(handle, 'updateFlagBearerState', [flagBearer])
        self._invokeMarker(handle, 'setHealth', [health])

    def __setEntityName(self, vInfo, arenaDP):
        vehicleID = vInfo.vehicleID
        if vehicleID not in self.__vehiclesMarkers:
            return
        handle = self.__vehiclesMarkers[vehicleID].getMarkerID()
        self._invokeMarker(handle, 'setEntityName', [arenaDP.getPlayerGuiProps(vehicleID, vInfo.team).name()])

    def __onVehicleMarkerAdded(self, vProxy, vInfo, guiProps):
        self.__addOrUpdateVehicleMarker(vProxy, vInfo, guiProps)

    def __onVehicleMarkerRemoved(self, vehicleID):
        self._hideVehicleMarker(vehicleID)

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if vehicleID not in self.__vehiclesMarkers:
            return
        handle = self.__vehiclesMarkers[vehicleID].getMarkerID()
        if eventID == _EVENT_ID.VEHICLE_HIT:
            self.__updateMarkerState(handle, 'hit', value)
        elif eventID == _EVENT_ID.VEHICLE_ARMOR_PIERCED:
            self.__updateMarkerState(handle, 'hit_pierced', value)
        elif eventID == _EVENT_ID.VEHICLE_DEAD:
            self.__updateMarkerState(handle, 'dead', value)
        elif eventID == _EVENT_ID.VEHICLE_SHOW_MARKER:
            self.__showActionMarker(handle, value)
        elif eventID == _EVENT_ID.VEHICLE_HEALTH:
            self.__updateVehicleHealth(handle, *value)

    def __updateMarkerState(self, handle, newState, isImmediate=False):
        self._invokeMarker(handle, 'updateState', [newState, isImmediate])

    def __showActionMarker(self, handle, newState):
        self._invokeMarker(handle, 'showActionMarker', [newState])

    def __updateVehicleHealth(self, handle, newHealth, aInfo, attackReasonID):
        if newHealth < 0 and not constants.SPECIAL_VEHICLE_HEALTH.IS_AMMO_BAY_DESTROYED(newHealth):
            newHealth = 0
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isTimeWarpInProgress:
            self._invokeMarker(handle, 'setHealth', [newHealth])
        else:
            self._invokeMarker(handle, 'updateHealth', [newHealth, self.__getVehicleDamageType(aInfo), constants.ATTACK_REASONS[attackReasonID]])

    def __onPlayerSpeaking(self, accountDBID, flag):
        """
        Listener for event g_messengerEvents.voip.onPlayerSpeaking.
        :param accountDBID: player db ID
        :param flag: isSpeaking (true or false)
        """
        vehicleID = g_sessionProvider.getCtx().getVehIDByAccDBID(accountDBID)
        if vehicleID in self.__vehiclesMarkers:
            marker = self.__vehiclesMarkers[vehicleID]
            if marker.setSpeaking(flag):
                self._invokeMarker(marker.getMarkerID(), 'setSpeaking', [flag])

    def __getVehicleDamageType(self, attackerInfo):
        if not attackerInfo:
            return settings.DAMAGE_TYPE.FROM_UNKNOWN
        attackerID = attackerInfo.vehicleID
        if attackerID == avatar_getter.getPlayerVehicleID():
            return settings.DAMAGE_TYPE.FROM_PLAYER
        entityName = g_sessionProvider.getCtx().getPlayerGuiProps(attackerID, attackerInfo.team)
        if entityName == PLAYER_GUI_PROPS.squadman:
            return settings.DAMAGE_TYPE.FROM_SQUAD
        if entityName == PLAYER_GUI_PROPS.ally:
            return settings.DAMAGE_TYPE.FROM_ALLY
        return settings.DAMAGE_TYPE.FROM_ENEMY if entityName == PLAYER_GUI_PROPS.enemy else settings.DAMAGE_TYPE.FROM_UNKNOWN


class RespawnableVehicleMarkerPlugin(VehicleMarkerPlugin):

    def _hideVehicleMarker(self, vehicleID):
        self._destroyVehicleMarker(vehicleID)


class EquipmentsMarkerPlugin(MarkerPlugin):
    __slots__ = ('__markers',)

    def __init__(self, parentObj):
        super(EquipmentsMarkerPlugin, self).__init__(parentObj)
        self.__markers = {}

    def init(self):
        super(EquipmentsMarkerPlugin, self).init()
        ctrl = g_sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentMarkerShown += self.__onShown
        return

    def fini(self):
        ctrl = g_sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentMarkerShown -= self.__onShown
        super(EquipmentsMarkerPlugin, self).fini()
        return

    def start(self):
        super(EquipmentsMarkerPlugin, self).start()

    def stop(self):
        for handle, callbackID in self.__markers.items():
            self._destroyMarker(handle)
            if callbackID is not None:
                BigWorld.cancelCallback(callbackID)

        self.__markers = None
        super(EquipmentsMarkerPlugin, self).stop()
        return

    def __onShown(self, item, pos, dir, time):
        handle = self._createMarker(pos + settings.MARKER_POSITION_ADJUSTMENT, settings.EQUIPMENT_MARKER_TYPE)
        defaultPostfix = i18n.makeString(INGAME_GUI.FORTCONSUMABLES_TIMER_POSTFIX)
        self._invokeMarker(handle, 'init', [item.getMarker(), str(int(time)), defaultPostfix])
        self.__initTimer(int(math.ceil(time)), handle)

    def __initTimer(self, timer, handle):
        timer -= 1
        if timer < 0:
            self._destroyMarker(handle)
            if handle in self.__markers:
                del self.__markers[handle]
            return
        self._invokeMarker(handle, 'updateTimer', [str(timer)])
        callbackId = BigWorld.callback(1, partial(self.__initTimer, timer, handle))
        self.__markers[handle] = callbackId


class VehicleAndFlagsMarkerPlugin(RespawnableVehicleMarkerPlugin):
    """
    This plugin handles Flags on 3d scene, also it switches flagBearer state for the base (vehicles) class.
    The flags are created at start and then they can be only updated for the remain life cycle.
    """
    __slots__ = ('__markers', '__spawnPoints', '__playerTeam', '__isTeamPlayer')

    def __init__(self, parentObj):
        super(VehicleAndFlagsMarkerPlugin, self).__init__(parentObj)
        self.__markers = {}
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
        visitor = g_sessionProvider.arenaVisitor
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
        for flagMarker in self.__markers.values():
            self.__cancelCallback(flagMarker)

        self.__markers = None
        self.__spawnPoints = None
        super(VehicleAndFlagsMarkerPlugin, self).stop()
        return

    def __addOrUpdateFlagMarker(self, flagID, flagPos, marker):
        position = flagPos + settings.MARKER_POSITION_ADJUSTMENT
        if flagID in self.__markers:
            flagMarker = self.__markers[flagID]
            handle = flagMarker.getMarkerID()
            self._setMarkerPos(handle, position)
            if flagMarker.setActive(True):
                self._setMarkerActive(handle, True)
            self.__cancelCallback(flagMarker)
        else:
            handle = self._createMarker(position, settings.FLAG_MARKER_TYPE)
            self.__markers[flagID] = FlagMarker(handle)
        self._invokeMarker(handle, 'setIcon', [marker])

    def __cancelCallback(self, flagMarker):
        callbackID = flagMarker.getCallbackID()
        if callbackID is not None:
            BigWorld.cancelCallback(callbackID)
            flagMarker.setCallbackID(None)
        return

    def __hideFlagMarker(self, flagID):
        if flagID in self.__markers:
            flagMarker = self.__markers[flagID]
            if flagMarker.setActive(False):
                self._setMarkerActive(flagMarker.getMarkerID(), False)
            self.__cancelCallback(flagMarker)

    def __initTimer(self, timer, flagID):
        if flagID not in self.__markers:
            LOG_ERROR('VehicleAndFlagsMarkerPlugin does not have marker with flag id: ', flagID)
            return
        else:
            timer -= 1
            flagMarker = self.__markers[flagID]
            if timer < 0:
                flagMarker.setCallbackID(None)
                return
            self._invokeMarker(flagMarker.getMarkerID(), 'setLabel', [i18n.makeString(INGAME_GUI.FLAGS_TIMER, time=str(timer))])
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

    def __onCapturedByVehicle(self, flagID, flagTeam, vehicleID):
        self._updateFlagbearerState(vehicleID, True)
        self.__hideFlagMarker(flagID)

    def __onDroppedToGround(self, flagID, flagTeam, loserVehicleID, flagPos, respawnTime):
        flagType = self.__getFlagMarkerType(flagID, flagTeam)
        self._updateFlagbearerState(loserVehicleID, False)
        self.__addOrUpdateFlagMarker(flagID, flagPos, flagType)
        timer = respawnTime - BigWorld.serverTime()
        self.__initTimer(int(math.ceil(timer)), flagID)

    def __onAbsorbed(self, flagID, flagTeam, vehicleID, respawnTime):
        self._updateFlagbearerState(vehicleID, False)
        self.__hideFlagMarker(flagID)

    def __onRemoved(self, flagID, flagTeam, vehicleID):
        self.__hideFlagMarker(flagID)
        if vehicleID is not None:
            self._updateFlagbearerState(vehicleID, False)
        return

    def __getFlagMarkerType(self, flagID, flagTeam=0):
        if flagTeam != NEUTRAL_TEAM:
            if flagTeam == self.__playerTeam:
                return settings.FLAG_TYPE.ALLY
            return settings.FLAG_TYPE.ENEMY
        return settings.FLAG_TYPE.NEUTRAL


class AbsorptionMarkersPlugin(MarkerPlugin):
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
        visitor = g_sessionProvider.arenaVisitor
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
                handle = self._createMarker(position + settings.MARKER_POSITION_ADJUSTMENT, settings.FLAG_CAPTURE_MARKER_TYPE, flagBearer)
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


class RepairsMarkerPlugin(MarkerPlugin):
    __slots__ = ('__markers',)

    def __init__(self, parentObj):
        super(RepairsMarkerPlugin, self).__init__(parentObj)
        self.__markers = {}

    def init(self):
        super(RepairsMarkerPlugin, self).init()
        ctrl = g_sessionProvider.dynamic.repair
        if ctrl is not None:
            ctrl.onStateCreated += self.__onRepairPointStateCreated
            ctrl.onTimerUpdated += self.__onRepairPointTimerUpdated
        return

    def fini(self):
        ctrl = g_sessionProvider.dynamic.repair
        if ctrl is not None:
            ctrl.onStateCreated -= self.__onRepairPointStateCreated
            ctrl.onTimerUpdated -= self.__onRepairPointTimerUpdated
        super(RepairsMarkerPlugin, self).fini()
        return

    def start(self):
        playerTeam = avatar_getter.getPlayerTeam()
        ctrl = g_sessionProvider.dynamic.repair
        if ctrl is not None:
            getPointStateID = ctrl.getPointStateID
        else:

            def getPointStateID(_):
                return REPAIR_STATE_ID.UNRESOLVED

        for pointID, (team, repairPos) in g_sessionProvider.arenaVisitor.type.getRepairPointIterator():
            isAlly = team in (NEUTRAL_TEAM, playerTeam)
            markerID = self._createMarker(repairPos + settings.MARKER_POSITION_ADJUSTMENT, settings.REPAIR_MARKER_TYPE)
            if getPointStateID(pointID) == REPAIR_STATE_ID.COOLDOWN:
                icon = 'cooldown'
            else:
                icon = 'active'
            self._invokeMarker(markerID, 'setIcon', [icon, isAlly])
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
        self._parentObj.invokeMarker(markerID, 'setIcon', [icon, isAlly])
        self._parentObj.invokeMarker(markerID, 'setLabel', [''])

    def __onRepairPointTimerUpdated(self, pointIndex, stateID, timeLeft):
        if stateID == REPAIR_STATE_ID.COOLDOWN and pointIndex in self.__markers:
            self._parentObj.invokeMarker(self.__markers[pointIndex][0], 'setLabel', [time_utils.getTimeLeftFormat(timeLeft)])


class ResourceMarkerPlugin(MarkerPlugin):
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
        arenaDP = g_sessionProvider.getArenaDP()
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
            handle = self._createMarker(resourcePos + settings.MARKER_POSITION_ADJUSTMENT, settings.RESOURCE_MARKER_TYPE)
            self._invokeMarker(handle, 'as_init', [pointID, state, progress])
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
            self._invokeMarker(handle, 'as_onSettingsChanged', [])

    def __onIsFree(self, pointID):
        handle, _, _, _ = self.__markers[pointID]
        self._invokeMarker(handle, 'as_setState', [settings.RESOURCE_STATE.READY])

    def __onCooldown(self, pointID, serverTime):
        handle, _, _, _ = self.__markers[pointID]
        self._invokeMarker(handle, 'as_setState', [settings.RESOURCE_STATE.COOLDOWN])

    def __onCaptured(self, pointID, team):
        handle, _, _, _ = self.__markers[pointID]
        state = settings.CAPTURE_STATE_BY_TEAMS[g_sessionProvider.getArenaDP().isAllyTeam(team)]
        self._invokeMarker(handle, 'as_setState', [state])

    def __onCapturedLocked(self, pointID, team):
        handle, _, _, _ = self.__markers[pointID]
        state = settings.CAPTURE_FROZEN_STATE_BY_TEAMS[g_sessionProvider.getArenaDP().isAllyTeam(team)]
        self._invokeMarker(handle, 'as_setState', [state])

    def __onBlocked(self, pointID):
        handle, _, _, _ = self.__markers[pointID]
        self._invokeMarker(handle, 'as_setState', [settings.RESOURCE_STATE.CONFLICT])

    def __onAmountChanged(self, pointID, amount, totalAmount):
        progress = float(amount) / totalAmount * 100
        handle, _, _, _ = self.__markers[pointID]
        self._invokeMarker(handle, 'as_setProgress', [progress])


class GasAttackSafeZonePlugin(MarkerPlugin):

    def __init__(self, parentObj):
        super(GasAttackSafeZonePlugin, self).__init__(parentObj)
        self.__safeZoneMarkerHandle = None
        self.__isMarkerVisible = False
        self.__settings = g_sessionProvider.arenaVisitor.getGasAttackSettings()
        return

    def init(self):
        super(GasAttackSafeZonePlugin, self).init()
        ctrl = g_sessionProvider.dynamic.gasAttack
        if ctrl is not None:
            ctrl.onUpdated += self.__onGasAttackUpdate
        self.__initMarker(self.__settings.position)
        return

    def fini(self):
        self.__settings = None
        ctrl = g_sessionProvider.dynamic.gasAttack
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
            self._invokeMarker(self.__safeZoneMarkerHandle, 'update', [self.__isMarkerVisible])

    def __initMarker(self, center):
        if self.__safeZoneMarkerHandle is None:
            self.__safeZoneMarkerHandle = self._createMarker(center + settings.MARKER_POSITION_ADJUSTMENT, settings.SAFE_ZONE_MARKER_TYPE)
        return

    def __delSafeZoneMarker(self):
        if self.__safeZoneMarkerHandle is not None:
            self._destroyMarker(self.__safeZoneMarkerHandle)
            self.__safeZoneMarkerHandle = None
        return

    def __onGasAttackUpdate(self, state):
        self.__updateSafeZoneMarker(state.state in GAS_ATTACK_STATE.VISIBLE)
