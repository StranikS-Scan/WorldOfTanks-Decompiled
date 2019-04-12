# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/markers2d/manager.py
import logging
import weakref
import GUI
import BattleReplay
from gui import DEPTH_OF_VehicleMarker, GUI_SETTINGS
from gui.Scaleform.daapi.view.battle.shared.markers2d import plugins
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings
from gui.Scaleform.daapi.view.external_components import ExternalFlashComponent
from gui.Scaleform.daapi.view.external_components import ExternalFlashSettings
from gui.Scaleform.daapi.view.meta.VehicleMarkersManagerMeta import VehicleMarkersManagerMeta
from gui.Scaleform.flash_wrapper import InputKeyMode
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.genConsts.ROOT_SWF_CONSTANTS import ROOT_SWF_CONSTANTS
from gui.shared.utils.plugins import PluginsCollection
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from soft_exception import SoftException
_logger = logging.getLogger(__name__)

class MarkersManager(ExternalFlashComponent, VehicleMarkersManagerMeta, plugins.IMarkersManager):

    def __init__(self):
        super(MarkersManager, self).__init__(ExternalFlashSettings(BATTLE_VIEW_ALIASES.MARKERS_2D, settings.MARKERS_MANAGER_SWF, 'root.vehicleMarkersCanvas', ROOT_SWF_CONSTANTS.BATTLE_VEHICLE_MARKERS_REGISTER_CALLBACK))
        self.__plugins = None
        self.__canvas = None
        self.__ids = set()
        return

    def setScaleProps(self, minScale=40, maxScale=100, defScale=100, speed=3.0):
        self.__canvas.scaleProperties = (minScale,
         maxScale,
         defScale,
         speed)

    def setAlphaProps(self, minAlpha=40, maxAlpha=100, defAlpha=100, speed=3.0):
        self.__canvas.alphaProperties = (minAlpha,
         maxAlpha,
         defAlpha,
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
        self.__canvas.markerSetSticky(markerID, isSticky)

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

    def getPlugin(self, name):
        return self.__plugins.getPlugin(name) if self.__plugins is not None else None

    def startPlugins(self):
        sessionProvider = dependency.instance(IBattleSessionProvider)
        if sessionProvider is not None:
            arenaVisitor = sessionProvider.arenaVisitor
            self.__addCanvas(arenaVisitor)
            self.__setMarkerDuration()
            self.__createPlugins(arenaVisitor)
        else:
            _logger.error('Could not create component due to data missing')
        return

    def stopPlugins(self):
        self.__destroyPlugins()
        self.__removeCanvas()

    def createExternalComponent(self):
        super(MarkersManager, self).createExternalComponent()
        self.component.wg_inputKeyMode = InputKeyMode.NO_HANDLE
        self.component.position.z = DEPTH_OF_VehicleMarker
        self.component.drawWithRestrictedViewPort = False
        self.movie.backgroundAlpha = 0

    def _populate(self):
        super(MarkersManager, self)._populate()
        self.startPlugins()

    def _dispose(self):
        self.stopPlugins()
        super(MarkersManager, self)._dispose()

    def _createCanvas(self, arenaVisitor):
        return GUI.WGVehicleMarkersCanvasFlashAS3(self.movie)

    def _setupPlugins(self, arenaVisitor):
        setup = {'settings': plugins.SettingsPlugin,
         'eventBus': plugins.EventBusPlugin,
         'equipments': plugins.EquipmentsMarkerPlugin,
         'area': plugins.AreaStaticMarkerPlugin,
         'vehiclesTargets': plugins.VehicleMarkerTargetPlugin}
        if BattleReplay.g_replayCtrl.isPlaying:
            setup['vehiclesTargets'] = plugins.VehicleMarkerTargetPluginReplayPlaying
        if BattleReplay.g_replayCtrl.isRecording:
            setup['vehiclesTargets'] = plugins.VehicleMarkerTargetPluginReplayRecording
        if arenaVisitor.hasRespawns():
            setup['vehicles'] = plugins.RespawnableVehicleMarkerPlugin
        else:
            setup['vehicles'] = plugins.VehicleMarkerPlugin
        return setup

    def __addCanvas(self, arenaVisitor):
        self.__canvas = self._createCanvas(arenaVisitor)
        self.__canvas.wg_inputKeyMode = InputKeyMode.NO_HANDLE
        self.__canvas.scaleProperties = GUI_SETTINGS.markerScaleSettings
        self.__canvas.alphaProperties = GUI_SETTINGS.markerBgSettings
        self.__canvasProxy = weakref.ref(self.__canvas)
        self.component.addChild(self.__canvas, 'vehicleMarkersCanvas')

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
