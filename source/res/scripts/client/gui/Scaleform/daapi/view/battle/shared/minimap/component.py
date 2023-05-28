# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/minimap/component.py
import logging
import weakref
import GUI
import Math
import SoundGroups
from AvatarInputHandler import AvatarInputHandler
from gui.Scaleform.daapi.view.battle.shared.map_zones.minimap import MapZonesEntriesPlugin
from gui.Scaleform.daapi.view.battle.shared.minimap import settings, plugins
from gui.Scaleform.daapi.view.meta.MinimapMeta import MinimapMeta
from gui.Scaleform.flash_wrapper import InputKeyMode
from gui.battle_control import minimap_utils, avatar_getter
from gui.shared.utils.plugins import PluginsCollection
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
_IMAGE_PATH_FORMATTER = 'img://{}'
_logger = logging.getLogger(__name__)
_DEFUALT_MINIMAP_DIMENSION = 10

class IMinimapComponent(object):

    def addEntry(self, symbol, container, matrix=None, active=False, transformProps=settings.TRANSFORM_FLAG.DEFAULT):
        raise NotImplementedError

    def delEntry(self, entryID):
        raise NotImplementedError

    def invoke(self, entryID, *signature):
        raise NotImplementedError

    def move(self, entryID, container):
        raise NotImplementedError

    def setMatrix(self, entryID, matrix):
        raise NotImplementedError

    def setActive(self, entryID, active):
        raise NotImplementedError

    def playSound2D(self, soundID):
        raise NotImplementedError


class MinimapComponent(MinimapMeta, IMinimapComponent):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(MinimapComponent, self).__init__()
        self.__component = None
        self.__ids = set()
        self.__plugins = None
        return

    def onMinimapClicked(self, x, y, buttonIdx, minimapScaleIndex):
        self.__plugins.onMinimapClicked(x, y, buttonIdx, minimapScaleIndex)

    def applyNewSize(self, sizeIndex):
        if self.__plugins is not None:
            self.__plugins.applyNewSize(sizeIndex)
        return

    def addEntry(self, symbol, container, matrix=None, active=False, transformProps=settings.TRANSFORM_FLAG.DEFAULT):
        entryID = self.__component.addEntry(symbol, container, matrix, active, transformProps)
        if entryID:
            self.__ids.add(entryID)
        return entryID

    def delEntry(self, entryID):
        if entryID in self.__ids:
            self.__component.delEntry(entryID)
            self.__ids.discard(entryID)
        else:
            self.__logEntryError(entryID)

    def invoke(self, entryID, *signature):
        if entryID in self.__ids:
            self.__component.entryInvoke(entryID, signature)
        else:
            self.__logEntryError(entryID)

    def move(self, entryID, container):
        if entryID in self.__ids:
            self.__component.moveEntry(entryID, container)
        else:
            self.__logEntryError(entryID)

    def setMatrix(self, entryID, matrix):
        if entryID in self.__ids:
            self.__component.entrySetMatrix(entryID, matrix)
        else:
            self.__logEntryError(entryID)

    def setActive(self, entryID, active):
        if entryID in self.__ids:
            self.__component.entrySetActive(entryID, active)
        else:
            self.__logEntryError(entryID)

    def playSound2D(self, soundID):
        if soundID:
            SoundGroups.g_instance.playSound2D(soundID)

    def isModalViewShown(self):
        return self.app is not None and self.app.isModalViewShown()

    def canChangeAlpha(self):
        return True

    def getPlugin(self, name):
        return self.__plugins.getPlugin(name) if self.__plugins is not None else None

    def getPlugins(self):
        return self.__plugins

    def getComponent(self, *_):
        return self.__component

    def getBoundingBox(self):
        arenaVisitor = self.sessionProvider.arenaVisitor
        bl, tr = arenaVisitor.type.getBoundingBox()
        if arenaVisitor.gui.isBootcampBattle():
            topRightX, topRightY = tr
            bottomLeftX, bottomLeftY = bl
            vSide = topRightX - bottomLeftX
            hSide = topRightY - bottomLeftY
            if vSide > hSide:
                bl = (bottomLeftX, bottomLeftX)
                tr = (topRightX, topRightX)
            else:
                bl = (bottomLeftY, bottomLeftY)
                tr = (topRightY, topRightY)
        return (bl, tr)

    @classmethod
    def getImagePath(cls, minimapTexture):
        return _IMAGE_PATH_FORMATTER.format(minimapTexture)

    def _populate(self):
        super(MinimapComponent, self)._populate()
        arenaVisitor = self.sessionProvider.arenaVisitor
        arenaDP = self.sessionProvider.getArenaDP()
        if self.sessionProvider is not None and arenaVisitor is not None and arenaDP is not None:
            if self.__createComponent(arenaVisitor):
                setup = self._setupPlugins(arenaVisitor)
                self.__plugins = MinimapPluginsCollection(self)
                self.__plugins.addPlugins(setup)
                self.__plugins.init(weakref.proxy(arenaVisitor), weakref.proxy(arenaDP))
                self.__plugins.start()
        else:
            _logger.error('Could not create component due to data missing: %r, %r, %r', self.sessionProvider, arenaVisitor, arenaDP)
        return

    def _dispose(self):
        for entryID in self.__ids:
            self.__component.delEntry(entryID)

        if self.__plugins is not None:
            self.__plugins.stop()
            self.__plugins.fini()
        self.__ids.clear()
        self.__destroyComponent()
        super(MinimapComponent, self)._dispose()
        return

    def _setupPlugins(self, arenaVisitor):
        setup = {'equipments': plugins.EquipmentsPlugin,
         'vehicles': plugins.ArenaVehiclesPlugin,
         'personal': plugins.PersonalEntriesPlugin,
         'area': plugins.AreaStaticMarkerPlugin,
         'area_markers': plugins.AreaMarkerEntriesPlugin,
         'spgShot': plugins.EnemySPGShotPlugin,
         'map_zones': MapZonesEntriesPlugin}
        return setup

    def _createFlashComponent(self):
        return GUI.WGMinimapFlashAS3(self.app.movie, settings.MINIMAP_COMPONENT_PATH)

    def _getMinimapSize(self):
        return minimap_utils.MINIMAP_SIZE

    def _getFlashName(self):
        pass

    def _getMinimapTexture(self, arenaVisitor):
        return self.getImagePath(arenaVisitor.type.getMinimapTexture())

    def _processMinimapSize(self, minSize, maxSize):
        pass

    def __createComponent(self, arenaVisitor):
        self.__component = self._createFlashComponent()
        if self.__component is None:
            return False
        else:
            self.__component.wg_inputKeyMode = InputKeyMode.NO_HANDLE
            self.app.component.addChild(self.__component, self._getFlashName())
            bl, tr = self.getBoundingBox()
            self.__component.setArenaBB(bl, tr)
            self._processMinimapSize(bl, tr)
            self.__component.mapSize = Math.Vector2(self._getMinimapSize())
            self.as_setBackgroundS(self._getMinimapTexture(arenaVisitor))
            return True

    def __destroyComponent(self):
        app = self.app
        if app is not None and self.__component is not None:
            app.component.delChild(self.__component)
        self.__component = None
        return

    def __logEntryError(self, entryID):
        _logger.error('Entry is not added by given ID = %d, available = %r', entryID, self.__ids)

    def hasMinimapGrid(self):
        return False

    def getMinimapDimensions(self):
        return _DEFUALT_MINIMAP_DIMENSION

    def getCellIdFromPosition(self, position, boundingBox):
        return None

    def getCellName(self, cellId):
        pass


class MinimapPluginsCollection(PluginsCollection):
    settingsCore = dependency.descriptor(ISettingsCore)

    def start(self):
        super(MinimapPluginsCollection, self).start()
        handler = avatar_getter.getInputHandler()
        if handler is not None:
            if isinstance(handler, AvatarInputHandler):
                handler.onCameraChanged += self.__onCameraChanged
            self._invoke('initControlMode', handler.ctrlModeName, handler.ctrls.keys())
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        self._invoke('setSettings')
        return

    def stop(self):
        handler = avatar_getter.getInputHandler()
        if handler is not None:
            if isinstance(handler, AvatarInputHandler):
                handler.onCameraChanged -= self.__onCameraChanged
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        super(MinimapPluginsCollection, self).stop()
        return

    def onMinimapClicked(self, x, y, buttonIdx, minimapScaleIndex):
        self._invoke('onMinimapClicked', x, y, buttonIdx, minimapScaleIndex)

    def applyNewSize(self, sizeIndex):
        self._invoke('applyNewSize', sizeIndex)

    def __onSettingsChanged(self, diff):
        self._invoke('updateSettings', diff)

    def __onCameraChanged(self, mode, vehicleID=0):
        self._invoke('updateControlMode', mode, vehicleID)
