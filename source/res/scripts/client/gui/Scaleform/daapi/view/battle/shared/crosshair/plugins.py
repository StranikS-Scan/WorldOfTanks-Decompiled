# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/crosshair/plugins.py
import math
from collections import defaultdict
from functools import partial
import BigWorld
import CommandMapping
from AvatarInputHandler import gun_marker_ctrl
from account_helpers.settings_core.settings_constants import GRAPHICS, AIM
from constants import VEHICLE_SIEGE_STATE as _SIEGE_STATE
from account_helpers.AccountSettings import AccountSettings, TRAJECTORY_VIEW_HINT_COUNTER
from debug_utils import LOG_DEBUG, LOG_WARNING
from gui import makeHtmlString
from gui.Scaleform.daapi.view.battle.shared.crosshair.settings import SHOT_RESULT_TO_ALT_COLOR
from gui.Scaleform.daapi.view.battle.shared.crosshair.settings import SHOT_RESULT_TO_DEFAULT_COLOR
from gui.Scaleform.daapi.view.battle.shared.formatters import getHealthPercent
from gui.Scaleform.genConsts.CROSSHAIR_CONSTANTS import CROSSHAIR_CONSTANTS
from gui.Scaleform.genConsts.GUN_MARKER_VIEW_CONSTANTS import GUN_MARKER_VIEW_CONSTANTS as _VIEW_CONSTANTS
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID, CROSSHAIR_VIEW_ID, SHELL_QUANTITY_UNKNOWN
from gui.battle_control.battle_constants import GUN_RELOADING_VALUE_TYPE
from gui.battle_control.battle_constants import SHELL_SET_RESULT, VEHICLE_VIEW_STATE, NET_TYPE_OVERRIDE
from gui.battle_control.battle_constants import STRATEGIC_CAMERA_ID
from gui.battle_control.controllers import crosshair_proxy
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from gui.shared.utils.TimeInterval import TimeInterval
from gui.shared.utils.plugins import IPlugin
from helpers import dependency, i18n
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IBootcampController
from PlayerEvents import g_playerEvents
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.shared.utils.key_mapping import getReadableKey
from gui import GUI_SETTINGS
_SETTINGS_KEY_TO_VIEW_ID = {AIM.ARCADE: CROSSHAIR_VIEW_ID.ARCADE,
 AIM.SNIPER: CROSSHAIR_VIEW_ID.SNIPER}
_SETTINGS_KEYS = set(_SETTINGS_KEY_TO_VIEW_ID.keys())
_SETTINGS_VIEWS = set(_SETTINGS_KEY_TO_VIEW_ID.values())
_TARGET_UPDATE_INTERVAL = 0.2
_TRAJECTORY_VIEW_HINT_POSITION = (0, 120)
_TRAJECTORY_VIEW_HINT_CHECK_STATES = (VEHICLE_VIEW_STATE.SHOW_DESTROY_TIMER,
 VEHICLE_VIEW_STATE.SHOW_DEATHZONE_TIMER,
 VEHICLE_VIEW_STATE.HIDE_DESTROY_TIMER,
 VEHICLE_VIEW_STATE.HIDE_DEATHZONE_TIMER,
 VEHICLE_VIEW_STATE.FIRE,
 VEHICLE_VIEW_STATE.STUN)

def createPlugins():
    return {'core': CorePlugin,
     'settings': SettingsPlugin,
     'events': EventBusPlugin,
     'ammo': AmmoPlugin,
     'vehicleState': VehicleStatePlugin,
     'targetDistance': TargetDistancePlugin,
     'gunMarkerDistance': GunMarkerDistancePlugin,
     'gunMarkersInvalidate': GunMarkersInvalidatePlugin,
     'shotResultIndicator': ShotResultIndicatorPlugin,
     'siegeMode': SiegeModePlugin,
     'trajectoryViewHint': TrajectoryViewHintPlugin,
     'shotDone': ShotDonePlugin}


def chooseSetting(viewID):
    return viewID if viewID in _SETTINGS_VIEWS else _SETTINGS_KEY_TO_VIEW_ID[AIM.ARCADE]


def _makeSettingsVO(settingsCore, *keys):
    getter = settingsCore.getSetting
    data = {}
    for mode in keys:
        settings = getter(mode)
        if settings is not None:
            data[_SETTINGS_KEY_TO_VIEW_ID[mode]] = {'centerAlphaValue': settings['centralTag'] / 100.0,
             'centerType': settings['centralTagType'],
             'netAlphaValue': settings['net'] / 100.0,
             'netType': settings['netType'],
             'reloaderAlphaValue': settings['reloader'] / 100.0,
             'conditionAlphaValue': settings['condition'] / 100.0,
             'cassetteAlphaValue': settings['cassette'] / 100.0,
             'reloaderTimerAlphaValue': settings['reloaderTimer'] / 100.0,
             'zoomIndicatorAlphaValue': settings['zoomIndicator'] / 100.0,
             'gunTagAlpha': settings['gunTag'] / 100.0,
             'gunTagType': settings['gunTagType'],
             'mixingAlpha': settings['mixing'] / 100.0,
             'mixingType': settings['mixingType']}

    return data


def _createAmmoSettings(gunSettings):
    clip = gunSettings.clip
    burst = gunSettings.burst.size
    if clip.size > 1:
        state = _CassetteSettings(clip, burst, gunSettings.hasAutoReload())
    else:
        state = _AmmoSettings(clip, burst)
    return state


class _AmmoSettings(object):

    def __init__(self, clip, burst, hasAutoReload=False):
        super(_AmmoSettings, self).__init__()
        self._clip = clip
        self._burst = burst
        self.__hasAutoReload = hasAutoReload

    @property
    def hasAutoReload(self):
        return self.__hasAutoReload

    def getClipCapacity(self):
        return self._clip.size

    def getClipInterval(self):
        return self._clip.interval

    def getBurstSize(self):
        return self._burst

    def getState(self, quantity, quantityInClip):
        return (quantity < 3, 'normal')


class _CassetteSettings(_AmmoSettings):

    def getState(self, quantity, quantityInClip):
        isLow, state = super(_CassetteSettings, self).getState(quantity, quantityInClip)
        isLow |= quantity <= self.getClipCapacity()
        if self._burst > 1:
            total = math.ceil(self.getClipCapacity() / float(self._burst))
            current = math.ceil(quantityInClip / float(self._burst))
        else:
            total = self.getClipCapacity()
            current = quantityInClip
        if current <= 0.5 * total:
            state = 'critical' if current == 1 else 'warning'
        return (isLow, state)


class CrosshairPlugin(IPlugin):
    __slots__ = ('__weakref__',)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)


class CorePlugin(CrosshairPlugin):
    __slots__ = ()

    def start(self):
        ctrl = self.sessionProvider.shared.crosshair
        self.__setup(ctrl)
        ctrl.onCrosshairViewChanged += self.__onCrosshairViewChanged
        ctrl.onCrosshairScaleChanged += self.__onCrosshairScaleChanged
        ctrl.onCrosshairSizeChanged += self.__onCrosshairSizeChanged
        ctrl.onCrosshairPositionChanged += self.__onCrosshairPositionChanged
        ctrl.onCrosshairZoomFactorChanged += self.__onCrosshairZoomFactorChanged

    def stop(self):
        ctrl = self.sessionProvider.shared.crosshair
        if ctrl is not None:
            ctrl.onCrosshairViewChanged -= self.__onCrosshairViewChanged
            ctrl.onCrosshairScaleChanged -= self.__onCrosshairScaleChanged
            ctrl.onCrosshairSizeChanged -= self.__onCrosshairSizeChanged
            ctrl.onCrosshairPositionChanged -= self.__onCrosshairPositionChanged
            ctrl.onCrosshairZoomFactorChanged -= self.__onCrosshairZoomFactorChanged
        return

    def __setup(self, ctrl):
        scale = ctrl.getScaleFactor()
        if scale > 1.0:
            self.__onCrosshairScaleChanged(scale)
        self.__onCrosshairViewChanged(ctrl.getViewID())
        self.__onCrosshairSizeChanged(*ctrl.getSize())
        self.__onCrosshairPositionChanged(*ctrl.getPosition())
        self.__onCrosshairZoomFactorChanged(ctrl.getZoomFactor())

    def __onCrosshairViewChanged(self, viewID):
        self._parentObj.setViewID(viewID)

    def __onCrosshairScaleChanged(self, scale):
        self._parentObj.setScale(scale)

    def __onCrosshairSizeChanged(self, width, height):
        self._parentObj.setSize(width, height)

    def __onCrosshairPositionChanged(self, x, y):
        self._parentObj.setPosition(x, y)

    def __onCrosshairZoomFactorChanged(self, zoomFactor):
        self._parentObj.setZoom(zoomFactor)


class SettingsPlugin(CrosshairPlugin):
    __slots__ = ()

    def start(self):
        self._parentObj.setSettings(_makeSettingsVO(self.settingsCore, *_SETTINGS_KEYS))
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged

    def stop(self):
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged

    def __onSettingsChanged(self, diff):
        changed = set(diff.keys()) & _SETTINGS_KEYS
        if changed:
            self._parentObj.setSettings(_makeSettingsVO(self.settingsCore, *changed))


class EventBusPlugin(CrosshairPlugin):
    __slots__ = ()

    def start(self):
        add = g_eventBus.addListener
        add(GameEvent.GUI_VISIBILITY, self.__handleGUIVisibility, scope=EVENT_BUS_SCOPE.BATTLE)
        add(GameEvent.CROSSHAIR_VISIBILITY, self.__handleCrosshairVisibility, scope=EVENT_BUS_SCOPE.BATTLE)
        add(GameEvent.CROSSHAIR_VIEW, self.__handleCrosshairView, scope=EVENT_BUS_SCOPE.BATTLE)

    def stop(self):
        remove = g_eventBus.removeListener
        remove(GameEvent.GUI_VISIBILITY, self.__handleGUIVisibility, scope=EVENT_BUS_SCOPE.BATTLE)
        remove(GameEvent.CROSSHAIR_VISIBILITY, self.__handleCrosshairVisibility, scope=EVENT_BUS_SCOPE.BATTLE)
        remove(GameEvent.CROSSHAIR_VIEW, self.__handleCrosshairView, scope=EVENT_BUS_SCOPE.BATTLE)

    def __handleGUIVisibility(self, event):
        self._parentObj.setVisible(event.ctx['visible'])

    def __handleCrosshairVisibility(self, _):
        self._parentObj.setVisible(not self._parentObj.isVisible())

    def __handleCrosshairView(self, event):
        self._parentObj.setViewID(crosshair_proxy.getCrosshairViewIDByCtrlMode(event.ctx['ctrlMode']))


class AmmoPlugin(CrosshairPlugin):
    __slots__ = ('__guiSettings', '__burstSize', '__shellsInClip', '__autoReloadCallbackID')
    bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self, parentObj):
        super(AmmoPlugin, self).__init__(parentObj)
        self.__guiSettings = None
        self.__shellsInClip = 0
        self.__autoReloadCallbackID = None
        return

    def start(self):
        ctrl = self.sessionProvider.shared.ammo
        self.__setup(ctrl, self.sessionProvider.isReplayPlaying)
        ctrl.onGunSettingsSet += self.__onGunSettingsSet
        ctrl.onGunReloadTimeSet += self.__onGunReloadTimeSet
        ctrl.onGunAutoReloadTimeSet += self.__onGunAutoReloadTimeSet
        ctrl.onShellsUpdated += self.__onShellsUpdated
        ctrl.onCurrentShellChanged += self.__onCurrentShellChanged

    def stop(self):
        ctrl = self.sessionProvider.shared.ammo
        if ctrl is not None:
            ctrl.onGunSettingsSet -= self.__onGunSettingsSet
            ctrl.onGunAutoReloadTimeSet -= self.__onGunAutoReloadTimeSet
            ctrl.onGunReloadTimeSet -= self.__onGunReloadTimeSet
            ctrl.onShellsUpdated -= self.__onShellsUpdated
            ctrl.onCurrentShellChanged -= self.__onCurrentShellChanged
        return

    def fini(self):
        if self.__autoReloadCallbackID:
            BigWorld.cancelCallback(self.__autoReloadCallbackID)
        super(AmmoPlugin, self).fini()

    def __setup(self, ctrl, isReplayPlaying=False):
        if isReplayPlaying:
            self._parentObj.as_setReloadingCounterShownS(False)
        self.__setupGuiSettings(ctrl.getGunSettings())
        quantity, quantityInClip = ctrl.getCurrentShells()
        if (quantity, quantityInClip) != (SHELL_QUANTITY_UNKNOWN,) * 2:
            isLow, state = self.__guiSettings.getState(quantity, quantityInClip)
            self._parentObj.as_setAmmoStockS(quantity, quantityInClip, isLow, state, False)
        reloadingState = ctrl.getGunReloadingState()
        self.__setReloadingState(reloadingState)
        if self.__guiSettings.hasAutoReload:
            self._parentObj.as_autoloaderUpdateS(reloadingState.getActualValue(), reloadingState.getBaseValue(), isStun=False)
        if self.bootcampController.isInBootcamp():
            self._parentObj.as_setNetVisibleS(CROSSHAIR_CONSTANTS.VISIBLE_NET)

    def __setReloadingState(self, state):
        valueType = state.getValueType()
        if valueType == GUN_RELOADING_VALUE_TYPE.PERCENT:
            self._parentObj.as_setReloadingAsPercentS(state.getActualValue(), False)
        elif valueType == GUN_RELOADING_VALUE_TYPE.TIME:
            LOG_DEBUG('Set reloading state', state)
            self._parentObj.as_setReloadingS(state.getActualValue(), state.getBaseValue(), state.getTimePassed(), state.isReloading())

    def __onGunSettingsSet(self, gunSettings):
        self.__setupGuiSettings(gunSettings)

    def __setupGuiSettings(self, gunSettings):
        guiSettings = _createAmmoSettings(gunSettings)
        self.__guiSettings = guiSettings
        self._parentObj.as_setClipParamsS(guiSettings.getClipCapacity(), guiSettings.getBurstSize(), guiSettings.hasAutoReload)

    def __onGunReloadTimeSet(self, _, state):
        self.__setReloadingState(state)
        if self.__guiSettings.hasAutoReload:
            self.__notifyAutoLoader(state)

    def __notifyAutoLoader(self, state):
        if self.__shellsInClip == 0 and state.isReloading():
            baseTime = actualTime = self.__guiSettings.getClipInterval()
            self.__autoReloadCallbackID = BigWorld.callback(actualTime, partial(self.__autoReloadLastShotCallback, state.getBaseValue() - baseTime))
            self._parentObj.as_autoloaderUpdateS(0, 0)
        else:
            actualTime = state.getActualValue()
            baseTime = state.getBaseValue()
        self._parentObj.as_setAutoloaderReloadingS(actualTime, baseTime)

    def __autoReloadLastShotCallback(self, timeLeft):
        self._parentObj.as_autoloaderUpdateS(timeLeft, timeLeft)
        self.__autoReloadCallbackID = None
        return

    def __onGunAutoReloadTimeSet(self, timeLeft, baseTime, stunned):
        if self.__shellsInClip > 0 or timeLeft == 0:
            self._parentObj.as_autoloaderUpdateS(timeLeft, baseTime, isStun=stunned, isTimerOn=True)

    def __onShellsUpdated(self, _, quantity, quantityInClip, result):
        if not result & SHELL_SET_RESULT.CURRENT:
            return
        self.__shellsInClip = quantityInClip
        isLow, state = self.__guiSettings.getState(quantity, quantityInClip)
        self._parentObj.as_setAmmoStockS(quantity, quantityInClip, isLow, state, result & SHELL_SET_RESULT.CASSETTE_RELOAD > 0)

    def __onCurrentShellChanged(self, _):
        ctrl = self.sessionProvider.shared.ammo
        if ctrl is not None:
            quantity, quantityInClip = ctrl.getCurrentShells()
            isLow, state = self.__guiSettings.getState(quantity, quantityInClip)
            self._parentObj.as_setAmmoStockS(quantity, quantityInClip, isLow, state, False)
        return


class VehicleStatePlugin(CrosshairPlugin):
    __slots__ = ('__playerInfo', '__isPlayerVehicle', '__maxHealth', '__healthPercent')

    def __init__(self, parentObj):
        super(VehicleStatePlugin, self).__init__(parentObj)
        self.__playerInfo = None
        self.__isPlayerVehicle = False
        self.__maxHealth = 0
        self.__healthPercent = 0
        return

    def start(self):
        ctrl = self.sessionProvider.shared.vehicleState
        vehicle = ctrl.getControllingVehicle()
        if vehicle is not None:
            self.__setPlayerInfo(vehicle.id)
            self.__onVehicleControlling(vehicle)
        ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        ctrl.onVehicleControlling += self.__onVehicleControlling
        ctrl.onPostMortemSwitched += self.__onPostMortemSwitched
        ctrl = self.sessionProvider.shared.feedback
        ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        return

    def stop(self):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
            ctrl.onVehicleControlling -= self.__onVehicleControlling
            ctrl.onPostMortemSwitched -= self.__onPostMortemSwitched
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        return

    def __setHealth(self, health):
        if self.__maxHealth != 0 and self.__maxHealth >= health:
            self.__healthPercent = getHealthPercent(health, self.__maxHealth)

    def __setPlayerInfo(self, vehicleID):
        self.__playerInfo = self.sessionProvider.getCtx().getPlayerFullNameParts(vID=vehicleID, showVehShortName=True)

    def __updateVehicleInfo(self):
        if self._parentObj.getViewID() == CROSSHAIR_VIEW_ID.POSTMORTEM:
            if self.__isPlayerVehicle:
                ctx = {'type': self.__playerInfo.vehicleName}
                template = 'personal'
            else:
                ctx = {'name': self.__playerInfo.playerFullName,
                 'health': self.__healthPercent * 100}
                template = 'other'
            self._parentObj.as_updatePlayerInfoS(makeHtmlString('html_templates:battle/postmortemMessages', template, ctx=ctx))
        else:
            self._parentObj.as_setHealthS(self.__healthPercent)

    def __onVehicleControlling(self, vehicle):
        self.__maxHealth = vehicle.typeDescriptor.maxHealth
        self.__isPlayerVehicle = vehicle.isPlayerVehicle
        self.__setHealth(vehicle.health)
        self.__updateVehicleInfo()

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.HEALTH:
            self.__setHealth(value)
            self.__updateVehicleInfo()
        elif state == VEHICLE_VIEW_STATE.PLAYER_INFO:
            self.__setPlayerInfo(value)
        elif state == VEHICLE_VIEW_STATE.SWITCHING:
            self.__maxHealth = 0
            self.__healthPercent = 0

    def __onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self.__updateVehicleInfo()

    def __onVehicleFeedbackReceived(self, eventID, _, value):
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_HAS_AMMO and self._parentObj.getViewID() == CROSSHAIR_VIEW_ID.POSTMORTEM:
            self._parentObj.setHasAmmo(value)


class _DistancePlugin(CrosshairPlugin):
    __slots__ = ('_interval', '_distance')

    def __init__(self, parentObj):
        super(_DistancePlugin, self).__init__(parentObj)
        self._interval = None
        self._distance = 0
        return

    def start(self):
        self._interval = TimeInterval(_TARGET_UPDATE_INTERVAL, self, '_update')
        ctrl = self.sessionProvider.shared.crosshair
        ctrl.onCrosshairViewChanged += self._onCrosshairViewChanged

    def stop(self):
        if self._interval is not None:
            self._interval.stop()
            self._interval = None
        ctrl = self.sessionProvider.shared.crosshair
        if ctrl is not None:
            ctrl.onCrosshairViewChanged -= self._onCrosshairViewChanged
        return

    def _update(self):
        raise NotImplementedError

    def _onCrosshairViewChanged(self, viewID):
        raise NotImplementedError


class TargetDistancePlugin(_DistancePlugin):
    __slots__ = ('__trackID',)

    def __init__(self, parentObj):
        super(TargetDistancePlugin, self).__init__(parentObj)
        self.__trackID = 0

    def start(self):
        super(TargetDistancePlugin, self).start()
        ctrl = self.sessionProvider.shared.feedback
        ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived

    def stop(self):
        super(TargetDistancePlugin, self).stop()
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        return

    def _update(self):
        target = BigWorld.entity(self.__trackID)
        if target is not None:
            self.__updateDistance(target)
        else:
            self.__stopTrack()
        return

    def _onCrosshairViewChanged(self, viewID):
        if viewID not in (CROSSHAIR_VIEW_ID.ARCADE, CROSSHAIR_VIEW_ID.SNIPER):
            self.__stopTrack(immediate=True)

    def __startTrack(self, vehicleID):
        self._interval.stop()
        target = BigWorld.entity(vehicleID)
        if target is not None:
            self.__trackID = vehicleID
            self.__updateDistance(target)
            self._interval.start()
        return

    def __stopTrack(self, immediate=False):
        self._interval.stop()
        self._parentObj.clearDistance(immediate=immediate)
        self.__trackID = 0

    def __updateDistance(self, target):
        self._parentObj.setDistance(int(avatar_getter.getDistanceToTarget(target)))

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_IN_FOCUS:
            if self._parentObj.getViewID() not in (CROSSHAIR_VIEW_ID.ARCADE, CROSSHAIR_VIEW_ID.SNIPER):
                return
            if value:
                self.__startTrack(vehicleID)
            else:
                self.__stopTrack()


class GunMarkerDistancePlugin(_DistancePlugin):
    __slots__ = ()

    def _update(self):
        self.__updateDistance()

    def _onCrosshairViewChanged(self, viewID):
        self._interval.stop()
        if viewID == CROSSHAIR_VIEW_ID.STRATEGIC:
            self.__updateDistance()
            self._interval.start()
        else:
            self._parentObj.clearDistance(immediate=True)

    def __updateDistance(self):
        self._parentObj.setDistance(int(avatar_getter.getDistanceToGunMarker()))


class GunMarkersInvalidatePlugin(CrosshairPlugin):
    __slots__ = ()

    def start(self):
        ctrl = self.sessionProvider.shared.crosshair
        self.__setup(ctrl)
        ctrl.onGunMarkersSetChanged += self.__onGunMarkersSetChanged
        ctrl = self.sessionProvider.shared.vehicleState
        ctrl.onVehicleControlling += self.__onVehicleControlling
        ctrl = self.sessionProvider.shared.ammo
        if ctrl is not None:
            ctrl.onGunSettingsSet += self.__onGunSettingsSet
        return

    def stop(self):
        ctrl = self.sessionProvider.shared.crosshair
        if ctrl is not None:
            ctrl.onGunMarkersSetChanged -= self.__onGunMarkersSetChanged
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleControlling -= self.__onVehicleControlling
        ctrl = self.sessionProvider.shared.ammo
        if ctrl is not None:
            ctrl.onGunSettingsSet -= self.__onGunSettingsSet
        return

    def __getVehicleInfo(self):
        vehicle = BigWorld.player().getVehicleAttached()
        return self.sessionProvider.getArenaDP().getVehicleInfo(vehicle.id if vehicle is not None else None)

    def __setup(self, ctrl):
        markersInfo = ctrl.getGunMarkersSetInfo()
        vehicleInfo = self.__getVehicleInfo()
        self._parentObj.createGunMarkers(markersInfo, vehicleInfo)

    def __onGunMarkersSetChanged(self, markersInfo):
        self._parentObj.invalidateGunMarkers(markersInfo, self.__getVehicleInfo())

    def __onVehicleControlling(self, vehicle):
        repository = self.sessionProvider.shared
        if not repository.vehicleState.isInPostmortem and vehicle.isPlayerVehicle:
            self._parentObj.invalidateGunMarkers(repository.crosshair.getGunMarkersSetInfo(), self.__getVehicleInfo())

    def __onGunSettingsSet(self, _):
        ctrl = self.sessionProvider.shared.crosshair
        if ctrl is not None:
            markersInfo = ctrl.getGunMarkersSetInfo()
            vehicleInfo = self.__getVehicleInfo()
            self._parentObj.invalidateGunMarkers(markersInfo, vehicleInfo)
        return


class ShotResultIndicatorPlugin(CrosshairPlugin):
    __slots__ = ('__isEnabled', '__playerTeam', '__cache', '__colors', '__mapping', '__shotResultResolver')

    def __init__(self, parentObj):
        super(ShotResultIndicatorPlugin, self).__init__(parentObj)
        self.__isEnabled = False
        self.__mapping = defaultdict(lambda : False)
        self.__playerTeam = 0
        self.__cache = defaultdict(str)
        self.__colors = None
        self.__shotResultResolver = gun_marker_ctrl.createShotResultResolver()
        return

    def start(self):
        ctrl = self.sessionProvider.shared.crosshair
        ctrl.onCrosshairViewChanged += self.__onCrosshairViewChanged
        ctrl.onGunMarkerStateChanged += self.__onGunMarkerStateChanged
        g_playerEvents.onTeamChanged += self.__onTeamChanged
        self.__playerTeam = self.sessionProvider.getArenaDP().getNumberOfTeam()
        self.__setColors(self.settingsCore.getSetting(GRAPHICS.COLOR_BLIND))
        self.__setMapping(_SETTINGS_KEYS)
        self.__setEnabled(self._parentObj.getViewID())
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged

    def stop(self):
        ctrl = self.sessionProvider.shared.crosshair
        if ctrl is not None:
            ctrl.onCrosshairViewChanged -= self.__onCrosshairViewChanged
            ctrl.onGunMarkerStateChanged -= self.__onGunMarkerStateChanged
        g_playerEvents.onTeamChanged -= self.__onTeamChanged
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.__colors = None
        return

    def __setColors(self, isColorBlind):
        if isColorBlind:
            self.__colors = SHOT_RESULT_TO_ALT_COLOR
        else:
            self.__colors = SHOT_RESULT_TO_DEFAULT_COLOR

    def __setMapping(self, keys):
        getter = self.settingsCore.getSetting
        for key in keys:
            settings = getter(key)
            if 'gunTagType' in settings:
                value = settings['gunTagType'] in _VIEW_CONSTANTS.GUN_TAG_SHOT_RESULT_TYPES
                self.__mapping[_SETTINGS_KEY_TO_VIEW_ID[key]] = value

    def __updateColor(self, markerType, position, collision, direction):
        result = self.__shotResultResolver.getShotResult(position, collision, direction, excludeTeam=self.__playerTeam)
        if result in self.__colors:
            color = self.__colors[result]
            if self.__cache[markerType] != result and self._parentObj.setGunMarkerColor(markerType, color):
                self.__cache[markerType] = result
        else:
            LOG_WARNING('Color is not found by shot result', result)

    def __setEnabled(self, viewID):
        self.__isEnabled = self.__mapping[viewID]
        if self.__isEnabled:
            for markerType, shotResult in self.__cache.iteritems():
                self._parentObj.setGunMarkerColor(markerType, self.__colors[shotResult])

        else:
            self.__cache.clear()

    def __onGunMarkerStateChanged(self, markerType, position, direction, collision):
        if self.__isEnabled:
            self.__updateColor(markerType, position, collision, direction)

    def __onCrosshairViewChanged(self, viewID):
        self.__setEnabled(viewID)

    def __onSettingsChanged(self, diff):
        update = False
        if GRAPHICS.COLOR_BLIND in diff:
            self.__setColors(diff[GRAPHICS.COLOR_BLIND])
            update = True
        changed = set(diff.keys()) & _SETTINGS_KEYS
        if changed:
            self.__setMapping(changed)
            update = True
        if update:
            self.__setEnabled(self._parentObj.getViewID())

    def __onTeamChanged(self, teamID):
        self.__playerTeam = teamID


class SiegeModePlugin(CrosshairPlugin):
    __slots__ = ('__siegeState',)

    def __init__(self, parentObj):
        super(SiegeModePlugin, self).__init__(parentObj)
        self.__siegeState = _SIEGE_STATE.DISABLED

    def start(self):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            vStateCtrl.onVehicleControlling += self.__onVehicleControlling
            vehicle = vStateCtrl.getControllingVehicle()
            if vehicle is not None:
                self.__onVehicleControlling(vehicle)
        return

    def stop(self):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
            vStateCtrl.onVehicleControlling -= self.__onVehicleControlling
        return

    def __onVehicleControlling(self, vehicle):
        ctrl = self.sessionProvider.shared.vehicleState
        vTypeDesc = vehicle.typeDescriptor
        if ctrl.isInPostmortem:
            return
        else:
            if vTypeDesc.hasSiegeMode:
                value = ctrl.getStateValue(VEHICLE_VIEW_STATE.SIEGE_MODE)
                if value is not None:
                    self.__onVehicleStateUpdated(VEHICLE_VIEW_STATE.SIEGE_MODE, value)
                else:
                    self.__updateView()
            else:
                self.__siegeState = _SIEGE_STATE.DISABLED
                self.__updateView()
            return

    def __onVehicleStateUpdated(self, stateID, value):
        if stateID == VEHICLE_VIEW_STATE.SIEGE_MODE:
            siegeState, _ = value
            self.__siegeState = siegeState
            self.__updateView()

    def __updateView(self):
        if self.__siegeState == _SIEGE_STATE.ENABLED:
            self._parentObj.as_setNetTypeS(NET_TYPE_OVERRIDE.SIEGE_MODE)
        elif self.__siegeState == _SIEGE_STATE.DISABLED:
            self._parentObj.as_setNetTypeS(NET_TYPE_OVERRIDE.DISABLED)
        visibleMask = CROSSHAIR_CONSTANTS.VISIBLE_ALL if self.__siegeState not in _SIEGE_STATE.SWITCHING else 0
        self._parentObj.as_setNetVisibleS(visibleMask)


class TrajectoryViewHintPlugin(CrosshairPlugin):
    __slots__ = ('__hintsLeft', '__isHintShown', '__cachedHint', '__isObserver', '__isDestroyTimerDisplaying', '__isDeathZoneTimerDisplaying')

    def __init__(self, parentObj):
        super(TrajectoryViewHintPlugin, self).__init__(parentObj)
        self.__hintsLeft = 0
        self.__isHintShown = False
        self.__cachedHint = None
        self.__isDestroyTimerDisplaying = False
        self.__isDeathZoneTimerDisplaying = False
        self.__isObserver = False
        return

    def start(self):
        arenaDP = self.sessionProvider.getArenaDP()
        crosshairCtrl = self.sessionProvider.shared.crosshair
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        vInfo = arenaDP.getVehicleInfo()
        self.__isObserver = vInfo.isObserver()
        crosshairCtrl.onCrosshairViewChanged += self.__onCrosshairViewChanged
        crosshairCtrl.onStrategicCameraChanged += self.__onStrategicCameraChanged
        vehicleCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        CommandMapping.g_instance.onMappingChanged += self.__onMappingChanged
        self.__hintsLeft = AccountSettings.getSettings(TRAJECTORY_VIEW_HINT_COUNTER)
        self.__setup(crosshairCtrl, vehicleCtrl)

    def stop(self):
        ctrl = self.sessionProvider.shared.crosshair
        if ctrl is not None:
            ctrl.onCrosshairViewChanged -= self.__onCrosshairViewChanged
            ctrl.onStrategicCameraChanged -= self.__onStrategicCameraChanged
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        CommandMapping.g_instance.onMappingChanged -= self.__onMappingChanged
        if not self.sessionProvider.isReplayPlaying:
            AccountSettings.setSettings(TRAJECTORY_VIEW_HINT_COUNTER, self.__hintsLeft)
        self.__cachedHint = None
        return

    def __setup(self, crosshairCtrl, vehicleCtrl):
        self.__onCrosshairViewChanged(crosshairCtrl.getViewID())
        self.__onStrategicCameraChanged(crosshairCtrl.getStrategicCameraID())
        checkStatesIDs = (VEHICLE_VIEW_STATE.FIRE,
         VEHICLE_VIEW_STATE.SHOW_DESTROY_TIMER,
         VEHICLE_VIEW_STATE.SHOW_DEATHZONE_TIMER,
         VEHICLE_VIEW_STATE.STUN)
        for stateID in checkStatesIDs:
            stateValue = vehicleCtrl.getStateValue(stateID)
            if stateValue:
                self.__onVehicleStateUpdated(stateID, stateValue)

    def __onCrosshairViewChanged(self, viewID):
        if viewID == CROSSHAIR_VIEW_ID.STRATEGIC and self.__hintsLeft:
            self.__showHint()
        elif self.__isHintShown:
            self.__hideHint()

    def __onStrategicCameraChanged(self, cameraID):
        if cameraID == STRATEGIC_CAMERA_ID.TRAJECTORY:
            self.__hintsLeft = max(0, self.__hintsLeft - 1)
        if not self.__hintsLeft and self.__isHintShown:
            self.__hideHint()

    def __onVehicleStateUpdated(self, stateID, stateValue):
        if self.__isHintShown or self.__hintsLeft and stateID in _TRAJECTORY_VIEW_HINT_CHECK_STATES:
            if stateID == VEHICLE_VIEW_STATE.SHOW_DESTROY_TIMER:
                self.__isDestroyTimerDisplaying = True
            elif stateID == VEHICLE_VIEW_STATE.HIDE_DESTROY_TIMER:
                self.__isDestroyTimerDisplaying = False
            elif stateID == VEHICLE_VIEW_STATE.SHOW_DEATHZONE_TIMER:
                self.__isDeathZoneTimerDisplaying = True
            elif stateID == VEHICLE_VIEW_STATE.HIDE_DEATHZONE_TIMER:
                self.__isDeathZoneTimerDisplaying = False
            if self.__isHintShown and self.__isThereAnyIndicators():
                self.__hideHint()
            else:
                ctrl = self.sessionProvider.shared.crosshair
                if ctrl is not None:
                    self.__onCrosshairViewChanged(ctrl.getViewID())
        return

    def __isThereAnyIndicators(self):
        if self.__isDestroyTimerDisplaying or self.__isDeathZoneTimerDisplaying:
            result = True
        else:
            ctrl = self.sessionProvider.shared.vehicleState
            result = ctrl is not None and ctrl.getStateValue(VEHICLE_VIEW_STATE.STUN) or ctrl.getStateValue(VEHICLE_VIEW_STATE.FIRE)
        return result

    def __onMappingChanged(self, *args):
        if self.__isHintShown:
            self.__cachedHint = self.__getHint()
            self.__showHint()
        elif self.__hintsLeft:
            self.__cachedHint = self.__getHint()

    def __showHint(self):
        if self.__isObserver:
            return
        else:
            if GUI_SETTINGS.spgAlternativeAimingCameraEnabled and not (self.sessionProvider.isReplayPlaying or self.__isThereAnyIndicators()):
                if self.__cachedHint is None:
                    self.__cachedHint = self.__getHint()
                self._parentObj.as_showHintS(*self.__cachedHint)
                self.__isHintShown = True
            return

    def __hideHint(self):
        if self.__isObserver:
            return
        if not self.sessionProvider.isReplayPlaying:
            self._parentObj.as_hideHintS()
            self.__isHintShown = False

    @staticmethod
    def __getHint():
        hintTextLeft = None
        keyName = getReadableKey(CommandMapping.CMD_CM_TRAJECTORY_VIEW)
        if keyName:
            hintTextLeft = i18n.makeString(INGAME_GUI.TRAJECTORYVIEW_HINT_ALTERNATEMODELEFT)
            hintTextRight = i18n.makeString(INGAME_GUI.TRAJECTORYVIEW_HINT_ALTERNATEMODERIGHT)
        else:
            hintTextRight = i18n.makeString(INGAME_GUI.TRAJECTORYVIEW_HINT_NOBINDINGKEY)
        return (keyName,
         hintTextLeft,
         hintTextRight,
         _TRAJECTORY_VIEW_HINT_POSITION[0],
         _TRAJECTORY_VIEW_HINT_POSITION[1])


class ShotDonePlugin(CrosshairPlugin):
    __slots__ = ()

    def start(self):
        feedbackCtrl = self.sessionProvider.shared.feedback
        feedbackCtrl.onShotDone += self.__onShotDone

    def stop(self):
        feedbackCtrl = self.sessionProvider.shared.feedback
        if feedbackCtrl is not None:
            feedbackCtrl.onShotDone -= self.__onShotDone
        return

    def __onShotDone(self):
        if self.sessionProvider.shared.ammo.getGunSettings().hasAutoReload():
            self._parentObj.as_showShotS()
