# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/markers2d/manager.py
import weakref
import GUI
from account_helpers.settings_core import g_settingsCore
import constants
from debug_utils import LOG_CURRENT_EXCEPTION
from gui import DEPTH_OF_VehicleMarker, GUI_SETTINGS, g_guiResetters
from gui.Scaleform import SCALEFORM_SWF_PATH_V3
from gui.Scaleform.Flash import Flash
from gui.Scaleform.daapi.view.meta.VehicleMarkersManagerMeta import VehicleMarkersManagerMeta
from gui.Scaleform.framework.application import DAAPIRootBridge
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings
from gui.Scaleform.daapi.view.battle.shared.markers2d import plugins
from gui.battle_control import g_sessionProvider
from gui.doc_loaders import GuiColorsLoader
from gui.shared.events import GameEvent

class MarkersManager(Flash, VehicleMarkersManagerMeta, plugins.IMarkersManager):

    def __init__(self, parentUI):
        super(MarkersManager, self).__init__(settings.MARKERS_MANAGER_SWF, path=SCALEFORM_SWF_PATH_V3)
        self.component.wg_inputKeyMode = 2
        self.component.position.z = DEPTH_OF_VehicleMarker
        self.component.drawWithRestrictedViewPort = False
        self.movie.backgroundAlpha = 0
        self.__plugins = None
        self.__canvas = None
        self.__parentUI = parentUI
        self.__daapiBridge = DAAPIRootBridge('root.vehicleMarkersCanvas', 'registerMarkersManager')
        self.__daapiBridge.setPyScript(weakref.proxy(self))
        return

    def close(self):
        if self.__daapiBridge is not None:
            self.__daapiBridge.clear()
            self.__daapiBridge = None
        super(MarkersManager, self).close()
        return

    def setScaleProps(self, minScale=40, maxScale=100, defScale=100, speed=3.0):
        if constants.IS_DEVELOPMENT:
            self.__canvas.scaleProperties = (minScale,
             maxScale,
             defScale,
             speed)

    def setAlphaProps(self, minAlpha=40, maxAlpha=100, defAlpha=100, speed=3.0):
        if constants.IS_DEVELOPMENT:
            self.__canvas.alphaProperties = (minAlpha,
             maxAlpha,
             defAlpha,
             speed)

    def createMarker(self, mProv, symbol, active=True):
        return self.__canvas.addMarker(mProv, symbol, active)

    def setMarkerActive(self, handle, active):
        self.__canvas.markerSetActive(handle, active)

    def setMarkerMatrix(self, handle, matrix):
        self.__canvas.markerSetMatrix(handle, matrix)

    def destroyMarker(self, handle):
        if self.__canvas:
            self.__canvas.delMarker(handle)

    def invokeMarker(self, handle, function, args=None):
        if handle == -1:
            return
        else:
            if args is None:
                args = []
            self.__canvas.markerInvoke(handle, (function, args))
            return

    def getCanvasProxy(self):
        return self.__canvasProxy

    def _populate(self):
        super(MarkersManager, self)._populate()
        self.__addCanvas()
        self.__setMarkersScale()
        self.__setMarkerDuration()
        self.__setMarkerSettings()
        self.__setColorsSchemes(g_settingsCore.getSetting('isColorBlind'))
        self.__addListeners()

    def _dispose(self):
        self.__removeListeners()
        self.__removeCanvas()
        self.__parentUI = None
        super(MarkersManager, self)._dispose()
        return

    def __addCanvas(self):
        if g_sessionProvider.arenaVisitor.hasFlags():
            self.__canvas = GUI.WGVehicleFalloutMarkersCanvasFlashAS3(self.movie)
        else:
            self.__canvas = GUI.WGVehicleMarkersCanvasFlashAS3(self.movie)
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

    def __setMarkersScale(self, scale=None):
        if scale is None:
            scale = g_settingsCore.interfaceScale.get()
        stage = self.movie.stage
        stage.scaleX = scale
        stage.scaleY = scale
        return

    def __setMarkerDuration(self):
        self.as_setMarkerDurationS(GUI_SETTINGS.markerHitSplashDuration)

    def __setMarkerSettings(self, update=False):
        getter = g_settingsCore.getSetting
        self.as_setMarkerSettingsS({'enemy': getter('enemy'),
         'dead': getter('dead'),
         'ally': getter('ally')})
        if update:
            self.as_updateMarkersSettingsS()

    def __setColorsSchemes(self, isColorBlind):
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

        self.as_setColorSchemesS(defaultSchemes, colorBlindSchemes)
        self.as_setColorBlindS(isColorBlind)

    def __addListeners(self):
        self.__plugins = plugins.createPlugins(self)
        self.__plugins.init()
        self.__plugins.start()
        g_settingsCore.interfaceScale.onScaleChanged += self.__setMarkersScale
        self.addListener(GameEvent.SHOW_EXTENDED_INFO, self.__handleShowExtendedInfo, scope=settings.SCOPE)
        self.addListener(GameEvent.GUI_VISIBILITY, self.__handleGUIVisibility, scope=settings.SCOPE)
        self.addListener(GameEvent.MARKERS_2D_VISIBILITY, self.__handleMarkerVisibility, scope=settings.SCOPE)
        g_settingsCore.onSettingsChanged += self.__onSettingsChanged
        g_guiResetters.add(self.__onRecreateDevice)

    def __removeListeners(self):
        self.removeListener(GameEvent.SHOW_EXTENDED_INFO, self.__handleShowExtendedInfo, scope=settings.SCOPE)
        self.removeListener(GameEvent.GUI_VISIBILITY, self.__handleGUIVisibility, scope=settings.SCOPE)
        self.removeListener(GameEvent.MARKERS_2D_VISIBILITY, self.__handleMarkerVisibility, scope=settings.SCOPE)
        if self.__plugins is not None:
            self.__plugins.stop()
            self.__plugins.fini()
        g_settingsCore.interfaceScale.onScaleChanged -= self.__setMarkersScale
        g_settingsCore.onSettingsChanged -= self.__onSettingsChanged
        g_guiResetters.discard(self.__onRecreateDevice)
        return

    def __handleShowExtendedInfo(self, event):
        """Show extended vehicle information, when player press [Left Alt] key.
        Vehicle marker consists:
            - vehicle type (permanent);
            - nickname (extended);
            - health bar (extended);
            - vehicle name (extended);
            - vehicle level (extended and configure in settings);
            - vehicle icon (extended and configure in settings).
        """
        if self.__parentUI is None or not self.__parentUI.isModalViewShown():
            self.as_setShowExInfoFlagS(event.ctx['isDown'])
        return

    def __handleGUIVisibility(self, event):
        self.component.visible = event.ctx['visible']

    def __handleMarkerVisibility(self, _):
        """Special event toggles markers visibility only by key sequence CAPS + N (by default)
        and no any UI visible."""
        self.component.visible = not self.component.visible

    def __onSettingsChanged(self, diff):
        """Listener for event g_settingsCore.onSettingsChanged.
        :param diff: dictionary containing changes in settings."""
        if 'isColorBlind' in diff:
            self.as_setColorBlindS(diff['isColorBlind'])
        if 'enemy' in diff or 'dead' in diff or 'ally' in diff:
            self.__setMarkerSettings(True)

    def __onRecreateDevice(self):
        """Listener for event personality.onRecreateDevice."""
        self.__setMarkersScale()
