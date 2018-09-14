# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/legacy/markers.py
import math
import weakref
from functools import partial
import BigWorld
import GUI
import constants
from CTFManager import g_ctfManager
from Math import Vector3, Matrix
from account_helpers.settings_core import g_settingsCore
from debug_utils import LOG_ERROR
from gui import DEPTH_OF_VehicleMarker, GUI_SETTINGS
from gui.Scaleform import ColorSchemeManager
from gui.Scaleform.Flash import Flash
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control import g_sessionProvider, avatar_getter
from gui.battle_control.arena_info.arena_vos import VehicleActions
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _EVENT_ID
from gui.battle_control.battle_constants import PLAYER_GUI_PROPS, NEUTRAL_TEAM
from gui.battle_control.battle_constants import REPAIR_STATE_ID, GAS_ATTACK_STATE
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from gui.shared.utils.plugins import PluginsCollection, IPlugin
from helpers import i18n, time_utils
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
_SCOPE = EVENT_BUS_SCOPE.BATTLE
_MARKER_POSITION_ADJUSTMENT = Vector3(0.0, 12.0, 0.0)
_MARKERS_MANAGER_SWF = 'VehicleMarkersManager.swf'

class _DAMAGE_TYPE():
    FROM_UNKNOWN = 0
    FROM_ALLY = 1
    FROM_ENEMY = 2
    FROM_SQUAD = 3
    FROM_PLAYER = 4


_EQUIPMENT_MARKER_TYPE = 'FortConsumablesMarker'
_FLAG_MARKER_TYPE = 'FlagIndicatorUI'
_FLAG_CAPTURE_MARKER_TYPE = 'CaptureIndicatorUI'

class _FLAG_TYPE():
    ALLY = 'ally'
    ENEMY = 'enemy'
    NEUTRAL = 'neutral'
    REPAIR = 'repair'
    COOLDOWN = 'cooldown'


_REPAIR_MARKER_TYPE = 'RepairPointIndicatorUI'
_SAFE_ZONE_MARKER_TYPE = 'SafeZoneIndicatorUI'
_RESOURCE_MARKER_TYPE = 'ResourcePointMarkerUI'

class _RESOURCE_STATE():
    FREEZE = 'freeze'
    COOLDOWN = 'cooldown'
    READY = 'ready'
    OWN_MINING = 'ownMining'
    ENEMY_MINING = 'enemyMining'
    OWN_MINING_FROZEN = 'ownMiningFrozen'
    ENEMY_MINING_FROZEN = 'enemyMiningFrozen'
    CONFLICT = 'conflict'


_CAPTURE_STATE_BY_TEAMS = {True: _RESOURCE_STATE.OWN_MINING,
 False: _RESOURCE_STATE.ENEMY_MINING}
_CAPTURE_FROZEN_STATE_BY_TEAMS = {True: _RESOURCE_STATE.OWN_MINING_FROZEN,
 False: _RESOURCE_STATE.ENEMY_MINING_FROZEN}

class MarkersManager(Flash):

    def __init__(self, parentUI):
        Flash.__init__(self, _MARKERS_MANAGER_SWF)
        self.component.wg_inputKeyMode = 2
        self.component.position.z = DEPTH_OF_VehicleMarker
        self.component.drawWithRestrictedViewPort = False
        self.movie.backgroundAlpha = 0
        self.colorManager = ColorSchemeManager._ColorSchemeManager()
        self.colorManager.populateUI(weakref.proxy(self))
        self.__plugins = PluginsCollection(self)
        plugins = {'equipments': _EquipmentsMarkerPlugin}
        visitor = g_sessionProvider.arenaVisitor
        if visitor.hasFlags():
            plugins['flags'] = _FlagsMarkerPlugin
        if visitor.hasRepairPoints():
            plugins['repairs'] = _RepairsMarkerPlugin
        if visitor.hasResourcePoints():
            plugins['resources'] = _ResourceMarkerPlugin
        if visitor.hasGasAttack():
            plugins['safe_zone'] = _GasAttackSafeZonePlugin
        self.__plugins.addPlugins(plugins)
        self.__ownUI = None
        self.__parentUI = parentUI
        self.__markers = {}
        return

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    def setScaleProps(self, minScale=40, maxScale=100, defScale=100, speed=3.0):
        if constants.IS_DEVELOPMENT:
            self.__ownUI.scaleProperties = (minScale,
             maxScale,
             defScale,
             speed)

    def setAlphaProps(self, minAlpha=40, maxAlpha=100, defAlpha=100, speed=3.0):
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
        ctrl = g_sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleMarkerAdded += self.__onVehicleMarkerAdded
            ctrl.onVehicleMarkerRemoved += self.__onVehicleMarkerRemoved
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        functional = g_sessionProvider.dynamic.dynSquads
        if functional is not None:
            functional.onPlayerBecomeSquadman += self.__onPlayerBecomeSquadman
        self.__plugins.start()
        g_eventBus.addListener(GameEvent.SHOW_EXTENDED_INFO, self.__handleShowExtendedInfo, scope=_SCOPE)
        g_eventBus.addListener(GameEvent.GUI_VISIBILITY, self.__handleGUIVisibility, scope=_SCOPE)
        g_eventBus.addListener(GameEvent.MARKERS_2D_VISIBILITY, self.__handleMarkerVisibility, scope=_SCOPE)
        return

    def destroy(self):
        g_eventBus.removeListener(GameEvent.SHOW_EXTENDED_INFO, self.__handleShowExtendedInfo, scope=_SCOPE)
        g_eventBus.removeListener(GameEvent.GUI_VISIBILITY, self.__handleGUIVisibility, scope=_SCOPE)
        g_eventBus.removeListener(GameEvent.MARKERS_2D_VISIBILITY, self.__handleMarkerVisibility, scope=_SCOPE)
        self.__plugins.stop()
        g_settingsCore.interfaceScale.onScaleChanged -= self.updateMarkersScale
        ctrl = g_sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleMarkerAdded -= self.__onVehicleMarkerAdded
            ctrl.onVehicleMarkerRemoved -= self.__onVehicleMarkerRemoved
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        functional = g_sessionProvider.dynamic.dynSquads
        if functional is not None:
            functional.onPlayerBecomeSquadman -= self.__onPlayerBecomeSquadman
        if self.__parentUI is not None:
            setattr(self.__parentUI.component, 'vehicleMarkersManager', None)
        self.__plugins.fini()
        self.__parentUI = None
        self.__ownUI = None
        self.__markersCanvasUI = None
        self.colorManager.dispossessUI()
        self.close()
        return

    def _createVehicleMarker(self, isAlly, mProv):
        markerLinkage = 'VehicleMarkerAlly' if isAlly else 'VehicleMarkerEnemy'
        if g_sessionProvider.arenaVisitor.hasFlags():
            markerID = self.__ownUI.addFalloutMarker(mProv, markerLinkage)
        else:
            markerID = self.__ownUI.addMarker(mProv, markerLinkage)
        return markerID

    def addVehicleMarker(self, vProxy, vInfo, guiProps):
        vTypeDescr = vProxy.typeDescriptor
        maxHealth = vTypeDescr.maxHealth
        mProv = vProxy.model.node('HP_gui')
        isAlly = guiProps.isFriend
        speaking = self.bwProto.voipController.isPlayerSpeaking(vInfo.player.accountDBID)
        hunting = VehicleActions.isHunting(vInfo.events)
        markerID = self._createVehicleMarker(isAlly, mProv)
        self.__markers[vInfo.vehicleID] = _VehicleMarker(markerID, vProxy, self.__ownUIProxy)
        battleCtx = g_sessionProvider.getCtx()
        result = battleCtx.getPlayerFullNameParts(vProxy.id)
        vType = vInfo.vehicleType
        squadIcon = ''
        if g_sessionProvider.arenaVisitor.gui.isFalloutMultiTeam() and vInfo.isSquadMan():
            if guiProps == PLAYER_GUI_PROPS.squadman:
                squadTeam = 'my'
            elif isAlly:
                squadTeam = 'ally'
            else:
                squadTeam = 'enemy'
            squadIcon = '%s%d' % (squadTeam, vInfo.squadIndex)
        self.invokeMarker(markerID, 'init', [vType.classTag,
         vType.iconPath,
         result.vehicleName,
         vType.level,
         result.playerFullName,
         result.playerName,
         result.clanAbbrev,
         result.regionCode,
         vProxy.health,
         maxHealth,
         guiProps.name(),
         speaking,
         hunting,
         guiProps.base,
         g_ctfManager.getVehicleCarriedFlagID(vInfo.vehicleID) is not None,
         squadIcon])
        return markerID

    def removeVehicleMarker(self, vehicleID):
        marker = self.__markers.pop(vehicleID, None)
        if marker is not None:
            self.__ownUI.delMarker(marker.id)
            marker.destroy()
        return

    def createStaticMarker(self, pos, symbol):
        mProv = Matrix()
        mProv.translation = pos
        handle = self.__ownUI.addMarker(mProv, symbol)
        return (mProv, handle)

    def destroyStaticMarker(self, handle):
        if self.__ownUI:
            self.__ownUI.delMarker(handle)

    def updateMarkerState(self, handle, newState, isImmediate=False):
        self.invokeMarker(handle, 'updateState', [newState, isImmediate])

    def showActionMarker(self, handle, newState):
        self.invokeMarker(handle, 'showActionMarker', [newState])

    def updateFlagbearerState(self, vehID, newState):
        marker = self.__markers.get(vehID)
        if marker is not None:
            self.invokeMarker(marker.id, 'updateFlagbearerState', [newState])
        return

    def updateVehicleHealth(self, handle, newHealth, aInfo, attackReasonID):
        if newHealth < 0 and not constants.SPECIAL_VEHICLE_HEALTH.IS_AMMO_BAY_DESTROYED(newHealth):
            newHealth = 0
        self.invokeMarker(handle, 'updateHealth', [newHealth, self.__getVehicleDamageType(aInfo), constants.ATTACK_REASONS[attackReasonID]])

    def showDynamic(self, vID, flag):
        if vID not in self.__markers:
            return
        marker = self.__markers[vID]
        self.invokeMarker(marker.id, 'setSpeaking', [flag])

    def updateMarkersScale(self, scale=None):
        if self.__ownUIProxy() is not None:
            if scale is None:
                self.__ownUIProxy().markerSetScale(g_settingsCore.interfaceScale.get())
            else:
                self.__ownUIProxy().markerSetScale(scale)
        return

    def setTeamKiller(self, vID):
        if vID not in self.__markers:
            return
        marker = self.__markers[vID]
        ctx = g_sessionProvider.getCtx()
        visitor = g_sessionProvider.arenaVisitor
        if not ctx.isTeamKiller(vID=vID) or ctx.isSquadMan(vID=vID) and not visitor.gui.isFalloutBattle():
            return
        self.invokeMarker(marker.id, 'setEntityName', [PLAYER_GUI_PROPS.teamKiller.name()])

    def invokeMarker(self, handle, function, args=None):
        if handle != -1:
            self.__ownUI.markerInvoke(handle, (function, args))

    def setMarkerSettings(self, settings):
        if self.__markersCanvasUI:
            self.__markersCanvasUI.setMarkerSettings(settings)

    def setMarkerDuration(self, value):
        self.__invokeCanvas('setMarkerDuration', [value])

    def updateMarkers(self):
        self.colorManager.update()
        for marker in self.__markers.itervalues():
            self.invokeMarker(marker.id, 'update')

        self.__plugins.update()

    def updateMarkerSettings(self):
        for marker in self.__markers.itervalues():
            self.invokeMarker(marker.id, 'updateMarkerSettings')

    def __invokeCanvas(self, function, args=None):
        if args is None:
            args = []
        self.call('battle.vehicleMarkersCanvas.' + function, args)
        return

    def __getVehicleDamageType(self, attackerInfo):
        if not attackerInfo:
            return _DAMAGE_TYPE.FROM_UNKNOWN
        attackerID = attackerInfo.vehicleID
        if attackerID == avatar_getter.getPlayerVehicleID():
            return _DAMAGE_TYPE.FROM_PLAYER
        entityName = g_sessionProvider.getCtx().getPlayerGuiProps(attackerID, attackerInfo.team)
        if entityName == PLAYER_GUI_PROPS.squadman:
            return _DAMAGE_TYPE.FROM_SQUAD
        if entityName == PLAYER_GUI_PROPS.ally:
            return _DAMAGE_TYPE.FROM_ALLY
        return _DAMAGE_TYPE.FROM_ENEMY if entityName == PLAYER_GUI_PROPS.enemy else _DAMAGE_TYPE.FROM_UNKNOWN

    def __onVehicleMarkerAdded(self, vProxy, vInfo, guiProps):
        self.addVehicleMarker(vProxy, vInfo, guiProps)

    def __onVehicleMarkerRemoved(self, vehicleID):
        self.removeVehicleMarker(vehicleID)

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if vehicleID not in self.__markers:
            return
        marker = self.__markers[vehicleID]
        if eventID == _EVENT_ID.VEHICLE_HIT:
            self.updateMarkerState(marker.id, 'hit', value)
        elif eventID == _EVENT_ID.VEHICLE_ARMOR_PIERCED:
            self.updateMarkerState(marker.id, 'hit_pierced', value)
        elif eventID == _EVENT_ID.VEHICLE_DEAD:
            self.updateMarkerState(marker.id, 'dead', value)
        elif eventID == _EVENT_ID.VEHICLE_SHOW_MARKER:
            self.showActionMarker(marker.id, value)
        elif eventID == _EVENT_ID.VEHICLE_HEALTH:
            self.updateVehicleHealth(marker.id, *value)

    def __onPlayerBecomeSquadman(self, vehicleID, guiProps):
        if vehicleID not in self.__markers:
            return
        marker = self.__markers[vehicleID]
        self.invokeMarker(marker.id, 'setEntityName', [guiProps.name()])

    def __handleShowExtendedInfo(self, event):
        isDown = event.ctx['isDown']
        self.__invokeCanvas('setShowExInfoFlag', [isDown])
        for marker in self.__markers.itervalues():
            self.invokeMarker(marker.id, 'showExInfo', [isDown])

    def __handleGUIVisibility(self, event):
        self.active(event.ctx['visible'])

    def __handleMarkerVisibility(self, _):
        self.active(not self.isActive)


class _VehicleMarker(object):

    def __init__(self, markerID, vProxy, uiProxy):
        self.id = markerID
        self.vProxy = vProxy
        self.uiProxy = uiProxy
        self.vProxy.appearance.onModelChanged += self.__onModelChanged

    def destroy(self):
        self.vProxy.appearance.onModelChanged -= self.__onModelChanged
        self.vProxy = None
        self.uiProxy = None
        self.markerID = -1
        return

    def __onModelChanged(self):
        if self.uiProxy() is not None:
            self.uiProxy().markerSetMatrix(self.id, self.vProxy.model.node('HP_gui'))
        return


class _EquipmentsMarkerPlugin(IPlugin):

    def __init__(self, parentObj):
        super(_EquipmentsMarkerPlugin, self).__init__(parentObj)
        self.__markers = {}

    def init(self):
        super(_EquipmentsMarkerPlugin, self).init()
        ctrl = g_sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentMarkerShown += self.__onShown
        return

    def fini(self):
        ctrl = g_sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentMarkerShown -= self.__onShown
        super(_EquipmentsMarkerPlugin, self).fini()
        return

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
        _, handle = self._parentObj.createStaticMarker(pos + _MARKER_POSITION_ADJUSTMENT, _EQUIPMENT_MARKER_TYPE)
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

    def __init__(self, parentObj):
        super(_FlagsMarkerPlugin, self).__init__(parentObj)
        self.__markers = {}
        self.__capturePoints = []
        self.__spawnPoints = []
        self.__captureMarkers = []
        self.__playerTeam = NEUTRAL_TEAM
        self.__isTeamPlayer = False

    def init(self):
        super(_FlagsMarkerPlugin, self).init()
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
        super(_FlagsMarkerPlugin, self).fini()

    def start(self):
        visitor = g_sessionProvider.arenaVisitor
        playerVehicleID = avatar_getter.getPlayerVehicleID()
        self.__playerTeam = avatar_getter.getPlayerTeam()
        self.__isTeamPlayer = not visitor.isSoloTeam(self.__playerTeam)
        self.__capturePoints = visitor.type.getFlagAbsorptionPoints()
        self.__spawnPoints = visitor.type.getFlagSpawnPoints()
        isFlagBearer = False
        for flagID, flagInfo in g_ctfManager.getFlags():
            vehicleID = flagInfo['vehicle']
            if vehicleID is None:
                flagState = flagInfo['state']
                if flagState == constants.FLAG_STATE.WAITING_FIRST_SPAWN:
                    self.__onFlagSpawning(flagID, flagInfo['respawnTime'])
                elif flagState in (constants.FLAG_STATE.ON_GROUND, constants.FLAG_STATE.ON_SPAWN):
                    self.__onSpawnedAtBase(flagID, flagInfo['team'], flagInfo['minimapPos'])
            if vehicleID == playerVehicleID:
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
        _, handle = self._parentObj.createStaticMarker(flagPos + _MARKER_POSITION_ADJUSTMENT, _FLAG_MARKER_TYPE)
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

    def __addCaptureMarkers(self):
        for point in self.__capturePoints:
            if self.__isTeamPlayer and point['team'] in (NEUTRAL_TEAM, self.__playerTeam):
                position = point['position']
                _, handle = self._parentObj.createStaticMarker(position + _MARKER_POSITION_ADJUSTMENT, _FLAG_CAPTURE_MARKER_TYPE)
                self.__captureMarkers.append((handle, None))

        return

    def __delCaptureMarkers(self):
        for handle, callbackID in self.__captureMarkers:
            self._parentObj.destroyStaticMarker(handle)
            if callbackID is not None:
                BigWorld.cancelCallback(callbackID)

        self.__captureMarkers = []
        return

    def __onFlagSpawning(self, flagID, respawnTime):
        flagType = _FLAG_TYPE.COOLDOWN
        flagPos = self.__spawnPoints[flagID]['position']
        self.__addFlagMarker(flagID, flagPos, flagType)
        timer = respawnTime - BigWorld.serverTime()
        self.__initTimer(int(math.ceil(timer)), flagID)

    def __onSpawnedAtBase(self, flagID, flagTeam, flagPos):
        flagType = self.__getFlagMarkerType(flagID, flagTeam)
        self.__delFlagMarker(flagID)
        self.__addFlagMarker(flagID, flagPos, flagType)

    def __onCapturedByVehicle(self, flagID, flagTeam, vehicleID):
        self._parentObj.updateFlagbearerState(vehicleID, True)
        self.__delFlagMarker(flagID)
        if vehicleID == BigWorld.player().playerVehicleID:
            self.__addCaptureMarkers()

    def __onDroppedToGround(self, flagID, flagTeam, loserVehicleID, flagPos, respawnTime):
        flagType = self.__getFlagMarkerType(flagID, flagTeam)
        self._parentObj.updateFlagbearerState(loserVehicleID, False)
        self.__addFlagMarker(flagID, flagPos, flagType)
        timer = respawnTime - BigWorld.serverTime()
        self.__initTimer(int(math.ceil(timer)), flagID)
        if loserVehicleID == BigWorld.player().playerVehicleID:
            self.__delCaptureMarkers()

    def __onAbsorbed(self, flagID, flagTeam, vehicleID, respawnTime):
        self._parentObj.updateFlagbearerState(vehicleID, False)
        self.__delFlagMarker(flagID)
        if vehicleID == BigWorld.player().playerVehicleID:
            self.__delCaptureMarkers()

    def __onRemoved(self, flagID, flagTeam, vehicleID):
        self.__delFlagMarker(flagID)
        if vehicleID is not None:
            self._parentObj.updateFlagbearerState(vehicleID, False)
            if vehicleID == BigWorld.player().playerVehicleID:
                self.__delCaptureMarkers()
        return

    def __getFlagMarkerType(self, flagID, flagTeam=0):
        player = BigWorld.player()
        currentTeam = player.team
        if flagTeam != NEUTRAL_TEAM:
            if flagTeam == currentTeam:
                return _FLAG_TYPE.ALLY
            return _FLAG_TYPE.ENEMY
        return _FLAG_TYPE.NEUTRAL


class _RepairsMarkerPlugin(IPlugin):

    def __init__(self, parentObj):
        super(_RepairsMarkerPlugin, self).__init__(parentObj)
        self.__markers = {}
        self.__playerTeam = NEUTRAL_TEAM

    def init(self):
        super(_RepairsMarkerPlugin, self).init()
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
        super(_RepairsMarkerPlugin, self).fini()
        return

    def start(self):
        player = BigWorld.player()
        playerTeam = player.team
        arena = player.arena
        arenaType = arena.arenaType
        for pointID, point in arenaType.repairPoints.iteritems():
            repairPos = point['position']
            team = point['team']
            isAlly = team in (NEUTRAL_TEAM, playerTeam)
            _, markerID = self._parentObj.createStaticMarker(repairPos + _MARKER_POSITION_ADJUSTMENT, _REPAIR_MARKER_TYPE)
            self._parentObj.invokeMarker(markerID, 'setIcon', ['active', isAlly])
            self.__markers[pointID] = (markerID, isAlly)

        super(_RepairsMarkerPlugin, self).start()

    def stop(self):
        for markerID, _ in self.__markers.values():
            self._parentObj.destroyStaticMarker(markerID)

        self.__markers.clear()
        super(_RepairsMarkerPlugin, self).stop()

    def __onRepairPointStateCreated(self, pointIndex, stateID):
        if pointIndex not in self.__markers:
            LOG_ERROR('Got repair point state changed for not available repair point: ', pointIndex, stateID)
            return
        if stateID == REPAIR_STATE_ID.DISABLED:
            handle, _ = self.__markers.pop(pointIndex)
            self._parentObj.destroyStaticMarker(handle)
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


class _ResourceMarkerPlugin(IPlugin):

    def __init__(self, parentObj):
        super(_ResourceMarkerPlugin, self).__init__(parentObj)
        self.__markers = {}

    def init(self):
        super(_ResourceMarkerPlugin, self).init()
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
        super(_ResourceMarkerPlugin, self).fini()

    def start(self):
        super(_ResourceMarkerPlugin, self).start()
        arenaDP = g_sessionProvider.getArenaDP()
        for pointID, point in g_ctfManager.getResourcePoints():
            resourcePos = point['minimapPos']
            amount = point['amount']
            pointState = point['state']
            progress = float(amount) / point['totalAmount'] * 100
            if pointState == constants.RESOURCE_POINT_STATE.FREE:
                state = _RESOURCE_STATE.READY
            elif pointState == constants.RESOURCE_POINT_STATE.COOLDOWN:
                state = _RESOURCE_STATE.COOLDOWN
            elif pointState == constants.RESOURCE_POINT_STATE.CAPTURED:
                state = _CAPTURE_STATE_BY_TEAMS[arenaDP.isAllyTeam(point['team'])]
            elif pointState == constants.RESOURCE_POINT_STATE.CAPTURED_LOCKED:
                state = _CAPTURE_FROZEN_STATE_BY_TEAMS[arenaDP.isAllyTeam(point['team'])]
            elif pointState == constants.RESOURCE_POINT_STATE.BLOCKED:
                state = _RESOURCE_STATE.CONFLICT
            else:
                state = _RESOURCE_STATE.FREEZE
            _, handle = self._parentObj.createStaticMarker(resourcePos + _MARKER_POSITION_ADJUSTMENT, _RESOURCE_MARKER_TYPE)
            self._parentObj.invokeMarker(handle, 'as_init', [pointID, state, progress])
            self.__markers[pointID] = (handle,
             None,
             resourcePos,
             state)

        return

    def stop(self):
        for handle, callbackID, _, _ in self.__markers.values():
            self._parentObj.destroyStaticMarker(handle)
            if callbackID is not None:
                BigWorld.cancelCallback(callbackID)

        self.__markers = None
        super(_ResourceMarkerPlugin, self).stop()
        return

    def update(self):
        super(_ResourceMarkerPlugin, self).update()
        for point in self.__markers.itervalues():
            handle = point[0]
            self._parentObj.invokeMarker(handle, 'as_onSettingsChanged')

    def __onIsFree(self, pointID):
        handle, _, _, _ = self.__markers[pointID]
        self._parentObj.invokeMarker(handle, 'as_setState', [_RESOURCE_STATE.READY])

    def __onCooldown(self, pointID, serverTime):
        handle, _, _, _ = self.__markers[pointID]
        self._parentObj.invokeMarker(handle, 'as_setState', [_RESOURCE_STATE.COOLDOWN])

    def __onCaptured(self, pointID, team):
        handle, _, _, _ = self.__markers[pointID]
        state = _CAPTURE_STATE_BY_TEAMS[g_sessionProvider.getArenaDP().isAllyTeam(team)]
        self._parentObj.invokeMarker(handle, 'as_setState', [state])

    def __onCapturedLocked(self, pointID, team):
        handle, _, _, _ = self.__markers[pointID]
        state = _CAPTURE_FROZEN_STATE_BY_TEAMS[g_sessionProvider.getArenaDP().isAllyTeam(team)]
        self._parentObj.invokeMarker(handle, 'as_setState', [state])

    def __onBlocked(self, pointID):
        handle, _, _, _ = self.__markers[pointID]
        self._parentObj.invokeMarker(handle, 'as_setState', [_RESOURCE_STATE.CONFLICT])

    def __onAmountChanged(self, pointID, amount, totalAmount):
        progress = float(amount) / totalAmount * 100
        handle, _, _, _ = self.__markers[pointID]
        self._parentObj.invokeMarker(handle, 'as_setProgress', [progress])


class _GasAttackSafeZonePlugin(IPlugin):

    def __init__(self, parentObj):
        super(_GasAttackSafeZonePlugin, self).__init__(parentObj)
        self.__safeZoneMarkerHandle = None
        self.__isMarkerVisible = False
        self.__settings = g_sessionProvider.arenaVisitor.getGasAttackSettings()
        return

    def init(self):
        super(_GasAttackSafeZonePlugin, self).init()
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
        super(_GasAttackSafeZonePlugin, self).fini()
        return

    def start(self):
        super(_GasAttackSafeZonePlugin, self).start()

    def stop(self):
        self.__delSafeZoneMarker()
        super(_GasAttackSafeZonePlugin, self).stop()

    def __updateSafeZoneMarker(self, isVisible):
        if not self.__isMarkerVisible == isVisible:
            self.__isMarkerVisible = isVisible
            self._parentObj.invokeMarker(self.__safeZoneMarkerHandle, 'update', [self.__isMarkerVisible])

    def __initMarker(self, center):
        if self.__safeZoneMarkerHandle is None:
            _, self.__safeZoneMarkerHandle = self._parentObj.createStaticMarker(center + _MARKER_POSITION_ADJUSTMENT, _SAFE_ZONE_MARKER_TYPE)
        return

    def __delSafeZoneMarker(self):
        if self.__safeZoneMarkerHandle is not None:
            self._parentObj.destroyStaticMarker(self.__safeZoneMarkerHandle)
            self.__safeZoneMarkerHandle = None
        return

    def __onGasAttackUpdate(self, state):
        self.__updateSafeZoneMarker(state.state in GAS_ATTACK_STATE.VISIBLE)
