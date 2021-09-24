# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/emblems.py
from adisp import process
from gui.battle_results.br_constants import EmblemType
from gui.shared.ClanCache import g_clanCache

class EmblemFetcher(object):
    __slots__ = ('_formationDBID', '_url', '_callback')

    def __init__(self, formationDBID):
        super(EmblemFetcher, self).__init__()
        self._formationDBID = formationDBID
        self._url = ''
        self._callback = None
        return

    def clear(self):
        self._callback = None
        return

    def fetch(self, callback):
        callback(None)
        return

    def getURL(self):
        return self._url


class ClanEmblemFetcher(EmblemFetcher):
    __slots__ = ('_url',)

    def __init__(self, formationDBID, textureID):
        super(ClanEmblemFetcher, self).__init__(formationDBID)
        self._url = textureID

    @process
    def fetch(self, callback):
        self._url = yield g_clanCache.getClanEmblemTextureID(self._formationDBID, False, self._url)
        callback(self._url)


def createFetcher(ctx):
    emblemType = ctx.getEmblemType()
    fetcher = None
    if emblemType == EmblemType.CLAN:
        fetcher = ClanEmblemFetcher(ctx.getFormationDBID(), ctx.getTextureID())
    return fetcher
