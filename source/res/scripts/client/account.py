# Embedded file name: scripts/client/Account.py
import cPickle
import zlib
import copy
from collections import namedtuple
import Event
import AccountCommands
import ClientPrebattle
from account_helpers import AccountSyncData, Inventory, DossierCache, Shop, Stats, QuestProgress, Trader, CustomFilesCache, BattleResultsCache, ClientClubs, ClientGoodies
from account_helpers.ClientInvitations import ClientInvitations
from ConnectionManager import connectionManager
from PlayerEvents import g_playerEvents as events
from account_helpers.settings_core import IntUserSettings
from constants import *
from messenger import MessengerEntry
from streamIDs import RangeStreamIDCallbacks, STREAM_ID_CHAT_MAX, STREAM_ID_CHAT_MIN
from debug_utils import *
from ContactInfo import ContactInfo
from ClientChat import ClientChat
from ChatManager import chatManager
from account_shared import NotificationItem
from OfflineMapCreator import g_offlineMapCreator
from ClientUnitMgr import ClientUnitMgr, ClientUnitBrowser
from ClientFortMgr import ClientFortMgr
from gui import game_control
from gui.wgnc import g_wgncProvider
from gui.shared.ClanCache import g_clanCache
StreamData = namedtuple('StreamData', ['data',
 'isCorrupted',
 'origPacketLen',
 'packetLen',
 'origCrc32',
 'crc32'])
StreamData.__new__.__defaults__ = (None,) * len(StreamData._fields)

class PlayerAccount(BigWorld.Entity, ClientChat):
    __onStreamCompletePredef = {AccountCommands.REQUEST_ID_PREBATTLES: 'receivePrebattles',
     AccountCommands.REQUEST_ID_PREBATTLE_ROSTER: 'receivePrebattleRoster'}

    def __init__(self):
        global g_accountRepository
        LOG_DEBUG('client Account.init')
        ClientChat.__init__(self)
        self.__rangeStreamIDCallbacks = RangeStreamIDCallbacks()
        self.__rangeStreamIDCallbacks.addRangeCallback((STREAM_ID_CHAT_MIN, STREAM_ID_CHAT_MAX), '_ClientChat__receiveStreamedData')
        self.lastStreamData = StreamData()
        if g_offlineMapCreator.Active():
            self.name = 'offline_account'
        if g_accountRepository is None:
            g_accountRepository = _AccountRepository(self.name, copy.copy(self.serverSettings))
        self.contactInfo = g_accountRepository.contactInfo
        self.syncData = g_accountRepository.syncData
        self.inventory = g_accountRepository.inventory
        self.stats = g_accountRepository.stats
        self.questProgress = g_accountRepository.questProgress
        self.trader = g_accountRepository.trader
        self.shop = g_accountRepository.shop
        self.dossierCache = g_accountRepository.dossierCache
        self.battleResultsCache = g_accountRepository.battleResultsCache
        self.intUserSettings = g_accountRepository.intUserSettings
        self.prebattleInvitations = g_accountRepository.prebattleInvitations
        self.fort = g_accountRepository.fort
        self.clubs = g_accountRepository.clubs
        self.goodies = g_accountRepository.goodies
        self.customFilesCache = g_accountRepository.customFilesCache
        self.syncData.setAccount(self)
        self.inventory.setAccount(self)
        self.stats.setAccount(self)
        self.questProgress.setAccount(self)
        self.trader.setAccount(self)
        self.shop.setAccount(self)
        self.dossierCache.setAccount(self)
        self.battleResultsCache.setAccount(self)
        self.intUserSettings.setProxy(self, self.syncData)
        self.prebattleInvitations.setProxy(self)
        self.fort._setAccount(self)
        self.fort._setServerSettings(g_accountRepository.serverSettings)
        self.clubs.setAccount(self)
        self.goodies.setAccount(self)
        self.isLongDisconnectedFromCenter = False
        self.prebattle = None
        self.unitBrowser = ClientUnitBrowser(self)
        self.unitMgr = ClientUnitMgr(self)
        self.clubs.onUnitMgrCreated(self.unitMgr)
        self.prebattleAutoInvites = g_accountRepository.prebattleAutoInvites
        self.globalRating = 0
        self.prebattleInvites = g_accountRepository.prebattleInvites
        self.eventNotifications = g_accountRepository.eventNotifications
        self.clanMembers = g_accountRepository.clanMembers
        self.eventsData = g_accountRepository.eventsData
        self.isInRandomQueue = False
        self.isInTutorialQueue = False
        self.isInUnitAssembler = False
        self.isInHistoricalQueue = False
        self.isInEventBattles = False
        self.__onCmdResponse = {}
        self.__onStreamComplete = {}
        propertyName, propertyValue = _CLIENT_SERVER_VERSION
        connectionManager.checkClientServerVersions(propertyValue, getattr(self, propertyName, None))
        return

    def onBecomePlayer(self):
        LOG_DEBUG('Account.onBecomePlayer()')
        self.isPlayer = True
        self.databaseID = None
        self.inputHandler = AccountInputHandler()
        BigWorld.clearAllSpaces()
        self.syncData.onAccountBecomePlayer()
        self.inventory.onAccountBecomePlayer()
        self.stats.onAccountBecomePlayer()
        self.questProgress.onAccountBecomePlayer()
        self.trader.onAccountBecomePlayer()
        self.shop.onAccountBecomePlayer()
        self.dossierCache.onAccountBecomePlayer()
        self.battleResultsCache.onAccountBecomePlayer()
        self.intUserSettings.onProxyBecomePlayer()
        self.prebattleInvitations.onProxyBecomePlayer()
        self.clubs.onAccountBecomePlayer()
        self.goodies.onAccountBecomePlayer()
        chatManager.switchPlayerProxy(self)
        events.onAccountBecomePlayer()
        return

    def onBecomeNonPlayer(self):
        LOG_DEBUG('Account.onBecomeNonPlayer()')
        if not (hasattr(self, 'isPlayer') and self.isPlayer):
            return
        else:
            self.isPlayer = False
            chatManager.switchPlayerProxy(None)
            self.syncData.onAccountBecomeNonPlayer()
            self.inventory.onAccountBecomeNonPlayer()
            self.stats.onAccountBecomeNonPlayer()
            self.questProgress.onAccountBecomeNonPlayer()
            self.trader.onAccountBecomeNonPlayer()
            self.shop.onAccountBecomeNonPlayer()
            self.dossierCache.onAccountBecomeNonPlayer()
            self.battleResultsCache.onAccountBecomeNonPlayer()
            self.intUserSettings.onProxyBecomeNonPlayer()
            self.prebattleInvitations.onProxyBecomeNonPlayer()
            self.clubs.onAccountBecomeNonPlayer()
            self.goodies.onAccountBecomeNonPlayer()
            self.__cancelCommands()
            self.syncData.setAccount(None)
            self.inventory.setAccount(None)
            self.stats.setAccount(None)
            self.questProgress.setAccount(None)
            self.trader.setAccount(None)
            self.shop.setAccount(None)
            self.dossierCache.setAccount(None)
            self.battleResultsCache.setAccount(None)
            self.intUserSettings.setProxy(None, None)
            self.prebattleInvitations.setProxy(None)
            self.clubs.setAccount(None)
            self.goodies.setAccount(None)
            self.fort.clear()
            events.onAccountBecomeNonPlayer()
            del self.inputHandler
            return

    def onCmdResponse(self, requestID, resultID, errorStr):
        callback = self.__onCmdResponse.pop(requestID, None)
        if callback is not None:
            callback(requestID, resultID, errorStr)
        return

    def onCmdResponseExt(self, requestID, resultID, errorStr, ext):
        ext = cPickle.loads(ext)
        if resultID == AccountCommands.RES_SHOP_DESYNC:
            self.shop.synchronize(ext.get('shopRev', None))
        callback = self.__onCmdResponse.pop(requestID, None)
        if callback is not None:
            callback(requestID, resultID, errorStr, ext)
        return

    def reloadShop(self):
        self.shop.synchronize(None)
        return

    def requestToken(self, requestID, tokenType):
        self.base.requestToken(requestID, tokenType)

    def onTokenReceived(self, requestID, tokenType, data):
        g_accountRepository.onTokenReceived(requestID, tokenType, data)

    def onIGRTypeChanged(self, data):
        try:
            data = cPickle.loads(data)
            events.onIGRTypeChanged(data.get('roomType'), data.get('igrXPFactor'))
            LOG_DEBUG('onIGRTypeChanged', data)
        except Exception:
            LOG_ERROR('Error while unpickling igr data information', data)

    def onKickedFromServer(self, reason, isBan, expiryTime):
        LOG_MX('onKickedFromServer', reason, isBan, expiryTime)
        connectionManager.onKickedFromServer(reason, isBan, expiryTime)

    def onStreamComplete(self, id, desc, data):
        isCorrupted, origPacketLen, packetLen, origCrc32, crc32 = desc
        self.lastStreamData = StreamData(data, *desc)
        if isCorrupted:
            self.base.logStreamCorruption(id, origPacketLen, packetLen, origCrc32, crc32)
        callback = self.__rangeStreamIDCallbacks.getCallbackForStreamID(id)
        if callback is not None:
            getattr(self, callback)(id, data)
            return
        else:
            callback = self.__onStreamCompletePredef.get(id, None)
            if callback is not None:
                getattr(self, callback)(True, data)
                return
            callback = self.__onStreamComplete.pop(id, None)
            if callback is not None:
                callback(True, data)
            self.lastStreamData = StreamData()
            return

    def onEnqueued(self, queueType):
        LOG_DEBUG('onEnqueued', queueType)
        if queueType == QUEUE_TYPE.RANDOMS:
            self.isInRandomQueue = True
            events.onEnqueuedRandom()
        elif queueType == QUEUE_TYPE.TUTORIAL:
            pass
        elif queueType == QUEUE_TYPE.HISTORICAL:
            self.isInHistoricalQueue = True
            events.onEnqueuedHistorical()
        elif queueType == QUEUE_TYPE.UNIT_ASSEMBLER:
            self.isInUnitAssembler = True
            events.onEnqueuedUnitAssembler()
        elif queueType == QUEUE_TYPE.EVENT_BATTLES:
            self.isInEventBattles = True
            events.onEnqueuedEventBattles()

    def onEnqueueFailure(self, queueType, errorCode, errorStr):
        LOG_DEBUG('onEnqueueFailure', queueType, errorCode, errorStr)
        if queueType == QUEUE_TYPE.RANDOMS:
            events.onEnqueueRandomFailure(errorCode, errorStr)
        elif queueType == QUEUE_TYPE.TUTORIAL:
            events.onTutorialEnqueueFailure(errorCode, errorStr)
        elif queueType == QUEUE_TYPE.UNIT_ASSEMBLER:
            events.onEnqueueUnitAssemblerFailure(errorCode, errorStr)
        elif queueType == QUEUE_TYPE.HISTORICAL:
            events.onEnqueueHistoricalFailure(errorCode, errorStr)
        elif queueType == QUEUE_TYPE.EVENT_BATTLES:
            events.onEnqueueEventBattlesFailure(errorCode, errorStr)

    def onDequeued(self, queueType):
        LOG_DEBUG('onDequeued', queueType)
        if queueType == QUEUE_TYPE.RANDOMS:
            self.isInRandomQueue = False
            events.onDequeuedRandom()
        elif queueType == QUEUE_TYPE.TUTORIAL:
            self.isInTutorialQueue = False
            events.onTutorialDequeued()
        elif queueType == QUEUE_TYPE.UNIT_ASSEMBLER:
            self.isInUnitAssembler = False
            events.onDequeuedUnitAssembler()
        elif queueType == QUEUE_TYPE.HISTORICAL:
            self.isInHistoricalQueue = False
            events.onDequeuedHistorical()
        elif queueType == QUEUE_TYPE.EVENT_BATTLES:
            self.isInEventBattles = False
            events.onDequeuedEventBattles()

    def onTutorialEnqueued(self, number, queueLen, avgWaitingTime):
        LOG_DEBUG('onTutorialEnqueued', number, queueLen, avgWaitingTime)
        self.isInTutorialQueue = True
        events.onTutorialEnqueued(number, queueLen, avgWaitingTime)

    def onKickedFromQueue(self, queueType):
        LOG_DEBUG('onKickedFromQueue', queueType)
        if queueType == QUEUE_TYPE.RANDOMS:
            self.isInRandomQueue = False
            events.onKickedFromRandomQueue()
        elif queueType == QUEUE_TYPE.TUTORIAL:
            self.isInTutorialQueue = False
            events.onKickedFromTutorialQueue()
        elif queueType == QUEUE_TYPE.UNIT_ASSEMBLER:
            self.isInUnitAssembler = False
            events.onKickedFromUnitAssembler()
        elif queueType == QUEUE_TYPE.HISTORICAL:
            self.isInHistoricalQueue = False
            events.onKickedFromHistoricalQueue()
        elif queueType == QUEUE_TYPE.EVENT_BATTLES:
            self.isInEventBattles = False
            events.onKickedFromEventBattles()

    def onArenaCreated(self):
        LOG_DEBUG('onArenaCreated')
        self.prebattle = None
        events.isPlayerEntityChanging = True
        events.onArenaCreated()
        events.onPlayerEntityChanging()
        return

    def onArenaJoinFailure(self, errorCode, errorStr):
        LOG_DEBUG('onArenaJoinFailure', errorCode, errorStr)
        events.isPlayerEntityChanging = False
        events.onPlayerEntityChangeCanceled()
        events.onArenaJoinFailure(errorCode, errorStr)

    def onPrebattleJoined(self, prebattleID):
        self.prebattle = ClientPrebattle.ClientPrebattle(prebattleID)
        events.onPrebattleJoined()

    def onPrebattleJoinFailure(self, errorCode):
        LOG_MX('onPrebattleJoinFailure', errorCode)
        events.onPrebattleJoinFailure(errorCode)

    def onPrebattleLeft(self):
        LOG_MX('onPrebattleLeft')
        self.prebattle = None
        events.onPrebattleLeft()
        return

    def setBattleID(self, *args):
        self.unitMgr.setBattleID(*args)

    def onUnitUpdate(self, *args):
        self.unitMgr.onUnitUpdate(*args)

    def onFortUpdate(self, *args):
        self.fort.onFortUpdate(*args)

    def onFortReply(self, *args):
        self.fort.onFortReply(*args)

    def onUnitError(self, *args):
        self.unitMgr.onUnitError(*args)

    def onUnitCallOk(self, *args):
        self.unitMgr.onUnitCallOk(*args)

    def onUnitBrowserError(self, *args):
        self.unitBrowser.onError(*args)

    def onUnitBrowserResultsSet(self, *args):
        self.unitBrowser.onResultsSet(*args)

    def onUnitBrowserResultsUpdate(self, *args):
        self.unitBrowser.onResultsUpdate(*args)

    def onUnitAssemblerSuccess(self, *args):
        self.unitBrowser.onSearchSuccess(*args)

    def onKickedFromArena(self, reasonCode):
        LOG_DEBUG('onKickedFromArena', reasonCode)
        self.isInRandomQueue = False
        self.isInTutorialQueue = False
        self.isInEventBattles = False
        self.isInHistoricalQueue = False
        events.isPlayerEntityChanging = False
        events.onPlayerEntityChangeCanceled()
        events.onKickedFromArena(reasonCode)

    def onKickedFromPrebattle(self, reasonCode):
        LOG_DEBUG('onKickedFromPrebattle', reasonCode)
        self.prebattle = None
        events.onKickedFromPrebattle(reasonCode)
        return

    def onCenterIsLongDisconnected(self, isLongDisconnected):
        LOG_DEBUG('onCenterIsLongDisconnected', isLongDisconnected)
        self.isLongDisconnectedFromCenter = isLongDisconnected
        events.onCenterIsLongDisconnected(isLongDisconnected)

    def onSendPrebattleInvites(self, dbID, name, clanDBID, clanAbbrev, prebattleID, status):
        LOG_DEBUG('onSendPrebattleInvites', dbID, name, clanDBID, clanAbbrev, prebattleID, status)
        if status != PREBATTLE_INVITE_STATUS.OK:
            events.onPrebattleInvitesStatus(dbID, name, status)

    def onClanInfoReceived(self, clanDBID, clanName, clanAbbrev, clanMotto, clanDescription):
        LOG_DEBUG('onClanInfoReceived', clanDBID, clanName, clanAbbrev, clanMotto, clanDescription)
        g_clanCache.onClanInfoReceived(clanDBID, clanName, clanAbbrev, clanMotto, clanDescription)

    def receiveClubUpdate(self, clubDBID, clubData, unitData):
        self.clubs.onClubUpdated(clubDBID, clubData, unitData)

    def receiveClubNotification(self, notification):
        self.clubs.onClubNotification(notification)

    def receiveNotification(self, notification):
        LOG_DEBUG('receiveNotification', notification)
        g_wgncProvider.fromXmlString(notification)

    def sendNotificationReply(self, notificationID, purge, actionName):
        self.base.doCmdInt2Str(0, AccountCommands.CMD_NOTIFICATION_REPLY, notificationID, purge, actionName)

    def handleKeyEvent(self, event):
        return False

    def showGUI(self, ctx):
        ctx = cPickle.loads(ctx)
        LOG_MX('showGUI', ctx)
        self.databaseID = ctx['databaseID']
        if 'prebattleID' in ctx:
            self.prebattle = ClientPrebattle.ClientPrebattle(ctx['prebattleID'])
        self.isInRandomQueue = ctx.get('isInRandomQueue', False)
        self.isInTutorialQueue = ctx.get('isInTutorialQueue', False)
        self.isInTutorialQueue = ctx.get('isInUnitAssembler', False)
        if 'serverUTC' in ctx:
            import helpers.time_utils as tm
            tm.setTimeCorrection(ctx['serverUTC'])
        if 'isLongDisconnectedFromCenter' in ctx:
            isLongDisconnectedFromCenter = ctx['isLongDisconnectedFromCenter']
            if self.isLongDisconnectedFromCenter != isLongDisconnectedFromCenter:
                self.isLongDisconnectedFromCenter = isLongDisconnectedFromCenter
                events.onCenterIsLongDisconnected(isLongDisconnectedFromCenter)
        events.isPlayerEntityChanging = False
        events.onAccountShowGUI(ctx)
        BigWorld.Screener.setUserId(self.databaseID)

    def receiveQueueInfo(self, randomsQueueInfo, companiesQueueInfo, historicalQueueInfo):
        unpacked = None
        if historicalQueueInfo is not None:
            unpacked = self.__unpackHistoricalQueueInfo(historicalQueueInfo)
        events.onQueueInfoReceived(randomsQueueInfo, companiesQueueInfo, unpacked)
        return

    def __unpackHistoricalQueueInfo(self, historicalQueueInfo):
        unpacked = {}
        hqi = historicalQueueInfo
        numClasses = len(VEHICLE_CLASSES)
        battleIDs, sides, classes = hqi['battleIDs'], hqi['sides'], hqi['classes']
        while len(battleIDs) >= 2:
            (battleID, numSides), battleIDs = battleIDs[:2], battleIDs[2:]
            curSides, sides = sides[:numSides], sides[numSides:]
            for side in curSides:
                curClasses, classes = classes[:numClasses], classes[numClasses:]
                sideStats = unpacked.setdefault(battleID, {}).setdefault(side, {})
                sideStats['by_class'] = dict(zip(VEHICLE_CLASSES, curClasses))

        return unpacked

    def receivePrebattles(self, isSuccess, data):
        if isSuccess:
            try:
                data = zlib.decompress(data)
                type, count, prebattles = cPickle.loads(data)
            except:
                LOG_CURRENT_EXCEPTION()
                isSuccess = False

        if not isSuccess:
            type, count, prebattles = 0, 0, []
        events.onPrebattlesListReceived(type, count, prebattles)

    def receivePrebattleRoster(self, isSuccess, data):
        if isSuccess:
            try:
                data = zlib.decompress(data)
                prebattleID, rosterAsList = cPickle.loads(data)
            except:
                LOG_CURRENT_EXCEPTION()
                isSuccess = False

        if not isSuccess:
            prebattleID, rosterAsList = 0, []
        events.onPrebattleRosterReceived(prebattleID, rosterAsList)

    def receiveActiveArenas(self, arenas):
        events.onArenaListReceived(arenas)

    def receiveServerStats(self, stats):
        events.onServerStatsReceived(stats)

    def updatePrebattle(self, updateType, argStr):
        if self.prebattle is not None:
            self.prebattle.update(updateType, argStr)
        return

    def requestFortPublicInfo(self, requestID, filterType, abbrevPattern, homePeripheryID, limit, lvlFrom, lvlTo, ownStartDefHourFrom, ownStartDefHourTo, nextOwnStartDefHourFrom, nextOwnStartDefHourTo, defHourChangeDay, extStartDefHourFrom, extStartDefHourTo, attackDay, ownFortLvl, ownProfitFactor10, avgBuildingLevel10, ownBattleCountForFort, firstDefaultQuery, electedClanDBIDs):
        self.base.requestFortPublicInfo(requestID, filterType, abbrevPattern, homePeripheryID, limit, lvlFrom, lvlTo, ownStartDefHourFrom, ownStartDefHourTo, nextOwnStartDefHourFrom, nextOwnStartDefHourTo, defHourChangeDay, extStartDefHourFrom, extStartDefHourTo, attackDay, ownFortLvl, ownProfitFactor10, avgBuildingLevel10, ownBattleCountForFort, firstDefaultQuery, electedClanDBIDs)

    def responseFortPublicInfo(self, requestID, errorID, resultSet):
        if errorID > 0:
            LOG_DEBUG('fort public info error', requestID, errorID, resultSet)
        self.fort.onResponseFortPublicInfo(requestID, errorID, cPickle.loads(resultSet))

    def update(self, diff):
        self._update(True, cPickle.loads(diff))

    def resyncDossiers(self):
        self.dossierCache.resynchronize()

    def requestQueueInfo(self, queueType):
        if getattr(self, 'isPlayer', False):
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_REQ_QUEUE_INFO, queueType, 0, 0)

    def requestPrebattles(self, type, sort_key, idle, start, end):
        if not events.isPlayerEntityChanging:
            self.base.doCmdIntArr(AccountCommands.REQUEST_ID_PREBATTLES, AccountCommands.CMD_REQ_PREBATTLES, [type,
             sort_key,
             int(idle),
             start,
             end])

    def requestPrebattlesByName(self, type, idle, creatorMask):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt2Str(AccountCommands.REQUEST_ID_PREBATTLES, AccountCommands.CMD_REQ_PREBATTLES_BY_CREATOR, type, int(idle), creatorMask)

    def requestPrebattlesByDivision(self, idle, division):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_PREBATTLES, AccountCommands.CMD_REQ_PREBATTLES_BY_DIVISION, int(idle), division, 0)

    def requestPrebattleRoster(self, prebattleID):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_PREBATTLE_ROSTER, AccountCommands.CMD_REQ_PREBATTLE_ROSTER, prebattleID, 0, 0)

    def requestServerStats(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_REQ_SERVER_STATS, 0, 0, 0)

    def requestPlayerInfo(self, databaseID, callback):
        if events.isPlayerEntityChanging:
            return
        proxy = lambda requestID, resultID, errorStr, ext = {}: callback(resultID, ext.get('databaseID', 0L), ext.get('dossier', ''), ext.get('clanDBID', 0), ext.get('clanInfo', None), ext.get('globalRating', 0))
        self._doCmdInt3(AccountCommands.CMD_REQ_PLAYER_INFO, databaseID, 0, 0, proxy)

    def requestAccountDossier(self, accountID, callback):
        if events.isPlayerEntityChanging:
            return
        proxy = lambda requestID, resultID, errorStr, ext = {}: callback(resultID, ext.get('dossier', ''))
        self._doCmdInt3(AccountCommands.CMD_REQ_ACCOUNT_DOSSIER, accountID, 0, 0, proxy)

    def requestVehicleDossier(self, databaseID, vehTypeCompDescr, callback):
        if events.isPlayerEntityChanging:
            return
        proxy = lambda requestID, resultID, errorStr, ext = {}: callback(resultID, ext.get('dossier', ''))
        self._doCmdInt3(AccountCommands.CMD_REQ_VEHICLE_DOSSIER, databaseID, vehTypeCompDescr, 0, proxy)

    def requestPlayerClanInfo(self, databaseID, callback):
        if events.isPlayerEntityChanging:
            return
        proxy = lambda requestID, resultID, errorStr, ext = {}: callback(resultID, errorStr, ext.get('clanDBID', 0), ext.get('clanInfo', None))
        self._doCmdInt3(AccountCommands.CMD_REQ_PLAYER_CLAN_INFO, databaseID, 0, 0, proxy)

    def cmdPublishBattleResults(self, uniqueSubUrl, arenaUniqueID):
        self._doCmdInt2Str(AccountCommands.CMD_PUBLISH_BATTLE_RESULTS, arenaUniqueID, 0, uniqueSubUrl, None)
        return

    def requestPlayerGlobalRating(self, accountID, callback):
        if events.isPlayerEntityChanging:
            return
        proxy = lambda requestID, resultID, errorStr, ext = {}: callback(resultID, errorStr, ext.get('globalRating', 0))
        self._doCmdInt3(AccountCommands.CMD_REQ_PLAYER_GLOBAL_RATING, accountID, 0, 0, proxy)

    def requestPlayersGlobalRating(self, accountIDs, callback):
        proxy = lambda requestID, resultID, errorStr, ext = None: callback(resultID, errorStr, ext)
        self._doCmdIntArrStrArr(AccountCommands.CMD_REQ_PLAYERS_GLOBAL_RATING, accountIDs, [], proxy)
        return

    def enqueueRandom(self, vehInvID, gameplaysMask = 65535, arenaTypeID = 0):
        if events.isPlayerEntityChanging:
            return
        self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_RANDOM, vehInvID, gameplaysMask, arenaTypeID)

    def dequeueRandom(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_RANDOM, 0, 0, 0)

    def enqueueTutorial(self):
        if events.isPlayerEntityChanging:
            return
        self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_TUTORIAL, 0, 0, 0)

    def dequeueTutorial(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_TUTORIAL, 0, 0, 0)

    def enqueueUnitAssembler(self, compactDescrs):
        if events.isPlayerEntityChanging:
            return
        args = list(compactDescrs)
        self.base.doCmdIntArr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_UNIT_ASSEMBLER, args)

    def dequeueUnitAssembler(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_UNIT_ASSEMBLER, 0, 0, 0)

    def enqueueHistorical(self, vehInvID, histBattleID, isCreditsAmmo = True):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_HISTORICAL, vehInvID, histBattleID, int(isCreditsAmmo))

    def dequeueHistorical(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_HISTORICAL, 0, 0, 0)

    def enqueueEventBattles(self, vehInvIDs):
        if not events.isPlayerEntityChanging:
            arr = [len(vehInvIDs)] + vehInvIDs
            self.base.doCmdIntArr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_EVENT_BATTLES, arr)

    def dequeueEventBattles(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_EVENT_BATTLES, 0, 0, 0)

    def createArenaFromQueue(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_FORCE_QUEUE, 0, 0, 0)

    def prb_createTraining(self, arenaTypeID, roundLength, isOpened, comment):
        if events.isPlayerEntityChanging:
            return
        self.base.createTraining(arenaTypeID, roundLength, isOpened, comment)

    def prb_createSquad(self):
        if events.isPlayerEntityChanging:
            return
        self.base.createSquad()

    def prb_createCompany(self, isOpened, comment, division = PREBATTLE_COMPANY_DIVISION.ABSOLUTE):
        if events.isPlayerEntityChanging:
            return
        self.base.createCompany(isOpened, comment, division)

    def prb_createDev(self, arenaTypeID, roundLength, comment, bonusType = ARENA_BONUS_TYPE.REGULAR):
        if events.isPlayerEntityChanging:
            return
        self.base.createDevPrebattle(bonusType, arenaTypeID, roundLength, comment)

    def prb_sendInvites(self, accountsToInvite, comment):
        if events.isPlayerEntityChanging:
            return
        self.base.sendPrebattleInvites(accountsToInvite, comment)

    def prb_acceptInvite(self, prebattleID, peripheryID):
        if events.isPlayerEntityChanging:
            return
        self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_PRB_ACCEPT_INVITE, prebattleID, peripheryID, 0)

    def prb_declineInvite(self, prebattleID, peripheryID):
        if events.isPlayerEntityChanging:
            return
        self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_PRB_DECLINE_INVITE, prebattleID, peripheryID, 0)

    def prb_join(self, prebattleID):
        if events.isPlayerEntityChanging:
            return
        self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_PRB_JOIN, prebattleID, 0, 0)

    def prb_leave(self, callback):
        if events.isPlayerEntityChanging:
            return
        self._doCmdInt3(AccountCommands.CMD_PRB_LEAVE, 0, 0, 0, lambda requestID, resultID, errorStr: callback(resultID))

    def prb_ready(self, vehInvID, callback):
        if events.isPlayerEntityChanging:
            return
        self._doCmdInt3(AccountCommands.CMD_PRB_READY, vehInvID, 0, 0, lambda requestID, resultID, errorStr: callback(resultID))

    def prb_notReady(self, state, callback):
        if events.isPlayerEntityChanging:
            return
        self._doCmdInt3(AccountCommands.CMD_PRB_NOT_READY, state, 0, 0, lambda requestID, resultID, errorStr: callback(resultID))

    def prb_assign(self, playerID, roster, callback):
        if events.isPlayerEntityChanging:
            return
        self._doCmdInt3(AccountCommands.CMD_PRB_ASSIGN, playerID, roster, 0, lambda requestID, resultID, errorStr: callback(resultID))

    def prb_swapTeams(self, callback):
        if events.isPlayerEntityChanging:
            return
        self._doCmdInt3(AccountCommands.CMD_PRB_SWAP_TEAM, 0, 0, 0, lambda requestID, resultID, errorStr: callback(resultID))

    def prb_changeArena(self, arenaTypeID, callback):
        if events.isPlayerEntityChanging:
            return
        self._doCmdInt3(AccountCommands.CMD_PRB_CH_ARENA, arenaTypeID, 0, 0, lambda requestID, resultID, errorStr: callback(resultID))

    def prb_changeRoundLength(self, roundLength, callback):
        if events.isPlayerEntityChanging:
            return
        self._doCmdInt3(AccountCommands.CMD_PRB_CH_ROUND, roundLength, 0, 0, lambda requestID, resultID, errorStr: callback(resultID))

    def prb_changeOpenStatus(self, isOpened, callback):
        if events.isPlayerEntityChanging:
            return
        self._doCmdInt3(AccountCommands.CMD_PRB_OPEN, 1 if isOpened else 0, 0, 0, lambda requestID, resultID, errorStr: callback(resultID))

    def prb_changeComment(self, comment, callback):
        if events.isPlayerEntityChanging:
            return
        self._doCmdStr(AccountCommands.CMD_PRB_CH_COMMENT, comment, lambda requestID, resultID, errorStr: callback(resultID))

    def prb_changeArenaVoip(self, arenaVoipChannels, callback):
        if events.isPlayerEntityChanging:
            return
        self._doCmdInt3(AccountCommands.CMD_PRB_CH_ARENAVOIP, arenaVoipChannels, 0, 0, lambda requestID, resultID, errorStr: callback(resultID))

    def prb_teamReady(self, team, force, gameplaysMask, callback):
        if events.isPlayerEntityChanging:
            return
        else:
            prb = self.prebattle
            if prb is None:
                LOG_ERROR('No prebattle info')
                return
            s = prb.settings
            if s['type'] == PREBATTLE_TYPE.SQUAD and s.get('gameplaysMask', 0) != gameplaysMask:
                self._doCmdInt3(AccountCommands.CMD_PRB_CH_GAMEPLAYSMASK, gameplaysMask, 0, 0, None)
            self._doCmdInt3(AccountCommands.CMD_PRB_TEAM_READY, team, 1 if force else 0, 0, lambda requestID, resultID, errorStr: callback(resultID, errorStr))
            return

    def prb_teamNotReady(self, team, callback):
        if events.isPlayerEntityChanging:
            return
        self._doCmdInt3(AccountCommands.CMD_PRB_TEAM_NOT_READY, team, 0, 0, lambda requestID, resultID, errorStr: callback(resultID))

    def prb_kick(self, playerID, callback):
        if events.isPlayerEntityChanging:
            return
        self._doCmdInt3(AccountCommands.CMD_PRB_KICK, playerID, 0, 0, lambda requestID, resultID, errorStr: callback(resultID))

    def prb_changeDivision(self, division, callback):
        if events.isPlayerEntityChanging:
            return
        self._doCmdInt3(AccountCommands.CMD_PRB_CH_DIVISION, division, 0, 0, lambda requestID, resultID, errorStr: callback(resultID))

    def prb_changeGameplaysMask(self, gameplaysMask, callback):
        if events.isPlayerEntityChanging:
            return
        self._doCmdInt3(AccountCommands.CMD_PRB_CH_GAMEPLAYSMASK, gameplaysMask, 0, 0, lambda requestID, resultID, errorStr: callback(resultID))

    def challengeCaptcha(self, challenge, response, callback):
        if events.isPlayerEntityChanging:
            return
        self._doCmdInt2Str(AccountCommands.CMD_CAPTCHA_CHALLENGE, len(challenge), 0, challenge + response, lambda requestID, resultID, errorCode: callback(resultID, errorCode))

    def setLanguage(self, language):
        self._doCmdStr(AccountCommands.CMD_SET_LANGUAGE, language, None)
        return

    def selectPotapovQuests(self, potapovQuestIDs, callback):
        self._doCmdIntArr(AccountCommands.CMD_SELECT_POTAPOV_QUESTS, potapovQuestIDs, lambda requestID, resultID, errorCode: callback(resultID, errorCode))

    def getPotapovQuestReward(self, potapovQuestID, needTamkman = False, tmanNation = 0, tmanInnation = 0, roleID = 1, callback = None):
        arr = [potapovQuestID,
         needTamkman,
         tmanNation,
         tmanInnation,
         roleID]
        if callback is not None:
            proxy = lambda requestID, resultID, errorCode: callback(resultID, errorCode)
        else:
            proxy = None
        self._doCmdIntArr(AccountCommands.CMD_GET_POTAPOV_QUEST_REWARD, arr, proxy)
        return

    def activateGoodie(self, goodieId, callback):
        self._doCmdIntArr(AccountCommands.CMD_ACTIVATE_GOODIE, goodieId, lambda requestID, resultID, errorCode: callback(resultID, errorCode))

    def makeDenunciation(self, violatorID, topicID, violatorKind):
        self._doCmdInt3(AccountCommands.CMD_MAKE_DENUNCIATION, violatorID, topicID, violatorKind, None)
        return

    def banUnbanUser(self, accountDBID, restrType, banPeriod, reason, isBan, callback = None):
        reason = reason.encode('utf8')
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext = {}: callback(resultID, errorStr, ext)
        else:
            proxy = None
        intArr = [accountDBID,
         restrType,
         banPeriod,
         isBan]
        strArr = [reason]
        self._doCmdIntArrStrArr(AccountCommands.CMD_BAN_UNBAN_USER, intArr, strArr, proxy)
        return

    def logUXEvents(self, intArr):
        if not game_control.g_instance.needLogUXEvents:
            return
        else:
            self._doCmdIntArr(AccountCommands.CMD_LOG_CLIENT_UX_EVENTS, intArr, None)
            return

    def logXMPPEvents(self, intArr, strArr):
        self._doCmdIntArrStrArr(AccountCommands.CMD_LOG_CLIENT_XMPP_EVENTS, intArr, strArr, None)
        return

    def completeTutorial(self, tutorialID, callback):
        from CurrentVehicle import g_currentVehicle
        self._doCmdInt3(AccountCommands.CMD_COMPLETE_TUTORIAL, tutorialID, g_currentVehicle.invID, 0, lambda requestID, resultID, errorStr: callback(resultID))

    def verifyFinPassword(self, finPassword, callback):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr: callback(resultID, errorStr)
        else:
            proxy = None
        self._doCmdStr(AccountCommands.CMD_VERIFY_FIN_PSWD, finPassword, proxy)
        return

    def steamInitTxn(self, steamID, itemID, callback):
        self.shop.getGoldPackets(lambda resultID, packets, rev: self.__steamInitTxn(steamID, itemID, callback, packets))

    def __steamInitTxn(self, steamID, itemID, callback, packets):
        try:
            packet = packets[itemID]
            data = str(steamID) + ':' + itemID + ';' + '%.2f' % packet['amount'] + ';' + packet['currency']
            self._doCmdStr(AccountCommands.CMD_STEAM_INIT_TXN, data, lambda requestID, error, errorStr: callback(steamID, itemID, error))
        except:
            callback(steamID, itemID, AccountCommands.RES_FAILURE)

    def steamFinalizeTxn(self, steamID, orderID, callback):
        try:
            data = str(steamID) + ':' + str(orderID)
            self._doCmdStr(AccountCommands.CMD_STEAM_FINALIZE_TXN, data, lambda requestID, error, errorStr: callback(steamID, orderID, error))
        except:
            callback(steamID, orderID, AccountCommands.RES_FAILURE)

    def ebankGetBalance(self, callback):
        self._doCmdStr(AccountCommands.CMD_EBANK_GET_BALANCE, '', lambda requestID, error, errorStr, ebankProps = {}: callback(error, errorStr, ebankProps))

    def ebankBuyGold(self, vcoin, callback):
        self.shop.ebankVCoinExchangeRate(lambda resultID, exchangeRate, rev: self.__ebankBuyGold(rev, vcoin, callback))

    def __ebankBuyGold(self, shopRev, vcoin, callback):
        self._doCmdInt3(AccountCommands.CMD_EBANK_BUY_GOLD, shopRev, vcoin, 0, lambda requestID, error, errorStr, ebankProps = {}: callback(error, errorStr, ebankProps))

    def messenger_onActionByServer_chat2(self, actionID, reqID, args):
        from messenger_common_chat2 import MESSENGER_ACTION_IDS as actions
        LOG_DEBUG('messenger_onActionByServer', actions.getActionName(actionID), reqID, args)
        MessengerEntry.g_instance.protos.BW_CHAT2.onActionReceived(actionID, reqID, args)

    def processInvitations(self, invitations):
        self.prebattleInvitations.processInvitations(invitations)

    def _doCmdStr(self, cmd, str, callback):
        self.__doCmd('doCmdStr', cmd, callback, str)

    def _doCmdInt3(self, cmd, int1, int2, int3, callback):
        self.__doCmd('doCmdInt3', cmd, callback, int1, int2, int3)

    def _doCmdInt4(self, cmd, int1, int2, int3, int4, callback):
        self.__doCmd('doCmdInt4', cmd, callback, int1, int2, int3, int4)

    def _doCmdInt2Str(self, cmd, int1, int2, str, callback):
        self.__doCmd('doCmdInt2Str', cmd, callback, int1, int2, str)

    def _doCmdIntArr(self, cmd, arr, callback):
        self.__doCmd('doCmdIntArr', cmd, callback, arr)

    def _doCmdIntArrStrArr(self, cmd, intArr, strArr, callback):
        self.__doCmd('doCmdIntArrStrArr', cmd, callback, intArr, strArr)

    def _makeTradeOffer(self, passwd, flags, dstDBID, validSec, price, srcWares, srcItemCount, callback):
        if g_accountRepository is None:
            return
        else:
            requestID = self.__getRequestID()
            if requestID is None:
                return
            if callback is not None:
                self.__onCmdResponse[requestID] = callback
            self.base.makeTradeOfferByClient(requestID, passwd, flags, dstDBID, validSec, price, srcWares, srcItemCount)
            return

    def _update(self, triggerEvents, diff):
        LOG_DAN_DEV('_update', diff if triggerEvents else 'full sync')
        isFullSync = diff.get('prevRev', None) is None
        if not self.syncData.updatePersistentCache(diff, isFullSync):
            return False
        else:
            self.syncData.revision = diff.get('rev', 0)
            self.inventory.synchronize(isFullSync, diff)
            self.stats.synchronize(isFullSync, diff)
            self.questProgress.synchronize(isFullSync, diff)
            self.trader.synchronize(isFullSync, diff)
            self.intUserSettings.synchronize(isFullSync, diff)
            self.clubs.synchronize(isFullSync, diff)
            self.goodies.synchronize(isFullSync, diff)
            self.__synchronizeEventNotifications(diff)
            self.__synchronizeCacheDict(self.prebattleAutoInvites, diff.get('account', None), 'prebattleAutoInvites', 'replace', events.onPrebattleAutoInvitesChanged)
            self.__synchronizeCacheDict(self.prebattleInvites, diff, 'prebattleInvites', 'update', lambda : events.onPrebattleInvitesChanged(diff))
            self.__synchronizeCacheDict(self.clanMembers, diff.get('cache', None), 'clanMembers', 'replace', events.onClanMembersListChanged)
            self.__synchronizeCacheDict(self.eventsData, diff, 'eventsData', 'replace', lambda : events.onEventsDataChanged())
            self.__synchronizeCacheSimpleValue('globalRating', diff.get('account', None), 'globalRating', events.onAccountGlobalRatingChanged)
            cacheDiff = diff.get('cache', {})
            clanFortState = cacheDiff.get('clanFortState', None)
            if clanFortState is not None:
                self.fort.onFortStateDiff(clanFortState)
            if triggerEvents:
                events.onClientUpdated(diff)
                if not isFullSync:
                    for vehTypeCompDescr in diff.get('stats', {}).get('eliteVehicles', ()):
                        events.onVehicleBecomeElite(vehTypeCompDescr)

                    for vehInvID, lockReason in diff.get('cache', {}).get('vehsLock', {}).iteritems():
                        if lockReason is None:
                            lockReason = AccountCommands.LOCK_REASON.NONE
                        events.onVehicleLockChanged(vehInvID, lockReason)

            return True

    def _subscribeForStream(self, requestID, callback):
        self.__onStreamComplete[requestID] = callback

    def __getRequestID(self):
        if g_accountRepository is None:
            return
        else:
            g_accountRepository.requestID += 1
            if g_accountRepository.requestID >= AccountCommands.REQUEST_ID_UNRESERVED_MAX:
                g_accountRepository.requestID = AccountCommands.REQUEST_ID_UNRESERVED_MIN
            return g_accountRepository.requestID

    def __doCmd(self, doCmdMethod, cmd, callback, *args):
        if g_accountRepository is None:
            return
        else:
            requestID = self.__getRequestID()
            if requestID is None:
                return
            if callback is not None:
                self.__onCmdResponse[requestID] = callback
            getattr(self.base, doCmdMethod)(requestID, cmd, *args)
            return

    def __cancelCommands(self):
        for requestID, callback in self.__onCmdResponse.iteritems():
            try:
                callback(requestID, AccountCommands.RES_NON_PLAYER, 'NON_PLAYER')
            except:
                LOG_CURRENT_EXCEPTION()

        self.__onCmdResponse.clear()
        for callback in self.__onStreamComplete.itervalues():
            try:
                callback(False, None)
            except:
                LOG_CURRENT_EXCEPTION()

        self.__onStreamComplete.clear()
        return

    def __synchronizeCacheDict(self, repDict, diffDict, key, syncMode, event):
        if not syncMode in ('update', 'replace'):
            raise AssertionError
            return diffDict is None and None
        else:
            repl = diffDict.get((key, '_r'), None)
            if repl is not None:
                repDict.clear()
                repDict.update(repl)
            diff = diffDict.get(key, None)
            if diff is not None:
                if isinstance(diff, dict):
                    for k, v in diff.iteritems():
                        if v is None:
                            repDict.pop(k, None)
                            continue
                        if syncMode == 'replace':
                            repDict[k] = v
                        else:
                            repDict.setdefault(k, {})
                            repDict[k].update(v)

                else:
                    LOG_WARNING('__synchronizeCacheDict: bad diff=%r for key=%r' % (diff, key))
            if repl is not None or diff is not None:
                event()
            return

    def __synchronizeCacheSimpleValue(self, accountPropName, diffDict, key, event):
        if diffDict is None:
            return
        else:
            for k in (key, (key, '_r')):
                if k in diffDict:
                    value = diffDict[k]
                    prevValue = getattr(self, accountPropName, None)
                    if value != prevValue:
                        setattr(self, accountPropName, diffDict[k])
                        return event(value)

            return

    def __synchronizeEventNotifications(self, diff):
        diffDict = {'added': [],
         'removed': []}
        if diff is None:
            return
        else:
            initialEventsData = diff.get(('eventsData', '_r'), {})
            initial = initialEventsData.pop(EVENT_CLIENT_DATA.NOTIFICATIONS, None)
            initialEventsData.pop(EVENT_CLIENT_DATA.NOTIFICATIONS_REV, None)
            if initial is not None:
                initial = cPickle.loads(zlib.decompress(initial))
                self.eventNotifications = g_accountRepository.eventNotifications = initial
                diffDict['added'].extend(initial)
            updatedEventsData = diff.get('eventsData', {})
            updated = updatedEventsData.pop(EVENT_CLIENT_DATA.NOTIFICATIONS, None)
            updatedEventsData.pop(EVENT_CLIENT_DATA.NOTIFICATIONS_REV, None)
            if updated is not None:
                updated = cPickle.loads(zlib.decompress(updated))
                eventNotifications = self.eventNotifications
                self.eventNotifications = g_accountRepository.eventNotifications = updated
                new = set([ NotificationItem(n) for n in updated ])
                prev = set([ NotificationItem(n) for n in eventNotifications ])
                added = new - prev
                removed = prev - new
                diffDict['added'].extend([ n.item for n in added ])
                diffDict['removed'].extend([ n.item for n in removed ])
            if initial is not None or updated is not None:
                events.onEventNotificationsChanged(diffDict)
                LOG_DZ('Account.__synchronizeEventNotifications, diff=%s' % (diffDict,))
            return


Account = PlayerAccount

class AccountInputHandler():

    def handleKeyEvent(self, event):
        return False

    def handleMouseEvent(self, dx, dy, dz):
        return False


class _AccountRepository(object):

    def __init__(self, name, serverSettings):
        self.contactInfo = ContactInfo()
        self.serverSettings = serverSettings
        self.fileServerSettings = serverSettings['file_server']
        self.syncData = AccountSyncData.AccountSyncData()
        self.inventory = Inventory.Inventory(self.syncData)
        self.stats = Stats.Stats(self.syncData)
        self.questProgress = QuestProgress.QuestProgress(self.syncData)
        self.trader = Trader.Trader(self.syncData)
        self.shop = Shop.Shop()
        self.dossierCache = DossierCache.DossierCache(name)
        self.battleResultsCache = BattleResultsCache.BattleResultsCache()
        self.prebattleAutoInvites = {}
        self.prebattleInvites = {}
        self.clanMembers = {}
        self.eventsData = {}
        self.customFilesCache = CustomFilesCache.CustomFilesCache()
        self.eventNotifications = []
        self.intUserSettings = IntUserSettings.IntUserSettings()
        self.prebattleInvitations = ClientInvitations()
        self.clubs = ClientClubs.ClientClubs(self.syncData)
        self.goodies = ClientGoodies.ClientGoodies(self.syncData)
        self.fort = ClientFortMgr(serverSettings=serverSettings)
        self.onTokenReceived = Event.Event()
        self.requestID = AccountCommands.REQUEST_ID_UNRESERVED_MIN


def _delAccountRepository():
    global g_accountRepository
    LOG_MX('_delAccountRepository')
    if g_accountRepository is None:
        LOG_WARNING('AccountRepository is None')
        return
    else:
        g_accountRepository.customFilesCache.close()
        g_accountRepository.onTokenReceived.clear()
        g_accountRepository = None
        return


def _readClientServerVersion():
    import ResMgr
    fileName = 'scripts/entity_defs/Account.def'
    section = ResMgr.openSection(fileName)
    if section is None:
        raise Exception, 'Cannot open ' + fileName
    for attrName, section in section['Properties'].items():
        if not attrName.startswith('requiredVersion_'):
            continue
        version = section.readString('Default')
        if not version:
            raise Exception, 'Subsection Account.def/Properties/%s/Default is missing or empty' % attrName
        section = None
        ResMgr.purge(fileName)
        return (attrName, version)

    raise Exception, 'Field Account.def/Properties/requiredVersion_* is not found'
    return


_CLIENT_SERVER_VERSION = _readClientServerVersion()
g_accountRepository = None
connectionManager.onDisconnected += _delAccountRepository
