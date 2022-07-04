# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/markers2d/vehicle_plugins.py
from collections import defaultdict
from functools import partial
import BattleReplay
import BigWorld
import Math
import constants
import settings
from AvatarInputHandler import AvatarInputHandler
from PlayerEvents import g_playerEvents
from account_helpers.settings_core.settings_constants import GAME
from aih_constants import CTRL_MODE_NAME
from arena_components.advanced_chat_component import _DEFAULT_ACTIVE_COMMAND_TIME, TARGET_CHAT_CMD_FLAG
from chat_commands_consts import INVALID_MARKER_SUBTYPE, MarkerType, DefaultMarkerSubType, INVALID_MARKER_ID
from gui.Scaleform.daapi.view.battle.shared.markers2d import markers
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import MarkerPlugin, ChatCommunicationComponent, MAX_DISTANCE_TEMP_STICKY
from gui.Scaleform.daapi.view.battle.shared.markers2d.timer import MarkerTimer
from gui.Scaleform.genConsts.BATTLE_MARKER_STATES import BATTLE_MARKER_STATES
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.arena_vos import VehicleActions
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _EVENT_ID, ENTITY_IN_FOCUS_TYPE
from gui.battle_control.battle_constants import MARKER_HIT_STATE, PLAYER_GUI_PROPS, MARKER_CRITICAL_HIT_STATES
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.battle_control.controllers.feedback_adaptor import EntityInFocusData
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from items.battle_royale import isSpawnedBot
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from skeletons.gui.game_control import IBootcampController
_STATUS_EFFECTS_PRIORITY = (BATTLE_MARKER_STATES.REPAIRING_STATE,
 BATTLE_MARKER_STATES.ENGINEER_STATE,
 BATTLE_MARKER_STATES.HEALING_STATE,
 BATTLE_MARKER_STATES.INSPIRING_STATE,
 BATTLE_MARKER_STATES.DEBUFF_STATE,
 BATTLE_MARKER_STATES.STUN_STATE,
 BATTLE_MARKER_STATES.INSPIRED_STATE)
_VEHICLE_MARKER_MIN_SCALE = 0.0
_VEHICLE_MARKER_CULL_DISTANCE = 1000000
_VEHICLE_MARKER_BOUNDS = Math.Vector4(50, 50, 80, 65)
_INNER_VEHICLE_MARKER_BOUNDS = Math.Vector4(17, 17, 55, 25)
_VEHICLE_MARKER_BOUNDS_MIN_SCALE = Math.Vector2(1.0, 1.0)
_HELP_ME_STATE = 'help_me'

class VehicleMarkerPlugin(MarkerPlugin, ChatCommunicationComponent, IArenaVehiclesController):
    bootcamp = dependency.descriptor(IBootcampController)
    __slots__ = ('_markers', '_markersStates', '_clazz', '__playerVehicleID', '_isSquadIndicatorEnabled', '__showDamageIcon', '_markerTimers', '__callbackIDs', '__targetedTankMarkerID', '__targetedMarkerFromCppID')

    def __init__(self, parentObj, clazz=markers.VehicleMarker):
        super(VehicleMarkerPlugin, self).__init__(parentObj)
        self._markers = {}
        self._markersStates = defaultdict(list)
        self._clazz = clazz
        self._markerTimers = defaultdict(dict)
        self._isSquadIndicatorEnabled = False
        self._playerVehicleID = 0
        self.__showDamageIcon = False
        self.__callbackIDs = {}
        self.__targetedTankMarkerID = -1
        self.__targetedMarkerFromCppID = -1
        self.__followingIgnoredTank = 0

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    def start(self):
        super(VehicleMarkerPlugin, self).start()
        self._playerVehicleID = self.sessionProvider.getArenaDP().getPlayerVehicleID()
        self.sessionProvider.addArenaCtrl(self)
        settingsDamageIcon = self.settingsCore.getSetting(GAME.SHOW_DAMAGE_ICON)
        isInBootcamp = self.bootcamp.isInBootcamp()
        enableInBootcamp = isInBootcamp and self.bootcamp.isEnableDamageIcon()
        self.__showDamageIcon = settingsDamageIcon and (not isInBootcamp or enableInBootcamp)
        handler = avatar_getter.getInputHandler()
        if handler is not None:
            if isinstance(handler, AvatarInputHandler):
                handler.onCameraChanged += self.__onCameraChanged
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleMarkerAdded += self.__onVehicleMarkerAdded
            ctrl.onVehicleMarkerRemoved += self.__onVehicleMarkerRemoved
            ctrl.onVehicleFeedbackReceived += self._onVehicleFeedbackReceived
            ctrl.setInFocusForPlayer += self.__setInFocusForPlayer
            ctrl.onRemoveCommandReceived += self.__onRemoveCommandReceived
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated += self._onVehicleStateUpdated
        arena = avatar_getter.getArena()
        if arena is not None:
            arena.onChatCommandTargetUpdate += self._onChatCommandTargetUpdate
        g_messengerEvents.voip.onPlayerSpeaking += self.__onPlayerSpeaking
        g_playerEvents.onTeamChanged += self.__onTeamChanged
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        return

    def stop(self):
        self.__removeMarkerCallbacks()
        while self._markers:
            _, marker = self._markers.popitem()
            marker.destroy()

        while self._markerTimers:
            _, timers = self._markerTimers.popitem()
            while timers:
                _, timer = timers.popitem()
                timer.clear()

        self._markerTimers.clear()
        handler = avatar_getter.getInputHandler()
        if handler is not None:
            if isinstance(handler, AvatarInputHandler):
                handler.onCameraChanged -= self.__onCameraChanged
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleMarkerAdded -= self.__onVehicleMarkerAdded
            ctrl.onVehicleMarkerRemoved -= self.__onVehicleMarkerRemoved
            ctrl.onVehicleFeedbackReceived -= self._onVehicleFeedbackReceived
            ctrl.setInFocusForPlayer -= self.__setInFocusForPlayer
            ctrl.onRemoveCommandReceived -= self.__onRemoveCommandReceived
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated -= self._onVehicleStateUpdated
        arena = avatar_getter.getArena()
        if arena is not None:
            arena.onChatCommandTargetUpdate -= self._onChatCommandTargetUpdate
        g_messengerEvents.voip.onPlayerSpeaking -= self.__onPlayerSpeaking
        g_playerEvents.onTeamChanged -= self.__onTeamChanged
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        super(VehicleMarkerPlugin, self).stop()
        return

    def invalidateArenaInfo(self):
        self.invalidateVehiclesInfo(self.sessionProvider.getArenaDP())

    def invalidateVehiclesInfo(self, arenaDP):
        getProps = arenaDP.getPlayerGuiProps
        getParts = self.sessionProvider.getCtx().getPlayerFullNameParts
        feedback = self.sessionProvider.shared.feedback
        for vInfo in arenaDP.getVehiclesInfoIterator():
            vehicleID = vInfo.vehicleID
            if vehicleID == self._playerVehicleID or vInfo.isObserver():
                continue
            if vehicleID not in self._markers:
                marker = self.__addMarkerToPool(vehicleID, vInfo=vInfo, vProxy=feedback.getVehicleProxy(vehicleID))
                if marker is None:
                    continue
            else:
                marker = self._markers[vehicleID]
            self.__setVehicleInfo(marker, vInfo, getProps(vehicleID, vInfo.team), getParts(vehicleID))
            self._setMarkerInitialState(marker, accountDBID=vInfo.player.accountDBID)

        return

    def addVehicleInfo(self, vInfo, arenaDP):
        if vInfo.isObserver():
            return
        else:
            vehicleID = vInfo.vehicleID
            if vehicleID in self._markers:
                return
            ctx = self.sessionProvider.getCtx()
            feedback = self.sessionProvider.shared.feedback
            marker = self.__addMarkerToPool(vehicleID, vInfo=vInfo, vProxy=feedback.getVehicleProxy(vehicleID))
            if marker is None:
                return
            self.__setVehicleInfo(marker, vInfo, ctx.getPlayerGuiProps(vehicleID, vInfo.team), ctx.getPlayerFullNameParts(vehicleID))
            self._setMarkerInitialState(marker, accountDBID=vInfo.player.accountDBID)
            return

    def updateVehiclesInfo(self, updated, arenaDP):
        getProps = arenaDP.getPlayerGuiProps
        getParts = self.sessionProvider.getCtx().getPlayerFullNameParts
        for _, vInfo in updated:
            vehicleID = vInfo.vehicleID
            if vehicleID not in self._markers:
                continue
            marker = self._markers[vehicleID]
            self.__setVehicleInfo(marker, vInfo, getProps(vehicleID, vInfo.team), getParts(vehicleID))

    def invalidatePlayerStatus(self, flags, vInfo, arenaDP):
        self.__setEntityName(vInfo, arenaDP)

    def getMarkerType(self):
        return MarkerType.VEHICLE_MARKER_TYPE

    def getTargetIDFromMarkerID(self, markerID):
        for vehicleID in self._markers:
            if self._markers[vehicleID].getMarkerID() == markerID:
                return vehicleID

        return INVALID_MARKER_ID

    def getMarkerSubtype(self, targetID):
        if targetID == INVALID_MARKER_ID or targetID not in self._markers:
            return INVALID_MARKER_SUBTYPE
        return DefaultMarkerSubType.ALLY_MARKER_SUBTYPE if self._markers[targetID].getIsPlayerTeam() else DefaultMarkerSubType.ENEMY_MARKER_SUBTYPE

    def showMarkerTimer(self, vehicleID, handle, statusID, leftTime, animated):
        self._updateStatusMarkerState(vehicleID, leftTime > 0, handle, statusID, leftTime, animated, False)

    def updateMarkerTimer(self, handle, leftTime, animated, statusID):
        self._updateStatusEffectTimer(handle, statusID, leftTime, animated)

    def hideMarkerTimer(self, vehicleID, handle, statusID, currentlyActiveStatusID, animated):
        self._updateStatusMarkerState(vehicleID, False, handle, statusID, 0, animated, False)

    def _setMarkerInitialState(self, marker, accountDBID=0):
        self.__setupDynamic(marker, accountDBID=accountDBID)
        if marker.isActive():
            self.__setupHealth(marker)
        self.__checkInspireMarker(marker)

    def _hideVehicleMarker(self, vehicleID):
        if vehicleID in self._markers:
            marker = self._markers[vehicleID]
            if marker.setActive(False):
                markerID = marker.getMarkerID()
                self._setMarkerActive(markerID, False)
                self._setMarkerMatrix(markerID, None)
            marker.detach()
        return

    def _destroyVehicleMarker(self, vehicleID):
        if vehicleID in self._markers:
            self._vehicleID = None
            marker = self._markers.pop(vehicleID)
            self._destroyMarker(marker.getMarkerID())
            marker.destroy()
        return

    def _getMarkerSymbol(self, vehicleID):
        return settings.MARKER_SYMBOL_NAME.VEHICLE_MARKER

    def _onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if eventID == _EVENT_ID.ENTITY_IN_FOCUS:
            self.__onVehicleInFocus(vehicleID, value)
        if vehicleID not in self._markers:
            return
        marker = self._markers[vehicleID]
        handle = marker.getMarkerID()
        if eventID in MARKER_HIT_STATE and (eventID not in MARKER_CRITICAL_HIT_STATES or self.__showDamageIcon):
            newState, stateText, iconAnimation = self.__getHitStateVO(eventID, MARKER_HIT_STATE)
            self.__updateMarkerState(handle, newState, value, stateText, iconAnimation)
        elif eventID == _EVENT_ID.VEHICLE_DEAD:
            self.__hide(handle, vehicleID)
            self.__stopActionMarker(handle, vehicleID)
            self.__updateMarkerState(handle, 'dead', value)
            self._setMarkerReplied(marker, False)
            self._setMarkerSticky(handle, False)
            self._setMarkerBoundEnabled(handle, False)
        elif eventID == _EVENT_ID.VEHICLE_SHOW_MARKER:
            vMarker, numberOfReplies, isTargetForPlayer, isPermanent = value
            self.__showActionMarker(handle, vMarker, vehicleID, numberOfReplies, isTargetForPlayer, isPermanent)
        elif eventID == _EVENT_ID.VEHICLE_HEALTH:
            self.__updateVehicleHealth(vehicleID, handle, *value)
        elif eventID == _EVENT_ID.VEHICLE_STUN:
            self._updateStunMarker(vehicleID, handle, value)
        elif eventID == _EVENT_ID.VEHICLE_DEBUFF:
            self.__updateDebuffMarker(vehicleID, handle, value)
        elif eventID == _EVENT_ID.VEHICLE_INSPIRE:
            self._updateInspireMarker(vehicleID, handle, **value)
        elif eventID == _EVENT_ID.VEHICLE_HEAL_POINT:
            self.__updateHealingMarker(vehicleID, handle, value.get('duration', 0))
        elif eventID == _EVENT_ID.VEHICLE_REPAIR_POINT:
            self._updateRepairingMarker(vehicleID, handle, value.get('duration', 0))
        elif eventID == _EVENT_ID.VEHICLE_PASSIVE_ENGINEERING:
            self.__updatePassiveEngineeringMarker(vehicleID, handle, *value)
        elif eventID == _EVENT_ID.VEHICLE_FRONTLINE_STEALTH_RADAR_ACTIVE:
            self.__updateStealthRadarMarker(vehicleID, handle, value)
        elif eventID == _EVENT_ID.VEHICLE_FRONTLINE_REGENERATION_KIT_ACTIVE:
            self.__updateFLRegenerationKitMarker(vehicleID, handle, value)

    def _onChatCommandTargetUpdate(self, _, chatCommandStates):
        for vehicleID, state in chatCommandStates.iteritems():
            vehMarker, chatCommandFlags = state
            if vehicleID in self._markers and chatCommandFlags & TARGET_CHAT_CMD_FLAG == 0:
                self._invokeMarker(self._markers[vehicleID].getMarkerID(), 'changeObjectiveActionMarker', vehMarker)

    def _getMarkerFromTargetID(self, targetID, markerType):
        return None if targetID not in self._markers or markerType != self.getMarkerType() else self._markers[targetID]

    def _updateStatusEffectTimer(self, handle, statusID, leftTime, animated):
        if self.__canUpdateStatus(handle):
            self._invokeMarker(handle, 'updateStatusEffectTimer', statusID, leftTime, animated)

    def _onReplyFeedbackReceived(self, targetID, replierID, markerType, oldReplyCount, newReplyCount):
        marker = self._getMarkerFromTargetID(targetID, markerType)
        if marker is not None:
            self._setMarkerRepliesAndCheckState(marker, newReplyCount, replierID == avatar_getter.getPlayerVehicleID(), False)
            markerID = marker.getMarkerID()
            if markerID in self.__callbackIDs and self.__callbackIDs[markerID] is not None:
                self.__handleCallback(markerID, targetID)
            else:
                self._checkNextState(marker)
        return

    def _updateStatusMarkerState(self, vehicleID, isShown, handle, statusID, duration, animated, isSourceVehicle):
        activeStatuses = self._markersStates[vehicleID]
        if isShown and statusID not in activeStatuses:
            activeStatuses.append(statusID)
            self._markersStates[vehicleID] = activeStatuses
        elif not isShown and statusID in activeStatuses:
            self._markersStates[vehicleID].remove(statusID)
        if self._markersStates[vehicleID]:
            activeStatuses = sorted(self._markersStates[vehicleID], key=self._getMarkerStatusPriority, reverse=False)
            self._markersStates[vehicleID] = activeStatuses
        currentlyActiveStatusID = self._markersStates[vehicleID][0] if self._markersStates[vehicleID] else -1
        if statusID in (BATTLE_MARKER_STATES.STUN_STATE, BATTLE_MARKER_STATES.HEALING_STATE):
            isSourceVehicle = True
        elif statusID == BATTLE_MARKER_STATES.DEBUFF_STATE:
            isSourceVehicle = False
        if isShown:
            self._invokeMarker(handle, 'showStatusMarker', statusID, self._getMarkerStatusPriority(statusID), isSourceVehicle, duration, currentlyActiveStatusID, self._getMarkerStatusPriority(currentlyActiveStatusID), animated)
        elif self.__canUpdateStatus(handle):
            self._invokeMarker(handle, 'hideStatusMarker', statusID, currentlyActiveStatusID, animated)

    def _updateInspireMarker(self, vehicleID, handle, isSourceVehicle, isInactivation, endTime, duration, primary=True, animated=True, equipmentID=None):
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle and vehicle.isAlive() and isInactivation is not None and duration > 0.0:
            statusID = BATTLE_MARKER_STATES.INSPIRING_STATE if isSourceVehicle else BATTLE_MARKER_STATES.INSPIRED_STATE
            if isSourceVehicle:
                hideStatusID = BATTLE_MARKER_STATES.INSPIRED_STATE
                self._updateMarkerTimer(vehicleID, handle, duration, statusID)
            else:
                hideStatusID = BATTLE_MARKER_STATES.INSPIRING_STATE
            self._updateStatusMarkerState(vehicleID, False, handle, hideStatusID, duration, animated, isSourceVehicle)
            self._updateStatusMarkerState(vehicleID, True, handle, statusID, duration, animated, isSourceVehicle)
        else:
            self._updateStatusMarkerState(vehicleID, False, handle, BATTLE_MARKER_STATES.INSPIRED_STATE, 0, animated, False)
            self._updateMarkerTimer(vehicleID, handle, 0, BATTLE_MARKER_STATES.INSPIRING_STATE)
            self._updateStatusMarkerState(vehicleID, False, handle, BATTLE_MARKER_STATES.INSPIRING_STATE, 0, animated, False)
        return

    def _updateMarkerTimer(self, vehicleID, handle, duration, statusID, showCountdown=True):
        activeTimers = self._markerTimers.get(handle, {})
        if statusID in activeTimers:
            timer = activeTimers.pop(statusID)
            timer.hide()
            timer.clear()
            if not activeTimers:
                self._markerTimers.pop(handle)
        if duration > 0:
            timer = MarkerTimer(self, vehicleID, handle, duration, statusID=statusID, showCountdown=showCountdown)
            self._markerTimers[handle][statusID] = timer
            timer.show(True)

    def __canUpdateStatus(self, handle):
        return any((marker.getMarkerID() == handle for marker in self._markers.itervalues()))

    def __checkInspireMarker(self, marker):
        vehicle = marker.getVehicleEntity()
        if vehicle is not None and vehicle.isStarted and vehicle.inspired is not None:
            data = vehicle.inspired
            currentTime = BigWorld.serverTime()
            isInactivation = data.inactivationStartTime <= currentTime <= data.inactivationEndTime
            if isInactivation:
                endTime = data.inactivationEndTime
                duration = max(endTime - data.inactivationStartTime, 0)
            else:
                endTime = data.endTime
                duration = max(endTime - data.startTime, 0)
            self._updateInspireMarker(marker.getVehicleID(), marker.getMarkerID(), isSourceVehicle=bool(data.inactivationSource), isInactivation=isInactivation, endTime=endTime, duration=duration, primary=bool(data.primary), equipmentID=data.equipmentID)
        return

    def __updateHealingMarker(self, vehicleID, handle, duration):
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle is None or not vehicle.isAlive():
            return
        else:
            self._updateMarkerTimer(vehicleID, handle, duration, BATTLE_MARKER_STATES.HEALING_STATE)
            return

    def _updateRepairingMarker(self, vehicleID, handle, duration):
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle is None or not vehicle.isAlive():
            return
        else:
            self._updateMarkerTimer(vehicleID, handle, duration, BATTLE_MARKER_STATES.REPAIRING_STATE)
            return

    def __updateStealthRadarMarker(self, vehicleID, handle, info):
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle is None or not vehicle.isAlive() or info is None:
            return
        else:
            duration = info.duration if info.isActive else 0
            self._updateMarkerTimer(vehicleID, handle, duration, BATTLE_MARKER_STATES.STEALTH_STATE, True)
            return

    def __updateFLRegenerationKitMarker(self, vehicleID, handle, info):
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle is None or not vehicle.isAlive():
            return
        else:
            duration = info.duration if info.isActive else 0
            self._updateMarkerTimer(vehicleID, handle, duration, BATTLE_MARKER_STATES.FL_REGENERATION_KIT_STATE, True)
            return

    def __onCameraChanged(self, mode, vehicleID=0):
        if mode != CTRL_MODE_NAME.POSTMORTEM or vehicleID == 0:
            self.__followingIgnoredTank = vehicleID
            return
        if self.__followingIgnoredTank > 0:
            oldMarker = self._markers.get(self.__followingIgnoredTank)
            if oldMarker and not (not avatar_getter.isVehicleAlive() and oldMarker.getIsPlayerTeam()):
                self._setMarkerBoundEnabled(oldMarker.getMarkerID(), True)
        if vehicleID > 0:
            newMarker = self._markers.get(vehicleID)
            if newMarker:
                self._setMarkerBoundEnabled(newMarker.getMarkerID(), False)
        self.__followingIgnoredTank = vehicleID

    def __addMarkerToPool(self, vehicleID, vInfo, vProxy=None):
        if not self.__needsMarker(vInfo):
            return
        else:
            if vProxy is not None:
                matrixProvider = self._clazz.fetchMatrixProvider(vProxy)
                active = True
            else:
                matrixProvider = None
                active = False
            markerID = self._createMarkerWithMatrix(self._getMarkerSymbol(vehicleID), matrixProvider=matrixProvider, active=active)
            self._setMarkerRenderInfo(markerID, _VEHICLE_MARKER_MIN_SCALE, _VEHICLE_MARKER_BOUNDS, _INNER_VEHICLE_MARKER_BOUNDS, _VEHICLE_MARKER_CULL_DISTANCE, _VEHICLE_MARKER_BOUNDS_MIN_SCALE)
            marker = self._clazz(markerID, vehicleID, vProxy=vProxy, active=active, isPlayerTeam=vInfo.team == avatar_getter.getPlayerTeam())
            marker.onVehicleModelChanged += self.__onVehicleModelChanged
            self._markers[vehicleID] = marker
            if marker.isActive():
                if not marker.isAlive():
                    self.__updateMarkerState(markerID, 'dead', True, '')
                    self._setMarkerBoundEnabled(markerID, False)
                elif not avatar_getter.isVehicleAlive() and marker.getIsPlayerTeam():
                    self._setMarkerBoundEnabled(markerID, False)
            return marker

    def __hide(self, handle, vehicleID):
        if handle in self._markerTimers:
            timers = self._markerTimers.get(handle, {})
            for timer in timers.values():
                timer.hide()
                timer.clear()

            self._markerTimers.pop(handle)
        if vehicleID in self._markersStates:
            currentStates = self._markersStates[vehicleID]
            for state in currentStates:
                self._markersStates[vehicleID].remove(state)
                self._invokeMarker(handle, 'hideStatusMarker', state, -1, False)

    def __setVehicleInfo(self, marker, vInfo, guiProps, nameParts):
        markerID = marker.getMarkerID()
        vType = vInfo.vehicleType
        if avatar_getter.isVehiclesColorized():
            guiPropsName = 'team{}'.format(vInfo.team)
        else:
            if avatar_getter.isObserver():
                arenaDP = self.sessionProvider.getArenaDP()
                obsVehId = BigWorld.player().observedVehicleID
                vehId = vInfo.vehicleID
                if vehId == obsVehId or arenaDP.isSquadMan(vehId, arenaDP.getVehicleInfo(obsVehId).prebattleID):
                    guiProps = PLAYER_GUI_PROPS.squadman
            guiPropsName = guiProps.name()
        if self._isSquadIndicatorEnabled and vInfo.squadIndex:
            squadIndex = vInfo.squadIndex
        else:
            squadIndex = 0
        hunting = VehicleActions.isHunting(vInfo.events)
        self._invokeMarker(markerID, 'setVehicleInfo', vType.classTag, vType.iconPath, nameParts.vehicleName, vType.level, nameParts.playerFullName, nameParts.playerName, nameParts.clanAbbrev, nameParts.regionCode, vType.maxHealth, guiPropsName, hunting, squadIndex, backport.text(R.strings.ingame_gui.stun.seconds()))
        self._invokeMarker(markerID, 'update')

    def __setupDynamic(self, marker, accountDBID=0):
        if accountDBID:
            speaking = self.bwProto.voipController.isPlayerSpeaking(accountDBID)
        else:
            speaking = False
        if marker.setSpeaking(speaking):
            self._invokeMarker(marker.getMarkerID(), 'setSpeaking', speaking)

    def __setupHealth(self, marker):
        self._invokeMarker(marker.getMarkerID(), 'setHealth', marker.getHealth())

    @staticmethod
    def __needsMarker(vInfo):
        return vInfo.isAlive() or not isSpawnedBot(vInfo.vehicleType.tags)

    def __setEntityName(self, vInfo, arenaDP):
        vehicleID = vInfo.vehicleID
        if vehicleID not in self._markers:
            return
        handle = self._markers[vehicleID].getMarkerID()
        self._invokeMarker(handle, 'setEntityName', arenaDP.getPlayerGuiProps(vehicleID, vInfo.team).name())

    def __onVehicleMarkerAdded(self, vProxy, vInfo, guiProps):
        if not self.__needsMarker(vInfo):
            return
        else:
            vehicleID = vInfo.vehicleID
            accountDBID = vInfo.player.accountDBID
            if vehicleID in self._markers:
                marker = self._markers[vInfo.vehicleID]
                if marker.setActive(True):
                    marker.attach(vProxy)
                    self._setMarkerMatrix(marker.getMarkerID(), marker.getMatrixProvider())
                    self._setMarkerActive(marker.getMarkerID(), True)
                    self._setMarkerInitialState(marker, accountDBID=accountDBID)
            else:
                if vInfo.isObserver():
                    return
                marker = self.__addMarkerToPool(vehicleID, vInfo=vInfo, vProxy=vProxy)
                if marker is None:
                    return
                self.__setVehicleInfo(marker, vInfo, guiProps, self.sessionProvider.getCtx().getPlayerFullNameParts(vehicleID))
                self._setMarkerInitialState(marker, accountDBID=accountDBID)
            return

    def __onVehicleMarkerRemoved(self, vehicleID):
        self._hideVehicleMarker(vehicleID)

    def __onVehicleInFocus(self, vehicleID, entityInFocusData):
        if entityInFocusData.entityTypeInFocus != ENTITY_IN_FOCUS_TYPE.VEHICLE:
            return
        markerID = -1
        if vehicleID > 0:
            focusedMarker = self._markers.get(vehicleID)
            if focusedMarker and focusedMarker.isAlive():
                isVehicleValid = avatar_getter.isVehicleAlive() or not focusedMarker.getIsPlayerTeam() and not focusedMarker.getIsActionMarkerActive()
                if isVehicleValid:
                    markerID = focusedMarker.getMarkerID()
        self._setMarkerObjectInFocus(markerID, entityInFocusData.isInFocus)

    def __setInFocusForPlayer(self, oldTargetID, oldTargetType, newTargetID, newTargetType, isOneShot):
        if oldTargetType == self.getMarkerType() and oldTargetID in self._markers:
            self.__makeMarkerSticky(oldTargetID, False, isOneShot)
        if newTargetType == self.getMarkerType() and newTargetID in self._markers:
            newMarker = self._markers[newTargetID]
            pos = self.__getVehicleMarkerPositionByVehicleID(newTargetID)
            if pos is not None:
                pos = Math.Vector3(pos[0], pos[1], pos[2])
                if pos.distTo(avatar_getter.getOwnVehiclePosition()) > MAX_DISTANCE_TEMP_STICKY and not newMarker.getIsRepliedByPlayer() and newMarker.getActionState() == _HELP_ME_STATE:
                    return
            self.__makeMarkerSticky(newTargetID, True, isOneShot)
        return

    def _onVehicleStateUpdated(self, state, value):
        if state in (VEHICLE_VIEW_STATE.DESTROYED, VEHICLE_VIEW_STATE.CREW_DEACTIVATED):
            for marker in self._markers.values():
                if marker.getIsPlayerTeam() or marker.getIsActionMarkerActive():
                    self._setMarkerBoundEnabled(marker.getMarkerID(), False)

        elif state in (VEHICLE_VIEW_STATE.SWITCHING, VEHICLE_VIEW_STATE.RESPAWNING):
            if not self.sessionProvider.getCtx().isPlayerObserver() and avatar_getter.isVehicleAlive():
                for marker in self._markers.values():
                    if marker.isAlive():
                        self._setMarkerBoundEnabled(marker.getMarkerID(), True)

        elif state == VEHICLE_VIEW_STATE.DEBUFF:
            vehicle = BigWorld.player().getVehicleAttached()
            if vehicle is not None:
                vehicleID = vehicle.id
                if vehicleID in self._markers:
                    self.__updateDebuffMarker(vehicleID, self._markers[vehicleID].getMarkerID(), value)
        elif state == VEHICLE_VIEW_STATE.STEALTH_RADAR:
            vehicle = BigWorld.player().getVehicleAttached()
            if vehicle is not None:
                vehicleID = vehicle.id
                if vehicleID in self._markers:
                    self.__updateStealthRadarMarker(vehicleID, self._markers[vehicleID].getMarkerID(), value)
        elif state == VEHICLE_VIEW_STATE.INSPIRE:
            vehicle = BigWorld.player().getVehicleAttached()
            if vehicle is not None:
                vehicleID = vehicle.id
                if vehicleID in self._markers:
                    self._updateInspireMarker(vehicleID, self._markers[vehicleID].getMarkerID(), **value)
        return

    def __makeMarkerSticky(self, targetID, setSticky, isOneShot):
        marker = self._markers[targetID]
        markerID = marker.getMarkerID()
        self._setMarkerSticky(markerID, setSticky)
        if not isOneShot:
            marker.setIsSticky(setSticky)
        self._checkNextState(marker)

    def __onVehicleModelChanged(self, markerID, matrixProvider):
        self._setMarkerMatrix(markerID, matrixProvider)

    def __onSettingsChanged(self, diff):
        if GAME.SHOW_DAMAGE_ICON in diff:
            self.__showDamageIcon = diff[GAME.SHOW_DAMAGE_ICON]

    def __updateMarkerState(self, handle, newState, isImmediate, text='', iconAnimation=''):
        self._invokeMarker(handle, 'updateState', newState, isImmediate, text, iconAnimation)

    def __showActionMarker(self, handle, newAction, vehicleID, numberOfReplies, isTargetForPlayer, isPermanent):
        self._invokeMarker(handle, 'showActionMarker', newAction)
        if not isPermanent:
            if handle in self.__callbackIDs and self.__callbackIDs[handle] is not None:
                self.__removeMarkerCallback(handle)
            self.__callbackIDs[handle] = BigWorld.callback(_DEFAULT_ACTIVE_COMMAND_TIME, partial(self.__handleCallback, handle, vehicleID))
        marker = self._markers[vehicleID]
        marker.setIsActionMarkerActive(True)
        if numberOfReplies > 0:
            marker.setActionState(newAction)
            marker.setIsSticky(isTargetForPlayer)
            self._setMarkerRepliesAndCheckState(marker, numberOfReplies, isTargetForPlayer)
        elif isPermanent:
            marker.setActionState(newAction)
        else:
            self._setMarkerSticky(handle, False)
            self._setMarkerReplied(marker, False)
        if marker and not avatar_getter.isVehicleAlive() and not marker.getIsPlayerTeam():
            self._setMarkerBoundEnabled(marker.getMarkerID(), False)
        return

    def __handleCallback(self, markerID, targetID):
        self.__removeMarkerCallback(markerID)
        marker = self._markers[targetID]
        if marker.getReplyCount() > 0:
            self._setMarkerReplied(marker, True)
            self.__showActionMarker(markerID, marker.getActionState(), targetID, marker.getReplyCount(), marker.getIsRepliedByPlayer(), True)
            self._checkNextState(marker, True)
        else:
            self.__stopActionMarker(markerID, targetID)
        if marker.getIsSticky():
            self._setMarkerSticky(markerID, True)

    def __stopActionMarker(self, markerID, vehicleID):
        self.__removeMarkerCallback(markerID)
        self._invokeMarker(markerID, 'stopActionMarker')
        marker = self._markers[vehicleID]
        marker.setIsActionMarkerActive(False)
        if marker and not avatar_getter.isVehicleAlive() and not marker.getIsPlayerTeam():
            self._setMarkerBoundEnabled(marker.getMarkerID(), True)

    def __onRemoveCommandReceived(self, vehicleID, markerType):
        if markerType != self.getMarkerType() or vehicleID not in self._markers:
            return
        else:
            marker = self._markers[vehicleID]
            markerID = marker.getMarkerID()
            isOneShotActive = self.__callbackIDs.get(markerID, None) is not None
            if not isOneShotActive:
                self.__stopActionMarker(markerID, vehicleID)
                if marker.getReplyCount > 0:
                    marker.setIsRepliedByPlayer(False)
                    self._setMarkerReplied(marker, False)
                    self._setMarkerReplyCount(marker, 0)
            return

    def __removeMarkerCallback(self, markerID):
        callbackID = self.__callbackIDs.pop(markerID, None)
        if callbackID is not None:
            BigWorld.cancelCallback(callbackID)
        return

    def __removeMarkerCallbacks(self):
        while self.__callbackIDs:
            _, callbackID = self.__callbackIDs.popitem()
            BigWorld.cancelCallback(callbackID)

    def _updateStunMarker(self, vehicleID, handle, value):
        self._updateMarkerTimer(vehicleID, handle, value.duration, BATTLE_MARKER_STATES.STUN_STATE, True)

    def __updateDebuffMarker(self, vehicleID, handle, value):
        self._updateMarkerTimer(vehicleID, handle, value.duration, BATTLE_MARKER_STATES.DEBUFF_STATE, False)

    def __updatePassiveEngineeringMarker(self, vehicleID, handle, isAttacker, enabled, animated=True):
        self._updateStatusMarkerState(vehicleID, enabled, handle, BATTLE_MARKER_STATES.ENGINEER_STATE, enabled, animated, isAttacker)

    def _getMarkerStatusPriority(self, statusID):
        try:
            return _STATUS_EFFECTS_PRIORITY.index(statusID)
        except ValueError:
            return -1

    def __statusCompareFunction(self, x, y):
        return x > y

    def __updateVehicleHealth(self, vehicleID, handle, newHealth, aInfo, attackReasonID):
        if newHealth < 0 and not constants.SPECIAL_VEHICLE_HEALTH.IS_AMMO_BAY_DESTROYED(newHealth):
            newHealth = 0
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isTimeWarpInProgress:
            self._invokeMarker(handle, 'setHealth', newHealth)
        else:
            self._invokeMarker(handle, 'updateHealth', newHealth, self.__getVehicleDamageType(aInfo), constants.ATTACK_REASONS[attackReasonID])

    def __onPlayerSpeaking(self, accountDBID, flag):
        vehicleID = self.sessionProvider.getArenaDP().getVehIDByAccDBID(accountDBID)
        if vehicleID in self._markers:
            marker = self._markers[vehicleID]
            if marker.setSpeaking(flag):
                self._invokeMarker(marker.getMarkerID(), 'setSpeaking', flag)

    def __onTeamChanged(self, teamID):
        self.invalidateArenaInfo()

    def __getVehicleDamageType(self, attackerInfo):
        if not attackerInfo:
            return settings.DAMAGE_TYPE.FROM_UNKNOWN
        attackerID = attackerInfo.vehicleID
        if attackerID == self._playerVehicleID:
            return settings.DAMAGE_TYPE.FROM_PLAYER
        entityName = self.sessionProvider.getCtx().getPlayerGuiProps(attackerID, attackerInfo.team)
        if entityName == PLAYER_GUI_PROPS.squadman:
            return settings.DAMAGE_TYPE.FROM_SQUAD
        if entityName == PLAYER_GUI_PROPS.ally:
            return settings.DAMAGE_TYPE.FROM_ALLY
        return settings.DAMAGE_TYPE.FROM_ENEMY if entityName == PLAYER_GUI_PROPS.enemy else settings.DAMAGE_TYPE.FROM_UNKNOWN

    def __getVehicleMarkerPositionByVehicleID(self, vehicleID):
        arenaDP = self.sessionProvider.getCtx().getArenaDP()
        if arenaDP is None:
            return
        else:
            marker = self._markers[vehicleID]
            if marker is None or marker.getMatrixProvider() is None:
                return
            matrixProvider = Math.Matrix(marker.getMatrixProvider())
            pos = matrixProvider.translation
            return pos

    def __getHitStateVO(self, eventID, states):
        newState = 'hit'
        iconAnimation = ''
        stateText = ''
        stateData = states.get(eventID)
        if stateData is not None:
            newState = stateData[0]
            iconAnimation = stateData[1]
            rText = stateData[2]
            stateText = backport.text(rText) if rText > 0 else ''
        return (newState, stateText, iconAnimation)


class RespawnableVehicleMarkerPlugin(VehicleMarkerPlugin):

    def start(self):
        super(RespawnableVehicleMarkerPlugin, self).start()
        self._isSquadIndicatorEnabled = False

    def _hideVehicleMarker(self, vehicleID):
        self._destroyVehicleMarker(vehicleID)
