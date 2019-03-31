# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Account.py
# Compiled at: 2019-03-27 17:55:20
import BigWorld, Keys
import cPickle
import zlib
import Event
import items
import copy
import nations
import AccountSyncData
import AccountCommands
import ClientPrebattle
import constants
import Settings
import helpers.i18n
from account_helpers import Inventory, DossierCache, Shop, Stats, Trader, CustomFilesCache
from itertools import izip
from ConnectionManager import connectionManager
from PlayerEvents import g_playerEvents as events
from constants import *
from streamIDs import CHAT_INITIALIZATION_ID, RangeStreamIDCallbacks, STREAM_ID_CHAT_MAX, STREAM_ID_CHAT_MIN
from debug_utils import *
from ContactInfo import ContactInfo
from ClientChat import ClientChat
from ChatManager import chatManager
from OfflineMapCreator import g_offlineMapCreator
from gui.Scaleform import VoiceChatInterface
from adisp import process
from wotdecorators import noexcept

class PlayerAccount(BigWorld.Entity, ClientChat):
    __onStreamCompletePredef = {AccountCommands.REQUEST_ID_PREBATTLES: 'receivePrebattles',
     AccountCommands.REQUEST_ID_PREBATTLE_ROSTER: 'receivePrebattleRoster'}
    __rangeStreamIDCallbacks = RangeStreamIDCallbacks()

    def version_1(self):
        pass

    def __init__(self):
        global g_accountRepository
        ClientChat.__init__(self)
        self.__rangeStreamIDCallbacks.addRangeCallback((STREAM_ID_CHAT_MIN, STREAM_ID_CHAT_MAX), '_ClientChat__receiveStreamedData')
        if g_offlineMapCreator.Active():
            self.name = 'offline_account'
        if g_accountRepository is None:
            g_accountRepository = _AccountRepository(self.name, copy.copy(self.serverSettings['file_server']))
        self.contactInfo = g_accountRepository.contactInfo
        self.syncData = g_accountRepository.syncData
        self.inventory = g_accountRepository.inventory
        self.stats = g_accountRepository.stats
        self.trader = g_accountRepository.trader
        self.shop = g_accountRepository.shop
        self.dossierCache = g_accountRepository.dossierCache
        self.customFilesCache = g_accountRepository.customFilesCache
        self.syncData.setAccount(self)
        self.inventory.setAccount(self)
        self.stats.setAccount(self)
        self.trader.setAccount(self)
        self.shop.setAccount(self)
        self.dossierCache.setAccount(self)
        self.isLongDisconnectedFromCenter = False
        self.prebattle = None
        self.prebattleAutoInvites = g_accountRepository.prebattleAutoInvites
        self.prebattleInvites = g_accountRepository.prebattleInvites
        self.clanMembers = g_accountRepository.clanMembers
        self.isInQueue = False
        self.__onCmdResponse = {}
        self.__onStreamComplete = {}
        return

    @process
    def onBecomePlayer(self):
        LOG_DEBUG('Account.onBecomePlayer()')
        self.isPlayer = True
        self.databaseID = None
        self.inputHandler = AccountInputHandler()
        BigWorld.resetEntityManager(True, False)
        BigWorld.clearAllSpaces()
        self.syncData.onAccountBecomePlayer()
        self.inventory.onAccountBecomePlayer()
        self.stats.onAccountBecomePlayer()
        self.trader.onAccountBecomePlayer()
        self.shop.onAccountBecomePlayer()
        self.dossierCache.onAccountBecomePlayer()
        chatManager.switchPlayerProxy(self)
        events.onAccountBecomePlayer()
        yield VoiceChatInterface.g_instance.initialize(self.serverSettings['vivoxDomain'])
        yield VoiceChatInterface.g_instance.requestCaptureDevices()
        return

    def onBecomeNonPlayer(self):
        LOG_DEBUG('Account.onBecomeNonPlayer()')
        if hasattr(self, 'isPlayer'):
            return self.isPlayer or None
        else:
            self.isPlayer = False
            chatManager.switchPlayerProxy(None)
            self.syncData.onAccountBecomeNonPlayer()
            self.inventory.onAccountBecomeNonPlayer()
            self.stats.onAccountBecomeNonPlayer()
            self.trader.onAccountBecomeNonPlayer()
            self.shop.onAccountBecomeNonPlayer()
            self.dossierCache.onAccountBecomeNonPlayer()
            self.__cancelCommands()
            self.syncData.setAccount(None)
            self.inventory.setAccount(None)
            self.stats.setAccount(None)
            self.trader.setAccount(None)
            self.shop.setAccount(None)
            self.dossierCache.setAccount(None)
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

    def onKickedFromServer(self, reason, isBan, expiryTime):
        LOG_MX('onKickedFromServer', reason, isBan, expiryTime)
        from gui.Scaleform.Disconnect import Disconnect
        Disconnect.showKick(reason, isBan, expiryTime)

    def onStreamComplete(self, id, data):
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
            return

    def onEnqueued(self):
        LOG_DEBUG('onEnqueued')
        self.isInQueue = True
        events.onEnqueued()

    def onEnqueueFailure(self, errorCode, errorStr):
        LOG_DEBUG('onEnqueueFailure', errorCode, errorStr)
        events.onEnqueueFailure(errorCode, errorStr)

    def onDequeued(self):
        LOG_DEBUG('onDequeued')
        self.isInQueue = False
        events.onDequeued()

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

    def onKickedFromQueue(self):
        LOG_DEBUG('onKickedFromQueue')
        self.isInQueue = False
        events.onKickedFromQueue()

    def onKickedFromArena(self, reasonCode):
        LOG_DEBUG('onKickedFromArena', reasonCode)
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

    def handleKeyEvent(self, event):
        return False

    def showGUI(self, ctx):
        ctx = cPickle.loads(ctx)
        LOG_MX('showGUI', ctx)
        self.databaseID = ctx['databaseID']
        if 'prebattleID' in ctx:
            self.prebattle = ClientPrebattle.ClientPrebattle(ctx['prebattleID'])
        if 'queueID' in ctx:
            self.isInQueue = True
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

    def receiveQueueInfo(self, randomsQueueInfo, companiesQueueInfo):
        events.onQueueInfoReceived(randomsQueueInfo, companiesQueueInfo)

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

    def update(self, diff):
        self._update(True, cPickle.loads(diff))

    def resyncDossiers(self):
        self.dossierCache.resynchronize()

    def requestQueueInfo(self, queueType):
        if not events.isPlayerEntityChanging:
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

    def requestArenaList(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_REQ_ARENA_LIST, 0, 0, 0)

    def requestServerStats(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_REQ_SERVER_STATS, 0, 0, 0)

    def requestPlayerInfo(self, name, callback):
        if events.isPlayerEntityChanging:
            return
        proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, ext.get('dossier', ''), ext.get('clanDBID', 0), ext.get('clanInfo', None))
        self._doCmdStr(AccountCommands.CMD_REQ_PLAYER_INFO, name, proxy)

    def requestAccountDossier(self, name, callback):
        if events.isPlayerEntityChanging:
            return
        proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, ext.get('dossier', ''))
        self._doCmdStr(AccountCommands.CMD_REQ_ACCOUNT_DOSSIER, name, proxy)

    def requestVehicleDossier(self, name, vehTypeCompDescr, callback):
        if events.isPlayerEntityChanging:
            return
        proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, ext.get('dossier', ''))
        self._doCmdInt2Str(AccountCommands.CMD_REQ_VEHICLE_DOSSIER, vehTypeCompDescr, 0, name, proxy)

    def requestPlayerClanInfo(self, name, callback):
        if events.isPlayerEntityChanging:
            return
        proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, errorStr, ext.get('clanDBID', 0), ext.get('clanInfo', None))
        self._doCmdInt2Str(AccountCommands.CMD_REQ_PLAYER_CLAN_INFO, 0, 0, name, proxy)

    def enqueueForArena(self, vehInvID, arenaTypeID=0):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_FOR_ARENA, vehInvID, arenaTypeID, 0)

    def dequeue(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE, 0, 0, 0)

    def createArenaFromQueue(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_FORCE_QUEUE, 0, 0, 0)

    def createArena(self, typeID, roundLength):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_CREATE_ARENA, roundLength, 0, typeID)

    def joinArena(self, arenaID, team, vehInvID):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_JOIN_ARENA, arenaID, team, vehInvID)

    def prb_createTraining(self, arenaTypeID, roundLength, isOpened, comment):
        if events.isPlayerEntityChanging:
            return
        self.base.createTraining(arenaTypeID, roundLength, isOpened, comment)

    def prb_createSquad(self):
        if events.isPlayerEntityChanging:
            return
        self.base.createSquad()

    def prb_createCompany(self, isOpened, comment, division=PREBATTLE_COMPANY_DIVISION.ABSOLUTE):
        if events.isPlayerEntityChanging:
            return
        self.base.createCompany(isOpened, comment, division)

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

    def prb_teamReady(self, team, force, callback):
        if events.isPlayerEntityChanging:
            return
        self._doCmdInt3(AccountCommands.CMD_PRB_TEAM_READY, team, 1 if force else 0, 0, lambda requestID, resultID, errorStr: callback(resultID))

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

    def challengeCaptcha(self, challenge, response, callback):
        if events.isPlayerEntityChanging:
            return
        self._doCmdInt2Str(AccountCommands.CMD_CAPTCHA_CHALLENGE, len(challenge), 0, challenge + response, lambda requestID, resultID, errorCode, ext={}: callback(resultID, errorCode))

    def setLanguage(self, language):
        self._doCmdStr(AccountCommands.CMD_SET_LANGUAGE, language, None)
        return

    def makeDenunciation(self, violatorID, topicID, violatorKind):
        self._doCmdInt3(AccountCommands.CMD_MAKE_DENUNCIATION, violatorID, topicID, violatorKind, None)
        return

    def completeTutorial(self, tutorialID, callback):
        from CurrentVehicle import g_currentVehicle
        curVehInvID = g_currentVehicle.vehicle.inventoryId
        proxy = lambda requestID, resultID, errorStr, bonus=None: callback(resultID, bonus)
        self._doCmdInt3(AccountCommands.CMD_COMPLETE_TUTORIAL, tutorialID, curVehInvID, 0, proxy)
        return

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
            callback(steamID, itemID, STEAM_ERROR.GENERAL)

    def steamFinalizeTxn(self, steamID, orderID, callback):
        try:
            data = str(steamID) + ':' + str(orderID)
            self._doCmdStr(AccountCommands.CMD_STEAM_FINALIZE_TXN, data, lambda requestID, error, errorStr: callback(steamID, orderID, error))
        except:
            callback(steamID, orderID, STEAM_ERROR.GENERAL)

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
        LOG_MX('_update', diff if triggerEvents else 'full sync')
        isFullSync = diff.get('prevRev', None) is None
        self.syncData.revision = diff.get('rev', 0)
        self.inventory.synchronize(isFullSync, diff)
        self.stats.synchronize(isFullSync, diff)
        self.trader.synchronize(isFullSync, diff)
        self.__synchronizeCacheDict(self.prebattleAutoInvites, diff.get('account', None), 'prebattleAutoInvites', 'replace', events.onPrebattleAutoInvitesChanged)
        self.__synchronizeCacheDict(self.prebattleInvites, diff, 'prebattleInvites', 'update', lambda : events.onPrebattleInvitesChanged(diff))
        self.__synchronizeCacheDict(self.clanMembers, diff.get('cache', None), 'clanMembers', 'replace', events.onClanMembersListChanged)
        if triggerEvents:
            events.onClientUpdated(diff)
            if not isFullSync:
                for vehTypeCompDescr in diff.get('stats', {}).get('eliteVehicles', ()):
                    events.onVehicleBecomeElite(vehTypeCompDescr)

                for vehInvID, lockReason in diff.get('cache', {}).get('vehsLock', {}).iteritems():
                    if lockReason is None:
                        lockReason = AccountCommands.LOCK_REASON.NONE
                    events.onVehicleLockChanged(vehInvID, lockReason)

        return

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
        assert syncMode in ('update', 'replace')
        if diffDict is None:
            return
        else:
            repl = diffDict.get('%s_r' % key, None)
            if repl is not None:
                repDict.clear()
                repDict.update(repl)
            diff = diffDict.get(key, None)
            if diff is not None:
                for k, v in diff.iteritems():
                    if v is None:
                        repDict.pop(k, None)
                        continue
                    if syncMode == 'replace':
                        repDict[k] = v
                    else:
                        repDict.setdefault(k, {})
                        repDict[k].update(v)

            if repl is not None or diff is not None:
                event()
            return


Account = PlayerAccount

class AccountInputHandler():

    def handleKeyEvent(self, event):
        return False

    def handleMouseEvent(self, dx, dy, dz):
        return False


class _AccountRepository(object):

    def __init__(self, name, fileServerSettings):
        self.contactInfo = ContactInfo()
        self.fileServerSettings = fileServerSettings
        self.syncData = AccountSyncData.AccountSyncData()
        self.inventory = Inventory.Inventory(self.syncData)
        self.stats = Stats.Stats(self.syncData)
        self.trader = Trader.Trader(self.syncData)
        self.shop = Shop.Shop()
        self.dossierCache = DossierCache.DossierCache(name)
        self.prebattleAutoInvites = {}
        self.prebattleInvites = {}
        self.clanMembers = {}
        self.customFilesCache = CustomFilesCache.CustomFilesCache()
        self.requestID = AccountCommands.REQUEST_ID_UNRESERVED_MIN


def _delAccountRepository():
    global g_accountRepository
    LOG_MX('_delAccountRepository')
    g_accountRepository = None
    return


g_accountRepository = None
connectionManager.onDisconnected += _delAccountRepository
