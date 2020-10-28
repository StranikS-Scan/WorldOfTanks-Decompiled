# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/markers2d/manager.py
import logging
import weakref
import BattleReplay
import GUI
from account_helpers.settings_core.settings_constants import BattleCommStorageKeys
from chat_commands_consts import INVALID_MARKER_SUBTYPE, MarkerType, INVALID_MARKER_ID
from gui import DEPTH_OF_VehicleMarker, GUI_SETTINGS
from gui.Scaleform.daapi.view.battle.shared.markers2d import plugins, vehicle_plugins
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import MarkerPlugin
from gui.Scaleform.daapi.view.external_components import ExternalFlashComponent
from gui.Scaleform.daapi.view.external_components import ExternalFlashSettings
from gui.Scaleform.daapi.view.meta.VehicleMarkersManagerMeta import VehicleMarkersManagerMeta
from gui.Scaleform.flash_wrapper import InputKeyMode
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.genConsts.ROOT_SWF_CONSTANTS import ROOT_SWF_CONSTANTS
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.utils.plugins import PluginsCollection
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from soft_exception import SoftException
_logger = logging.getLogger(__name__)
_STICKY_MARKER_RADIUS_SCALE = 0.7

class MarkersManager(ExternalFlashComponent, VehicleMarkersManagerMeta, plugins.IMarkersManager):
    settingsCore = dependency.descriptor(ISettingsCore)
    setablePluginsDict = {'area': plugins.AreaStaticMarkerPlugin,
     'teamAndControlPoints': plugins.TeamsOrControlsPointsPlugin}

    def __init__(self):
        super(MarkersManager, self).__init__(ExternalFlashSettings(BATTLE_VIEW_ALIASES.MARKERS_2D, settings.MARKERS_MANAGER_SWF, 'root.vehicleMarkersCanvas', ROOT_SWF_CONSTANTS.BATTLE_VEHICLE_MARKERS_REGISTER_CALLBACK))
        self.__plugins = None
        self.__canvas = None
        self.__ids = set()
        self.__isIBCEnabled = False
        self.__isStickyEnabled = False
        self.__showBaseMarkers = False
        self.__showLocationMarkers = False
        return

    @property
    def __isMarkerHoveringEnabled(self):
        sessionProvider = dependency.instance(IBattleSessionProvider)
        arenaVisitor = sessionProvider.arenaVisitor
        return self.__isIBCEnabled and not (arenaVisitor.gui.isBootcampBattle() or sessionProvider.getCtx().isPlayerObserver() or arenaVisitor.gui.isBattleRoyale())

    def setScaleProps(self, minScale=40, maxScale=100, defScale=100, speed=3.0):
        self.__canvas.scaleProperties = (minScale,
         maxScale,
         defScale,
         speed)

    def setMarkerSettings(self, markerSettings, notify=False):
        self.as_setMarkerSettingsS(markerSettings)
        if notify:
            self.as_updateMarkersSettingsS()

    def setColorsSchemes(self, defaultSchemes, colorBlindSchemes):
        self.as_setColorSchemesS(defaultSchemes, colorBlindSchemes)

    def setColorBlindFlag(self, isColorBlind):
        self.as_setColorBlindS(isColorBlind)

    def setShowExInfoFlag(self, flag):
        if self.owner is None or not self.owner.isModalViewShown():
            self.as_setShowExInfoFlagS(flag)
        return

    def createMarker(self, symbol, matrixProvider=None, active=True):
        if active and matrixProvider is None:
            raise SoftException('Active marker {} must has matrixProvider'.format(symbol))
        markerID = self.__canvas.addMarker(matrixProvider, symbol, active)
        self.__ids.add(markerID)
        return markerID

    def setMarkerActive(self, markerID, active):
        if markerID in self.__ids:
            self.__canvas.markerSetActive(markerID, active)
        else:
            _logger.error('Marker %d is not added by given ID', markerID)

    def setMarkerSticky(self, markerID, isSticky):
        if self.__isStickyEnabled:
            self.__canvas.markerSetSticky(markerID, isSticky)

    def markerSetCustomStickyRadiusScale(self, markerID, scale):
        if self.__isStickyEnabled:
            self.__canvas.markerSetCustomStickyRadiusScale(markerID, scale)

    def setMarkerRenderInfo(self, markerID, minScale, bounds, innerBounds, cullDistance, markerBoundsScale):
        self.__canvas.markerSetRenderInfo(markerID, minScale, bounds, innerBounds, cullDistance, markerBoundsScale)

    def setMarkerLocationOffset(self, markerID, minYOffset, maxYOffset, distanceForMinYOffset, maxBoost, boostStart):
        self.__canvas.markerSetLocationOffset(markerID, minYOffset, maxYOffset, distanceForMinYOffset, maxBoost, boostStart)

    def setMarkerBoundCheckEnabled(self, markerID, enabled):
        self.__canvas.markerSetBoundCheckEnabled(markerID, enabled)

    def setMarkerObjectInFocus(self, markerID, inFocus):
        if not self.__isMarkerHoveringEnabled:
            return
        self.__canvas.markerSetMarkerObjectInFocus(markerID, inFocus)

    def setMarkerMinScale(self, markerID, minScale):
        self.__canvas.markerSetMinScale(markerID, minScale)

    def setMarkerMatrix(self, markerID, matrix):
        if markerID in self.__ids:
            self.__canvas.markerSetMatrix(markerID, matrix)
        else:
            _logger.error('Marker %d is not added by given ID', markerID)

    def destroyMarker(self, markerID):
        if self.__canvas:
            if markerID in self.__ids:
                self.__canvas.delMarker(markerID)
                self.__ids.discard(markerID)
            else:
                _logger.error('Marker %d is not added by given ID', markerID)

    def invokeMarker(self, markerID, *signature):
        if markerID in self.__ids:
            self.__canvas.markerInvoke(markerID, signature)
        else:
            _logger.error('Marker %d is not added by given ID', markerID)

    def updateCameraAimOffset(self, offset):
        self.__canvas.updateCameraAimOffset(offset)

    def setActiveCameraAimOffset(self, aimOffset):
        self.__canvas.activeCameraAimOffset = aimOffset

    def getPlugin(self, name):
        return self.__plugins.getPlugin(name) if self.__plugins is not None else None

    def startPlugins(self):
        sessionProvider = dependency.instance(IBattleSessionProvider)
        if sessionProvider is not None:
            arenaVisitor = sessionProvider.arenaVisitor
            self.__addCanvas(sessionProvider, arenaVisitor)
            self.__setMarkerDuration()
            self.__createPlugins(arenaVisitor)
        else:
            _logger.error('Could not create component due to data missing')
        return

    def stopPlugins(self):
        self.__destroyPlugins()
        self.__removeCanvas()

    def getCurrentlyAimedAtMarkerIDAndType(self):
        if not self.__isMarkerHoveringEnabled:
            return (INVALID_MARKER_ID, MarkerType.INVALID_MARKER_TYPE, INVALID_MARKER_SUBTYPE)
        else:
            aimedAtMarkerID = self.__canvas.getAimedAtMarker()
            if aimedAtMarkerID is None:
                return (INVALID_MARKER_ID, MarkerType.INVALID_MARKER_TYPE, INVALID_MARKER_SUBTYPE)
            for pluginName in self.__plugins:
                plugin = self.__plugins.getPlugin(pluginName)
                if plugin is None:
                    continue
                targetID = plugin.getTargetIDFromMarkerID(aimedAtMarkerID)
                if targetID > -1:
                    return (targetID, plugin.getMarkerType(), plugin.getMarkerSubtype(targetID))

            return (INVALID_MARKER_ID, MarkerType.INVALID_MARKER_TYPE, INVALID_MARKER_SUBTYPE)

    def createExternalComponent(self):
        super(MarkersManager, self).createExternalComponent()
        self.component.wg_inputKeyMode = InputKeyMode.NO_HANDLE
        self.component.position.z = DEPTH_OF_VehicleMarker
        self.component.drawWithRestrictedViewPort = False
        self.movie.backgroundAlpha = 0

    def _populate(self):
        super(MarkersManager, self)._populate()
        self.__isIBCEnabled = bool(self.settingsCore.getSetting(BattleCommStorageKeys.ENABLE_BATTLE_COMMUNICATION))
        self.__isStickyEnabled = bool(self.settingsCore.getSetting(BattleCommStorageKeys.SHOW_STICKY_MARKERS))
        self.__showBaseMarkers = bool(self.settingsCore.getSetting(BattleCommStorageKeys.SHOW_BASE_MARKERS))
        self.__showLocationMarkers = bool(self.settingsCore.getSetting(BattleCommStorageKeys.SHOW_LOCATION_MARKERS))
        self.settingsCore.onSettingsChanged += self.__onSettingsChange
        self.startPlugins()

    def _dispose(self):
        self.stopPlugins()
        self.settingsCore.onSettingsChanged -= self.__onSettingsChange
        super(MarkersManager, self)._dispose()

    def _createCanvas(self, arenaVisitor):
        return GUI.WGVehicleMarkersCanvasFlashAS3(self.movie)

    def _setupPlugins(self, arenaVisitor):
        setup = {'eventBus': plugins.EventBusPlugin,
         'equipments': plugins.EquipmentsMarkerPlugin,
         'vehiclesTargets': plugins.VehicleMarkerTargetPlugin,
         'controlMode': plugins.ControlModePlugin}
        if self.__showBaseMarkers:
            setup['teamAndControlPoints'] = plugins.TeamsOrControlsPointsPlugin
        if self.__showLocationMarkers:
            setup['area'] = plugins.AreaStaticMarkerPlugin
        if BattleReplay.g_replayCtrl.isPlaying:
            setup['vehiclesTargets'] = plugins.VehicleMarkerTargetPluginReplayPlaying
        if BattleReplay.g_replayCtrl.isRecording:
            setup['vehiclesTargets'] = plugins.VehicleMarkerTargetPluginReplayRecording
        if arenaVisitor.hasRespawns():
            setup['vehicles'] = vehicle_plugins.RespawnableVehicleMarkerPlugin
        else:
            setup['vehicles'] = vehicle_plugins.VehicleMarkerPlugin
        setup['settings'] = plugins.SettingsPlugin
        return setup

    def __addCanvas(self, sessionProvider, arenaVisitor):
        self.__canvas = self._createCanvas(arenaVisitor)
        self.__canvas.script = self
        self.__canvas.wg_inputKeyMode = InputKeyMode.NO_HANDLE
        self.__canvas.scaleProperties = GUI_SETTINGS.markerScaleSettings
        self.__canvas.enableMarkerHovering = self.__isMarkerHoveringEnabled
        self.__canvas.stickyMarkerRadiusScale = _STICKY_MARKER_RADIUS_SCALE
        self.__canvasProxy = weakref.ref(self.__canvas)
        self.component.addChild(self.__canvas, 'vehicleMarkersCanvas')
        g_eventBus.handleEvent(events.MarkersManagerEvent(events.MarkersManagerEvent.MARKERS_CREATED, self), EVENT_BUS_SCOPE.BATTLE)

    def __removeCanvas(self):
        if self.__canvas is not None:
            self.component.delChild(self.__canvas)
        self.__canvas = None
        self.__canvasProxy = None
        return

    def __setMarkerDuration(self):
        self.as_setMarkerDurationS(GUI_SETTINGS.markerHitSplashDuration)

    def __createPlugins(self, arenaVisitor):
        setup = self._setupPlugins(arenaVisitor)
        self.__plugins = PluginsCollection(self)
        self.__plugins.addPlugins(setup)
        self.__plugins.init()
        self.__plugins.start()

    def __destroyPlugins(self):
        if self.__plugins is not None:
            self.__plugins.stop()
            self.__plugins.fini()
        return

    def __onSettingsChange(self, diff):
        sessionProvider = dependency.instance(IBattleSessionProvider)
        isEventBattle = sessionProvider.arenaVisitor.gui.isEventBattle()
        addSettings = {}
        for item in diff:
            if item in (BattleCommStorageKeys.ENABLE_BATTLE_COMMUNICATION,
             BattleCommStorageKeys.SHOW_STICKY_MARKERS,
             BattleCommStorageKeys.SHOW_BASE_MARKERS,
             BattleCommStorageKeys.SHOW_LOCATION_MARKERS):
                addSettings[item] = diff[item]

        if not addSettings:
            return
        newIBCEnabled = bool(addSettings.get(BattleCommStorageKeys.ENABLE_BATTLE_COMMUNICATION, self.__isIBCEnabled))
        newShowBaseMarkers = bool(addSettings.get(BattleCommStorageKeys.SHOW_BASE_MARKERS, self.__showBaseMarkers)) or isEventBattle
        newIsSticky = bool(addSettings.get(BattleCommStorageKeys.SHOW_STICKY_MARKERS, self.__isStickyEnabled)) or isEventBattle
        new3DMarkers = bool(addSettings.get(BattleCommStorageKeys.SHOW_LOCATION_MARKERS, self.__showLocationMarkers))
        if newIBCEnabled != self.__isIBCEnabled:
            self.__isIBCEnabled = newIBCEnabled
            self.__canvas.enableMarkerHovering = self.__isMarkerHoveringEnabled
        if not newIsSticky:
            for markerId in self.__ids:
                self.__canvas.markerSetSticky(markerId, False)

        if newShowBaseMarkers != self.__showBaseMarkers or isEventBattle:
            self.__setPlugin(pluginName='teamAndControlPoints', startPlugin=newShowBaseMarkers)
            self.__showBaseMarkers = newShowBaseMarkers
        if new3DMarkers != self.__showLocationMarkers:
            self.__setPlugin(pluginName='area', startPlugin=new3DMarkers)
            self.__showLocationMarkers = new3DMarkers
        self.__isStickyEnabled = newIsSticky

    def __setPlugin(self, pluginName, startPlugin):
        plugin = self.__plugins.getPlugin(pluginName)
        if not plugin and startPlugin:
            self.__plugins.addPlugins({pluginName: self.setablePluginsDict[pluginName]})
            plugin = self.__plugins.getPlugin(pluginName)
            plugin.init()
        if startPlugin:
            plugin.start()
        elif plugin:
            plugin.stop()
