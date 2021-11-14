# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/markers2d/plugins.py
import logging
from collections import defaultdict
from functools import partial
import BattleReplay
import BigWorld
import Math
import constants
from AvatarInputHandler import aih_global_binding
from AvatarInputHandler.aih_global_binding import BINDING_ID
from BattleReplay import CallbackDataNames
from Math import Matrix
from PlayerEvents import g_playerEvents
from account_helpers.settings_core.options import VehicleMarkerSetting
from account_helpers.settings_core.settings_constants import MARKERS, GRAPHICS
from battleground.location_point_manager import g_locationPointManager, COMMAND_NAME_TO_LOCATION_MARKER_SUBTYPE
from chat_commands_consts import getUniqueTeamOrControlPointID, INVALID_MARKER_SUBTYPE, INVALID_MARKER_ID, LocationMarkerSubType, MarkerType, DefaultMarkerSubType, INVALID_COMMAND_ID
from gui.Scaleform.daapi.view.battle.shared.markers2d import markers
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings
from gui.Scaleform.daapi.view.battle.shared.markers2d.markers import LocationMarker, BaseMarker, Marker, ReplyStateForMarker
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _EVENT_ID
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.doc_loaders import GuiColorsLoader
from gui.shared import g_eventBus
from gui.shared.events import GameEvent
from gui.shared.utils.plugins import IPlugin
from helpers import dependency
from helpers import i18n
from messenger.proto.bw_chat2.battle_chat_cmd import AUTOCOMMIT_COMMAND_NAMES
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.impl import backport
from gui.impl.gen import R
_logger = logging.getLogger(__name__)
_LOCATION_SUBTYPE_TO_FLASH_SYMBOL_NAME = {LocationMarkerSubType.SPG_AIM_AREA_SUBTYPE: settings.MARKER_SYMBOL_NAME.STATIC_ARTY_MARKER,
 LocationMarkerSubType.GOING_TO_MARKER_SUBTYPE: settings.MARKER_SYMBOL_NAME.LOCATION_MARKER,
 LocationMarkerSubType.PREBATTLE_WAYPOINT_SUBTYPE: settings.MARKER_SYMBOL_NAME.LOCATION_MARKER,
 LocationMarkerSubType.ATTENTION_TO_MARKER_SUBTYPE: settings.MARKER_SYMBOL_NAME.ATTENTION_MARKER,
 LocationMarkerSubType.SHOOTING_POINT_SUBTYPE: settings.MARKER_SYMBOL_NAME.SHOOTING_MARKER,
 LocationMarkerSubType.NAVIGATION_POINT_SUBTYPE: settings.MARKER_SYMBOL_NAME.NAVIGATION_MARKER}
_STATIC_MARKER_CULL_DISTANCE = 1800
_STATIC_MARKER_MIN_SCALE = 60.0
_BASE_MARKER_MIN_SCALE = 100.0
RANDOM_BATTLE_BASE_ID = 7
_STATIC_MARKER_BOUNDS = Math.Vector4(30, 30, 90, -15)
_INNER_STATIC_MARKER_BOUNDS = Math.Vector4(15, 15, 70, -35)
_STATIC_MARKER_BOUNDS_MIN_SCALE = Math.Vector2(1.0, 0.8)
_BASE_MARKER_BOUNDS = Math.Vector4(30, 30, 30, 30)
_INNER_BASE_MARKER_BOUNDS = Math.Vector4(17, 17, 18, 18)
_BASE_MARKER_BOUND_MIN_SCALE = Math.Vector2(1.0, 1.0)
MAX_DISTANCE_TEMP_STICKY = 350

class IMarkersManager(object):

    def createMarker(self, symbol, matrixProvider=None, active=True):
        raise NotImplementedError

    def invokeMarker(self, markerID, *signature):
        raise NotImplementedError

    def setMarkerMatrix(self, markerID, matrix):
        raise NotImplementedError

    def setMarkerActive(self, markerID, active):
        raise NotImplementedError

    def setMarkerLocationOffset(self, markerID, minY, maxY, distForMinY, maxBoost, boostStart):
        raise NotImplementedError

    def setMarkerRenderInfo(self, markerID, minScale, offset, innerOffset, cullDistance, boundsMinScale):
        raise NotImplementedError

    def destroyMarker(self, markerID):
        raise NotImplementedError

    def _createCanvas(self, arenaVisitor):
        raise NotImplementedError

    def _setupPlugins(self, arenaVisitor):
        raise NotImplementedError


class MarkerPlugin(IPlugin):
    __slots__ = ()
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)

    def getTargetIDFromMarkerID(self, markerID):
        return INVALID_MARKER_ID

    def getMarkerType(self):
        return MarkerType.INVALID_MARKER_TYPE

    def getMarkerSubtype(self, targetID):
        return INVALID_MARKER_SUBTYPE

    def _createMarkerWithPosition(self, symbol, position, active=True):
        matrixProvider = Matrix()
        matrixProvider.translation = position
        return self._parentObj.createMarker(symbol, matrixProvider, active)

    def _createMarkerWithMatrix(self, symbol, matrixProvider=None, active=True):
        return self._parentObj.createMarker(symbol, matrixProvider=matrixProvider, active=active)

    def _invokeMarker(self, markerID, function, *args):
        self._parentObj.invokeMarker(markerID, function, *args)

    def _setMarkerPosition(self, markerID, position):
        matrix = Matrix()
        matrix.setTranslate(position)
        self._parentObj.setMarkerMatrix(markerID, matrix)

    def _setMarkerMatrix(self, markerID, matrix):
        self._parentObj.setMarkerMatrix(markerID, matrix)

    def _setMarkerActive(self, markerID, active):
        self._parentObj.setMarkerActive(markerID, active)

    def _destroyMarker(self, markerID):
        self._parentObj.destroyMarker(markerID)

    def _setMarkerSticky(self, markerID, isSticky):
        self._parentObj.setMarkerSticky(markerID, isSticky)

    def _setMarkerRenderInfo(self, markerID, minScale, offset, innerOffset, cullDistance, boundsMinScale):
        self._parentObj.setMarkerRenderInfo(markerID, minScale, offset, innerOffset, cullDistance, boundsMinScale)

    def _setMarkerLocationOffset(self, markerID, minYOffset, maxYOffset, distanceForMinYOffset, maxBoost, boostStart):
        self._parentObj.setMarkerLocationOffset(markerID, minYOffset, maxYOffset, distanceForMinYOffset, maxBoost, boostStart)

    def _setMarkerBoundEnabled(self, markerID, isBoundEnabled):
        self._parentObj.setMarkerBoundCheckEnabled(markerID, isBoundEnabled)

    def _setMarkerObjectInFocus(self, markerID, isBoundEnabled):
        self._parentObj.setMarkerObjectInFocus(markerID, isBoundEnabled)


class ControlModePlugin(MarkerPlugin):
    _aimOffset = aih_global_binding.bindRO(aih_global_binding.BINDING_ID.AIM_OFFSET)

    def start(self):
        aih_global_binding.subscribe(BINDING_ID.AIM_OFFSET, self.__onAimOffsetChanged)
        self.__onAimOffsetChanged(self._aimOffset)

    def stop(self):
        aih_global_binding.unsubscribe(BINDING_ID.AIM_OFFSET, self.__onAimOffsetChanged)

    def __onAimOffsetChanged(self, offset):
        self._parentObj.setActiveCameraAimOffset(offset)


class SettingsPlugin(MarkerPlugin):

    def start(self, *args):
        super(SettingsPlugin, self).init(*args)
        self._setMarkerSettings(notify=False)
        self.__setColorsSchemes()
        self._parentObj.setColorBlindFlag(self.settingsCore.getSetting(GRAPHICS.COLOR_BLIND))
        self._parentObj.setScale(self.settingsCore.interfaceScale.get())
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.settingsCore.interfaceScale.onScaleChanged += self.__onScaleChanged

    def stop(self):
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.settingsCore.interfaceScale.onScaleChanged -= self.__onScaleChanged
        super(SettingsPlugin, self).fini()

    def _setMarkerSettings(self, notify=False):
        getter = self.settingsCore.getSetting
        self._parentObj.setMarkerSettings(dict(((name, getter(name)) for name in MARKERS.ALL())), notify=notify)

    def __setColorsSchemes(self):
        colors = GuiColorsLoader.load()
        defaultSchemes = {}
        for name in colors.schemasNames():
            if not name.startswith(settings.MARKERS_COLOR_SCHEME_PREFIX):
                continue
            defaultSchemes[name] = colors.getSubSchemeToFlash(name, GuiColorsLoader.DEFAULT_SUB_SCHEME)

        colorBlindSchemes = {}
        for name in colors.schemasNames():
            if not name.startswith(settings.MARKERS_COLOR_SCHEME_PREFIX):
                continue
            colorBlindSchemes[name] = colors.getSubSchemeToFlash(name, GuiColorsLoader.COLOR_BLIND_SUB_SCHEME)

        self._parentObj.setColorsSchemes(defaultSchemes, colorBlindSchemes)

    def __onSettingsChanged(self, diff):
        if GRAPHICS.COLOR_BLIND in diff:
            self._parentObj.setColorBlindFlag(diff[GRAPHICS.COLOR_BLIND])
        if set(MARKERS.ALL()) & set(diff):
            self._setMarkerSettings(notify=True)

    def __onScaleChanged(self, scale):
        self._parentObj.setScale(scale)


class EventBusPlugin(MarkerPlugin):

    def start(self, *args):
        super(EventBusPlugin, self).init(*args)
        add = g_eventBus.addListener
        add(GameEvent.SHOW_EXTENDED_INFO, self.__handleShowExtendedInfo, scope=settings.SCOPE)
        add(GameEvent.GUI_VISIBILITY, self.__handleGUIVisibility, scope=settings.SCOPE)
        add(GameEvent.MARKERS_2D_VISIBILITY, self.__handleMarkerVisibility, scope=settings.SCOPE)

    def stop(self):
        remove = g_eventBus.removeListener
        remove(GameEvent.SHOW_EXTENDED_INFO, self.__handleShowExtendedInfo, scope=settings.SCOPE)
        remove(GameEvent.GUI_VISIBILITY, self.__handleGUIVisibility, scope=settings.SCOPE)
        remove(GameEvent.MARKERS_2D_VISIBILITY, self.__handleMarkerVisibility, scope=settings.SCOPE)
        super(EventBusPlugin, self).fini()

    def __handleShowExtendedInfo(self, event):
        self._parentObj.setShowExInfoFlag(event.ctx['isDown'])

    def __handleGUIVisibility(self, event):
        self._parentObj.setVisible(event.ctx['visible'])

    def __handleMarkerVisibility(self, _):
        self._parentObj.setVisible(not self._parentObj.isVisible())


class ChatCommunicationComponent(IPlugin):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def start(self):
        super(ChatCommunicationComponent, self).start()
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onReplyFeedbackReceived += self._onReplyFeedbackReceived
        return

    def stop(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onReplyFeedbackReceived -= self._onReplyFeedbackReceived
        super(ChatCommunicationComponent, self).stop()
        return

    def _getMarkerFromTargetID(self, targetID, markerType):
        raise NotImplementedError

    def _onReplyFeedbackReceived(self, targetID, replierID, markerType, oldReplyCount, newReplyCount):
        marker = self._getMarkerFromTargetID(targetID, markerType)
        if marker is not None:
            self._setMarkerRepliesAndCheckState(marker, newReplyCount, replierID == avatar_getter.getPlayerVehicleID())
        return

    def _setMarkerRepliesAndCheckState(self, marker, count, isTargetForPlayer, checkState=True):
        markerID = marker.getMarkerID()
        oldReplyCount = marker.getReplyCount()
        if isTargetForPlayer:
            if marker.getIsRepliedByPlayer():
                isRepliedByPlayer = count >= oldReplyCount
            else:
                isRepliedByPlayer = count > oldReplyCount
            marker.setIsRepliedByPlayer(isRepliedByPlayer)
            self._parentObj.invokeMarker(markerID, 'triggerClickAnimation')
        if oldReplyCount != count and (oldReplyCount == 0 or count == 0):
            self._setMarkerReplied(marker, count > 0)
        self._setMarkerReplyCount(marker, count)
        if checkState:
            self._checkNextState(marker)

    def _checkNextState(self, marker, forceUpdate=False):
        oldState = marker.getState()
        if marker.getReplyCount() == 0:
            self._setMarkerReplied(marker, False)
            if marker.getActiveCommandID() is not None and marker.getActiveCommandID() == INVALID_COMMAND_ID:
                newState = ReplyStateForMarker.NO_ACTION
            else:
                newState = ReplyStateForMarker.CREATE_STATE
        elif marker.getIsRepliedByPlayer():
            newState = ReplyStateForMarker.REPLIED_ME_STATE
        else:
            newState = ReplyStateForMarker.REPLIED_ALLY_STATE
        if oldState != newState or forceUpdate:
            marker.setState(newState)
            self._setActiveState(marker, newState)
        return

    def _setMarkerReplied(self, marker, isReplied):
        if marker.getIsReplied() != isReplied:
            self._parentObj.invokeMarker(marker.getMarkerID(), 'setMarkerReplied', isReplied)
            marker.setIsReplied(isReplied)

    def _setMarkerReplyCount(self, marker, replyCount):
        if marker.getReplyCount() != replyCount:
            self._parentObj.invokeMarker(marker.getMarkerID(), 'setReplyCount', replyCount)
            marker.setReplyCount(replyCount)

    def _setActiveState(self, marker, state):
        markerID = marker.getMarkerID()
        if state is None:
            state = marker.getState()
        self._parentObj.invokeMarker(markerID, 'setActiveState', state.value)
        return


class VehicleMarkerTargetPlugin(MarkerPlugin, IArenaVehiclesController):
    __slots__ = ('_markers', '_vehicleID', '_showExtendedInfo', '_markersStates', '_clazz', '__markerType', '__markerBaseAimMarker2D', '__markerAltAimMarker2D', '__arenaDP', '__baseMarker', '__altMarker')

    def __init__(self, parentObj, clazz=markers.VehicleTargetMarker):
        super(VehicleMarkerTargetPlugin, self).__init__(parentObj)
        self._markers = {}
        self._vehicleID = None
        self._showExtendedInfo = False
        self._markersStates = defaultdict(list)
        self._clazz = clazz
        self.__markerType = settings.MARKER_SYMBOL_NAME.TARGET_MARKER
        self.__markerBaseAimMarker2D = VehicleMarkerSetting.OPTIONS.getOptionName(VehicleMarkerSetting.OPTIONS.TYPES.BASE, VehicleMarkerSetting.OPTIONS.PARAMS.AIM_MARKER_2D)
        self.__markerAltAimMarker2D = VehicleMarkerSetting.OPTIONS.getOptionName(VehicleMarkerSetting.OPTIONS.TYPES.ALT, VehicleMarkerSetting.OPTIONS.PARAMS.AIM_MARKER_2D)
        self.__arenaDP = None
        self.__baseMarker = None
        self.__altMarker = None
        return

    def start(self):
        super(VehicleMarkerTargetPlugin, self).start()
        self.sessionProvider.addArenaCtrl(self)
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        ctrl = self.sessionProvider.shared.feedback
        self.__arenaDP = self.sessionProvider.getArenaDP()
        if ctrl is not None:
            ctrl.onVehicleMarkerRemoved += self.onVehicleMarkerRemoved
            ctrl.onVehicleFeedbackReceived += self.onVehicleFeedbackReceived
        add = g_eventBus.addListener
        add(GameEvent.ADD_AUTO_AIM_MARKER, self.__addAutoAimMarker, scope=settings.SCOPE)
        add(GameEvent.HIDE_AUTO_AIM_MARKER, self._hideAllMarkers, scope=settings.SCOPE)
        add(GameEvent.SHOW_EXTENDED_INFO, self.__showExtendedInfo, scope=settings.SCOPE)
        self.__baseMarker = self.settingsCore.getSetting(MARKERS.ENEMY).get(self.__markerBaseAimMarker2D)
        self.__altMarker = self.settingsCore.getSetting(MARKERS.ENEMY).get(self.__markerAltAimMarker2D)
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        return

    def stop(self):
        while self._markers:
            _, marker = self._markers.popitem()
            marker.destroy()

        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleMarkerRemoved -= self.onVehicleMarkerRemoved
            ctrl.onVehicleFeedbackReceived -= self.onVehicleFeedbackReceived
        remove = g_eventBus.removeListener
        remove(GameEvent.ADD_AUTO_AIM_MARKER, self.__addAutoAimMarker, scope=settings.SCOPE)
        remove(GameEvent.HIDE_AUTO_AIM_MARKER, self._hideAllMarkers, scope=settings.SCOPE)
        remove(GameEvent.SHOW_EXTENDED_INFO, self.__showExtendedInfo, scope=settings.SCOPE)
        self.__baseMarker = None
        self.__altMarker = None
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.sessionProvider.removeArenaCtrl(self)
        super(VehicleMarkerTargetPlugin, self).stop()
        return

    def onVehicleFeedbackReceived(self, eventID, vehicleID, _):
        if vehicleID not in self._markers:
            return
        if eventID == _EVENT_ID.VEHICLE_DEAD:
            self._destroyVehicleMarker(vehicleID)

    def onVehicleMarkerRemoved(self, vehicleID):
        self._hideVehicleMarker(vehicleID)

    def _destroyVehicleMarker(self, vehicleID):
        if vehicleID in self._markers:
            self._vehicleID = None
            marker = self._markers.pop(vehicleID)
            self._destroyMarker(marker.getMarkerID())
            marker.destroy()
        return

    def _onVehicleMarkerAdded(self, vehicleID):
        feedback = self.sessionProvider.shared.feedback
        vProxy = feedback.getVehicleProxy(vehicleID)
        vInfo = self.__arenaDP.getVehicleInfo(vehicleID)
        self._vehicleID = vehicleID
        if vehicleID in self._markers:
            marker = self._markers[vehicleID]
            if marker.setActive(True) and vProxy is not None:
                marker.attach(vProxy)
                self._setMarkerMatrix(marker.getMarkerID(), marker.getMatrixProvider())
                self._setMarkerActive(marker.getMarkerID(), True)
        else:
            if vInfo.isObserver():
                return
            self.__addMarkerToPool(vehicleID, vProxy)
        return

    def _addMarker(self, vehicleID):
        if self._vehicleID is not None:
            self._hideAllMarkers()
        if vehicleID is not None:
            self._onVehicleMarkerAdded(vehicleID)
        return

    def _hideAllMarkers(self, event=None, clearVehicleID=True):
        if event and not event.ctx.get('vehicle'):
            self._vehicleID = None
        for vehicleID in self._markers:
            self._hideVehicleMarker(vehicleID, clearVehicleID)

        return

    def _hideVehicleMarker(self, vehicleID, clearVehicleID=True):
        if vehicleID in self._markers:
            marker = self._markers[vehicleID]
            if clearVehicleID:
                self._vehicleID = None
            if marker.setActive(False):
                markerID = marker.getMarkerID()
                self._setMarkerActive(markerID, False)
                self._setMarkerMatrix(markerID, None)
            marker.detach()
        return

    def __addMarkerToPool(self, vehicleID, vProxy=None):
        if vProxy is not None:
            matrixProvider = self._clazz.fetchMatrixProvider(vProxy)
            active = True
        else:
            matrixProvider = None
            active = False
        markerID = self._createMarkerWithMatrix(self.__markerType, matrixProvider=matrixProvider, active=active)
        marker = self._clazz(markerID, vehicleID, vProxy=vProxy, active=active)
        self._markers[vehicleID] = marker
        return

    def __addAutoAimMarker(self, event):
        vehicle = event.ctx.get('vehicle')
        self._vehicleID = vehicle.id if vehicle is not None else None
        if self._showExtendedInfo:
            if self.__altMarker:
                self._addMarker(self._vehicleID)
        elif self.__baseMarker:
            self._addMarker(self._vehicleID)
        return

    def __onVehicleStateUpdated(self, state, value):
        if state in (VEHICLE_VIEW_STATE.DESTROYED, VEHICLE_VIEW_STATE.CREW_DEACTIVATED):
            self._hideAllMarkers()

    def __onSettingsChanged(self, diff):
        if MARKERS.ENEMY in diff:
            isMarkerEnabled = diff[MARKERS.ENEMY].get(self.__markerBaseAimMarker2D)
            if isMarkerEnabled:
                self._addMarker(self._vehicleID)
            elif isMarkerEnabled is False:
                self._hideAllMarkers(clearVehicleID=False)
            self.__baseMarker = diff[MARKERS.ENEMY].get(self.__markerBaseAimMarker2D)
            self.__altMarker = diff[MARKERS.ENEMY].get(self.__markerAltAimMarker2D)

    def __showExtendedInfo(self, event):
        isDown = event.ctx['isDown']
        self._showExtendedInfo = isDown if isDown is not None else False
        self._hideAllMarkers(clearVehicleID=False)
        if self._showExtendedInfo:
            if self.__altMarker:
                self._addMarker(self._vehicleID)
        elif self.__baseMarker:
            self._addMarker(self._vehicleID)
        return


class VehicleMarkerTargetPluginReplayPlaying(VehicleMarkerTargetPlugin):

    def __init__(self, parentObj):
        super(VehicleMarkerTargetPluginReplayPlaying, self).__init__(parentObj)
        if BattleReplay.g_replayCtrl.isPlaying:
            BattleReplay.g_replayCtrl.setDataCallback(CallbackDataNames.SHOW_AUTO_AIM_MARKER, self._addMarker)
            BattleReplay.g_replayCtrl.setDataCallback(CallbackDataNames.HIDE_AUTO_AIM_MARKER, self._hideVehicleMarker)


class VehicleMarkerTargetPluginReplayRecording(VehicleMarkerTargetPlugin):

    def _addMarker(self, vehicleID):
        super(VehicleMarkerTargetPluginReplayRecording, self)._addMarker(vehicleID)
        if BattleReplay.g_replayCtrl.isRecording:
            BattleReplay.g_replayCtrl.serializeCallbackData(CallbackDataNames.SHOW_AUTO_AIM_MARKER, (vehicleID,))

    def _hideVehicleMarker(self, vehicleID, clearVehicleID=True):
        if BattleReplay.g_replayCtrl.isRecording:
            BattleReplay.g_replayCtrl.serializeCallbackData(CallbackDataNames.HIDE_AUTO_AIM_MARKER, (vehicleID, clearVehicleID))
        super(VehicleMarkerTargetPluginReplayRecording, self)._hideVehicleMarker(vehicleID, clearVehicleID)


_EQUIPMENT_DEFAULT_INTERVAL = 1.0
_EQUIPMENT_DELAY_FORMAT = '{0:.0f}'

class EquipmentsMarkerPlugin(MarkerPlugin):
    __slots__ = ('__callbackIDs', '__finishTime', '__defaultPostfix')

    def __init__(self, parentObj):
        super(EquipmentsMarkerPlugin, self).__init__(parentObj)
        self.__callbackIDs = {}
        self.__finishTime = {}
        self.__defaultPostfix = i18n.makeString(INGAME_GUI.FORTCONSUMABLES_TIMER_POSTFIX)

    def start(self):
        super(EquipmentsMarkerPlugin, self).init()
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentMarkerShown += self.__onEquipmentMarkerShown
        return

    def stop(self):
        while self.__callbackIDs:
            _, callbackID = self.__callbackIDs.popitem()
            if callbackID is not None:
                BigWorld.cancelCallback(callbackID)

        ctrl = self.sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentMarkerShown -= self.__onEquipmentMarkerShown
        super(EquipmentsMarkerPlugin, self).stop()
        return

    def __onEquipmentMarkerShown(self, item, position, _, delay):
        markerID = self._createMarkerWithPosition(settings.MARKER_SYMBOL_NAME.EQUIPMENT_MARKER, position + settings.MARKER_POSITION_ADJUSTMENT)
        self._invokeMarker(markerID, 'init', item.getMarker(), _EQUIPMENT_DELAY_FORMAT.format(round(delay)), self.__defaultPostfix)
        self.__setCallback(markerID, round(BigWorld.serverTime() + delay))

    def __setCallback(self, markerID, finishTime, interval=_EQUIPMENT_DEFAULT_INTERVAL):
        self.__callbackIDs[markerID] = BigWorld.callback(interval, partial(self.__handleCallback, markerID, finishTime))

    def __clearCallback(self, markerID):
        callbackID = self.__callbackIDs.pop(markerID, None)
        if callbackID is not None:
            BigWorld.cancelCallback(callbackID)
        return

    def __handleCallback(self, markerID, finishTime):
        self.__callbackIDs[markerID] = None
        delay = round(finishTime - BigWorld.serverTime())
        if delay <= 0:
            self._destroyMarker(markerID)
        else:
            self._invokeMarker(markerID, 'updateTimer', _EQUIPMENT_DELAY_FORMAT.format(abs(delay)))
            self.__setCallback(markerID, finishTime)
        return


_AREA_STATIC_MARKER_DEFAULT_CREATED_TIME = 3.0

class AreaStaticMarkerPlugin(MarkerPlugin, ChatCommunicationComponent):
    _MIN_Y_OFFSET = 1.2
    _MAX_Y_OFFSET = 3.0
    _DISTANCE_FOR_MIN_Y_OFFSET = 400
    _MAX_Y_BOOST = 1.4
    _BOOST_START = 120
    __slots__ = ('_markers', '__defaultPostfix', '__clazz', '__prevPeriod')

    def __init__(self, parentObj, clazz=LocationMarker):
        super(AreaStaticMarkerPlugin, self).__init__(parentObj)
        self._markers = {}
        self.__defaultPostfix = 0
        self.__clazz = clazz
        self.__prevPeriod = None
        return

    def start(self):
        super(AreaStaticMarkerPlugin, self).start()
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onStaticMarkerAdded += self.__onStaticMarkerAdded
            ctrl.onStaticMarkerRemoved += self.__onStaticMarkerRemoved
            ctrl.setInFocusForPlayer += self.__setInFocusForPlayer
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        self.__checkMarkers()
        return

    def stop(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onStaticMarkerAdded -= self.__onStaticMarkerAdded
            ctrl.onStaticMarkerRemoved -= self.__onStaticMarkerRemoved
            ctrl.setInFocusForPlayer -= self.__setInFocusForPlayer
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        for markerKey in self._markers.iterkeys():
            self._destroyMarker(self._markers[markerKey].getMarkerID())

        self._markers.clear()
        super(AreaStaticMarkerPlugin, self).stop()
        return

    def getMarkerType(self):
        return MarkerType.LOCATION_MARKER_TYPE

    def getTargetIDFromMarkerID(self, markerID):
        for targetID in self._markers:
            if self._markers[targetID].getMarkerID() == markerID:
                return targetID

        return INVALID_MARKER_ID

    def getMarkerSubtype(self, targetID):
        if targetID not in self._markers:
            return INVALID_MARKER_SUBTYPE
        markerSubtypeName = self._markers[targetID].getMarkerSubtype()
        if markerSubtypeName not in COMMAND_NAME_TO_LOCATION_MARKER_SUBTYPE.values():
            _logger.warning("Marker subtype name '%s' is not supported.", markerSubtypeName)
            return INVALID_MARKER_SUBTYPE
        return markerSubtypeName

    def _getMarkerFromTargetID(self, targetID, markerType):
        return None if targetID not in self._markers or markerType != self.getMarkerType() else self._markers[targetID]

    def __onVehicleStateUpdated(self, state, value):
        if state in (VEHICLE_VIEW_STATE.DESTROYED, VEHICLE_VIEW_STATE.CREW_DEACTIVATED):
            for marker in self._markers.values():
                self._setMarkerBoundEnabled(marker.getMarkerID(), False)

        elif state in (VEHICLE_VIEW_STATE.SWITCHING, VEHICLE_VIEW_STATE.RESPAWNING):
            if not self.sessionProvider.getCtx().isPlayerObserver() and avatar_getter.isVehicleAlive():
                for marker in self._markers.values():
                    self._setMarkerBoundEnabled(marker.getMarkerID(), True)

    def __checkMarkers(self):
        _logger.debug('__checkPrebattleMarkers')
        for key in g_locationPointManager.markedAreas:
            locationPoint = g_locationPointManager.markedAreas[key]
            _logger.debug('created a marker')
            self.__onStaticMarkerAdded(locationPoint.targetID, locationPoint.creatorID, locationPoint.position, locationPoint.markerSubType, locationPoint.markerText, locationPoint.replyCount, False)

    def __onStaticMarkerAdded(self, areaID, creatorID, position, locationMarkerSubtype, markerText='', numberOfReplies=0, isTargetForPlayer=False):
        if locationMarkerSubtype not in _LOCATION_SUBTYPE_TO_FLASH_SYMBOL_NAME:
            return
        if areaID in self._markers:
            _logger.debug('__onStaticMarkerAdded should not be called 2 times with the same areaID')
            return
        markerID = self._createMarkerWithPosition(_LOCATION_SUBTYPE_TO_FLASH_SYMBOL_NAME[locationMarkerSubtype], position)
        marker = self.__clazz(markerID, position, True, locationMarkerSubtype)
        self._setMarkerRenderInfo(markerID, _STATIC_MARKER_MIN_SCALE, _STATIC_MARKER_BOUNDS, _INNER_STATIC_MARKER_BOUNDS, _STATIC_MARKER_CULL_DISTANCE, _STATIC_MARKER_BOUNDS_MIN_SCALE)
        self._setMarkerLocationOffset(markerID, self._MIN_Y_OFFSET, self._MAX_Y_OFFSET, self._DISTANCE_FOR_MIN_Y_OFFSET, self._MAX_Y_BOOST, self._BOOST_START)
        self._markers[areaID] = marker
        marker.setState(ReplyStateForMarker.CREATE_STATE)
        if locationMarkerSubtype == LocationMarkerSubType.PREBATTLE_WAYPOINT_SUBTYPE:
            currentPeriod = avatar_getter.getArena().period
            if currentPeriod not in [constants.ARENA_PERIOD.BATTLE, constants.ARENA_PERIOD.AFTERBATTLE]:
                self._invokeMarker(markerID, 'alwaysShowCreatorName', True)
            else:
                self._invokeMarker(markerID, 'alwaysShowCreatorName', False)
        if locationMarkerSubtype == LocationMarkerSubType.GOING_TO_MARKER_SUBTYPE:
            marker.setIsSticky(isTargetForPlayer)
            self._setMarkerRepliesAndCheckState(marker, 1, isTargetForPlayer)
        else:
            self._setActiveState(marker, ReplyStateForMarker.CREATE_STATE)
        self._invokeMarker(markerID, 'setCreator', markerText)
        if self.sessionProvider.getCtx().isPlayerObserver() or not avatar_getter.isVehicleAlive():
            self._setMarkerBoundEnabled(marker.getMarkerID(), False)

    def __onStaticMarkerRemoved(self, targetID):
        if targetID in self._markers:
            marker = self._markers[targetID]
            markerID = marker.getMarkerID()
            self._markers.pop(targetID, None)
            marker.setReplyCount(0)
            marker.setState(0)
            self._destroyMarker(markerID)
        return

    def __onArenaPeriodChange(self, period, endTime, *_):
        if period == constants.ARENA_PERIOD.BATTLE and period != self.__prevPeriod:
            self.__onArenaPeriodBattleState()
            self.__prevPeriod = period

    def __onArenaPeriodBattleState(self):
        if self.parentObj is None:
            return
        else:
            advChatCmp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'advancedChatComponent', None)
            if advChatCmp is None:
                return
            for targetID in self._markers:
                marker = self._markers[targetID]
                replyCount = marker.getReplyCount()
                if marker.getMarkerSubtype() == LocationMarkerSubType.PREBATTLE_WAYPOINT_SUBTYPE and replyCount > 0:
                    self._invokeMarker(marker.getMarkerID(), 'alwaysShowCreatorName', False)

            return

    def __setInFocusForPlayer(self, oldTargetID, oldTargetType, newTargetID, newTargetType, oneShot):
        if oldTargetType == self.getMarkerType() and oldTargetID in self._markers:
            self.__makeMarkerSticky(oldTargetID, False)
        if newTargetType == self.getMarkerType() and newTargetID in self._markers:
            newMarker = self._markers[newTargetID]
            pos = newMarker.getPosition()
            if pos is not None and newMarker.getMarkerSubtype() in [LocationMarkerSubType.SPG_AIM_AREA_SUBTYPE, LocationMarkerSubType.ATTENTION_TO_MARKER_SUBTYPE]:
                if pos.distTo(avatar_getter.getOwnVehiclePosition()) > MAX_DISTANCE_TEMP_STICKY:
                    return
            self.__makeMarkerSticky(newTargetID, True)
        return

    def __makeMarkerSticky(self, targetID, setSticky):
        marker = self._markers[targetID]
        markerID = marker.getMarkerID()
        self._setMarkerSticky(markerID, setSticky)
        marker.setIsSticky(setSticky)
        self._checkNextState(marker)


class TeamsOrControlsPointsPlugin(MarkerPlugin, ChatCommunicationComponent):
    __slots__ = ('__personalTeam', '_markers', '__clazz')

    def __init__(self, parentObj, clazz=BaseMarker):
        super(TeamsOrControlsPointsPlugin, self).__init__(parentObj)
        self.__personalTeam = 0
        self.__clazz = clazz
        self._markers = {}

    def start(self):
        super(TeamsOrControlsPointsPlugin, self).start()
        g_playerEvents.onTeamChanged += self.__onTeamChanged
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onActionAddedToMarkerReceived += self.__onActionAddedToMarkerReceived
            ctrl.setInFocusForPlayer += self.__setInFocusForPlayer
            ctrl.onRemoveCommandReceived += self.__onRemoveCommandReceived
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        self._restart()
        return

    def stop(self):
        g_playerEvents.onTeamChanged -= self.__onTeamChanged
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onActionAddedToMarkerReceived -= self.__onActionAddedToMarkerReceived
            ctrl.setInFocusForPlayer -= self.__setInFocusForPlayer
            ctrl.onRemoveCommandReceived -= self.__onRemoveCommandReceived
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        self.__removeExistingMarkers()
        super(TeamsOrControlsPointsPlugin, self).stop()
        return

    def __removeExistingMarkers(self):
        for markerKey in self._markers.iterkeys():
            self._destroyMarker(self._markers[markerKey].getMarkerID())

        self._markers.clear()

    def getMarkerType(self):
        return MarkerType.BASE_MARKER_TYPE

    def getTargetIDFromMarkerID(self, markerID):
        for baseID, marker in self._markers.iteritems():
            if markerID == marker.getMarkerID():
                return baseID

        return INVALID_MARKER_ID

    def getMarkerSubtype(self, targetID):
        foundMarker = self._markers.get(targetID, None)
        if foundMarker is None:
            return INVALID_MARKER_SUBTYPE
        else:
            return DefaultMarkerSubType.ALLY_MARKER_SUBTYPE if foundMarker.getOwningTeam() == 'ally' else DefaultMarkerSubType.ENEMY_MARKER_SUBTYPE

    def _restart(self):
        self.__personalTeam = self.sessionProvider.getArenaDP().getNumberOfTeam()
        self.__removeExistingMarkers()
        self.__addTeamBasePositions()
        self.__addControlPoints()

    def _getMarkerFromTargetID(self, targetID, markerType):
        return None if targetID not in self._markers or markerType != self.getMarkerType() else self._markers[targetID]

    def _getTerrainHeightAt(self, spaceID, x, z):
        collisionWithTerrain = BigWorld.wg_collideSegment(spaceID, Math.Vector3(x, 1000.0, z), Math.Vector3(x, -1000.0, z), 128)
        return collisionWithTerrain.closestPoint if collisionWithTerrain is not None else (x, 0, z)

    def __addBaseOrControlPointMarker(self, owner, position, baseOrControlPointID):
        position = self._getTerrainHeightAt(BigWorld.player().spaceID, position[0], position[2])
        truePosition = position + settings.MARKER_POSITION_ADJUSTMENT
        markerID = self._createMarkerWithPosition(settings.MARKER_SYMBOL_NAME.SECTOR_BASE_TYPE, truePosition)
        if markerID < 0:
            return
        self._invokeMarker(markerID, 'setOwningTeam', owner)
        self._invokeMarker(markerID, 'setIdentifier', RANDOM_BATTLE_BASE_ID)
        self._invokeMarker(markerID, 'setActive', True)
        self._setMarkerRenderInfo(markerID, _BASE_MARKER_MIN_SCALE, _BASE_MARKER_BOUNDS, _INNER_BASE_MARKER_BOUNDS, _STATIC_MARKER_CULL_DISTANCE, _BASE_MARKER_BOUND_MIN_SCALE)
        marker = self.__clazz(markerID, True, owner)
        self._markers[baseOrControlPointID] = marker
        marker.setState(ReplyStateForMarker.NO_ACTION)
        self._setActiveState(marker, marker.getState())
        self._setMarkerSticky(markerID, False)
        self.__addActiveCommandsOnMarker(baseOrControlPointID)

    def __addTeamBasePositions(self):
        positions = self.sessionProvider.arenaVisitor.type.getTeamBasePositionsIterator()
        for team, position, number in positions:
            if team == self.__personalTeam:
                owner = 'ally'
            else:
                owner = 'enemy'
            baseID = getUniqueTeamOrControlPointID(team, number)
            self.__addBaseOrControlPointMarker(owner, position, baseID)

    def __addControlPoints(self):
        points = self.sessionProvider.arenaVisitor.type.getControlPointsIterator()
        for position, number in points:
            baseID = getUniqueTeamOrControlPointID(0, number)
            self.__addBaseOrControlPointMarker('neutral', position, baseID)

    def __onTeamChanged(self, teamID):
        self._restart()

    def __onActionAddedToMarkerReceived(self, senderID, commandID, markerType, uniqueBaseID):
        if markerType != self.getMarkerType() or uniqueBaseID not in self._markers:
            return
        marker = self._markers[uniqueBaseID]
        marker.setState(ReplyStateForMarker.CREATE_STATE)
        marker.setActiveCommandID(commandID)
        if _ACTIONS.battleChatCommandFromActionID(commandID).name in AUTOCOMMIT_COMMAND_NAMES:
            isPlayerSender = senderID == avatar_getter.getPlayerVehicleID()
            marker.setIsSticky(isPlayerSender)
            self._setMarkerRepliesAndCheckState(marker, 1, isPlayerSender)
        else:
            self._setActiveState(marker, ReplyStateForMarker.CREATE_STATE)
        if not avatar_getter.isVehicleAlive() and marker.getBoundCheckEnabled():
            marker.setBoundCheckEnabled(False)
            self._setMarkerBoundEnabled(marker.getMarkerID(), False)

    def __addActiveCommandsOnMarker(self, markerId):
        advChatCmp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'advancedChatComponent', None)
        if advChatCmp is None:
            return
        else:
            cmdData = advChatCmp.getCommandDataForTargetIDAndMarkerType(markerId, MarkerType.BASE_MARKER_TYPE)
            if cmdData:
                marker = self._markers[markerId]
                isPlayerSender = avatar_getter.getPlayerVehicleID() in cmdData.owners
                countNumber = len(cmdData.owners)
                marker.setIsSticky(isPlayerSender)
                self._setMarkerRepliesAndCheckState(marker, countNumber, isPlayerSender)
            return

    def __onRemoveCommandReceived(self, removeID, markerType):
        if markerType != MarkerType.BASE_MARKER_TYPE or removeID not in self._markers:
            return
        marker = self._markers[removeID]
        marker.setActiveCommandID(INVALID_COMMAND_ID)
        if marker.getReplyCount() != 0:
            marker.setIsRepliedByPlayer(False)
            self._setMarkerReplied(marker, False)
            self._setMarkerReplyCount(marker, 0)
        self._checkNextState(marker)
        if marker.getState() == ReplyStateForMarker.NO_ACTION and not marker.getBoundCheckEnabled():
            marker.setBoundCheckEnabled(True)
            self._setMarkerBoundEnabled(marker.getMarkerID(), True)

    def __onVehicleStateUpdated(self, state, value):
        if state in (VEHICLE_VIEW_STATE.DESTROYED, VEHICLE_VIEW_STATE.CREW_DEACTIVATED):
            for marker in self._markers.values():
                if marker.getState() != ReplyStateForMarker.NO_ACTION:
                    self._setMarkerBoundEnabled(marker.getMarkerID(), False)

        elif state in (VEHICLE_VIEW_STATE.SWITCHING, VEHICLE_VIEW_STATE.RESPAWNING):
            if not self.sessionProvider.getCtx().isPlayerObserver() and avatar_getter.isVehicleAlive():
                for marker in self._markers.values():
                    if not marker.getBoundCheckEnabled():
                        self._setMarkerBoundEnabled(marker.getMarkerID(), True)

    def __setInFocusForPlayer(self, oldTargetID, oldTargetType, newTargetID, newTargetType, oneShot):
        if oldTargetType == self.getMarkerType() and oldTargetID in self._markers:
            self.__makeMarkerSticky(oldTargetID, False)
        if newTargetType == self.getMarkerType() and newTargetID in self._markers:
            self.__makeMarkerSticky(newTargetID, True)

    def __makeMarkerSticky(self, targetID, setSticky):
        marker = self._markers[targetID]
        markerID = marker.getMarkerID()
        self._setMarkerSticky(markerID, setSticky)
        marker.setIsSticky(setSticky)
        self._checkNextState(marker)


class BaseAreaMarkerPlugin(MarkerPlugin):
    __slots__ = ('__markers',)

    def __init__(self, parentObj):
        super(BaseAreaMarkerPlugin, self).__init__(parentObj)
        self.__markers = {}

    def start(self):
        self.__markers = {}
        super(BaseAreaMarkerPlugin, self).start()

    def stop(self):
        self.__markers = {}
        super(BaseAreaMarkerPlugin, self).stop()

    def createMarker(self, uniqueID, matrixProvider, active):
        if uniqueID in self.__markers:
            return False
        markerID = self._createMarkerWithMatrix(settings.MARKER_SYMBOL_NAME.STATIC_OBJECT_MARKER, matrixProvider, active=active)
        self.__markers[uniqueID] = markerID
        return True

    def deleteMarker(self, uniqueID):
        markerID = self.__markers.pop(uniqueID, None)
        if markerID is not None:
            self._destroyMarker(markerID)
            return True
        else:
            return False

    def setupMarker(self, uniqueID, shape, minDistance, maxDistance, distance, distanceFieldColor):
        if uniqueID not in self.__markers:
            return
        self._invokeMarker(self.__markers[uniqueID], 'init', shape, minDistance, maxDistance, distance, backport.text(R.strings.ingame_gui.marker.meters()), distanceFieldColor)

    def markerSetDistance(self, uniqueID, distance):
        if uniqueID not in self.__markers:
            return
        self._invokeMarker(self.__markers[uniqueID], 'setDistance', distance)

    def setMarkerMatrix(self, uniqueID, matrix):
        markerID = self.__markers.pop(uniqueID, None)
        if markerID is None:
            return
        else:
            self._parentObj.setMarkerMatrix(markerID, matrix)
            return


class AreaMarkerPlugin(BaseAreaMarkerPlugin):
    pass
