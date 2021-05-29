# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/view_helpers/emblems.py
from functools import partial
from enum import IntEnum
from gui.clans import settings as clan_settings
from gui.shared.image_helper import ImageHelper, readLocalImage
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext

def getClanEmblemURL(clanDbID, size):
    lobbyContext = dependency.instance(ILobbyContext)
    svrSettings = lobbyContext.getServerSettings()
    return svrSettings.fileServer.getClanEmblemBySize(clanDbID, size) if svrSettings is not None else None


class EmblemSize(IntEnum):
    SIZE_16 = 16
    SIZE_32 = 32
    SIZE_64 = 64
    SIZE_128 = 128
    SIZE_256 = 256


class ClanEmblemsHelper(ImageHelper):
    __default = {EmblemSize.SIZE_16: clan_settings.getDefaultEmblem16x16(),
     EmblemSize.SIZE_32: clan_settings.getDefaultEmblem32x32(),
     EmblemSize.SIZE_64: None,
     EmblemSize.SIZE_128: clan_settings.getDefaultEmblem128x128(),
     EmblemSize.SIZE_256: clan_settings.getDefaultEmblem256x256()}

    def requestClanEmblem16x16(self, clanDbID):
        self.__makeRequest(clanDbID, EmblemSize.SIZE_16, self.onClanEmblem16x16Received)

    def requestClanEmblem32x32(self, clanDbID):
        self.__makeRequest(clanDbID, EmblemSize.SIZE_32, self.onClanEmblem32x32Received)

    def requestClanEmblem64x64(self, clanDbID):
        self.__makeRequest(clanDbID, EmblemSize.SIZE_64, self.onClanEmblem64x64Received)

    def requestClanEmblem128x128(self, clanDbID):
        self.__makeRequest(clanDbID, EmblemSize.SIZE_128, self.onClanEmblem128x128Received)

    def requestClanEmblem256x256(self, clanDbID):
        self.__makeRequest(clanDbID, EmblemSize.SIZE_256, self.onClanEmblem256x256Received)

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
        return readLocalImage(self.__default.get(width, None))

    def __makeRequest(self, clanDbID, size, handler):
        url = getClanEmblemURL(clanDbID, size)
        cb = partial(handler, clanDbID)
        self.requestImageByUrl(url, cb, (size, size), self.getDefaultClanEmblem)
