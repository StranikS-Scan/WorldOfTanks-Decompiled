# Embedded file name: scripts/client/gui/shared/view_helpers/emblems.py
import BigWorld
import ResMgr
from functools import partial
from debug_utils import LOG_WARNING, LOG_CURRENT_EXCEPTION
from club_shared import EMBLEM_TYPE
from gui import GUI_SETTINGS
from gui.LobbyContext import g_lobbyContext
from gui.shared.utils import mapTextureToTheMemory, getImageSize
from gui.clubs import settings as club_settings
from gui.clans import settings as clan_settings

def _readEmblem(filePath):
    data = ResMgr.openSection(filePath)
    if data is not None:
        return data.asBinary
    else:
        return


def _getClubEmblemUrl(emblemID, size):
    try:
        urlPattern = GUI_SETTINGS.lookup('clubEmblems')
        if urlPattern and emblemID:
            return urlPattern % {'emblemID': emblemID,
             'size': size}
    except:
        LOG_CURRENT_EXCEPTION()

    return None


class _EmblemsHelper(object):

    @property
    def remoteCache(self):
        from gui.shared.RemoteDataDownloader import g_remoteCache
        return g_remoteCache

    @classmethod
    def getMemoryTexturePath(cls, emblem):
        return mapTextureToTheMemory(emblem)

    @classmethod
    def requestEmblemByUrl(cls, url, size, callback, defaultEmblemGetter = None):
        defaultEmblemGetter = defaultEmblemGetter or (lambda v: None)

        def _onEmblemReceived(_, emblem):
            imgSize = getImageSize(emblem)
            if imgSize != size:
                LOG_WARNING('Received emblem has invalid size, use default instead', imgSize, size, url, type(emblem))
                emblem = defaultEmblemGetter(size)
            callback(emblem)

        if hasattr(BigWorld.player(), 'customFilesCache'):
            if url is not None:
                BigWorld.player().customFilesCache.get(url, _onEmblemReceived)
            else:
                BigWorld.callback(0.0, lambda : callback(defaultEmblemGetter(size)))
        else:
            LOG_WARNING('Trying to get emblem by url from non-account', url)
        return


class ClanEmblemsHelper(_EmblemsHelper):
    __default = {16: _readEmblem(clan_settings.getDefaultEmblem16x16()),
     32: _readEmblem(clan_settings.getDefaultEmblem32x32()),
     64: None,
     128: _readEmblem(clan_settings.getDefaultEmblem128x128()),
     256: _readEmblem(clan_settings.getDefaultEmblem256x256())}

    def requestClanEmblem16x16(self, clanDbID):
        self.__makeRequest(clanDbID, 16, self.onClanEmblem16x16Received)

    def requestClanEmblem32x32(self, clanDbID):
        self.__makeRequest(clanDbID, 32, self.onClanEmblem32x32Received)

    def requestClanEmblem64x64(self, clanDbID):
        self.__makeRequest(clanDbID, 64, self.onClanEmblem64x64Received)

    def requestClanEmblem128x128(self, clanDbID):
        self.__makeRequest(clanDbID, 128, self.onClanEmblem128x128Received)

    def requestClanEmblem256x256(self, clanDbID):
        self.__makeRequest(clanDbID, 256, self.onClanEmblem256x256Received)

    def onClanEmblem16x16Received(self, clanDbID, emblem):
        pass

    def onClanEmblem32x32Received(self, clanDbID, emblem):
        pass

    def onClanEmblem64x64Received(self, clanDbID, emblem):
        pass

    def onClanEmblem128x128Received(self, clanDbID, emblem):
        pass

    def onClanEmblem256x256Received(self, clanDbID, emblem):
        pass

    def getDefaultClanEmblem(self, size):
        width, _ = size
        return self.__default.get(width, None)

    def _requestClanEmblem(self, clanDbID, url, size, handler):
        cb = partial(handler, clanDbID)
        self.requestEmblemByUrl(url, (size, size), cb, self.getDefaultClanEmblem)

    def __makeRequest(self, clanDbID, size, requestHandler):
        svrSettings = g_lobbyContext.getServerSettings()
        url = svrSettings.fileServer.getClanEmblemBySize(clanDbID, size) if svrSettings is not None else None
        self._requestClanEmblem(clanDbID, url, size, requestHandler)
        return


class ClubEmblemsHelper(_EmblemsHelper):
    __default = {24: _readEmblem(club_settings.getDefaultEmblem24x24()),
     32: _readEmblem(club_settings.getDefaultEmblem32x32()),
     64: _readEmblem(club_settings.getDefaultEmblem64x64())}
    __stubs = {24: _readEmblem(club_settings.getStubEmblem24x24()),
     32: _readEmblem(club_settings.getStubEmblem32x32()),
     64: _readEmblem(club_settings.getStubEmblem64x64())}

    def requestClubEmblem24x24(self, clubDbID, emblemID, callback = None):
        self._requestClubEmblem(clubDbID, emblemID, 24, self.onClubEmblem24x24Received, callback)

    def requestClubEmblem32x32(self, clubDbID, emblemID, callback = None):
        self._requestClubEmblem(clubDbID, emblemID, 32, self.onClubEmblem32x32Received, callback)

    def requestClubEmblem64x64(self, clubDbID, emblemID, callback = None):
        self._requestClubEmblem(clubDbID, emblemID, 64, self.onClubEmblem64x64Received, callback)

    def onClubEmblem24x24Received(self, clubDbID, emblem):
        pass

    def onClubEmblem32x32Received(self, clubDbID, emblem):
        pass

    def onClubEmblem64x64Received(self, clubDbID, emblem):
        pass

    def getDefaultClubEmblem(self, size):
        width, _ = size
        return self.__stubs.get(width)

    def _requestClubEmblem(self, clubDbID, emblemID, size, handler, callback):
        cb = partial(self.__onEmblemReceived, handler, callback, clubDbID)
        url = _getClubEmblemUrl(emblemID, size)
        if url:
            self.requestEmblemByUrl(url, (size, size), cb, self.getDefaultClubEmblem)
        else:
            self._doDefaultResponse(cb, size)

    def _doDefaultResponse(self, callback, size):
        BigWorld.callback(0.0, lambda : callback(self.__default.get(size)))

    def __onEmblemReceived(self, handler, callback, clubDbID, emblem):
        handler(clubDbID, emblem)
        if callback is not None:
            callback(clubDbID, emblem)
        return
