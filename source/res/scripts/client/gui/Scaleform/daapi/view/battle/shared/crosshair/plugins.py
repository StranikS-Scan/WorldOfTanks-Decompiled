# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/crosshair/plugins.py
import math
from collections import defaultdict
import BattleReplay
import BigWorld
from AvatarInputHandler import gun_marker_ctrl, aih_global_binding
from PlayerEvents import g_playerEvents
from ReplayEvents import g_replayEvents
from account_helpers.settings_core.settings_constants import GRAPHICS, AIM, GAME
from aih_constants import CHARGE_MARKER_STATE
from constants import VEHICLE_SIEGE_STATE as _SIEGE_STATE, DUALGUN_CHARGER_STATUS, SERVER_TICK_LENGTH
from debug_utils import LOG_WARNING
from gui import makeHtmlString
from gui.Scaleform.daapi.view.battle.shared.crosshair.settings import SHOT_RESULT_TO_ALT_COLOR
from gui.Scaleform.daapi.view.battle.shared.crosshair.settings import SHOT_RESULT_TO_DEFAULT_COLOR
from gui.Scaleform.daapi.view.battle.shared.formatters import getHealthPercent
from gui.Scaleform.daapi.view.battle.shared.timers_common import PythonTimer
from gui.Scaleform.genConsts.CROSSHAIR_CONSTANTS import CROSSHAIR_CONSTANTS
from gui.Scaleform.genConsts.DUAL_GUN_MARKER_STATE import DUAL_GUN_MARKER_STATE
from gui.Scaleform.genConsts.GUN_MARKER_VIEW_CONSTANTS import GUN_MARKER_VIEW_CONSTANTS as _VIEW_CONSTANTS
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID, CROSSHAIR_VIEW_ID, SHELL_QUANTITY_UNKNOWN
from gui.battle_control.battle_constants import SHELL_SET_RESULT, VEHICLE_VIEW_STATE, NET_TYPE_OVERRIDE
from gui.battle_control.controllers import crosshair_proxy
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from gui.shared.utils.TimeInterval import TimeInterval
from gui.shared.utils.plugins import IPlugin
from helpers import dependency
from helpers.time_utils import MS_IN_SECOND
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IBootcampController
_SETTINGS_KEY_TO_VIEW_ID = {AIM.ARCADE: CROSSHAIR_VIEW_ID.ARCADE,
 AIM.SNIPER: CROSSHAIR_VIEW_ID.SNIPER}
_SETTINGS_KEYS = set(_SETTINGS_KEY_TO_VIEW_ID.keys())
_SETTINGS_VIEWS = set(_SETTINGS_KEY_TO_VIEW_ID.values())
_DEVICE_ENGINE_NAME = 'engine'
_DEVICE_REPAIRED = 'repaired'
_TARGET_UPDATE_INTERVAL = 0.2
_DUAL_GUN_MARKER_STATES_MAP = {CHARGE_MARKER_STATE.VISIBLE: DUAL_GUN_MARKER_STATE.VISIBLE,
 CHARGE_MARKER_STATE.LEFT_ACTIVE: DUAL_GUN_MARKER_STATE.LEFT_PART_ACTIVE,
 CHARGE_MARKER_STATE.RIGHT_ACTIVE: DUAL_GUN_MARKER_STATE.RIGHT_PART_ACTIVE,
 CHARGE_MARKER_STATE.DIMMED: DUAL_GUN_MARKER_STATE.DIMMED}

def createPlugins():
    resultPlugins = {'core': CorePlugin,
     'settings': SettingsPlugin,
     'events': EventBusPlugin,
     'ammo': AmmoPlugin,
     'vehicleState': VehicleStatePlugin,
     'targetDistance': TargetDistancePlugin,
     'gunMarkerDistance': GunMarkerDistancePlugin,
     'gunMarkersInvalidate': GunMarkersInvalidatePlugin,
     'shotResultIndicator': ShotResultIndicatorPlugin,
     'shotDone': ShotDonePlugin,
     'speedometerWheeledTech': SpeedometerWheeledTech,
     'siegeMode': SiegeModePlugin,
     'dualgun': DualGunPlugin}
    return resultPlugins


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


class _PythonTicker(PythonTimer):

    def __init__(self, viewObject):
        super(_PythonTicker, self).__init__(viewObject, 0, 0, 0, 0, interval=0.1)

    def _hideView(self):
        pass

    def _showView(self, isBubble):
        pass

    def startAnimation(self, actualTime, baseTime):
        self._totalTime = baseTime
        if actualTime > 0:
            self._finishTime = BigWorld.serverTime() + actualTime
            self.show()
        else:
            self._stopTick()

    def _setViewSnapshot(self, timeLeft):
        raise NotImplementedError


class _PythonShellInGunTicker(_PythonTicker):

    def _setViewSnapshot(self, timeLeft):
        if self._totalTime > 0:
            progress = self._totalTime - timeLeft
            percent = round(float(progress) / self._totalTime, 2)
            self._viewObject.as_setAutoloaderReloadasPercentS(percent)

    def _stopTick(self):
        super(_PythonShellInGunTicker, self)._stopTick()
        self._viewObject.as_setAutoloaderReloadasPercentS(1.0)


class _PythonClipLoadingTicker(_PythonTicker):

    def __init__(self, viewObject):
        super(_PythonClipLoadingTicker, self).__init__(viewObject)
        self.__isStunned = False
        self.__showTimer = True

    def setShowTimer(self, showTimer):
        self.__showTimer = showTimer

    def setStun(self, isStunned):
        self.__isStunned = isStunned

    def _setViewSnapshot(self, timeLeft):
        if self._totalTime > 0:
            percent = round(float(timeLeft) / self._totalTime, 2)
            self._viewObject.as_setAutoloaderPercentS(percent, timeLeft, self.__showTimer)

    def _stopTick(self):
        super(_PythonClipLoadingTicker, self)._stopTick()
        self._viewObject.as_setAutoloaderPercentS(1.0, self._totalTime, self.__showTimer)


class _PythonReloadTicker(_PythonTicker):

    def _setViewSnapshot(self, timeLeft):
        if self._totalTime > 0:
            timeGone = self._totalTime - timeLeft
            progressInPercents = round(float(timeGone) / self._totalTime * 100, 2)
            self._viewObject.as_setReloadingAsPercentS(progressInPercents, True)

    def _stopTick(self):
        super(_PythonReloadTicker, self)._stopTick()
        self._viewObject.as_setReloadingAsPercentS(100.0, False)


class _ReloadingAnimationsProxy(object):

    def __init__(self, panel):
        super(_ReloadingAnimationsProxy, self).__init__()
        self._panel = panel

    def setShellLoading(self, actualTime, baseTime):
        raise NotImplementedError

    def setClipAutoLoading(self, timeLeft, baseTime, isStun=False, isTimerOn=False, isRedText=False):
        raise NotImplementedError

    def setReloading(self, state):
        raise NotImplementedError


class _ASAutoReloadProxy(_ReloadingAnimationsProxy):

    def setShellLoading(self, actualTime, baseTime):
        self._panel.as_setAutoloaderReloadingS(actualTime, baseTime)

    def setClipAutoLoading(self, timeLeft, baseTime, isStun=False, isTimerOn=False, isRedText=False):
        self._panel.as_autoloaderUpdateS(timeLeft, baseTime, isStun=isStun, isTimerOn=isTimerOn, isRedText=isRedText)

    def setReloading(self, state):
        self._panel.as_setReloadingS(state.getActualValue(), state.getBaseValue(), state.getTimePassed(), state.isReloading())


class _PythonAutoReloadProxy(_ReloadingAnimationsProxy):

    def __init__(self, panel):
        super(_PythonAutoReloadProxy, self).__init__(panel)
        self.__shellTicker = _PythonShellInGunTicker(panel)
        self.__clipTicker = _PythonClipLoadingTicker(panel)
        self.__reloadTicker = _PythonReloadTicker(panel)

    def setShellLoading(self, actualTime, baseTime):
        self.__shellTicker.startAnimation(actualTime, baseTime)

    def setClipAutoLoading(self, timeLeft, baseTime, isStun=False, isTimerOn=False, isRedText=False):
        self.__clipTicker.setStun(isStun)
        self.__clipTicker.setShowTimer(isTimerOn)
        self.__clipTicker.startAnimation(timeLeft, baseTime)

    def setReloading(self, state):
        self.__reloadTicker.startAnimation(state.getActualValue(), state.getBaseValue())


class AmmoPlugin(CrosshairPlugin):
    __slots__ = ('__guiSettings', '__burstSize', '__shellsInClip', '__autoReloadCallbackID', '__autoReloadSnapshot', '__scaledInterval', '__reloadAnimator')
    bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self, parentObj):
        super(AmmoPlugin, self).__init__(parentObj)
        self.__guiSettings = None
        self.__shellsInClip = 0
        self.__autoReloadCallbackID = None
        self.__autoReloadSnapshot = None
        self.__reloadAnimator = None
        self.__scaledInterval = None
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
        self.__shellsInClip = ctrl.getCurrentShells()[1]
        if isReplayPlaying:
            self._parentObj.as_setReloadingCounterShownS(False)
            self.__reloadAnimator = _PythonAutoReloadProxy(self._parentObj)
        else:
            self.__reloadAnimator = _ASAutoReloadProxy(self._parentObj)
        self.__setupGuiSettings(ctrl.getGunSettings())
        quantity, quantityInClip = ctrl.getCurrentShells()
        if (quantity, quantityInClip) != (SHELL_QUANTITY_UNKNOWN,) * 2:
            isLow, state = self.__guiSettings.getState(quantity, quantityInClip)
            self._parentObj.as_setAmmoStockS(quantity, quantityInClip, isLow, state, False)
        reloadingState = ctrl.getGunReloadingState()
        self.__setReloadingState(reloadingState)
        if self.__guiSettings.hasAutoReload:
            self.__reloadAnimator.setClipAutoLoading(reloadingState.getActualValue(), reloadingState.getBaseValue(), isStun=False)
        if self.bootcampController.isInBootcamp():
            self._parentObj.as_setNetVisibleS(CROSSHAIR_CONSTANTS.VISIBLE_NET)

    def __setReloadingState(self, state):
        self.__reloadAnimator.setReloading(state)

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
        actualTime = state.getActualValue()
        baseTime = state.getBaseValue()
        if self.__shellsInClip <= 0 and state.isReloading():
            timeGone = baseTime - actualTime
            clipInterval = self.__guiSettings.getClipInterval()
            if clipInterval > timeGone:
                actualTime = clipInterval - timeGone
                baseTime = clipInterval
                if self.__autoReloadCallbackID is not None:
                    BigWorld.cancelCallback(self.__autoReloadCallbackID)
                self.__autoReloadCallbackID = BigWorld.callback(actualTime, self.__autoReloadFirstShellCallback)
                self.__scaledInterval = clipInterval
            else:
                self.__reloadAnimator.setClipAutoLoading(actualTime, self.__reCalcFirstShellAutoReload(baseTime), isRedText=True)
                actualTime = baseTime = 0
            self.__autoReloadSnapshot = state
        self.__reloadAnimator.setShellLoading(actualTime, baseTime)
        return

    def __autoReloadFirstShellCallback(self):
        timeLeft = min(self.__autoReloadSnapshot.getTimeLeft(), self.__autoReloadSnapshot.getActualValue())
        self.__reloadAnimator.setClipAutoLoading(timeLeft, timeLeft, isTimerOn=True, isRedText=True)
        self.__autoReloadCallbackID = None
        return

    def __onGunAutoReloadTimeSet(self, state, stunned):
        if not self.__autoReloadCallbackID:
            timeLeft = min(state.getTimeLeft(), state.getActualValue())
            baseValue = state.getBaseValue()
            if self.__shellsInClip == 0:
                baseValue = self.__reCalcFirstShellAutoReload(baseValue)
            self.__reloadAnimator.setClipAutoLoading(timeLeft, baseValue, isStun=stunned, isTimerOn=True, isRedText=self.__shellsInClip == 0)
        self.__autoReloadSnapshot = state

    def __reCalcFirstShellAutoReload(self, baseTime):
        if not self.__scaledInterval:
            return baseTime
        newScaledInterval = self.__scaledInterval * baseTime / self.__autoReloadSnapshot.getBaseValue()
        result = baseTime - newScaledInterval
        self.__scaledInterval = newScaledInterval
        return result

    def __onShellsUpdated(self, _, quantity, quantityInClip, result):
        self.__shellsInClip = quantityInClip
        if not result & SHELL_SET_RESULT.CURRENT:
            return
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
            if vTypeDesc.hasSiegeMode and not vTypeDesc.isWheeledVehicle and not vTypeDesc.hasAutoSiegeMode and not vTypeDesc.isDualgunVehicle:
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
        vStateCtrl = self.sessionProvider.shared.vehicleState
        vehicle = vStateCtrl.getControllingVehicle()
        if vehicle is not None:
            vTypeDescr = vehicle.typeDescriptor
            if vTypeDescr.isWheeledVehicle or vTypeDescr.hasAutoSiegeMode or vTypeDescr.isDualgunVehicle:
                self._parentObj.as_setNetTypeS(NET_TYPE_OVERRIDE.DISABLED)
                return
        else:
            return
        if self.__siegeState == _SIEGE_STATE.ENABLED:
            self._parentObj.as_setNetTypeS(NET_TYPE_OVERRIDE.SIEGE_MODE)
        elif self.__siegeState == _SIEGE_STATE.DISABLED:
            self._parentObj.as_setNetTypeS(NET_TYPE_OVERRIDE.DISABLED)
        visibleMask = CROSSHAIR_CONSTANTS.VISIBLE_ALL if self.__siegeState not in _SIEGE_STATE.SWITCHING else 0
        self._parentObj.as_setNetVisibleS(visibleMask)
        return


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


class SpeedometerWheeledTech(CrosshairPlugin):
    __slots__ = ('__siegeState', '__burnoutLevelMax', '__burnoutWarningOn', '__viewID', '__destroyTimerShown', '__cachedBurnoutLevel')

    def __init__(self, parentObj):
        super(SpeedometerWheeledTech, self).__init__(parentObj)
        self.__siegeState = _SIEGE_STATE.DISABLED
        self.__burnoutLevelMax = 255.0
        self.__burnoutWarningOn = False
        self.__viewID = -1
        self.__destroyTimerShown = False
        self.__cachedBurnoutLevel = None
        return

    def start(self):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onTimeWarpStart += self.__onReplayTimeWarpStart
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            vStateCtrl.onVehicleControlling += self.__onVehicleControlling
            crosshairCtrl.onCrosshairViewChanged += self.__onCrosshairViewChanged
            vehicle = vStateCtrl.getControllingVehicle()
            if vehicle is not None and vehicle.isWheeledTech:
                self.__onVehicleControlling(vehicle)
        specCtrl = self.sessionProvider.dynamic.spectator
        if specCtrl is not None:
            specCtrl.onSpectatorViewModeChanged += self.__onSpectatorModeChanged
        add = g_eventBus.addListener
        add(GameEvent.DESTROY_TIMERS_PANEL, self.__destroyTimersListener, scope=EVENT_BUS_SCOPE.BATTLE)
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        return

    def stop(self):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
            vStateCtrl.onVehicleControlling -= self.__onVehicleControlling
            crosshairCtrl.onCrosshairViewChanged -= self.__onCrosshairViewChanged
        specCtrl = self.sessionProvider.dynamic.spectator
        if specCtrl is not None:
            specCtrl.onSpectatorViewModeChanged -= self.__onSpectatorModeChanged
        remove = g_eventBus.removeListener
        remove(GameEvent.DESTROY_TIMERS_PANEL, self.__destroyTimersListener, scope=EVENT_BUS_SCOPE.BATTLE)
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        return

    def __onVehicleControlling(self, vehicle):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        vTypeDesc = vehicle.typeDescriptor
        if vTypeDesc.isWheeledVehicle and vehicle.health > 0:
            if vStateCtrl.isInPostmortem:
                self.__resetSpeedometer()
            self.__updateBurnoutWarning(vStateCtrl)
            self.__updateCurrentBurnoutLevel(vehicle)
            if self.settingsCore.getSetting(GAME.ENABLE_SPEEDOMETER):
                self.__addSpedometer(vehicle)
            self.__updateCurStateSpeedMode(vStateCtrl)
        else:
            self.parentObj.as_removeSpeedometerS()

    def __onVehicleStateUpdated(self, stateID, value):
        if stateID == VEHICLE_VIEW_STATE.SPEED and self.parentObj is not None:
            self.parentObj.as_updateSpeedS(value)
        elif stateID == VEHICLE_VIEW_STATE.SIEGE_MODE:
            self.__changeSpeedoType(*value)
        elif stateID == VEHICLE_VIEW_STATE.BURNOUT:
            self.__changeBurnoutLevel(value)
        elif stateID == VEHICLE_VIEW_STATE.REPAIRING:
            self.__stopEngineDamageWarning()
        elif stateID == VEHICLE_VIEW_STATE.BURNOUT_WARNING:
            if value > 0:
                self.__setEngineDamageWarning()
            elif self.__burnoutWarningOn:
                self.__stopEngineDamageWarning()
        elif stateID == VEHICLE_VIEW_STATE.DEVICES and self.parentObj is not None:
            if _DEVICE_ENGINE_NAME in value and _DEVICE_REPAIRED in value:
                self.parentObj.as_stopEngineCrushErrorS()
                self.__stopEngineDamageWarning()
        elif stateID == VEHICLE_VIEW_STATE.BURNOUT_UNAVAILABLE_DUE_TO_BROKEN_ENGINE and self.parentObj is not None:
            if not self.__destroyTimerShown:
                self.parentObj.as_setEngineCrushErrorS(INGAME_GUI.BURNOUT_HINT_ENGINEDAMAGED)
        return

    def __onCrosshairViewChanged(self, viewID):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        vehicle = vStateCtrl.getControllingVehicle()
        if vehicle is None:
            return
        else:
            if vehicle.typeDescriptor.isWheeledVehicle and viewID == CROSSHAIR_VIEW_ID.ARCADE:
                self.__onVehicleControlling(vehicle)
                self.__updateCurStateSpeedMode(vStateCtrl)
            return

    def __resetSpeedometer(self):
        self.parentObj.as_updateSpeedS(0)
        if self.__cachedBurnoutLevel is not None:
            self.parentObj.as_updateBurnoutS(self.__cachedBurnoutLevel)
        if self.__burnoutWarningOn:
            self.parentObj.as_setBurnoutWarningS(INGAME_GUI.BURNOUT_HINT_ENGINEDAMAGEWARNING)
        else:
            self.parentObj.as_stopBurnoutWarningS()
        return

    def __onSpectatorModeChanged(self, mode):
        self.parentObj.as_removeSpeedometerS()

    def __onReplayTimeWarpStart(self):
        self.__resetSpeedometer()

    def __updateCurStateSpeedMode(self, vStateCtrl):
        value = vStateCtrl.getStateValue(VEHICLE_VIEW_STATE.SIEGE_MODE)
        if value is not None:
            self.__onVehicleStateUpdated(VEHICLE_VIEW_STATE.SIEGE_MODE, value)
        else:
            self.__onVehicleStateUpdated(VEHICLE_VIEW_STATE.SIEGE_MODE, (_SIEGE_STATE.DISABLED, None))
        return

    def __updateCurrentBurnoutLevel(self, vehicle):
        self.__cachedBurnoutLevel = vehicle.burnoutLevel

    def __updateBurnoutWarning(self, vStateCtrl):
        value = vStateCtrl.getStateValue(VEHICLE_VIEW_STATE.BURNOUT_WARNING)
        self.__burnoutWarningOn = value

    def __getMaxSpeeds(self, vehicle):
        typeDesc = vehicle.typeDescriptor
        defaultVehicleDescr = typeDesc
        siegeVehicleDescr = None
        siegeMaxSpd = None
        if typeDesc.hasSiegeMode:
            defaultVehicleDescr = typeDesc.defaultVehicleDescr
            siegeVehicleDescr = typeDesc.siegeVehicleDescr
        if siegeVehicleDescr is not None:
            siegeEngineCfg = siegeVehicleDescr.type.xphysics['engines'][typeDesc.engine.name]
            siegeMaxSpd = siegeEngineCfg['smplFwMaxSpeed']
        defaultVehicleCfg = defaultVehicleDescr.type.xphysics['engines'][typeDesc.engine.name]
        normalMaxSpd = defaultVehicleCfg['smplFwMaxSpeed']
        return (normalMaxSpd, siegeMaxSpd)

    def __addSpedometer(self, vehicle):
        normalMaxSpd, siegeMaxSpd = self.__getMaxSpeeds(vehicle)
        self.parentObj.as_removeSpeedometerS()
        self.parentObj.as_addSpeedometerS(normalMaxSpd, siegeMaxSpd)
        if self.__cachedBurnoutLevel is not None:
            self.parentObj.as_updateBurnoutS(self.__cachedBurnoutLevel)
        if self.__burnoutWarningOn:
            self.parentObj.as_setBurnoutWarningS(INGAME_GUI.BURNOUT_HINT_ENGINEDAMAGEWARNING)
        else:
            self.parentObj.as_stopBurnoutWarningS()
        return

    def __changeSpeedoType(self, siegeState, _):
        if siegeState == _SIEGE_STATE.ENABLED:
            self.parentObj.as_setSpeedModeS(True)
        elif siegeState == _SIEGE_STATE.DISABLED:
            self.parentObj.as_setSpeedModeS(False)
        self.__siegeState = siegeState

    def __changeBurnoutLevel(self, burnoutLevel):
        if burnoutLevel is not None and burnoutLevel <= self.__burnoutLevelMax:
            burnoutLevel = burnoutLevel / self.__burnoutLevelMax
            self.parentObj.as_updateBurnoutS(burnoutLevel)
            self.__cachedBurnoutLevel = burnoutLevel
        return

    def __setEngineDamageWarning(self):
        if not self.__destroyTimerShown:
            self.__burnoutWarningOn = True
            self.parentObj.as_setBurnoutWarningS(INGAME_GUI.BURNOUT_HINT_ENGINEDAMAGEWARNING)

    def __stopEngineDamageWarning(self):
        if self.parentObj is not None:
            self.__burnoutWarningOn = False
            self.parentObj.as_stopBurnoutWarningS()
        return

    def __destroyTimersListener(self, event):
        isShown = event.ctx['shown']
        if isShown is not None:
            self.__destroyTimerShown = isShown
        if not isShown:
            self.__stopEngineDamageWarning()
            self.parentObj.as_stopEngineCrushErrorS()
        return

    def __onSettingsChanged(self, diff):
        if GAME.ENABLE_SPEEDOMETER not in diff:
            return
        else:
            if diff[GAME.ENABLE_SPEEDOMETER]:
                vStateCtrl = self.sessionProvider.shared.vehicleState
                if vStateCtrl is not None:
                    vehicle = vStateCtrl.getControllingVehicle()
                    if vehicle is not None and vehicle.isWheeledTech:
                        self.__onVehicleControlling(vehicle)
            else:
                self.parentObj.as_removeSpeedometerS()
            return


class DualGunPlugin(CrosshairPlugin):
    __chargeMarkerState = aih_global_binding.bindRO(aih_global_binding.BINDING_ID.CHARGE_MARKER_STATE)

    def start(self):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            vStateCtrl.onVehicleControlling += self.__onVehicleControlling
            vehicle = vStateCtrl.getControllingVehicle()
            self.__onVehicleControlling(vehicle)
        if crosshairCtrl is not None:
            crosshairCtrl.onChargeMarkerStateUpdated += self.__dualGunMarkerStateUpdated
        add = g_eventBus.addListener
        add(GameEvent.SNIPER_CAMERA_TRANSITION, self.__onSniperCameraTransition, scope=EVENT_BUS_SCOPE.BATTLE)
        self.__dualGunMarkerStateUpdated(self.__chargeMarkerState)
        return

    def stop(self):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
            vStateCtrl.onVehicleControlling -= self.__onVehicleControlling
        if crosshairCtrl is not None:
            crosshairCtrl.onChargeMarkerStateUpdated -= self.__dualGunMarkerStateUpdated
        remove = g_eventBus.removeListener
        remove(GameEvent.SNIPER_CAMERA_TRANSITION, self.__onSniperCameraTransition, scope=EVENT_BUS_SCOPE.BATTLE)
        return

    def __onVehicleControlling(self, vehicle):
        if vehicle is None:
            return
        else:
            vTypeDesc = vehicle.typeDescriptor
            if vehicle.isAlive() and vTypeDesc.isDualgunVehicle:
                self._parentObj.as_setNetSeparatorVisibleS(False)
            return

    def __onVehicleStateUpdated(self, stateID, value):
        if stateID == VEHICLE_VIEW_STATE.SIEGE_MODE:
            self.__onSiegeStateUpdated(value)
        if stateID == VEHICLE_VIEW_STATE.DUAL_GUN_CHARGER:
            self.__onDualGunChargeStateUpdated(value)

    def __onSiegeStateUpdated(self, value):
        siegeState, _ = value
        if siegeState is _SIEGE_STATE.DISABLED:
            self.parentObj.as_cancelDualGunChargeS()

    def __onDualGunChargeStateUpdated(self, value):
        state, time = value
        pingCompensation = SERVER_TICK_LENGTH * MS_IN_SECOND
        if state == DUALGUN_CHARGER_STATUS.PREPARING:
            baseTime, timeLeft = time
            self.parentObj.as_startDualGunChargingS(timeLeft * MS_IN_SECOND - pingCompensation, baseTime * MS_IN_SECOND)
        elif state in (DUALGUN_CHARGER_STATUS.CANCELED, DUALGUN_CHARGER_STATUS.UNAVAILABLE):
            self.parentObj.as_cancelDualGunChargeS()

    def __dualGunMarkerStateUpdated(self, markerState):
        dualGunMarkerState = _DUAL_GUN_MARKER_STATES_MAP[markerState]
        self.parentObj.as_updateDualGunMarkerStateS(dualGunMarkerState)

    def __onSniperCameraTransition(self, event):
        transitionTimeInSeconds = event.ctx.get('transitionTime')
        gunIndex = event.ctx.get('currentGunIndex')
        self.parentObj.as_runCameraTransitionFxS(gunIndex, transitionTimeInSeconds * MS_IN_SECOND)
