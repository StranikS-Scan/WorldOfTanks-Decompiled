# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/minimap/component.py
import weakref
import GUI
import Math
import SoundGroups
from debug_utils import LOG_WARNING
from AvatarInputHandler import AvatarInputHandler
from constants import IS_DEVELOPMENT
from gui.Scaleform.daapi.view.battle.shared.minimap import settings, plugins
from gui.Scaleform.daapi.view.meta.MinimapMeta import MinimapMeta
from gui.battle_control import minimap_utils, avatar_getter
from gui.shared.utils.plugins import PluginsCollection
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
_IMAGE_PATH_FORMATTER = 'img://{}'

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

    def __init__(self):
        super(MinimapComponent, self).__init__()
        self.__component = None
        self.__ids = set()
        self.__plugins = None
        return

    def setAttentionToCell(self, x, y, isRightClick):
        self.__plugins.setAttentionToCell(x, y, isRightClick)

    def applyNewSize(self, sizeIndex):
        self.__plugins.applyNewSize(sizeIndex)

    def addEntry(self, symbol, container, matrix=None, active=False, transformProps=settings.TRANSFORM_FLAG.DEFAULT):
        entryID = self.__component.addEntry(symbol, container, matrix, active, transformProps)
        if entryID:
            self.__ids.add(entryID)
        return entryID

    def delEntry(self, entryID):
        assert entryID in self.__ids, 'Entry is not added by given ID'
        self.__component.delEntry(entryID)
        self.__ids.discard(entryID)

    def invoke(self, entryID, *signature):
        assert entryID in self.__ids, 'Entry is not added by given ID'
        self.__component.entryInvoke(entryID, signature)

    def move(self, entryID, container):
        assert entryID in self.__ids, 'Entry is not added by given ID'
        self.__component.moveEntry(entryID, container)

    def setMatrix(self, entryID, matrix):
        assert entryID in self.__ids, 'Entry is not added by given ID'
        self.__component.entrySetMatrix(entryID, matrix)

    def setActive(self, entryID, active):
        assert entryID in self.__ids, 'Entry is not added by given ID'
        self.__component.entrySetActive(entryID, active)

    def playSound2D(self, soundID):
        if soundID:
            SoundGroups.g_instance.playSound2D(soundID)

    def isModalViewShown(self):
        return self.app is not None and self.app.isModalViewShown()

    def getPlugin(self, name):
        if self.__plugins is not None:
            return self.__plugins.getPlugin(name)
        else:
            return
            return

    def getPlugins(self):
        return self.__plugins

    def _populate(self):
        super(MinimapComponent, self)._populate()
        sessionProvider = dependency.instance(IBattleSessionProvider)
        arenaVisitor = sessionProvider.arenaVisitor
        arenaDP = sessionProvider.getArenaDP()
        if sessionProvider is not None and arenaVisitor is not None and arenaDP is not None:
            if self.__createComponent(arenaVisitor):
                setup = self._setupPlugins(arenaVisitor)
                self.__plugins = MinimapPluginsCollection(self)
                self.__plugins.addPlugins(setup)
                self.__plugins.init(weakref.proxy(arenaVisitor), weakref.proxy(arenaDP))
                self.__plugins.start()
        else:
            LOG_WARNING('Could not create component due to data missing: sessionProvider={}, arenaVisitor={}, arenaDP={}'.format(sessionProvider, arenaVisitor, arenaDP))
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
        """
        This method creates dict with minimap plugins.
        Override this method in child subclasses to add or replace plugins.
        :return: dict with plugins
        """
        setup = {'equipments': plugins.EquipmentsPlugin,
         'vehicles': plugins.ArenaVehiclesPlugin,
         'personal': plugins.PersonalEntriesPlugin}
        if IS_DEVELOPMENT:
            setup['teleport'] = plugins.TeleportPlugin
        return setup

    def __createComponent(self, arenaVisitor):
        self.__component = GUI.WGMinimapFlashAS3(self.app.movie, settings.MINIMAP_COMPONENT_PATH)
        if self.__component is None:
            return False
        else:
            self.__component.wg_inputKeyMode = 2
            self.app.component.addChild(self.__component, 'minimap')
            self.__component.mapSize = Math.Vector2(minimap_utils.MINIMAP_SIZE)
            bl, tr = arenaVisitor.type.getBoundingBox()
            self.__component.setArenaBB(bl, tr)
            self.as_setBackgroundS(_IMAGE_PATH_FORMATTER.format(arenaVisitor.type.getMinimapTexture()))
            return True

    def __destroyComponent(self):
        app = self.app
        if app is not None:
            app.component.delChild(self.__component)
        self.__component = None
        return


class MinimapPluginsCollection(PluginsCollection):
    settingsCore = dependency.descriptor(ISettingsCore)

    def init(self, arenaVisitor, arenaDP):
        super(MinimapPluginsCollection, self).init(arenaVisitor, arenaDP)

    def start(self):
        super(MinimapPluginsCollection, self).start()
        handler = avatar_getter.getInputHandler()
        if handler is not None:
            if isinstance(handler, AvatarInputHandler):
                handler.onCameraChanged += self.__onCameraChanged
                handler.onPostmortemVehicleChanged += self.__onPostmortemVehicleChanged
            self._invoke('initControlMode', handler.ctrlModeName, handler.ctrls.keys())
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        self._invoke('setSettings')
        return

    def stop(self):
        handler = avatar_getter.getInputHandler()
        if handler is not None:
            if isinstance(handler, AvatarInputHandler):
                handler.onCameraChanged -= self.__onCameraChanged
                handler.onPostmortemVehicleChanged -= self.__onPostmortemVehicleChanged
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        super(MinimapPluginsCollection, self).stop()
        return

    def setAttentionToCell(self, x, y, isRightClick):
        self._invoke('setAttentionToCell', x, y, isRightClick)

    def applyNewSize(self, sizeIndex):
        self._invoke('applyNewSize', sizeIndex)

    def __onSettingsChanged(self, diff):
        """
        Listener of event "ISettingsCore.onSettingsChanged".
        :param diff: dict containing pairs key-value that are changed.
        """
        self._invoke('updateSettings', diff)

    def __onPostmortemVehicleChanged(self, _):
        """
        Listener of event "AvatarInputHandler.onPostmortemVehicleChanged".
        
        That event is invoked at first time, after that should be invoke event
        "AvatarInputHandler.onPostmortemVehicleChanged" when avatar is moved
        to desired vehicle.
        
        :param _: long containing unique ID of vehicle's entity.
        """
        self._invoke('clearCamera')

    def __onCameraChanged(self, mode, vehicleID=0):
        """
        Listener of event "AvatarInputHandler.onCameraChanged".
        
        Resolves camera matrix and view point matrix.
        """
        self._invoke('updateControlMode', mode, vehicleID)
