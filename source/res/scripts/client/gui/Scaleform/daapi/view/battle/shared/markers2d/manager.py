# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/markers2d/manager.py
import logging
import weakref
import BattleReplay
import GUI
from chat_commands_consts import INVALID_MARKER_SUBTYPE, MarkerType, INVALID_MARKER_ID
from gui import DEPTH_OF_VehicleMarker, GUI_SETTINGS
from gui.Scaleform.daapi.view.battle.shared.map_zones.markers2d import MapZonesPlugin
from gui.Scaleform.daapi.view.battle.shared.markers2d import plugins, vehicle_plugins
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import MarkerPlugin
from gui.Scaleform.daapi.view.battle.shared.markers2d.settings import CommonMarkerType
from gui.Scaleform.daapi.view.external_components import ExternalFlashComponent
from gui.Scaleform.daapi.view.external_components import ExternalFlashSettings
from gui.Scaleform.daapi.view.meta.VehicleMarkersManagerMeta import VehicleMarkersManagerMeta
from gui.Scaleform.flash_wrapper import InputKeyMode
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.genConsts.ROOT_SWF_CONSTANTS import ROOT_SWF_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import MarkersManagerEvent
from gui.shared.utils.plugins import PluginsCollection
from helpers import dependency, isPlayerAvatar
from skeletons.account_helpers.settings_core import IBattleCommunicationsSettings
from skeletons.gui.battle_session import IBattleSessionProvider
from soft_exception import SoftException
from helpers.CallbackDelayer import CallbackDelayer
_logger = logging.getLogger(__name__)
_STICKY_MARKER_RADIUS_SCALE = 0.7

class MarkersManager(ExternalFlashComponent, VehicleMarkersManagerMeta, plugins.IMarkersManager, CallbackDelayer):
    MARKERS_MANAGER_SWF = 'battleVehicleMarkersApp.swf'
    battleCommunications = dependency.descriptor(IBattleCommunicationsSettings)
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    setablePluginsDict = {'area': plugins.AreaStaticMarkerPlugin,
     'teamAndControlPoints': plugins.TeamsOrControlsPointsPlugin}

    def __init__(self, settings=None):
        if settings is None:
            settings = ExternalFlashSettings(BATTLE_VIEW_ALIASES.MARKERS_2D, self.MARKERS_MANAGER_SWF, 'root.vehicleMarkersCanvas', ROOT_SWF_CONSTANTS.BATTLE_VEHICLE_MARKERS_REGISTER_CALLBACK)
        super(MarkersManager, self).__init__(settings)
        self.__plugins = None
        self.__canvas = None
        self.__ids = set()
        self.__isIBCEnabled = False
        self.__isStickyEnabled = False
        self.__showBaseMarkers = False
        self.__showLocationMarkers = False
        CallbackDelayer.__init__(self)
        return

    @property
    def _isMarkerHoveringEnabled(self):
        sessionProvider = dependency.instance(IBattleSessionProvider)
        return self.__isIBCEnabled and not sessionProvider.getCtx().isPlayerObserver()

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

    def createMarker(self, symbol, matrixProvider=None, active=True, markerType=CommonMarkerType.NORMAL):
        if active and matrixProvider is None:
            raise SoftException('Active marker {} must has matrixProvider'.format(symbol))
        markerID = self.__canvas.addMarker(matrixProvider, symbol, active, markerType)
        self.__ids.add(markerID)
        return markerID

    def setMarkerActive(self, markerID, active):
        if markerID in self.__ids:
            self.__canvas.markerSetActive(markerID, active)
        else:
            _logger.error('Marker %d is not added by given ID. Ids: %s. Active: %d', markerID, self.__ids, active)

    def setMarkerSticky(self, markerID, isSticky):
        if self.__isStickyEnabled and self.__isIBCEnabled:
            self.__canvas.markerSetSticky(markerID, isSticky)

    def setMarkerRenderInfo(self, markerID, minScale, bounds, innerBounds, cullDistance, markerBoundsScale):
        self.__canvas.markerSetRenderInfo(markerID, minScale, bounds, innerBounds, cullDistance, markerBoundsScale)

    def setMarkerLocationOffset(self, markerID, minYOffset, maxYOffset, distanceForMinYOffset, maxBoost, boostStart):
        self.__canvas.markerSetLocationOffset(markerID, minYOffset, maxYOffset, distanceForMinYOffset, maxBoost, boostStart)

    def setMarkerBoundCheckEnabled(self, markerID, enabled):
        self.__canvas.markerSetBoundCheckEnabled(markerID, enabled)

    def setMarkerObjectInFocus(self, markerID, inFocus):
        if not self._isMarkerHoveringEnabled:
            return
        self.__canvas.markerSetMarkerObjectInFocus(markerID, inFocus)

    def setMarkerMinScale(self, markerID, minScale):
        self.__canvas.markerSetMinScale(markerID, minScale)

    def setMarkerMatrix(self, markerID, matrix):
        if markerID in self.__ids:
            self.__canvas.markerSetMatrix(markerID, matrix)
        else:
            _logger.error('Marker %d is not added by given ID. Ids: %s. Matrix: %s', markerID, self.__ids, matrix)

    def destroyMarker(self, markerID):
        if self.__canvas:
            if markerID in self.__ids:
                self.__canvas.delMarker(markerID)
                self.__ids.discard(markerID)
            else:
                _logger.error('Marker %d is not added by given ID. Ids: %s', markerID, self.__ids)

    def invokeMarker(self, markerID, *signature):
        if markerID in self.__ids:
            self.__canvas.markerInvoke(markerID, signature)
        else:
            _logger.error('Marker %d is not added by given ID. Ids: %s. Signature: %s', markerID, self.__ids, signature)

    def updateCameraAimOffset(self, offset):
        self.__canvas.updateCameraAimOffset(offset)

    def setActiveCameraAimOffset(self, aimOffset):
        self.__canvas.activeCameraAimOffset = aimOffset

    def setIsPivotAtCameraForMarkers(self, isPivotAtCamera):
        self.__canvas.setIsPivotAtCamera(isPivotAtCamera)

    def getPlugin(self, name):
        return self.__plugins.getPlugin(name) if self.__plugins is not None else None

    def startPlugins(self):
        if not isPlayerAvatar():
            log = _logger.warning if BattleReplay.g_replayCtrl.isPlaying else _logger.error
            log('Failed to start plugins for %s', self.__class__.__name__)
            return
        else:
            sessionProvider = dependency.instance(IBattleSessionProvider)
            if sessionProvider is not None:
                arenaVisitor = sessionProvider.arenaVisitor
                self.__addCanvas(sessionProvider, arenaVisitor)
                self.__setMarkerDuration()
                self.__createPlugins(arenaVisitor)
                self.fireEvent(MarkersManagerEvent(MarkersManagerEvent.MARKERS_CREATED, self), EVENT_BUS_SCOPE.BATTLE)
            else:
                _logger.error('Could not create component due to data missing')
            return

    def stopPlugins(self):
        self.__destroyPlugins()
        self.__removeCanvas()

    def getCurrentlyAimedAtMarkerIDAndType(self):
        if not self._isMarkerHoveringEnabled:
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
                    return (targetID, plugin.getMarkerType(aimedAtMarkerID), plugin.getMarkerSubtype(targetID))

            return (INVALID_MARKER_ID, MarkerType.INVALID_MARKER_TYPE, INVALID_MARKER_SUBTYPE)

    def createExternalComponent(self):
        super(MarkersManager, self).createExternalComponent()
        self.component.wg_inputKeyMode = InputKeyMode.NO_HANDLE
        self.component.position.z = DEPTH_OF_VehicleMarker
        self.component.drawWithRestrictedViewPort = False
        self.movie.backgroundAlpha = 0

    def _populate(self):
        super(MarkersManager, self)._populate()
        self.__isIBCEnabled = bool(self.battleCommunications.isEnabled)
        self.__isStickyEnabled = bool(self.battleCommunications.showStickyMarkers)
        self.__showBaseMarkers = bool(self.battleCommunications.showBaseMarkers)
        self.__showLocationMarkers = bool(self.battleCommunications.showLocationMarkers)
        self.battleCommunications.onChanged += self.__onBattleCommunicationSettingsChanged
        self.startPlugins()

    def _dispose(self):
        CallbackDelayer.destroy(self)
        self.stopPlugins()
        self.battleCommunications.onChanged -= self.__onBattleCommunicationSettingsChanged
        super(MarkersManager, self)._dispose()

    def _createCanvas(self, arenaVisitor):
        return GUI.WGVehicleMarkersCanvasFlashAS3(self.movie)

    def _setupPlugins(self, arenaVisitor):
        setup = {'eventBus': plugins.EventBusPlugin,
         'equipments': plugins.EquipmentsMarkerPlugin,
         'vehiclesTargets': plugins.VehicleMarkerTargetPlugin,
         'controlMode': plugins.ControlModePlugin,
         'area_markers': plugins.AreaMarkerPlugin}
        if self.__showBaseMarkers:
            setup['teamAndControlPoints'] = plugins.TeamsOrControlsPointsPlugin
        if self.__showLocationMarkers:
            setup['area'] = plugins.AreaStaticMarkerPlugin
        if BattleReplay.g_replayCtrl.isPlaying:
            setup['vehiclesTargets'] = plugins.VehicleMarkerTargetPluginReplayPlaying
        if BattleReplay.g_replayCtrl.isRecording:
            setup['vehiclesTargets'] = plugins.VehicleMarkerTargetPluginReplayRecording
        if arenaVisitor.hasRespawns() or arenaVisitor.isEnableExternalRespawn():
            setup['vehicles'] = vehicle_plugins.RespawnableVehicleMarkerPlugin
        else:
            setup['vehicles'] = vehicle_plugins.VehicleMarkerPlugin
        setup['settings'] = plugins.SettingsPlugin
        setup['map_zones'] = MapZonesPlugin
        return setup

    def __addCanvas(self, sessionProvider, arenaVisitor):
        self.__canvas = self._createCanvas(arenaVisitor)
        self.__canvas.script = self
        self.__canvas.wg_inputKeyMode = InputKeyMode.NO_HANDLE
        self.__canvas.scaleProperties = GUI_SETTINGS.markerScaleSettings
        self.__canvas.enableMarkerHovering = self._isMarkerHoveringEnabled
        self.__canvas.stickyMarkerRadiusScale = _STICKY_MARKER_RADIUS_SCALE
        self.__canvasProxy = weakref.ref(self.__canvas)
        self.component.addChild(self.__canvas, 'vehicleMarkersCanvas')
        self.__canvas.setMetersLocalization(' ' + backport.text(R.strings.ingame_gui.marker.meters()))

    def __removeCanvas(self):
        if self.__canvas is not None:
            self.component.delChild(self.__canvas)
        self.__canvas = None
        self.__canvasProxy = None
        return

    def __setMarkerDuration(self):
        self.as_setMarkerDurationS(GUI_SETTINGS.markerHitSplashDuration)

    def onMarkerBeingHovered(self, isHovered):
        self.delayCallback(0.0, self.__markerWasHovered, isHovered)

    def __markerWasHovered(self, isHovered):
        targetID, _, _ = self.getCurrentlyAimedAtMarkerIDAndType()
        if self.guiSessionProvider.shared.spectator:
            self.guiSessionProvider.shared.spectator.markerWasHovered(isHovered, targetID)

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

    def __onBattleCommunicationSettingsChanged(self):
        newIBCEnabled = bool(self.battleCommunications.isEnabled)
        newShowBaseMarkers = bool(self.battleCommunications.showBaseMarkers)
        newIsSticky = bool(self.battleCommunications.showStickyMarkers)
        new3DMarkers = bool(self.battleCommunications.showLocationMarkers)
        if newIBCEnabled != self.__isIBCEnabled:
            self.__isIBCEnabled = newIBCEnabled
            self.__canvas.enableMarkerHovering = self._isMarkerHoveringEnabled
        if not newIsSticky:
            for markerId in self.__ids:
                self.__canvas.markerSetSticky(markerId, False)

        if newShowBaseMarkers != self.__showBaseMarkers:
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


class KillCamMarkersManager(MarkersManager):

    def __init__(self):
        super(KillCamMarkersManager, self).__init__(settings=ExternalFlashSettings(BATTLE_VIEW_ALIASES.MARKERS_2D, self.MARKERS_MANAGER_SWF, 'root.vehicleMarkersCanvas', ROOT_SWF_CONSTANTS.BATTLE_VEHICLE_MARKERS_REGISTER_CALLBACK))

    def _setupPlugins(self, arenaVisitor):
        super(KillCamMarkersManager, self)._setupPlugins(arenaVisitor)
        setup = {'settings': plugins.SettingsPlugin}
        return setup
