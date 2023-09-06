# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/collection/resources/common.py
import logging
from gui.collection.resources.cdn.cache import CollectionsCdnCacheMgr
from gui.collection.resources.local.cache import CollectionsLocalCacheMgr
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def makeCacheMgr(lobbyContext=None):
    settings = lobbyContext.getServerSettings()
    if settings.collectionsConfig.useCdnResourceCache:
        if settings.fileServer.getCollectionsContentConfigUrl():
            return CollectionsCdnCacheMgr()
        _logger.warning('External url not configured yet. The local cache will be used.')
    return CollectionsLocalCacheMgr()
