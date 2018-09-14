# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/crosshair_panel.py
import math
import weakref
import BattleReplay
import BigWorld
from account_helpers.settings_core import g_settingsCore
from debug_utils import LOG_DEBUG
from gui import DEPTH_OF_Aim, makeHtmlString
from gui.Scaleform import Flash, SCALEFORM_SWF_PATH_V3
from gui.Scaleform.daapi.view.meta.CrosshairPanelMeta import CrosshairPanelMeta
from gui.Scaleform.framework.application import DAAPIRootBridge
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control import g_sessionProvider, avatar_getter
from gui.battle_control.battle_constants import CROSSHAIR_VIEW_ID, FEEDBACK_EVENT_ID, getCrosshairViewIDByCtrlMode
from gui.battle_control.battle_constants import GUN_RELOADING_VALUE_TYPE
from gui.battle_control.battle_constants import SHELL_SET_RESULT, VEHICLE_VIEW_STATE
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from gui.shared.utils.TimeInterval import TimeInterval
from gui.shared.utils.plugins import IPlugin, PluginsCollection
from helpers import i18n
_CROSSHAIR_PANEL_SWF = 'crosshairPanel.swf'
_CROSSHAIR_PANEL_COMPONENT = 'WGAimFlash'
_SETTINGS_KEY_TO_VIEW_ID = {'arcade': CROSSHAIR_VIEW_ID.ARCADE,
 'sniper': CROSSHAIR_VIEW_ID.SNIPER}
_SETTINGS_KEYS = set(_SETTINGS_KEY_TO_VIEW_ID.keys())
_TARGET_UPDATE_INTERVAL = 0.2

def _makeSettingsVO(*keys):
    getter = g_settingsCore.getSetting
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
             'zoomIndicatorAlphaValue': settings['zoomIndicator'] / 100.0}

    return data


def _getHealthPercent(health, maxHealth):
    value = min(1.0, max(0, health) / float(maxHealth))
    return round(value, 2)


class _AmmoSettings(object):

    def __init__(self, capacity, burst):
        super(_AmmoSettings, self).__init__()
        self._capacity = capacity
        self._burst = burst

    def getClipCapacity(self):
        return self._capacity

    def getBurstSize(self):
        return self._burst

    def getState(self, quantity, quantityInClip):
        return (quantity < 3, 'normal')


class _CassetteSettings(_AmmoSettings):

    def getState(self, quantity, quantityInClip):
        isLow, state = super(_CassetteSettings, self).getState(quantity, quantityInClip)
        isLow |= quantity <= self._capacity
        if self._burst > 1:
            total = math.ceil(self._capacity / float(self._burst))
            current = math.ceil(quantityInClip / float(self._burst))
        else:
            total = self._capacity
            current = quantityInClip
        if current <= 0.5 * total:
            state = 'critical' if current == 1 else 'warning'
        return (isLow, state)


def createAmmoSettings(gunSettings):
    capacity = gunSettings.clip.size
    burst = gunSettings.burst.size
    if capacity > 1:
        state = _CassetteSettings(capacity, burst)
    else:
        state = _AmmoSettings(capacity, burst)
    return state


class CorePlugin(IPlugin):
    """Plugin listens changes of global descriptors that are provided by CrosshairDataProxy.
    This plugin sets all geometry metrics of panel, switches panel to new view."""

    def start(self):
        ctrl = g_sessionProvider.shared.crosshair
        assert ctrl is not None, 'Crosshair controller is not found'
        self.__setup(ctrl)
        ctrl.onCrosshairViewChanged += self.__onCrosshairViewChanged
        ctrl.onCrosshairScaleChanged += self.__onCrosshairScaleChanged
        ctrl.onCrosshairSizeChanged += self.__onCrosshairSizeChanged
        ctrl.onCrosshairPositionChanged += self.__onCrosshairPositionChanged
        ctrl.onGunMarkerPositionChanged += self.__onGunMarkerPositionChanged
        ctrl.onCrosshairZoomFactorChanged += self.__onCrosshairZoomFactorChanged
        return

    def stop(self):
        ctrl = g_sessionProvider.shared.crosshair
        if ctrl is not None:
            ctrl.onCrosshairViewChanged -= self.__onCrosshairViewChanged
            ctrl.onCrosshairScaleChanged -= self.__onCrosshairScaleChanged
            ctrl.onCrosshairSizeChanged -= self.__onCrosshairSizeChanged
            ctrl.onCrosshairPositionChanged -= self.__onCrosshairPositionChanged
            ctrl.onGunMarkerPositionChanged -= self.__onGunMarkerPositionChanged
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

    def __onGunMarkerPositionChanged(self, position, relaxTime):
        self._parentObj.setGunMarkerPosition(position, relaxTime)


class SettingsPlugin(IPlugin):
    """Plugin listens changes of settings and transfers desired settings to Action Script."""

    def start(self):
        self._parentObj.as_setSettingsS(_makeSettingsVO(*_SETTINGS_KEYS))
        g_settingsCore.onSettingsChanged += self.__onSettingsChanged

    def stop(self):
        g_settingsCore.onSettingsChanged -= self.__onSettingsChanged

    def __onSettingsChanged(self, diff):
        changed = set(diff.keys()) & _SETTINGS_KEYS
        if changed:
            self._parentObj.as_setSettingsS(_makeSettingsVO(*changed))


class EventBusPlugin(IPlugin):
    """Plugin listens events of event bus and invokes next actions:
        - toggle crosshair visibility if player press V (by default).
        - toggle crosshair visibility in some special cases: CAPS + X (see tag "keys" in avatar_input_handler.xml).
        - change view if player switches to video mode (CAPS + F3) and presses LShift + B or RShift + B (
            see tag "videoMode/keyBindToVehicle" in avatar_input_handler.xml).
    """
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
        self._parentObj.setViewID(getCrosshairViewIDByCtrlMode(event.ctx['ctrlMode']))


class AmmoPlugin(IPlugin):
    """Plugins listens all desired changes of ammo and updates UI panel if it needs."""
    __slots__ = ('__guiSettings', '__burstSize')

    def __init__(self, parentObj):
        super(AmmoPlugin, self).__init__(parentObj)
        self.__guiSettings = None
        return

    def start(self):
        ctrl = g_sessionProvider.shared.ammo
        assert ctrl is not None, 'Ammo controller is not found'
        self.__setup(ctrl)
        ctrl.onGunSettingsSet += self.__onGunSettingsSet
        ctrl.onGunReloadTimeSet += self.__onGunReloadTimeSet
        ctrl.onShellsUpdated += self.__onShellsUpdated
        ctrl.onCurrentShellChanged += self.__onCurrentShellChanged
        return

    def stop(self):
        ctrl = g_sessionProvider.shared.ammo
        if ctrl is not None:
            ctrl.onGunSettingsSet -= self.__onGunSettingsSet
            ctrl.onGunReloadTimeSet -= self.__onGunReloadTimeSet
            ctrl.onShellsUpdated -= self.__onShellsUpdated
            ctrl.onCurrentShellChanged -= self.__onCurrentShellChanged
        return

    def __setup(self, ctrl):
        if BattleReplay.g_replayCtrl.isPlaying:
            self._parentObj.as_setReloadingCounterShownS(False)
        self.__guiSettings = createAmmoSettings(ctrl.getGunSettings())
        self._parentObj.as_setClipParamsS(self.__guiSettings.getClipCapacity(), self.__guiSettings.getBurstSize())
        quantity, quantityInClip = ctrl.getCurrentShells()
        isLow, state = self.__guiSettings.getState(quantity, quantityInClip)
        self._parentObj.as_setAmmoStockS(quantity, quantityInClip, isLow, state, False)
        self.__setReloadingState(ctrl.getGunReloadingState())

    def __setReloadingState(self, state):
        valueType = state.getValueType()
        if valueType == GUN_RELOADING_VALUE_TYPE.PERCENT:
            self._parentObj.as_setReloadingAsPercentS(state.getActualValue(), False)
        elif valueType == GUN_RELOADING_VALUE_TYPE.TIME:
            LOG_DEBUG('Set reloading state', state)
            self._parentObj.as_setReloadingS(state.getActualValue(), state.getBaseValue(), state.getTimePassed(), state.isReloading())

    def __onGunSettingsSet(self, gunSettings):
        self.__guiSettings = createAmmoSettings(gunSettings)
        self._parentObj.as_setClipParamsS(self.__guiSettings.getClipCapacity(), self.__guiSettings.getBurstSize())

    def __onGunReloadTimeSet(self, _, state):
        self.__setReloadingState(state)

    def __onShellsUpdated(self, _, quantity, quantityInClip, result):
        if not result & SHELL_SET_RESULT.CURRENT:
            return
        isLow, state = self.__guiSettings.getState(quantity, quantityInClip)
        self._parentObj.as_setAmmoStockS(quantity, quantityInClip, isLow, state, result & SHELL_SET_RESULT.CASSETTE_RELOAD > 0)

    def __onCurrentShellChanged(self, _):
        ctrl = g_sessionProvider.shared.ammo
        if ctrl is not None:
            quantity, quantityInClip = ctrl.getCurrentShells()
            isLow, state = self.__guiSettings.getState(quantity, quantityInClip)
            self._parentObj.as_setAmmoStockS(quantity, quantityInClip, isLow, state, False)
        return


class VehicleStatePlugin(IPlugin):
    """Plugin listens events of controlling vehicle and update information about given vehicle
    (health, vehicles has no any ammo, etc.) in UI panel."""
    __slots__ = ('__playerInfo', '__isPlayerVehicle', '__maxHealth', '__healthPercent')

    def __init__(self, parentObj):
        super(VehicleStatePlugin, self).__init__(parentObj)
        self.__playerInfo = None
        self.__isPlayerVehicle = False
        self.__maxHealth = 0
        self.__healthPercent = 0
        return

    def start(self):
        ctrl = g_sessionProvider.shared.vehicleState
        assert ctrl is not None, 'Vehicles state controller is not found'
        vehicle = ctrl.getControllingVehicle()
        if vehicle is not None:
            self.__setPlayerInfo(vehicle.id)
            self.__onVehicleControlling(vehicle)
        ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        ctrl.onVehicleControlling += self.__onVehicleControlling
        ctrl.onPostMortemSwitched += self.__onPostMortemSwitched
        ctrl = g_sessionProvider.shared.feedback
        assert ctrl is not None, 'Feedback adaptor is not found'
        ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        return

    def stop(self):
        ctrl = g_sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
            ctrl.onVehicleControlling -= self.__onVehicleControlling
            ctrl.onPostMortemSwitched -= self.__onPostMortemSwitched
        ctrl = g_sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        return

    def __setHealth(self, health):
        self.__healthPercent = _getHealthPercent(health, self.__maxHealth)

    def __setPlayerInfo(self, vehicleID):
        self.__playerInfo = g_sessionProvider.getCtx().getPlayerFullNameParts(vID=vehicleID, showVehShortName=True)

    def __updateVehicleInfo(self):
        if self._parentObj.getViewID() == CROSSHAIR_VIEW_ID.POSTMORTEM:
            assert self.__playerInfo is not None, 'Player info must be defined at first, see vehicle_state_ctrl'
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
        return

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

    def __onPostMortemSwitched(self):
        self.__updateVehicleInfo()

    def __onVehicleFeedbackReceived(self, eventID, _, value):
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_HAS_AMMO and self._parentObj.getViewID() == CROSSHAIR_VIEW_ID.POSTMORTEM:
            self._parentObj.setHasAmmo(value)


class _DistancePlugin(IPlugin):
    __slots__ = ('__weakref__', '_interval', '_distance')

    def __init__(self, parentObj):
        super(_DistancePlugin, self).__init__(parentObj)
        self._interval = None
        self._distance = 0
        return

    def start(self):
        self._interval = TimeInterval(_TARGET_UPDATE_INTERVAL, self, '_update')
        ctrl = g_sessionProvider.shared.crosshair
        assert ctrl is not None, 'Crosshair controller is not found'
        ctrl.onCrosshairViewChanged += self._onCrosshairViewChanged
        return

    def stop(self):
        if self._interval is not None:
            self._interval.stop()
            self._interval = None
        ctrl = g_sessionProvider.shared.crosshair
        if ctrl is not None:
            ctrl.onCrosshairViewChanged -= self._onCrosshairViewChanged
        return

    def _update(self):
        raise NotImplementedError

    def _onCrosshairViewChanged(self, viewID):
        raise NotImplementedError


class TargetDistancePlugin(_DistancePlugin):
    """Plugin keeps track of distance between player's vehicle position and target position
    (it is vehicle in focus) when player is in arcade or sniper mode. It updates UI panel if distance is changed only,
    and distance string is hidden if player switches to other mode or target is lost."""
    __slots__ = ('__trackID',)

    def __init__(self, parentObj):
        super(TargetDistancePlugin, self).__init__(parentObj)
        self.__trackID = 0

    def start(self):
        super(TargetDistancePlugin, self).start()
        ctrl = g_sessionProvider.shared.feedback
        assert ctrl is not None, 'Feedback adaptor is not found'
        ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        return

    def stop(self):
        super(TargetDistancePlugin, self).stop()
        ctrl = g_sessionProvider.shared.feedback
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
        self._distance = 0
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
    """Plugin keeps track of distance between player's vehicle position and gun maker position (avatar position)
    when player switches to strategic mode. It updates UI panel if distance is changed only, and distance string
    is hidden if player switches to other mode."""
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


class CrosshairPanel(Flash.Flash, CrosshairPanelMeta):
    """Class is UI component of crosshair panel. It provides access to Action Script."""

    def __init__(self):
        super(CrosshairPanel, self).__init__('crosshairPanel.swf', className=_CROSSHAIR_PANEL_COMPONENT, path=SCALEFORM_SWF_PATH_V3)
        self.__plugins = PluginsCollection(self)
        self.__plugins.addPlugins({'core': CorePlugin,
         'settings': SettingsPlugin,
         'events': EventBusPlugin,
         'ammo': AmmoPlugin,
         'vehicleState': VehicleStatePlugin,
         'targetDistance': TargetDistancePlugin,
         'gunMarkerDistance': GunMarkerDistancePlugin})
        self.__viewID = CROSSHAIR_VIEW_ID.UNDEFINED
        self.__zoomFactor = 0.0
        self.__distance = 0
        self.__hasAmmo = True
        self.__configure()
        self.__daapiBridge = DAAPIRootBridge(rootPath='root.g_modeMC', initCallback='registerCrosshairPanel')
        self.__daapiBridge.setPyScript(weakref.proxy(self))

    def close(self):
        if self.__daapiBridge is not None:
            self.__daapiBridge.clear()
            self.__daapiBridge = None
        super(CrosshairPanel, self).close()
        return

    def isVisible(self):
        """Is component visible.
        :return: bool.
        """
        return self.component.visible

    def setVisible(self, visible):
        """Sets visibility of component.
        :param visible: bool.
        """
        self.component.visible = visible

    def getViewID(self):
        """Gets current view ID of panel.
        :return: integer containing of CROSSHAIR_VIEW_ID.
        """
        return self.__viewID

    def setViewID(self, viewID):
        """Sets view ID of panel to change view presentation.
        :param viewID:
        """
        if viewID != self.__viewID:
            self.__viewID = viewID
            self.as_setViewS(viewID)

    def getSize(self):
        """Gets size of crosshair panel.
        :return: tuple(width, height).
        """
        return self.component.size

    def setSize(self, width, height):
        """Sets size of crosshair panel in pixels.
        :param width: integer containing width of panel.
        :param height: integer containing height of panel.
        """
        self.component.size = (width, height)

    def setPosition(self, x, y):
        """Sets position of crosshair panel in pixels.
        :param x: integer containing x coordinate of center in pixels.
        :param y: integer containing y coordinate of center in pixels.
        """
        self.as_recreateDeviceS(x, y)

    def getScale(self):
        """Gets scale factor.
        :return: float containing scale factor.
        """
        return self.movie.stage.scaleX

    def setScale(self, scale):
        """Sets scale factor.
        :param scale: float containing new scale factor.
        """
        self.movie.stage.scaleX = scale
        self.movie.stage.scaleY = scale

    def getZoom(self):
        """Gets current zoom factor of player's camera.
        :return: float containing zoom factor.
        """
        return self.__zoomFactor

    def setZoom(self, zoomFactor):
        """Gets current zoom factor of player's camera.
        :param zoomFactor: float containing zoom factor.
        """
        if zoomFactor == self.__zoomFactor:
            return
        self.__zoomFactor = zoomFactor
        if zoomFactor > 1:
            zoomString = i18n.makeString(INGAME_GUI.AIM_ZOOM, zoom=zoomFactor)
        else:
            zoomString = ''
        self.as_setZoomS(zoomString)

    def getDistance(self):
        """Gets distance to desired target(point).
        :return: integer containing distance in meters.
        """
        return self.__distance

    def setDistance(self, distance):
        """Sets distance to desired target(point).
        :param distance: integer containing distance in meters.
        """
        if distance != self.__distance:
            self.__distance = distance
            self.as_setDistanceS(i18n.makeString(INGAME_GUI.DISTANCE_METERS, meters=distance))

    def clearDistance(self, immediate=True):
        """Removes distance string from UI.
        :param immediate: if value equals True than removes distance string from UI immediately,
            otherwise - hides this sting with animation.
        """
        self.__distance = 0
        self.as_clearDistanceS(immediate)

    def setHasAmmo(self, hasAmmo):
        """Sets flag that indicates controlling vehicle has ammo.
        :param hasAmmo: bool.
        """
        if self.__hasAmmo != hasAmmo:
            self.__hasAmmo = hasAmmo
            if not hasAmmo:
                self.as_updateAmmoStateS(i18n.makeString(INGAME_GUI.PLAYER_MESSAGES_POSTMORTEM_USERNOHASAMMO))
            else:
                self.as_updateAmmoStateS('')

    def setGunMarkerPosition(self, position, relaxTime):
        """Sets new position of gun marker. This value is transferred to cpp component.
        :param position: vector3
        :param relaxTime: float.
        """
        self.component.updateMarkerPos(position, relaxTime)

    def _populate(self):
        super(CrosshairPanel, self)._populate()
        self.__plugins.init()
        self.__plugins.start()

    def _dispose(self):
        self.__plugins.stop()
        self.__plugins.fini()
        super(CrosshairPanel, self)._dispose()

    def __configure(self):
        self.component.wg_inputKeyMode = 2
        self.component.position.z = DEPTH_OF_Aim
        self.component.focus = False
        self.component.moveFocus = False
        self.component.heightMode = 'PIXEL'
        self.component.widthMode = 'PIXEL'
        self.movie.backgroundAlpha = 0
