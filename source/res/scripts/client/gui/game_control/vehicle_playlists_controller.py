# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/vehicle_playlists_controller.py
import logging
import os
import BigWorld
import typing
import Event
from PlayerEvents import g_playerEvents
from helpers.local_cache import FileLocalCache
from params_schemas.veh_playlists_schema import vehPlaylistsConfigSchema
from skeletons.gui.game_control import IVehiclePlaylistsController
if typing.TYPE_CHECKING:
    from typing import Optional, Dict, Iterator, Tuple
_logger = logging.getLogger(__name__)

class _CurrentlyBeingModifiedData(object):

    def __init__(self):
        super(_CurrentlyBeingModifiedData, self).__init__()
        self.id = ''
        self.data = ''
        self.initial = ''
        self.isReallyChanged = False

    def clear(self):
        self.id = ''
        self.data = ''
        self.initial = ''
        self.isReallyChanged = False


class _VehiclePlaylistsCache(FileLocalCache):
    __VERSION = 1
    __SPACE = 'playlists_cache'

    def __init__(self, userDatabaseID):
        fileTags = ('playlists', userDatabaseID)
        super(_VehiclePlaylistsCache, self).__init__(self.__SPACE, fileTags, async=True)
        self.__filePath = self._buildLocalCachePath(self.__SPACE, fileTags)
        self.data = {}
        self.selectedID = ''

    def write(self):
        if self.data:
            super(_VehiclePlaylistsCache, self).write()
            return
        try:
            os.remove(self.__filePath)
        except OSError:
            _logger.debug("Playlist Data file '%s' deletion failed.", self.__filePath)

    def clear(self):
        self.data = None
        super(_VehiclePlaylistsCache, self).clear()
        return

    def _getCache(self):
        return (self.__VERSION, self.selectedID, self.data.copy())

    def _setCache(self, data):
        if not isinstance(data, tuple):
            _logger.warning('Unexpected data type %s of the cached data!', str(type(data)))
            return
        if len(data) != 3:
            _logger.warning('Expected len of cached data is 3, but received %d', len(data))
            return
        if self.__VERSION == data[0]:
            self.selectedID = data[1]
            self.data = data[2] or {}
            return
        self.data = {}
        self.selectedID = ''


class VehiclePlaylistsController(IVehiclePlaylistsController):

    def __init__(self):
        super(VehiclePlaylistsController, self).__init__()
        self.__eventManager = Event.EventManager()
        self.onEnabledStatusChanged = Event.Event(self.__eventManager)
        self.onModifiedPlaylistDiscarded = Event.Event(self.__eventManager)
        self.onDirtyClean = Event.Event(self.__eventManager)
        self.onPlaylistSaved = Event.Event(self.__eventManager)
        self.__isEnabled = False
        self.__cache = None
        self.__modifiedPlaylist = _CurrentlyBeingModifiedData()
        return

    def onLobbyStarted(self, ctx):
        if self.__cache is None:
            databaseID = BigWorld.player().databaseID if BigWorld.player() else 0
            if not databaseID:
                _logger.error("Couldn't obtain valid player.databaseID: %s", str(databaseID))
            self.__cache = _VehiclePlaylistsCache(databaseID)
            self.__cache.read()
            g_playerEvents.onConfigModelUpdated += self.__onConfigModelUpdated
            config = vehPlaylistsConfigSchema.getModel()
            if not config:
                return
            self.__isEnabled = config.isVehPlaylistsEnabled
        return

    def onDisconnected(self):
        self.clearModifiedPlaylist()
        self.__dispose()

    def fini(self):
        self.clearModifiedPlaylist()
        self.__eventManager.clear()
        self.__dispose()

    @property
    def isEnabled(self):
        return self.__isEnabled

    def getSelectedID(self):
        return '' if not self.isEnabled else self.__cache.selectedID

    def setSelectedID(self, val):
        if not self.isEnabled:
            return False
        self.__cache.selectedID = val
        self.__cache.write()
        return True

    def iterPlaylists(self):
        if self.isEnabled and self.__cache:
            for plID, pStrData in self.__cache.data.iteritems():
                yield (plID, pStrData)

    def updateModifiedPlaylist(self, plStrID, playlistData):
        if not self.isEnabled:
            return False
        if not plStrID:
            _logger.warning("Attempt to update modified playlist with invalid ID='%s'. ", plStrID)
            return False
        if not playlistData:
            _logger.warning("Attempt to  update modified playlist with invalid data='%s'. ", playlistData)
            return False
        self.__modifiedPlaylist.id = plStrID
        self.__modifiedPlaylist.data = playlistData
        return True

    def setInitialModifiedPlaylist(self, plStrID, playlistData):
        if not self.isEnabled:
            return False
        if not plStrID:
            _logger.warning("Attempt to update modified playlist with invalid ID='%s'. ", plStrID)
            return False
        if not playlistData:
            _logger.warning("Attempt to  update modified playlist with invalid data='%s'. ", playlistData)
            return False
        self.__modifiedPlaylist.initial = playlistData
        return True

    def clearModifiedPlaylist(self):
        if not self.__cache:
            return False
        self.__modifiedPlaylist.clear()
        self.onDirtyClean()
        return True

    def saveModifiedPlaylist(self):
        if not self.isEnabled:
            return tuple()
        if not self.__modifiedPlaylist.id:
            _logger.warning('Attempt to save empty playlist.')
            return tuple()
        playlisID = self.__modifiedPlaylist.id
        playlist = self.__modifiedPlaylist.data
        self.__cache.data[playlisID] = playlist
        self.setInitialModifiedPlaylist(playlisID, playlist)
        self.setSelectedID(playlisID)
        self.__cache.write()
        self.onPlaylistSaved(playlisID, playlist)
        return (playlisID, playlist)

    def setModifiedPlaylistChanged(self, isChanged):
        if not self.isEnabled:
            return False
        if not self.__modifiedPlaylist.id:
            return False
        if self.__modifiedPlaylist.isReallyChanged != isChanged:
            self.__modifiedPlaylist.isReallyChanged = isChanged
            return True
        return False

    @property
    def isModifiedPlaylistChanged(self):
        if not self.isEnabled:
            return False
        return False if not self.__modifiedPlaylist.id else self.__modifiedPlaylist.isReallyChanged

    def createPlaylist(self, plStrID, playlistData):
        if not self.isEnabled:
            return False
        if not plStrID:
            _logger.warning("Attempt to create playlist with invalid ID='%s'. ", plStrID)
            return False
        if not playlistData:
            _logger.warning("Attempt to create playlist with invalid data='%s'. ", playlistData)
            return False
        if plStrID in self.__cache.data:
            _logger.warning("Attempt to create playlist '%s' that is already in the storage. Previous one will be overridden", plStrID)
        self.__cache.data[plStrID] = playlistData
        self.setSelectedID(plStrID)
        return True

    def deletePlaylist(self, plStrID):
        if not self.isEnabled:
            return False
        if plStrID not in self.__cache.data:
            _logger.error("Couldn't delete nonexistent playlist '%s'", plStrID)
            return False
        del self.__cache.data[plStrID]
        if self.getSelectedID() == plStrID:
            self.setSelectedID('')
        if plStrID == self.__modifiedPlaylist.id:
            self.clearModifiedPlaylist()
        return True

    def getPlaylistDataByID(self, plStrID):
        if not self.isEnabled:
            return None
        else:
            plStrData = self.__cache.data.get(plStrID)
            if not plStrData:
                _logger.error("Couldn't get playlist by ID '%s'", plStrID)
                return None
            return plStrData

    def discardModifiedPlaylist(self):
        if not self.isEnabled:
            return False
        if not self.__modifiedPlaylist.initial:
            _logger.warning("Couldn't discard changes, initial modified list is incorrect '%s'", self.__modifiedPlaylist.initial)
            return False
        self.onModifiedPlaylistDiscarded(self.__modifiedPlaylist.id, self.__modifiedPlaylist.initial)
        self.clearModifiedPlaylist()
        return True

    def __setEnabledFeature(self, enabled):
        if self.__isEnabled == enabled:
            return
        self.__isEnabled = enabled
        if not self.__isEnabled:
            self.clearModifiedPlaylist()
        self.onEnabledStatusChanged(self.__isEnabled)

    def __dispose(self):
        if self.__cache is not None:
            self.__cache.clear()
            self.__cache = None
            g_playerEvents.onConfigModelUpdated -= self.__onConfigModelUpdated
        return

    def __onConfigModelUpdated(self, gpKey):
        if vehPlaylistsConfigSchema.gpKey == gpKey:
            config = vehPlaylistsConfigSchema.getModel()
            if not config:
                return
            self.__setEnabledFeature(config.isVehPlaylistsEnabled)
