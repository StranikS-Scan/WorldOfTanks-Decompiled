# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/markers2d/manager.py
import weakref
import GUI
from gui import DEPTH_OF_VehicleMarker, GUI_SETTINGS
from gui.Scaleform.daapi.view.meta.VehicleMarkersManagerMeta import VehicleMarkersManagerMeta
from gui.Scaleform.daapi.view.battle.shared.external_components import ExternalFlashComponent
from gui.Scaleform.daapi.view.battle.shared.external_components import ExternalFlashSettings
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings
from gui.Scaleform.daapi.view.battle.shared.markers2d import plugins
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.shared.utils.plugins import PluginsCollection
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class MarkersManager(ExternalFlashComponent, VehicleMarkersManagerMeta, plugins.IMarkersManager):
    """ Represents gui markers always displayed on top of the scene.
    Note: The pipeline is very similar to the minimap's pipeline. I.e. We request C++ flash UI
    component called WGVehicleMarkersCanvasFlash for creating and deleting markers by markerID (int).
    Access to an individual marker also performed via that markerID. We can directly
    invoke any flash function of each marker. The same is true for the whole manager object.
    For more details see the C++ class realization.
    """

    def __init__(self):
        super(MarkersManager, self).__init__(ExternalFlashSettings(BATTLE_VIEW_ALIASES.MARKERS_2D, settings.MARKERS_MANAGER_SWF, 'root.vehicleMarkersCanvas', 'registerMarkersManager'))
        self.component.wg_inputKeyMode = 2
        self.component.position.z = DEPTH_OF_VehicleMarker
        self.component.drawWithRestrictedViewPort = False
        self.movie.backgroundAlpha = 0
        self.__plugins = None
        self.__canvas = None
        self.__ids = set()
        return

    def setScaleProps(self, minScale=40, maxScale=100, defScale=100, speed=3.0):
        """Sets properties of scale for markers.
        :param minScale: minimum value of scale for markers.
        :param maxScale: maximum value of scale for markers.
        :param defScale: default value of scale for markers.
        :param speed: rate of decrease with distance to markers.
        """
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
        """ Sets new markers settings.
        :param markerSettings: dictionary containing markers settings.
        :param notify: if value equals True, than view of markers can be updated to check settings.
        """
        self.as_setMarkerSettingsS(markerSettings)
        if notify:
            self.as_updateMarkersSettingsS()

    def setColorsSchemes(self, defaultSchemes, colorBlindSchemes):
        """Sets new colors schemes of markers.
        :param defaultSchemes: dictionary containing colors schemes
            if player does not use setting "colorBlind".
        :param colorBlindSchemes: dictionary containing colors schemes
            if player uses setting "colorBlind".
        """
        self.as_setColorSchemesS(defaultSchemes, colorBlindSchemes)

    def setColorBlindFlag(self, isColorBlind):
        """ Sets setting "colorBlind".
        :param isColorBlind: bool.
        """
        self.as_setColorBlindS(isColorBlind)

    def setShowExInfoFlag(self, flag):
        """Show extended vehicle information. For example, player presses [Left Alt] key.
        :param flag: bool.
        Vehicle marker consists:
            - vehicle type (permanent);
            - nickname (extended);
            - health bar (extended);
            - vehicle name (extended);
            - vehicle level (extended and configure in settings);
            - vehicle icon (extended and configure in settings).
        """
        if self.owner is None or not self.owner.isModalViewShown():
            self.as_setShowExInfoFlagS(flag)
        return

    def createMarker(self, symbol, matrixProvider=None, active=True):
        """ Create Marker object and view in Flash by providing Matrix.
        :param symbol: string containing symbol of marker.
        :param matrixProvider: instance of matrix provider or None.
        :param active: bool.
        :return: integer containing unique ID of marker.
        """
        if active and matrixProvider is None:
            raise ValueError('Active marker {} must has matrixProvider'.format(symbol))
        markerID = self.__canvas.addMarker(matrixProvider, symbol, active)
        self.__ids.add(markerID)
        return markerID

    def setMarkerActive(self, markerID, active):
        """Sets active flag (visible property) to marker.
        :param markerID: marker handle
        :param active: is entry active (visible).
        """
        assert markerID in self.__ids, 'Marker is not added by given ID'
        self.__canvas.markerSetActive(markerID, active)

    def setMarkerMatrix(self, markerID, matrix):
        """Sets new matrix to specified marker.
        :param markerID: integer containing unique ID of marker.
        :param matrix: instance of Matrix or MatrixProvider.
        """
        assert markerID in self.__ids, 'Marker is not added by given ID'
        self.__canvas.markerSetMatrix(markerID, matrix)

    def destroyMarker(self, markerID):
        """Destroys 2D marker.
        :param markerID: integer containing unique ID of marker.
        """
        if self.__canvas:
            assert markerID in self.__ids, 'Marker is not added by given ID'
            self.__canvas.delMarker(markerID)
            self.__ids.discard(markerID)

    def invokeMarker(self, markerID, *signature):
        """Invokes desired method of marker in the Action Script.
        :param markerID: integer containing unique ID of marker.
        :param signature: tuple(<name of method in the Action Script>, *args)
        """
        assert markerID in self.__ids, 'Marker is not added by given ID'
        self.__canvas.markerInvoke(markerID, signature)

    def getPlugin(self, name):
        """Gets plugin by name.
        :param name: unique name of plugin.
        :return: instance of plugin or None.
        """
        if self.__plugins is not None:
            return self.__plugins.getPlugin(name)
        else:
            return
            return

    def startPlugins(self):
        sessionProvider = dependency.instance(IBattleSessionProvider)
        assert sessionProvider is not None, 'Session provider can not be None'
        arenaVisitor = sessionProvider.arenaVisitor
        assert arenaVisitor is not None, 'Arena visitor can not be None'
        self.__addCanvas(arenaVisitor)
        self.__setMarkerDuration()
        self.__createPlugins(arenaVisitor)
        return

    def stopPlugins(self):
        self.__destroyPlugins()
        self.__removeCanvas()

    def _populate(self):
        super(MarkersManager, self)._populate()
        self.startPlugins()

    def _dispose(self):
        self.stopPlugins()
        super(MarkersManager, self)._dispose()

    def _createCanvas(self, arenaVisitor):
        return GUI.WGVehicleMarkersCanvasFlashAS3(self.movie)

    def _setupPlugins(self, arenaVisitor):
        return {'settings': plugins.SettingsPlugin,
         'eventBus': plugins.EventBusPlugin,
         'vehicles': plugins.VehicleMarkerPlugin,
         'equipments': plugins.EquipmentsMarkerPlugin}

    def __addCanvas(self, arenaVisitor):
        self.__canvas = self._createCanvas(arenaVisitor)
        self.__canvas.wg_inputKeyMode = 2
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
