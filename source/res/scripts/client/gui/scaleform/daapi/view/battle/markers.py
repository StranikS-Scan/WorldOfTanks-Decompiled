# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/markers.py
from functools import partial
import math
import weakref
from Math import Vector3, Matrix
import BattleReplay
from CTFManager import g_ctfManager
import SoundGroups
from account_helpers.settings_core import g_settingsCore
import constants
import GUI
import BigWorld
from gui.battle_control.dyn_squad_arena_controllers import IDynSquadEntityClient
from gui.shared.utils.plugins import PluginsCollection, IPlugin
from helpers import i18n, time_utils
from debug_utils import LOG_ERROR
from gui import DEPTH_OF_VehicleMarker, GUI_SETTINGS
from gui.Scaleform import VoiceChatInterface, ColorSchemeManager
from gui.Scaleform.Flash import Flash
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control import g_sessionProvider
from gui.battle_control.arena_info import isEventBattle
from gui.battle_control.arena_info.arena_vos import VehicleActions
from gui.battle_control.battle_constants import PLAYER_ENTITY_NAME
from items.vehicles import VEHICLE_CLASS_TAGS

class MarkersManager(Flash, IDynSquadEntityClient):
    __SWF_FILE_NAME = 'VehicleMarkersManager.swf'
    MARKER_POSITION_ADJUSTMENT = Vector3(0.0, 12.0, 0.0)

    class DAMAGE_TYPE:
        FROM_UNKNOWN = 0
        FROM_ALLY = 1
        FROM_ENEMY = 2
        FROM_SQUAD = 3
        FROM_PLAYER = 4

    def __init__(self, parentUI):
        Flash.__init__(self, self.__SWF_FILE_NAME)
        self.component.wg_inputKeyMode = 2
        self.component.position.z = DEPTH_OF_VehicleMarker
        self.component.drawWithRestrictedViewPort = False
        self.movie.backgroundAlpha = 0
        self.colorManager = ColorSchemeManager._ColorSchemeManager()
        self.colorManager.populateUI(weakref.proxy(self))
        self.__plugins = PluginsCollection(self)
        plugins = {'equipments': _EquipmentsMarkerPlugin}
        if isEventBattle():
            plugins.update({'flags': _FlagsMarkerPlugin,
             'repairs': _RepairsMarkerPlugin})
        self.__plugins.addPlugins(plugins)
        self.__ownUI = None
        self.__parentUI = parentUI
        self.__markers = dict()
        return

    def updateSquadmanVeh(self, vID):
        handle = getattr(BigWorld.entity(vID), 'marker', None)
        if handle is not None:
            self.invokeMarker(handle, 'setEntityName', [PLAYER_ENTITY_NAME.squadman.name()])
        return

    def showExtendedInfo(self, value):
        self.__invokeCanvas('setShowExInfoFlag', [value])
        for handle in self.__markers.iterkeys():
            self.invokeMarker(handle, 'showExInfo', [value])

    def setScaleProps(self, minScale = 40, maxScale = 100, defScale = 100, speed = 3.0):
        if constants.IS_DEVELOPMENT:
            self.__ownUI.scaleProperties = (minScale,
             maxScale,
             defScale,
             speed)

    def setAlphaProps(self, minAlpha = 40, maxAlpha = 100, defAlpha = 100, speed = 3.0):
        if constants.IS_DEVELOPMENT:
            self.__ownUI.alphaProperties = (minAlpha,
             maxAlpha,
             defAlpha,
             speed)

    def start(self):
        self.active(True)
        self.__ownUI = GUI.WGVehicleMarkersCanvasFlash(self.movie)
        self.__ownUI.wg_inputKeyMode = 2
        self.__ownUI.scaleProperties = GUI_SETTINGS.markerScaleSettings
        self.__ownUI.alphaProperties = GUI_SETTINGS.markerBgSettings
        self.__ownUIProxy = weakref.ref(self.__ownUI)
        self.__ownUIProxy().markerSetScale(g_settingsCore.interfaceScale.get())
        g_settingsCore.interfaceScale.onScaleChanged += self.updateMarkersScale
        self.__parentUI.component.addChild(self.__ownUI, 'vehicleMarkersManager')
        self.__markersCanvasUI = self.getMember('vehicleMarkersCanvas')
        self.__plugins.init()
        self.__plugins.start()

    def destroy(self):
        self.__plugins.stop()
        g_settingsCore.interfaceScale.onScaleChanged -= self.updateMarkersScale
        if self.__parentUI is not None:
            setattr(self.__parentUI.component, 'vehicleMarkersManager', None)
        self.__plugins.fini()
        self.__parentUI = None
        self.__ownUI = None
        self.__markersCanvasUI = None
        self.colorManager.dispossessUI()
        self.close()
        return

    def createMarker(self, vProxy):
        vInfo = dict(vProxy.publicInfo)
        battleCtx = g_sessionProvider.getCtx()
        if battleCtx.isObserver(vProxy.id):
            return -1
        isFriend = vInfo['team'] == BigWorld.player().team
        vehID = vProxy.id
        vInfoEx = g_sessionProvider.getArenaDP().getVehicleInfo(vehID)
        vTypeDescr = vProxy.typeDescriptor
        maxHealth = vTypeDescr.maxHealth
        mProv = vProxy.model.node('HP_gui')
        tags = set(vTypeDescr.type.tags & VEHICLE_CLASS_TAGS)
        vClass = tags.pop() if len(tags) > 0 else ''
        entityName = battleCtx.getPlayerEntityName(vehID, vInfoEx.team)
        entityType = 'ally' if BigWorld.player().team == vInfoEx.team else 'enemy'
        speaking = False
        if GUI_SETTINGS.voiceChat:
            speaking = VoiceChatInterface.g_instance.isPlayerSpeaking(vInfoEx.player.accountDBID)
        hunting = VehicleActions.isHunting(vInfoEx.events)
        handle = self.__ownUI.addMarker(mProv, 'VehicleMarkerAlly' if isFriend else 'VehicleMarkerEnemy')
        self.__markers[handle] = _VehicleMarker(vProxy, self.__ownUIProxy(), handle)
        fullName, pName, clanAbbrev, regionCode, vehShortName = battleCtx.getFullPlayerNameWithParts(vProxy.id)
        self.invokeMarker(handle, 'init', [vClass,
         vInfoEx.vehicleType.iconPath,
         vehShortName,
         vInfoEx.vehicleType.level,
         fullName,
         pName,
         clanAbbrev,
         regionCode,
         vProxy.health,
         maxHealth,
         entityName.name(),
         speaking,
         hunting,
         entityType,
         self.isVehicleFlagbearer(vehID)])
        return handle

    def destroyMarker(self, handle):
        if self.__markers.has_key(handle):
            self.__markers[handle].destroy()
            del self.__markers[handle]
            self.__ownUI.delMarker(handle)

    def createStaticMarker(self, pos, symbol):
        mProv = Matrix()
        mProv.translation = pos
        handle = self.__ownUI.addMarker(mProv, symbol)
        return (mProv, handle)

    def destroyStaticMarker(self, handle):
        if self.__ownUI:
            self.__ownUI.delMarker(handle)

    def updateMarkerState(self, handle, newState, isImmediate = False):
        self.invokeMarker(handle, 'updateState', [newState, isImmediate])

    def showActionMarker(self, handle, newState):
        self.invokeMarker(handle, 'showActionMarker', [newState])

    def updateFlagbearerState(self, handle, newState):
        self.invokeMarker(handle, 'updateFlagbearerState', [newState])

    def onVehicleHealthChanged(self, handle, curHealth, attackerID = -1, attackReasonID = 0):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isTimeWarpInProgress:
            return
        if curHealth < 0 and curHealth not in constants.SPECIAL_VEHICLE_HEALTH.AMMO_BAY_EXPLOSION:
            curHealth = 0
        self.invokeMarker(handle, 'updateHealth', [curHealth, self.__getVehicleDamageType(attackerID), constants.ATTACK_REASONS[attackReasonID]])

    def showDynamic(self, vID, flag):
        handle = getattr(BigWorld.entity(vID), 'marker', None)
        if handle is not None and GUI_SETTINGS.voiceChat:
            self.invokeMarker(handle, 'setSpeaking', [flag])
        return

    def updateMarkersScale(self, scale = None):
        if self.__ownUIProxy() is not None:
            if scale is None:
                self.__ownUIProxy().markerSetScale(g_settingsCore.interfaceScale.get())
            else:
                self.__ownUIProxy().markerSetScale(scale)
        return

    def setTeamKiller(self, vID):
        ctx = g_sessionProvider.getCtx()
        if not ctx.isTeamKiller(vID=vID) or ctx.isSquadMan(vID=vID):
            return
        else:
            handle = getattr(BigWorld.entity(vID), 'marker', None)
            if handle is not None:
                self.invokeMarker(handle, 'setEntityName', [PLAYER_ENTITY_NAME.teamKiller.name()])
            return

    def invokeMarker(self, handle, function, args = None):
        if handle == -1:
            return
        else:
            if args is None:
                args = []
            self.__ownUI.markerInvoke(handle, (function, args))
            return

    def setMarkerSettings(self, settings):
        if self.__markersCanvasUI:
            self.__markersCanvasUI.setMarkerSettings(settings)

    def setMarkerDuration(self, value):
        self.__invokeCanvas('setMarkerDuration', [value])

    def updateMarkers(self):
        self.colorManager.update()
        for handle in self.__markers.iterkeys():
            self.invokeMarker(handle, 'update', [])

    def updateMarkerSettings(self):
        for handle in self.__markers.iterkeys():
            self.invokeMarker(handle, 'updateMarkerSettings', [])

    def isVehicleFlagbearer(self, vehicleID):
        for flagID in g_ctfManager.getFlags():
            flagInfo = g_ctfManager.getFlagInfo(flagID)
            if flagInfo['vehicle'] == vehicleID:
                return True

        return False

    def __invokeCanvas(self, function, args = None):
        if args is None:
            args = []
        self.call('battle.vehicleMarkersCanvas.' + function, args)
        return

    def __getVehicleDamageType(self, attackerID):
        if not attackerID:
            return MarkersManager.DAMAGE_TYPE.FROM_UNKNOWN
        if attackerID == BigWorld.player().playerVehicleID:
            return MarkersManager.DAMAGE_TYPE.FROM_PLAYER
        entityName = g_sessionProvider.getCtx().getPlayerEntityName(attackerID, BigWorld.player().arena.vehicles.get(attackerID, dict()).get('team'))
        if entityName == PLAYER_ENTITY_NAME.squadman:
            return MarkersManager.DAMAGE_TYPE.FROM_SQUAD
        if entityName == PLAYER_ENTITY_NAME.ally:
            return MarkersManager.DAMAGE_TYPE.FROM_ALLY
        if entityName == PLAYER_ENTITY_NAME.enemy:
            return MarkersManager.DAMAGE_TYPE.FROM_ENEMY
        return MarkersManager.DAMAGE_TYPE.FROM_UNKNOWN


class _VehicleMarker():

    def __init__(self, vProxy, uiProxy, handle):
        self.vProxy = vProxy
        self.uiProxy = uiProxy
        self.handle = handle
        self.uiProxy.markerSetScale(g_settingsCore.interfaceScale.get())
        self.vProxy.appearance.onModelChanged += self.__onModelChanged
        g_settingsCore.interfaceScale.onScaleChanged += self.__onScaleChanged

    def destroy(self):
        g_settingsCore.interfaceScale.onScaleChanged -= self.__onScaleChanged
        self.vProxy.appearance.onModelChanged -= self.__onModelChanged
        self.vProxy = None
        self.uiProxy = None
        self.handle = -1
        return

    def __onModelChanged(self):
        if self.uiProxy is not None:
            self.uiProxy.markerSetMatrix(self.handle, self.vProxy.model.node('HP_gui'))
        return

    def __onScaleChanged(self, scale):
        if self.uiProxy is not None:
            self.uiProxy.markerSetScale(scale)
        return


class _EquipmentsMarkerPlugin(IPlugin):
    __MARKER_TYPE = 'FortConsumablesMarker'

    def __init__(self, parentObj):
        super(_EquipmentsMarkerPlugin, self).__init__(parentObj)
        self.__markers = {}

    def init(self):
        super(_EquipmentsMarkerPlugin, self).init()
        ctrl = g_sessionProvider.getEquipmentsCtrl()
        if ctrl:
            ctrl.onEquipmentMarkerShown += self.__onShown

    def fini(self):
        ctrl = g_sessionProvider.getEquipmentsCtrl()
        if ctrl:
            ctrl.onEquipmentMarkerShown -= self.__onShown
        super(_EquipmentsMarkerPlugin, self).fini()

    def start(self):
        super(_EquipmentsMarkerPlugin, self).start()

    def stop(self):
        for handle, callbackID in self.__markers.items():
            self._parentObj.destroyStaticMarker(handle)
            if callbackID is not None:
                BigWorld.cancelCallback(callbackID)

        self.__markers = None
        super(_EquipmentsMarkerPlugin, self).stop()
        return

    def __onShown(self, item, pos, dir, time):
        _, handle = self._parentObj.createStaticMarker(pos + self._parentObj.MARKER_POSITION_ADJUSTMENT, self.__MARKER_TYPE)
        defaultPostfix = i18n.makeString(INGAME_GUI.FORTCONSUMABLES_TIMER_POSTFIX)
        self._parentObj.invokeMarker(handle, 'init', [item.getMarker(), str(int(time)), defaultPostfix])
        self.__initTimer(int(math.ceil(time)), handle)

    def __initTimer(self, timer, handle):
        timer -= 1
        if timer < 0:
            self._parentObj.destroyStaticMarker(handle)
            if handle in self.__markers:
                del self.__markers[handle]
            return
        self._parentObj.invokeMarker(handle, 'updateTimer', [str(timer)])
        callbackId = BigWorld.callback(1, partial(self.__initTimer, timer, handle))
        self.__markers[handle] = callbackId


class _FlagsMarkerPlugin(IPlugin):
    __MARKER_TYPE = 'FlagIndicatorUI'
    __CAPTURE_MARKER_TYPE = 'CaptureIndicatorUI'

    class __FLAG_TYPE:
        ALLY = 'ally'
        ENEMY = 'enemy'
        NEUTRAL = 'neutral'
        REPAIR = 'repair'

    __FLAG_CAPTURE_SOUND_NAME = '/GUI/fallout/capture_flag'
    __FLAG_DELIVERY_SOUND_NAME = '/GUI/fallout/delivery flag'

    def __init__(self, parentObj):
        super(_FlagsMarkerPlugin, self).__init__(parentObj)
        self.__markers = {}
        self.__capturePoints = []
        self.__spawnPoints = []
        self.__captureMarkers = []

    def init(self):
        super(_FlagsMarkerPlugin, self).init()
        g_ctfManager.onFlagSpawnedAtBase += self.__onSpawnedAtBase
        g_ctfManager.onFlagCapturedByVehicle += self.__onCapturedByVehicle
        g_ctfManager.onFlagDroppedToGround += self.__onDroppedToGround
        g_ctfManager.onFlagAbsorbed += self.__onAbsorbed

    def fini(self):
        g_ctfManager.onFlagSpawnedAtBase -= self.__onSpawnedAtBase
        g_ctfManager.onFlagCapturedByVehicle -= self.__onCapturedByVehicle
        g_ctfManager.onFlagDroppedToGround -= self.__onDroppedToGround
        g_ctfManager.onFlagAbsorbed -= self.__onAbsorbed
        super(_FlagsMarkerPlugin, self).fini()

    def start(self):
        player = BigWorld.player()
        playerVehicleID = player.playerVehicleID
        arena = player.arena
        arenaType = arena.arenaType
        self.__capturePoints = arenaType.flagAbsorptionPoints
        self.__spawnPoints = arenaType.flagSpawnPoints
        isFlagBearer = False
        for flagID in g_ctfManager.getFlags():
            flagInfo = g_ctfManager.getFlagInfo(flagID)
            vehicleID = flagInfo['vehicle']
            if vehicleID is None:
                self.__onSpawnedAtBase(flagID, flagInfo['minimapPos'])
            elif vehicleID == playerVehicleID:
                isFlagBearer = True

        if isFlagBearer:
            self.__addCaptureMarkers()
        super(_FlagsMarkerPlugin, self).start()
        return

    def stop(self):
        for handle, callbackID in self.__markers.values():
            self._parentObj.destroyStaticMarker(handle)
            if callbackID is not None:
                BigWorld.cancelCallback(callbackID)

        self.__markers = None
        self.__delCaptureMarkers()
        self.__capturePoints = None
        self.__spawnPoints = None
        super(_FlagsMarkerPlugin, self).stop()
        return

    def __addFlagMarker(self, flagID, flagPos, marker):
        _, handle = self._parentObj.createStaticMarker(flagPos + self._parentObj.MARKER_POSITION_ADJUSTMENT, self.__MARKER_TYPE)
        self._parentObj.invokeMarker(handle, 'setIcon', [marker])
        self.__markers[flagID] = (handle, None)
        return

    def __delFlagMarker(self, flagID):
        handle, callbackID = self.__markers.pop(flagID, (None, None))
        if handle is not None:
            self._parentObj.destroyStaticMarker(handle)
        if callbackID is not None:
            BigWorld.cancelCallback(callbackID)
        return

    def __initTimer(self, timer, flagID):
        timer -= 1
        handle, _ = self.__markers[flagID]
        if timer < 0:
            self.__markers[flagID] = (handle, None)
            return
        else:
            self._parentObj.invokeMarker(handle, 'setLabel', [i18n.makeString(INGAME_GUI.FLAGS_TIMER, time=str(timer))])
            callbackId = BigWorld.callback(1, partial(self.__initTimer, timer, flagID))
            self.__markers[flagID] = (handle, callbackId)
            return

    def __updateFlagbearerMarker(self, vehicleID, state = False):
        vehHandle = getattr(BigWorld.entity(vehicleID), 'marker', None)
        if vehHandle is not None:
            self._parentObj.invokeMarker(vehHandle, 'updateFlagbearerState', [state])
        return

    def __addCaptureMarkers(self):
        player = BigWorld.player()
        currentTeam = player.team
        for point in self.__capturePoints:
            if point['team'] == currentTeam:
                position = point['position']
                _, handle = self._parentObj.createStaticMarker(position + self._parentObj.MARKER_POSITION_ADJUSTMENT, self.__CAPTURE_MARKER_TYPE)
                self.__captureMarkers.append((handle, None))

        return

    def __delCaptureMarkers(self):
        for handle, callbackID in self.__captureMarkers:
            self._parentObj.destroyStaticMarker(handle)
            if callbackID is not None:
                BigWorld.cancelCallback(callbackID)

        self.__captureMarkers = []
        return

    def __onSpawnedAtBase(self, flagID, flagPos):
        flagType = self.__getFlagMarkerType(flagID)
        self.__delFlagMarker(flagID)
        self.__addFlagMarker(flagID, flagPos, flagType)

    def __onCapturedByVehicle(self, flagID, vehicleID):
        self.__updateFlagbearerMarker(vehicleID, True)
        self.__delFlagMarker(flagID)
        if vehicleID == BigWorld.player().playerVehicleID:
            self.__addCaptureMarkers()
            SoundGroups.g_instance.FMODplaySound(self.__FLAG_CAPTURE_SOUND_NAME)

    def __onDroppedToGround(self, flagID, loserVehicleID, flagPos, respawnTime):
        flagType = self.__getFlagMarkerType(flagID)
        self.__updateFlagbearerMarker(loserVehicleID)
        self.__addFlagMarker(flagID, flagPos, flagType)
        timer = respawnTime - BigWorld.serverTime()
        self.__initTimer(int(math.ceil(timer)), flagID)
        if loserVehicleID == BigWorld.player().playerVehicleID:
            self.__delCaptureMarkers()

    def __onAbsorbed(self, flagID, vehicleID, respawnTime):
        self.__updateFlagbearerMarker(vehicleID)
        self.__delFlagMarker(flagID)
        if vehicleID == BigWorld.player().playerVehicleID:
            self.__delCaptureMarkers()
            SoundGroups.g_instance.FMODplaySound(self.__FLAG_DELIVERY_SOUND_NAME)

    def __getFlagMarkerType(self, flagID):
        player = BigWorld.player()
        currentTeam = player.team
        spawnID = flagID
        spawn = self.__spawnPoints[spawnID]
        flagTeam = spawn['team']
        if flagTeam > 0:
            if spawn['team'] == currentTeam:
                return self.__FLAG_TYPE.ALLY
            return self.__FLAG_TYPE.ENEMY
        return self.__FLAG_TYPE.NEUTRAL


class _RepairsMarkerPlugin(IPlugin):
    __MARKER_TYPE = 'RepairPointIndicatorUI'

    def __init__(self, parentObj):
        super(_RepairsMarkerPlugin, self).__init__(parentObj)
        self.__markers = {}

    def init(self):
        super(_RepairsMarkerPlugin, self).init()
        g_sessionProvider.getRepairCtrl().onRepairPointStateChanged += self.__onStateChanged

    def fini(self):
        g_sessionProvider.getRepairCtrl().onRepairPointStateChanged -= self.__onStateChanged
        super(_RepairsMarkerPlugin, self).fini()

    def start(self):
        player = BigWorld.player()
        arena = player.arena
        arenaType = arena.arenaType
        for pointID, point in enumerate(arenaType.repairPoints):
            repairPos, radius = point['position'], point['radius']
            self.__addRepairMarker(pointID, repairPos)

        super(_RepairsMarkerPlugin, self).start()

    def stop(self):
        for handle, callbackID, _, _ in self.__markers.values():
            self._parentObj.destroyStaticMarker(handle)
            if callbackID is not None:
                BigWorld.cancelCallback(callbackID)

        self.__markers = None
        super(_RepairsMarkerPlugin, self).stop()
        return

    def __addRepairMarker(self, repairID, repairPos, isActive = True):
        _, handle = self._parentObj.createStaticMarker(repairPos + self._parentObj.MARKER_POSITION_ADJUSTMENT, self.__MARKER_TYPE)
        self._parentObj.invokeMarker(handle, 'setIcon', ['active' if isActive else 'cooldown'])
        self.__markers[repairID] = (handle,
         None,
         repairPos,
         isActive)
        return

    def __delRepairMarker(self, repairID):
        handle, callbackID, _, _ = self.__markers.pop(repairID, (None, None, None, None))
        if handle is not None:
            self._parentObj.destroyStaticMarker(handle)
        if callbackID is not None:
            BigWorld.cancelCallback(callbackID)
        return

    def __initTimer(self, timer, repairID):
        timer -= 1
        handle, _, repairPos, wasActive = self.__markers[repairID]
        if timer < 0:
            self.__markers[repairID] = (handle,
             None,
             repairPos,
             wasActive)
            return
        else:
            self._parentObj.invokeMarker(handle, 'setLabel', [time_utils.getTimeLeftFormat(timer)])
            callbackId = BigWorld.callback(1, partial(self.__initTimer, timer, repairID))
            self.__markers[repairID] = (handle,
             callbackId,
             repairPos,
             wasActive)
            return

    def __onStateChanged(self, repairPointID, action, timeLeft = 0):
        if repairPointID not in self.__markers:
            LOG_ERROR('Got repair point state changed for not available repair point: ', repairPointID, action, timeLeft)
            return
        else:
            if action in (constants.REPAIR_POINT_ACTION.START_REPAIR, constants.REPAIR_POINT_ACTION.COMPLETE_REPAIR, constants.REPAIR_POINT_ACTION.BECOME_READY):
                handle, callbackID, repairPos, wasActive = self.__markers[repairPointID]
                isActive = action in (constants.REPAIR_POINT_ACTION.START_REPAIR, constants.REPAIR_POINT_ACTION.BECOME_READY)
                if wasActive == isActive:
                    return
                if callbackID is not None:
                    BigWorld.cancelCallback(callbackID)
                    callbackID = None
                self._parentObj.invokeMarker(handle, 'setIcon', ['active' if isActive else 'cooldown'])
                self._parentObj.invokeMarker(handle, 'setLabel', [''])
                self.__markers[repairPointID] = (handle,
                 callbackID,
                 repairPos,
                 isActive)
                if not isActive:
                    self.__initTimer(int(math.ceil(timeLeft)), repairPointID)
            return
