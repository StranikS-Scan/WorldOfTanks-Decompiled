# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/clans/clan_cache.py
from collections import namedtuple
import typing
import BigWorld
from Event import Event
from account_helpers import getAccountDatabaseID
from adisp import adisp_async, adisp_process
from constants import CLAN_MEMBER_FLAGS
from debug_utils import LOG_ERROR
from helpers import dependency
from helpers import html
from gui.clans.formatters import getClanRoleString
from gui.shared.utils import code2str
from messenger.ext import passCensor
from messenger.storage import storage_getter
from shared_utils import CONST_CONTAINER
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.clans.cache_providers.base_provider import IBaseProvider

class ProviderNames(CONST_CONTAINER):
    STRONGHOLD = 'STRONGHOLD'
    MISSIONS = 'MISSIONS'
    STRONGHOLD_EVENT = 'STRONGHOLD_EVENT'


class ClanInfo(namedtuple('ClanInfo', ['clanName',
 'clanAbbrev',
 'chatChannelDBID',
 'memberFlags',
 'enteringTime'])):

    def getClanName(self):
        return self.clanName

    def getClanAbbrev(self):
        return self.clanAbbrev

    def getMembersFlags(self):
        return self.memberFlags

    def getJoiningTime(self):
        return self.enteringTime


class _ClanCache(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self.__waitForSync = False
        self.__clanMembersLen = None
        self.__clanMotto = ''
        self.__clanDescription = ''
        self.__providers = {}
        self.onSyncStarted = Event()
        self.onSyncCompleted = Event()
        return

    def init(self):
        from gui.clans.cache_providers.stronghold_provider import ClientStrongholdProvider
        from gui.clans.cache_providers.missions_provider import ClientMissionsProvider
        from gui.clans.cache_providers.stronghold_event_provider import StrongholdEventProvider
        for name, clazz, args in ((ProviderNames.STRONGHOLD, ClientStrongholdProvider, ()), (ProviderNames.MISSIONS, ClientMissionsProvider, ()), (ProviderNames.STRONGHOLD_EVENT, StrongholdEventProvider, (self,))):
            self.__registerProvider(name, clazz, args)

    def fini(self):
        self.onSyncStarted.clear()
        self.onSyncCompleted.clear()
        self.__stopProviders(withClear=True)
        self.__providers.clear()

    def onAccountShowGUI(self):
        self.__startProviders()

    def onAvatarBecomePlayer(self):
        self.__stopProviders()

    def onDisconnected(self):
        self.__stopProviders(withClear=True)

    @property
    def waitForSync(self):
        return self.__waitForSync

    @adisp_async
    def update(self, diff=None, callback=None):
        self.__invalidateData(diff, callback)

    def clear(self):
        self.__stopProviders()

    @storage_getter('users')
    def usersStorage(self):
        return None

    @property
    def clanDBID(self):
        return self.itemsCache.items.stats.clanDBID

    @property
    def isInClan(self):
        return self.clanDBID is not None and self.clanDBID != 0

    @property
    def clanMembers(self):
        members = set()
        if self.isInClan:
            members = set(self.usersStorage.getClanMembersIterator(False))
        return members

    @property
    def clanInfo(self):
        info = self.itemsCache.items.stats.clanInfo
        return info if info and len(info) > 1 else (None, None, -1, 0, 0)

    @property
    def clanName(self):
        return passCensor(html.escape(self.clanInfo[0]))

    @property
    def clanAbbrev(self):
        return self.clanInfo[1]

    @property
    def clanMotto(self):
        return self.__clanMotto

    @property
    def clanDescription(self):
        return self.__clanDescription

    @property
    def clanTag(self):
        result = self.clanAbbrev
        return '[%s]' % result if result else result

    @property
    def clanCommanderName(self):
        for member in self.clanMembers:
            if member.getClanRole() == CLAN_MEMBER_FLAGS.LEADER:
                return member.getName()

        return None

    @property
    def clanRole(self):
        user = self.usersStorage.getUser(getAccountDatabaseID())
        if user:
            role = user.getClanRole()
        else:
            role = 0
        return role

    @property
    def isClanLeader(self):
        return self.clanRole == CLAN_MEMBER_FLAGS.LEADER

    @property
    def strongholdProvider(self):
        return self.__providers.get(ProviderNames.STRONGHOLD)

    @property
    def strongholdEventProvider(self):
        return self.__providers.get(ProviderNames.STRONGHOLD_EVENT)

    @adisp_async
    @adisp_process
    def getClanEmblemID(self, callback):
        clanEmblem = None
        if self.isInClan:
            tID = 'clanInfo' + BigWorld.player().name
            clanEmblem = yield self.getClanEmblemTextureID(self.clanDBID, False, tID)
        callback(clanEmblem)
        return

    @adisp_async
    def getFileFromServer(self, clanId, fileType, callback):
        if not BigWorld.player().serverSettings['file_server'].has_key(fileType):
            LOG_ERROR("Invalid server's file type: %s" % fileType)
            self._valueResponse(0, (None, None), callback)
            return None
        else:
            clanEmblems = BigWorld.player().serverSettings['file_server'][fileType]
            BigWorld.player().customFilesCache.get(clanEmblems['url_template'] % clanId, lambda url, file: self._valueResponse(0, (url, file), callback), True)
            return None

    @adisp_async
    @adisp_process
    def getClanEmblemTextureID(self, clanDBID, isBig, textureID, callback):
        import imghdr
        if clanDBID is not None and clanDBID != 0:
            _, clanEmblemFile = yield self.getFileFromServer(clanDBID, 'clan_emblems_small' if not isBig else 'clan_emblems_big')
            if clanEmblemFile and imghdr.what(None, clanEmblemFile) is not None:
                BigWorld.wg_addTempScaleformTexture(textureID, clanEmblemFile)
                callback(textureID)
                return
        callback(None)
        return

    def getClanRoleUserString(self):
        position = self.clanInfo[3]
        return getClanRoleString(position)

    def onClanInfoReceived(self, clanDBID, clanName, clanAbbrev, clanMotto, clanDescription):
        self.__clanMotto = passCensor(html.escape(clanMotto))
        self.__clanDescription = passCensor(html.escape(clanDescription))

    def _valueResponse(self, resID, value, callback):
        if resID < 0:
            LOG_ERROR('[class %s] There is error while getting data from cache: %s[%d]' % (self.__class__.__name__, code2str(resID), resID))
            return callback(value)
        callback(value)

    def _onResync(self):
        if not self.__waitForSync:
            self.__invalidateData()

    def __invalidateData(self, diff=None, callback=lambda *args: None):
        callback(True)

    def __registerProvider(self, providerName, providerClazz, args):
        self.__providers[providerName] = providerClazz(*args)

    def __startProviders(self):
        for provider in self.__providers.values():
            provider.start()

    def __stopProviders(self, withClear=False):
        for provider in self.__providers.values():
            provider.stop(withClear=withClear)

    def __me_onClanMembersListChanged(self):
        clanMembersLen = len(self.clanMembers)
        if self.__clanMembersLen is not None and clanMembersLen != self.__clanMembersLen:
            self.__clanMembersLen = clanMembersLen
        return


g_clanCache = _ClanCache()
