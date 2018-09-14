# Embedded file name: scripts/client/gui/battle_results/data_providers.py
import BigWorld
import ArenaType
from adisp import async, process
from collections import namedtuple, defaultdict
from gui.LobbyContext import g_lobbyContext
from gui.shared.utils.requesters.abstract import AbstractRequester
from gui.battle_results import formatters as results_fmts, results
from messenger.proto.xmpp.spa_requesters import NicknameResolver

class _PlayerData(namedtuple('_PlayerData', 'dbID team name prebattleID igrType clanAbbrev clanDBID')):

    def __new__(cls, dbID = 0, team = 0, name = results_fmts.getUnknownPlayerName(), prebattleID = 0, igrType = 0, clanAbbrev = '', clanDBID = 0):
        return super(_PlayerData, cls).__new__(cls, dbID, team, name, prebattleID, igrType, clanAbbrev, clanDBID)

    def getFullName(self):
        return g_lobbyContext.getPlayerFullName(self.name, clanAbbrev=self.clanAbbrev, pDBID=self.dbID)

    def getRegionCode(self):
        return g_lobbyContext.getRegionCode(self.dbID)


_PlayerInfo = namedtuple('_PlayerInfo', 'name clanAbbrev')
_PlayerInfo.__new__.__defaults__ = (results_fmts.getUnknownPlayerName(), '')

class _PlayersInfoGetter(object):

    def __init__(self):
        self._infoCache = {}

    @async
    def invalidate(self, results, callback):
        callback(True)

    def getInfo(self, playerDbID):
        return self._infoCache.get(playerDbID, _PlayerInfo())


class _PlayersInfoFromDataGetter(_PlayersInfoGetter):

    @async
    def invalidate(self, results, callback):
        self._infoCache.clear()
        if results is not None:
            for playerDbID, pData in results['players'].iteritems():
                self._infoCache[playerDbID] = _PlayerInfo(pData['name'], pData['clanAbbrev'])

        callback(True)
        return


class _PlayersInfoFromXmppGetter(_PlayersInfoGetter):

    def __init__(self):
        super(_PlayersInfoFromXmppGetter, self).__init__()
        self._spaResolver = NicknameResolver()
        self._spaResolver.registerHandlers()

    def __del__(self):
        self._spaResolver.unregisterHandlers()
        self._spaResolver.clear()

    @async
    def invalidate(self, results, callback):
        self._infoCache.clear()

        def _cbWrapper(players, error):
            self._infoCache = dict(map(lambda (pID, n): (pID, _PlayerInfo(n)), players.iteritems()))
            callback(True)

        self._spaResolver.resolve(results['players'].keys(), _cbWrapper)


class _AsyncPostBattleResultsDataProvider(AbstractRequester):

    def __init__(self, arenaUniqueID, playerInfoGetter = None):
        super(_AsyncPostBattleResultsDataProvider, self).__init__()
        self._arenaUniqueID = arenaUniqueID
        self._playerInfoGetter = playerInfoGetter or _PlayersInfoFromDataGetter()
        self.__results = None
        self.__players = {}
        self.__vehicles = defaultdict(list)
        self.__vehicleIDToAccountDBID = {}
        self.__accountDBIDToVehicleID = {}
        return

    def destroy(self):
        self.__accountDBIDToVehicleID = None
        self.__vehicleIDToAccountDBID = None
        self.__vehicles.clear()
        self.__players.clear()
        self.__results.clear()
        del self._playerInfoGetter
        return

    @property
    def results(self):
        return self.__results

    def getResults(self):
        return self._data

    def getArenaUniqueID(self):
        return self._arenaUniqueID

    def getArenaTypeID(self):
        return self.__results.common.arenaTypeID

    def getArenaType(self):
        return ArenaType.g_cache[self.getArenaTypeID()]

    def getArenaGuiType(self):
        return self.__results.common.guiType

    def getArenaBonusType(self):
        return self.__results.common.bonusType

    def getPlayers(self):
        return self.__players

    def wasInBattle(self, playerDBID):
        return playerDBID in self.__players

    def getPlayerData(self, playerDbID):
        return self.__players.get(playerDbID, _PlayerData(playerDbID))

    def getVehicles(self):
        return self.__vehicles

    def getVehiclesData(self, playerDbID):
        return self.__vehicles.get(playerDbID, ())

    def getAccountDBID(self, vehicleID):
        return self.__vehicleIDToAccountDBID.get(vehicleID)

    def getVehicleID(self, accountDBID):
        return self.__accountDBIDToVehicleID.get(accountDBID)

    @async
    @process
    def request(self, callback):
        yield super(_AsyncPostBattleResultsDataProvider, self).request()
        if self.isSynced():
            yield self._playerInfoGetter.invalidate(self.getResults())
            self._invalidateCaches()
        callback(self)

    def _invalidateCaches(self):
        self.__players.clear()
        self.__results = None
        if self._data is not None:
            for playerDbID, pData in self._data['players'].iteritems():
                info = dict(pData)
                info.update(self._playerInfoGetter.getInfo(playerDbID)._asdict())
                self.__players[playerDbID] = _PlayerData(playerDbID, **info)

            for vId, vInfos in self._data['vehicles'].iteritems():
                for vInfo in vInfos:
                    accountDBID = vInfo['accountDBID']
                    self.__vehicleIDToAccountDBID[vId] = accountDBID
                    self.__accountDBIDToVehicleID[accountDBID] = vId
                    self.__vehicles[accountDBID].append(vInfo)

            self.__results = results.createResults(self._data, self)
        return

    def __repr__(self):
        return '%s(arenaID=%d; synced=%d)' % (self.__class__.__name__, self._arenaUniqueID, int(self.isSynced()))


class DirectDataProvider(_AsyncPostBattleResultsDataProvider):

    def __init__(self, arenaUniqueID, fullResultsData):
        super(DirectDataProvider, self).__init__(arenaUniqueID)
        self.__fullResultsData = fullResultsData

    @async
    def _requestCache(self, callback):
        self._response(0, self.__fullResultsData, callback)


class OwnResultsDataProvider(_AsyncPostBattleResultsDataProvider):

    def __init__(self, arenaUniqueID):
        super(OwnResultsDataProvider, self).__init__(arenaUniqueID)

    @async
    def _requestCache(self, callback):
        BigWorld.player().battleResultsCache.get(self._arenaUniqueID, lambda resID, value: self._response(resID, value, callback))


class UserResultsDataProvider(_AsyncPostBattleResultsDataProvider):

    def __init__(self, arenaUniqueID, svrPackedData):
        super(UserResultsDataProvider, self).__init__(arenaUniqueID, playerInfoGetter=_PlayersInfoFromXmppGetter())
        self.__svrPackedData = svrPackedData

    @async
    def _requestCache(self, callback):
        BigWorld.player().battleResultsCache.getOther(self._arenaUniqueID, self.__svrPackedData, lambda resID, value: self._response(resID, value, callback))

    def __repr__(self):
        return 'UserResultsDataProvider(arenaID=%d; svrPackedData=%s; synced=%d)' % (self._arenaUniqueID, self.__svrPackedData, int(self.isSynced()))
