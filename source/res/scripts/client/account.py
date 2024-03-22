# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Account.py
import cPickle
import copy
import logging
import weakref
import zlib
from collections import namedtuple
import BigWorld
import AccountCommands
import ClientPrebattle
import Event
from ChatManager import chatManager
from ClientChat import ClientChat
from ClientGlobalMap import ClientGlobalMap
from ClientUnitMgr import ClientUnitMgr, ClientUnitBrowser
from ContactInfo import ContactInfo
from OfflineMapCreator import g_offlineMapCreator
from PlayerEvents import g_playerEvents as events
from account_helpers import AccountSyncData, Inventory, DossierCache, Shop, Stats, QuestProgress, CustomFilesCache, BattleResultsCache, ClientGoodies, client_blueprints, client_recycle_bin, client_anonymizer, ClientBattleRoyale
from account_helpers import ClientInvitations, vehicle_rotation
from account_helpers import client_epic_meta_game, tokens
from account_helpers import client_ranked, ClientBadges
from account_helpers.achievements20 import Achievements20
from account_helpers.battle_pass import BattlePassManager
from account_helpers.dog_tags import DogTags
from account_helpers.festivity_manager import FestivityManager
from account_helpers.game_restrictions import GameRestrictions
from account_helpers.gift_system import GiftSystem
from account_helpers.maps_training import MapsTraining
from account_helpers.offers.sync_data import OffersSyncData
from account_helpers.resource_well import ResourceWell
from account_helpers.session_statistics import SessionStatistics
from account_helpers.settings_core import IntUserSettings
from account_helpers.spa_flags import SPAFlags
from account_helpers.telecom_rentals import TelecomRentals
from account_helpers.trade_in import TradeIn
from account_helpers.winback import Winback
from account_shared import NotificationItem, readClientServerVersion
from constants import ARENA_BONUS_TYPE, QUEUE_TYPE, EVENT_CLIENT_DATA, ARENA_GUI_TYPE
from constants import PREBATTLE_INVITE_STATUS, PREBATTLE_TYPE, ARENA_GAMEPLAY_MASK_DEFAULT, ENABLE_FREE_PREMIUM_CREW
from debug_utils import LOG_DEBUG, LOG_CURRENT_EXCEPTION, LOG_ERROR, LOG_DEBUG_DEV, LOG_WARNING
from gui.clans.clan_cache import g_clanCache
from gui.prb_control import prbEntityProperty
from gui.wgnc import g_wgncProvider
from helpers import dependency
from helpers import uniprof
from items import tankmen
from messenger import MessengerEntry
from shared_utils.account_helpers.diff_utils import synchronizeDicts
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared.utils import IHangarSpace
from soft_exception import SoftException
from streamIDs import RangeStreamIDCallbacks, STREAM_ID_CHAT_MAX, STREAM_ID_CHAT_MIN
StreamData = namedtuple('StreamData', ['data',
 'isCorrupted',
 'origPacketLen',
 'packetLen',
 'origCrc32',
 'crc32'])
StreamData.__new__.__defaults__ = (None,) * len(StreamData._fields)
_logger = logging.getLogger(__name__)

def _isInt(a):
    return isinstance(a, (int, long))


def _isStr(a):
    return isinstance(a, str)


def _isList(a):
    return isinstance(a, (list, tuple))


def _isIntList(l):
    return _isList(l) and all([ _isInt(arg) for arg in l ])


def _isStrList(l):
    return _isList(l) and all([ _isStr(arg) for arg in l ])


class _ClientCommandProxy(object):
    _COMMAND_SIGNATURES = (('doCmdStr', lambda args: len(args) == 1 and _isStr(args[0])),
     ('doCmdIntStr', lambda args: len(args) == 2 and _isInt(args[0]) and _isStr(args[1])),
     ('doCmdInt', lambda args: len(args) == 1 and _isInt(args[0])),
     ('doCmdInt2', lambda args: len(args) == 2 and all([ _isInt(arg) for arg in args ])),
     ('doCmdInt3', lambda args: len(args) == 3 and all([ _isInt(arg) for arg in args ])),
     ('doCmdInt4', lambda args: len(args) == 4 and all([ _isInt(arg) for arg in args ])),
     ('doCmdInt2Str', lambda args: len(args) == 3 and _isStr(args[2]) and all([ _isInt(arg) for arg in args[:2] ])),
     ('doCmdInt3Str', lambda args: len(args) == 4 and _isStr(args[3]) and all([ _isInt(arg) for arg in args[:3] ])),
     ('doCmdIntArr', lambda args: len(args) == 1 and _isIntList(args[0])),
     ('doCmdIntStrArr', lambda args: len(args) == 2 and _isInt(args[0]) and _isStrList(args[1])),
     ('doCmdStrArr', lambda args: len(args) == 1 and _isStrList(args[0])),
     ('doCmdIntArrStrArr', lambda args: len(args) == 2 and _isIntList(args[0]) and _isStrList(args[1])))

    def __init__(self):
        super(_ClientCommandProxy, self).__init__()
        self.__commandGateway = None
        return

    def setGateway(self, commandGateway):
        self.__commandGateway = commandGateway

    def perform(self, commandName, *args):
        if self.__commandGateway is None:
            raise SoftException('Cliend command proxy is not ready')
        callback = args[-1]
        commandArgs = args[:-1]
        for commandType, signatureCheck in self._COMMAND_SIGNATURES:
            if signatureCheck(commandArgs):
                self.__commandGateway(commandType, commandName, callback, *commandArgs)
                break
        else:
            raise SoftException('Command "{}" failed. Given signature is not supported.'.format(commandName))

        return


class PlayerAccount(BigWorld.Entity, ClientChat):
    __onStreamCompletePredef = {AccountCommands.REQUEST_ID_PREBATTLES: 'receivePrebattles',
     AccountCommands.REQUEST_ID_PREBATTLE_ROSTER: 'receivePrebattleRoster'}
    lobbyContext = dependency.descriptor(ILobbyContext)
    connectionMgr = dependency.descriptor(IConnectionManager)
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        global g_accountRepository
        _logger.info('client Account.init')
        propertyName, propertyValue = _CLIENT_SERVER_VERSION
        self.connectionMgr.checkClientServerVersions(propertyValue, getattr(self, propertyName, None))
        ClientChat.__init__(self)
        self.__rangeStreamIDCallbacks = RangeStreamIDCallbacks()
        self.__rangeStreamIDCallbacks.addRangeCallback((STREAM_ID_CHAT_MIN, STREAM_ID_CHAT_MAX), '_ClientChat__receiveStreamedData')
        self.lastStreamData = StreamData()
        if g_offlineMapCreator.Active():
            self.name = 'offline_account'
        className = self.__class__.__name__
        if g_accountRepository is not None and g_accountRepository.className != className:
            self.connectionMgr.onDisconnected -= delAccountRepository
            delAccountRepository()
        if g_accountRepository is None:
            g_accountRepository = _AccountRepository(self.name, className, self.initialServerSettings)
            self.connectionMgr.onDisconnected += delAccountRepository
        self.contactInfo = g_accountRepository.contactInfo
        self.syncData = g_accountRepository.syncData
        self.serverSettings = g_accountRepository.serverSettings
        self.inventory = g_accountRepository.inventory
        self.stats = g_accountRepository.stats
        self.questProgress = g_accountRepository.questProgress
        self.shop = g_accountRepository.shop
        self.dossierCache = g_accountRepository.dossierCache
        self.battleResultsCache = g_accountRepository.battleResultsCache
        self.intUserSettings = g_accountRepository.intUserSettings
        self.prebattleInvitations = g_accountRepository.prebattleInvitations
        self.gMap = g_accountRepository.gMap
        self.goodies = g_accountRepository.goodies
        self.vehicleRotation = g_accountRepository.vehicleRotation
        self.recycleBin = g_accountRepository.recycleBin
        self.ranked = g_accountRepository.ranked
        self.battleRoyale = g_accountRepository.battleRoyale
        self.badges = g_accountRepository.badges
        self.tokens = g_accountRepository.tokens
        self.epicMetaGame = g_accountRepository.epicMetaGame
        self.blueprints = g_accountRepository.blueprints
        self.festivities = g_accountRepository.festivities
        self.sessionStats = g_accountRepository.sessionStats
        self.spaFlags = g_accountRepository.spaFlags
        self.anonymizer = g_accountRepository.anonymizer
        self.dailyQuests = g_accountRepository.dailyQuests
        self.battlePass = g_accountRepository.battlePass
        self.offers = g_accountRepository.offers
        self.dogTags = g_accountRepository.dogTags
        self.mapsTraining = g_accountRepository.mapsTraining
        self.telecomRentals = g_accountRepository.telecomRentals
        self.tradeIn = g_accountRepository.tradeIn
        self.giftSystem = g_accountRepository.giftSystem
        self.gameRestrictions = g_accountRepository.gameRestrictions
        self.resourceWell = g_accountRepository.resourceWell
        self.winback = g_accountRepository.winback
        self.achievements20 = g_accountRepository.achievements20
        self.customFilesCache = g_accountRepository.customFilesCache
        self.syncData.setAccount(self)
        self.inventory.setAccount(self)
        self.stats.setAccount(self)
        self.questProgress.setAccount(self)
        self.shop.setAccount(self)
        self.achievements20.setAccount(self)
        self.dossierCache.setAccount(self)
        self.battleResultsCache.setAccount(self)
        self.intUserSettings.setProxy(self, self.syncData)
        self.prebattleInvitations.setProxy(self)
        self.gMap.setAccount(self)
        self.goodies.setAccount(self)
        self.vehicleRotation.setAccount(self)
        self.recycleBin.setAccount(self)
        self.ranked.setAccount(self)
        self.battleRoyale.setAccount(self)
        self.badges.setAccount(self)
        self.tokens.setAccount(self)
        self.epicMetaGame.setAccount(self)
        self.blueprints.setAccount(self)
        self.sessionStats.setAccount(self)
        self.spaFlags.setAccount(self)
        self.anonymizer.setAccount(self)
        self.offers.setAccount(self)
        self.dogTags.setAccount(self)
        self.mapsTraining.setAccount(self)
        self.telecomRentals.setAccount(self)
        self.tradeIn.setAccount(self)
        g_accountRepository.commandProxy.setGateway(self.__doCmd)
        self.isLongDisconnectedFromCenter = False
        self.prebattle = None
        self.unitBrowser = ClientUnitBrowser(self)
        self.unitMgr = ClientUnitMgr(self)
        self.prebattleAutoInvites = g_accountRepository.prebattleAutoInvites
        self.globalRating = 0
        self.prebattleInvites = g_accountRepository.prebattleInvites
        self.eventNotifications = g_accountRepository.eventNotifications
        self.clanMembers = g_accountRepository.clanMembers
        self.eventsData = g_accountRepository.eventsData
        self.__eventsDataUnpacked = {}
        self.personalMissionsLock = g_accountRepository.personalMissionsLock
        self.battleQueueType = QUEUE_TYPE.UNKNOWN
        self.platformBlueprintsConvertSaleLimits = g_accountRepository.platformBlueprintsConvertSaleLimits
        self.freePremiumCrew = g_accountRepository.freePremiumCrew
        self.__onCmdResponse = {}
        self.__onStreamComplete = {}
        self.__objectsSelectionEnabled = True
        self.__selectedEntity = None
        return

    def onBecomePlayer(self):
        uniprof.enterToRegion('player.account.entering')
        _logger.info('Account.onBecomePlayer()')
        self.databaseID = None
        self.inputHandler = AccountInputHandler()
        BigWorld.clearAllSpaces()
        self.syncData.onAccountBecomePlayer()
        self.inventory.onAccountBecomePlayer()
        self.stats.onAccountBecomePlayer()
        self.questProgress.onAccountBecomePlayer()
        self.shop.onAccountBecomePlayer()
        self.dossierCache.onAccountBecomePlayer()
        self.battleResultsCache.onAccountBecomePlayer()
        self.intUserSettings.onProxyBecomePlayer()
        self.prebattleInvitations.onProxyBecomePlayer()
        self.goodies.onAccountBecomePlayer()
        self.vehicleRotation.onAccountBecomePlayer()
        self.recycleBin.onAccountBecomePlayer()
        self.ranked.onAccountBecomePlayer()
        self.battleRoyale.onAccountBecomePlayer()
        self.badges.onAccountBecomePlayer()
        self.tokens.onAccountBecomeNonPlayer()
        self.epicMetaGame.onAccountBecomePlayer()
        self.blueprints.onAccountBecomePlayer()
        self.festivities.onAccountBecomePlayer()
        self.dogTags.onAccountBecomePlayer()
        self.mapsTraining.onAccountBecomePlayer()
        self.telecomRentals.onAccountBecomePlayer()
        self.sessionStats.onAccountBecomePlayer()
        self.spaFlags.onAccountBecomePlayer()
        self.anonymizer.onAccountBecomePlayer()
        self.battlePass.onAccountBecomePlayer()
        self.offers.onAccountBecomePlayer()
        self.giftSystem.onAccountBecomePlayer()
        self.gameRestrictions.onAccountBecomePlayer()
        self.resourceWell.onAccountBecomePlayer()
        self.achievements20.onAccountBecomePlayer()
        chatManager.switchPlayerProxy(self)
        events.onAccountBecomePlayer()
        BigWorld.target.source = BigWorld.MouseTargetingMatrix()
        BigWorld.target.maxDistance = 700
        BigWorld.target.skeletonCheckEnabled = True
        BigWorld.target.caps()
        BigWorld.target.isEnabled = True
        uniprof.exitFromRegion('player.account.entering')
        return

    def onBecomeNonPlayer(self):
        uniprof.enterToRegion('player.account.exiting')
        _logger.info('Account.onBecomeNonPlayer()')
        chatManager.switchPlayerProxy(None)
        self.syncData.onAccountBecomeNonPlayer()
        self.inventory.onAccountBecomeNonPlayer()
        self.stats.onAccountBecomeNonPlayer()
        self.questProgress.onAccountBecomeNonPlayer()
        self.shop.onAccountBecomeNonPlayer()
        self.dossierCache.onAccountBecomeNonPlayer()
        self.battleResultsCache.onAccountBecomeNonPlayer()
        self.intUserSettings.onProxyBecomeNonPlayer()
        self.prebattleInvitations.onProxyBecomeNonPlayer()
        self.goodies.onAccountBecomeNonPlayer()
        self.vehicleRotation.onAccountBecomeNonPlayer()
        self.recycleBin.onAccountBecomeNonPlayer()
        self.ranked.onAccountBecomeNonPlayer()
        self.battleRoyale.onAccountBecomeNonPlayer()
        self.badges.onAccountBecomeNonPlayer()
        self.tokens.onAccountBecomeNonPlayer()
        self.epicMetaGame.onAccountBecomeNonPlayer()
        self.blueprints.onAccountBecomeNonPlayer()
        self.festivities.onAccountBecomeNonPlayer()
        self.sessionStats.onAccountBecomeNonPlayer()
        self.spaFlags.onAccountBecomeNonPlayer()
        self.anonymizer.onAccountBecomeNonPlayer()
        self.battlePass.onAccountBecomeNonPlayer()
        self.offers.onAccountBecomeNonPlayer()
        self.dogTags.onAccountBecomeNonPlayer()
        self.mapsTraining.onAccountBecomeNonPlayer()
        self.telecomRentals.onAccountBecomeNonPlayer()
        self.giftSystem.onAccountBecomeNonPlayer()
        self.gameRestrictions.onAccountBecomeNonPlayer()
        self.resourceWell.onAccountBecomeNonPlayer()
        self.achievements20.onAccountBecomeNonPlayer()
        self.__cancelCommands()
        self.syncData.setAccount(None)
        self.inventory.setAccount(None)
        self.stats.setAccount(None)
        self.questProgress.setAccount(None)
        self.shop.setAccount(None)
        self.dossierCache.setAccount(None)
        self.battleResultsCache.setAccount(None)
        self.intUserSettings.setProxy(None, None)
        self.prebattleInvitations.setProxy(None)
        self.goodies.setAccount(None)
        self.vehicleRotation.setAccount(None)
        self.recycleBin.setAccount(None)
        self.ranked.setAccount(None)
        self.battleRoyale.setAccount(None)
        self.badges.setAccount(None)
        self.tokens.setAccount(None)
        self.epicMetaGame.setAccount(None)
        self.blueprints.setAccount(None)
        self.sessionStats.setAccount(None)
        self.spaFlags.setAccount(None)
        self.anonymizer.setAccount(None)
        self.offers.setAccount(None)
        self.achievements20.setAccount(None)
        g_accountRepository.commandProxy.setGateway(None)
        self.unitMgr.clear()
        self.unitBrowser.clear()
        events.onAccountBecomeNonPlayer()
        del self.inputHandler
        uniprof.exitFromRegion('player.account.exiting')
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

    def getServerSettings(self):
        return g_accountRepository.serverSettings

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

    def onKickedFromServer(self, reason, kickReasonType, expiryTime):
        LOG_DEBUG('onKickedFromServer', reason, kickReasonType, expiryTime)
        self.connectionMgr.setKickedFromServer(reason, kickReasonType, expiryTime)

    def getUnpackedEventsData(self, typeID):
        eventsData = {}
        if typeID not in self.eventsData:
            return eventsData
        currentRevID = EVENT_CLIENT_DATA.REVISION(typeID)
        currentRev = self.eventsData[currentRevID]
        if typeID in self.__eventsDataUnpacked:
            unpackedRev, eventsData = self.__eventsDataUnpacked[typeID]
            if unpackedRev != currentRev:
                del self.__eventsDataUnpacked[typeID]
            else:
                return eventsData
        try:
            eventsData = cPickle.loads(zlib.decompress(self.eventsData[typeID]))
            self.__eventsDataUnpacked[typeID] = (currentRev, eventsData)
        except (zlib.error, cPickle.UnpicklingError):
            LOG_CURRENT_EXCEPTION()

        return eventsData

    def onStreamComplete(self, streamID, desc, data):
        isCorrupted, origPacketLen, packetLen, origCrc32, crc32 = desc
        self.lastStreamData = StreamData(data, *desc)
        if isCorrupted:
            self.base.logStreamCorruption(streamID, origPacketLen, packetLen, origCrc32, crc32)
        callback = self.__rangeStreamIDCallbacks.getCallbackForStreamID(streamID)
        if callback is not None:
            getattr(self, callback)(streamID, data)
            return
        else:
            callback = self.__onStreamCompletePredef.get(streamID, None)
            if callback is not None:
                getattr(self, callback)(True, data)
                return
            callback = self.__onStreamComplete.pop(streamID, None)
            if callback is not None:
                callback(True, data)
            self.lastStreamData = StreamData()
            return

    def isInBattleQueue(self):
        return self.battleQueueType != QUEUE_TYPE.UNKNOWN

    def onEnqueued(self, queueType):
        LOG_DEBUG('onEnqueued', queueType)
        self.battleQueueType = queueType
        events.onEnqueued(queueType)

    def onEnqueueFailure(self, queueType, errorCode, errorStr):
        LOG_DEBUG('onEnqueueFailure', queueType, errorCode, errorStr)
        events.onEnqueueFailure(queueType, errorCode, errorStr)

    def onDequeued(self, queueType):
        LOG_DEBUG('onDequeued', queueType)
        self.battleQueueType = QUEUE_TYPE.UNKNOWN
        events.onDequeued(queueType)

    def targetFocus(self, entity):
        if self.__objectsSelectionEnabled:
            self.hangarSpace.onMouseEnter(entity)
            self.__selectedEntity = weakref.proxy(entity)

    def targetBlur(self, prevEntity):
        if self.__objectsSelectionEnabled:
            self.hangarSpace.onMouseExit(prevEntity)
            self.__selectedEntity = None
        return

    def objectsSelectionEnabled(self, enabled):
        if not enabled and self.__selectedEntity is not None:
            self.targetBlur(self.__selectedEntity)
        self.__objectsSelectionEnabled = enabled
        return

    def onKickedFromQueue(self, queueType):
        LOG_DEBUG('onKickedFromQueue', queueType)
        self.battleQueueType = QUEUE_TYPE.UNKNOWN
        events.onKickedFromQueue(queueType)

    def onArenaCreated(self):
        LOG_DEBUG('onArenaCreated')
        self.prebattle = None
        events.isPlayerEntityChanging = True
        events.onArenaCreated()
        events.onPlayerEntityChanging()
        return

    def onArenaJoinFailure(self, errorCode, errorStr):
        LOG_DEBUG('onArenaJoinFailure', errorCode, errorStr)
        self.battleQueueType = QUEUE_TYPE.UNKNOWN
        events.isPlayerEntityChanging = False
        events.onPlayerEntityChangeCanceled()
        events.onArenaJoinFailure(errorCode, errorStr)

    def onPrebattleJoined(self, prebattleID):
        self.prebattle = ClientPrebattle.ClientPrebattle(prebattleID)
        events.onPrebattleJoined()

    def onPrebattleJoinFailure(self, errorCode):
        LOG_DEBUG('onPrebattleJoinFailure', errorCode)
        events.onPrebattleJoinFailure(errorCode)

    def onPrebattleLeft(self):
        LOG_DEBUG('onPrebattleLeft')
        self.prebattle = None
        events.onPrebattleLeft()
        return

    def onUnitUpdate(self, *args):
        self.unitMgr.onUnitUpdate(*args)

    def onGlobalMapUpdate(self, *args):
        self.gMap.onGlobalMapUpdate(*args)

    def onGlobalMapReply(self, *args):
        self.gMap.onGlobalMapReply(*args)

    def onUnitError(self, *args):
        self.unitMgr.onUnitError(*args)

    def onUnitNotify(self, *args):
        self.unitMgr.onUnitNotify(*args)

    def onUnitCallOk(self, *args):
        self.unitMgr.onUnitCallOk(*args)

    def onUnitBrowserError(self, *args):
        self.unitBrowser.onError(*args)

    def onUnitBrowserResultsSet(self, *args):
        self.unitBrowser.onResultsSet(*args)

    def onUnitBrowserResultsUpdate(self, *args):
        self.unitBrowser.onResultsUpdate(*args)

    def onKickedFromArena(self, reasonCode):
        LOG_DEBUG('onKickedFromArena', reasonCode)
        self.battleQueueType = QUEUE_TYPE.UNKNOWN
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

    def receiveNotification(self, notification):
        LOG_DEBUG('receiveNotification', notification)
        g_wgncProvider.fromXmlString(notification)
        events.onNotification(notification)

    def sendNotificationReply(self, notificationID, purge, actionName):
        self.base.doCmdInt2Str(0, AccountCommands.CMD_NOTIFICATION_REPLY, notificationID, purge, actionName)

    def handleKeyEvent(self, event):
        return False

    def showGUI(self, ctx):
        ctx = cPickle.loads(ctx)
        _logger.info('showGUI %r', ctx)
        self.databaseID = ctx['databaseID']
        if 'prebattleID' in ctx:
            self.prebattle = ClientPrebattle.ClientPrebattle(ctx['prebattleID'])
        self.battleQueueType = ctx.get('inQueue', QUEUE_TYPE.UNKNOWN)
        self._initTimeCorrection(ctx)
        if 'isLongDisconnectedFromCenter' in ctx:
            isLongDisconnectedFromCenter = ctx['isLongDisconnectedFromCenter']
            if self.isLongDisconnectedFromCenter != isLongDisconnectedFromCenter:
                self.isLongDisconnectedFromCenter = isLongDisconnectedFromCenter
                events.onCenterIsLongDisconnected(isLongDisconnectedFromCenter)
        events.isPlayerEntityChanging = False
        if ctx.get('skipShowGUI', False):
            events.onAccountShowGUISkipped(ctx)
        else:
            events.onAccountShowGUI(ctx)

    def receiveQueueInfo(self, queueInfo):
        events.onQueueInfoReceived(queueInfo)

    def receivePrebattles(self, isSuccess, data):
        if isSuccess:
            try:
                data = zlib.decompress(data)
                prbType, prbCount, prebattles = cPickle.loads(data)
            except Exception:
                LOG_CURRENT_EXCEPTION()
                isSuccess = False

        if not isSuccess:
            prbType, prbCount, prebattles = 0, 0, []
        events.onPrebattlesListReceived(prbType, prbCount, prebattles)

    def receivePrebattleRoster(self, isSuccess, data):
        if isSuccess:
            try:
                data = zlib.decompress(data)
                prebattleID, rosterAsList = cPickle.loads(data)
            except Exception:
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

    def resyncDossiers(self, isFullResync):
        self.dossierCache.resynchronize(isFullResync)

    def requestQueueInfo(self, queueType, intArg1=0, intArg2=0):
        if self.isPlayer:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_REQ_QUEUE_INFO, queueType, intArg1, intArg2)

    def requestPrebattles(self, prbType, sort_key, idle, start, end):
        if not events.isPlayerEntityChanging:
            self.base.doCmdIntArr(AccountCommands.REQUEST_ID_PREBATTLES, AccountCommands.CMD_REQ_PREBATTLES, [prbType,
             sort_key,
             int(idle),
             start,
             end])

    def requestPrebattlesByName(self, prbType, idle, creatorMask):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt2Str(AccountCommands.REQUEST_ID_PREBATTLES, AccountCommands.CMD_REQ_PREBATTLES_BY_CREATOR, prbType, int(idle), creatorMask)

    def requestPrebattleRoster(self, prebattleID):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_PREBATTLE_ROSTER, AccountCommands.CMD_REQ_PREBATTLE_ROSTER, prebattleID, 0, 0)

    def requestServerStats(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_REQ_SERVER_STATS, 0, 0, 0)

    def requestPlayerInfo(self, databaseID, callback):
        if events.isPlayerEntityChanging:
            return
        proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, ext.get('databaseID', 0L), ext.get('dossier', ''), ext.get('clanDBID', 0), ext.get('clanInfo', None), ext.get('globalRating', 0), ext.get('eSportSeasons', {}), ext.get('ranked', {}), ext.get('dogTag', {}), ext.get('battleRoyaleStats', {}), ext.get('wtr', None), ext.get('layout', None), ext.get('layoutState', None))
        self._doCmdInt3(AccountCommands.CMD_REQ_PLAYER_INFO, databaseID, 0, 0, proxy)

    def requestAccountDossier(self, accountID, callback):
        if events.isPlayerEntityChanging:
            return
        proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, ext.get('dossier', ''))
        self._doCmdInt3(AccountCommands.CMD_REQ_ACCOUNT_DOSSIER, accountID, 0, 0, proxy)

    def requestVehicleDossier(self, databaseID, vehTypeCompDescr, callback):
        if events.isPlayerEntityChanging:
            return
        proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, ext.get('dossier', ''))
        self._doCmdInt3(AccountCommands.CMD_REQ_VEHICLE_DOSSIER, databaseID, vehTypeCompDescr, 0, proxy)

    def requestPlayerClanInfo(self, databaseID, callback):
        if events.isPlayerEntityChanging:
            return
        proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, errorStr, ext.get('clanDBID', 0), ext.get('clanInfo', None))
        self._doCmdInt3(AccountCommands.CMD_REQ_PLAYER_CLAN_INFO, databaseID, 0, 0, proxy)

    def requestPlayerGlobalRating(self, accountID, callback):
        if events.isPlayerEntityChanging:
            return
        proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, errorStr, ext.get('globalRating', 0))
        self._doCmdInt3(AccountCommands.CMD_REQ_PLAYER_GLOBAL_RATING, accountID, 0, 0, proxy)

    def requestPlayersGlobalRating(self, accountIDs, callback):
        proxy = lambda requestID, resultID, errorStr, ext=None: callback(resultID, errorStr, ext)
        self._doCmdIntArrStrArr(AccountCommands.CMD_REQ_PLAYERS_GLOBAL_RATING, accountIDs, [], proxy)
        return

    def enqueueRandom(self, vehInvID, gameplaysMask=ARENA_GAMEPLAY_MASK_DEFAULT, arenaTypeID=0, randomFlags=0):
        if events.isPlayerEntityChanging:
            return
        self.base.doCmdIntArr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_IN_BATTLE_QUEUE, [QUEUE_TYPE.RANDOMS,
         vehInvID,
         gameplaysMask,
         arenaTypeID,
         randomFlags])

    def dequeueRandom(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_FROM_BATTLE_QUEUE, QUEUE_TYPE.RANDOMS)

    def enqueueEventBattles(self, vehInvID):
        if not events.isPlayerEntityChanging:
            self.base.doCmdIntArr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_IN_BATTLE_QUEUE, [QUEUE_TYPE.EVENT_BATTLES, vehInvID])

    def dequeueEventBattles(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_FROM_BATTLE_QUEUE, QUEUE_TYPE.EVENT_BATTLES)

    def enqueueRanked(self, vehInvID):
        if events.isPlayerEntityChanging:
            return
        self.base.doCmdIntArr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_IN_BATTLE_QUEUE, [QUEUE_TYPE.RANKED, vehInvID, 0])

    def dequeueRanked(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_FROM_BATTLE_QUEUE, QUEUE_TYPE.RANKED)

    def enqueueMapbox(self, vehInvID):
        if not events.isPlayerEntityChanging:
            self.base.doCmdIntArr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_IN_BATTLE_QUEUE, [QUEUE_TYPE.MAPBOX, vehInvID])

    def dequeueMapbox(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_FROM_BATTLE_QUEUE, QUEUE_TYPE.MAPBOX)

    def enqueueComp7(self, vehInvID):
        if not events.isPlayerEntityChanging:
            self.base.doCmdIntArr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_IN_BATTLE_QUEUE, [QUEUE_TYPE.COMP7, vehInvID])

    def dequeueComp7(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_FROM_BATTLE_QUEUE, QUEUE_TYPE.COMP7)

    def enqueueMapsTraininig(self, mapGeometryID, vehCompDescr, team):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_MAPS_TRAINING, mapGeometryID, vehCompDescr, team)

    def dequeueMapsTraininig(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_MAPS_TRAINING, 0, 0, 0)

    def enqueueWinback(self, vehInvID):
        if events.isPlayerEntityChanging:
            return
        self.base.doCmdIntArr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_IN_BATTLE_QUEUE, [QUEUE_TYPE.WINBACK, vehInvID])

    def dequeueWinback(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_FROM_BATTLE_QUEUE, QUEUE_TYPE.WINBACK)

    def requestMapsTrainingInitialConfiguration(self, accountID, callback):
        if not events.isPlayerEntityChanging:
            proxy = lambda requestID, resultID, errorStr, ext=[]: callback(resultID, errorStr, ext)
            self._doCmdInt3(AccountCommands.CMD_REQ_MAPS_TRAINING_INITIAL_CONFIGURATION, accountID, 0, 0, proxy)

    def createArenaFromQueue(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_FORCE_QUEUE, 0, 0, 0)

    def prb_createTraining(self, arenaTypeID, roundLength, isOpened, comment):
        if events.isPlayerEntityChanging:
            return
        self.base.accountPrebattle_createTraining(arenaTypeID, roundLength, isOpened, comment)

    def prb_createDev(self, arenaTypeID, roundLength, comment, bonusType=ARENA_BONUS_TYPE.REGULAR, arenaGuiType=ARENA_GUI_TYPE.TRAINING):
        if events.isPlayerEntityChanging:
            return
        self.base.accountPrebattle_createDevPrebattle(bonusType, arenaGuiType, arenaTypeID, roundLength, comment)

    def prb_sendInvites(self, accountsToInvite, comment):
        if events.isPlayerEntityChanging:
            return
        self.base.accountPrebattle_sendPrebattleInvites(accountsToInvite, comment)

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
        self._doCmdInt3(AccountCommands.CMD_PRB_READY, vehInvID, 0, 0, lambda requestID, resultID, errorStr: callback(resultID, errorStr))

    def prb_notReady(self, state, callback):
        if events.isPlayerEntityChanging:
            return
        self._doCmdInt3(AccountCommands.CMD_PRB_NOT_READY, state, 0, 0, lambda requestID, resultID, errorStr: callback(resultID))

    def prb_assign(self, playerID, roster, callback):
        if events.isPlayerEntityChanging:
            return
        self._doCmdInt3(AccountCommands.CMD_PRB_ASSIGN, playerID, roster, 0, lambda requestID, resultID, errorStr: callback(resultID, errorStr))

    def prb_assignGroup(self, playerID, roster, group, callback):
        if events.isPlayerEntityChanging:
            return
        self._doCmdInt3(AccountCommands.CMD_PRB_ASSIGN, playerID, roster, group, lambda requestID, resultID, errorStr: callback(resultID))

    def prb_swapTeams(self, callback):
        if events.isPlayerEntityChanging:
            return
        self._doCmdInt3(AccountCommands.CMD_PRB_SWAP_TEAM, 0, 0, 0, lambda requestID, resultID, errorStr: callback(resultID))

    def prb_swapTeamsWithinGroup(self, group, callback):
        if events.isPlayerEntityChanging:
            return
        self._doCmdInt3(AccountCommands.CMD_PRB_SWAP_TEAMS_WITHIN_GROUP, group, 0, 0, lambda requestID, resultID, errorStr: callback(resultID))

    def prb_swapGroupsWithinTeam(self, team, groupA, groupB, callback):
        if events.isPlayerEntityChanging:
            return
        self._doCmdInt3(AccountCommands.CMD_PRB_SWAP_GROUPS_WITHIN_TEAM, team, groupA, groupB, lambda requestID, resultID, errorStr: callback(resultID))

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

    def prb_changeGameplaysMask(self, gameplaysMask, callback):
        if events.isPlayerEntityChanging:
            return
        self._doCmdInt3(AccountCommands.CMD_PRB_CH_GAMEPLAYSMASK, gameplaysMask, 0, 0, lambda requestID, resultID, errorStr: callback(resultID))

    def setLanguage(self, language):
        self._doCmdStr(AccountCommands.CMD_SET_LANGUAGE, language, None)
        return

    def selectPersonalMissions(self, personalMissionsIDs, questType, callback):
        args = [questType]
        args.extend(personalMissionsIDs)
        self._doCmdIntArr(AccountCommands.CMD_SELECT_POTAPOV_QUESTS, args, lambda requestID, resultID, errorCode: callback(resultID, errorCode))

    def resetPersonalMissions(self, personalMissionsIDs, questType, callback):
        args = [questType]
        args.extend(personalMissionsIDs)
        self._doCmdIntArr(AccountCommands.CMD_RESET_POTAPOV_QUESTS, args, lambda requestID, resultID, errorCode: callback(resultID, errorCode))

    def pausePersonalMissions(self, personalMissionsIDs, questType, enable, callback):
        args = [questType, enable]
        args.extend(personalMissionsIDs)
        self._doCmdIntArr(AccountCommands.CMD_PAUSE_POTAPOV_QUESTS, args, lambda requestID, resultID, errorCode: callback(resultID, errorCode))

    def getPersonalMissionReward(self, personalMissionsIDs, questType, needTamkman=False, tmanNation=0, tmanInnation=0, roleID=1, callback=None):
        arr = [questType,
         personalMissionsIDs,
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

    def activateGoodie(self, goodieID, callback):
        self._doCmdInt(AccountCommands.CMD_ACTIVATE_GOODIE, goodieID, lambda requestID, resultID, errorCode: callback(resultID, errorCode))

    def removeGoodie(self, goodieID, count, callback):
        self._doCmdInt2(AccountCommands.CMD_REMOVE_GOODIES_DEV, goodieID, count, lambda requestID, resultID, errorCode: callback(resultID, errorCode))

    def activateClanBooster(self, boosterId, callback):
        self._doCmdInt(AccountCommands.CMD_ACTIVATE_CLAN_BOOSTER, boosterId, callback)

    def deactivateClanBoosters(self, callback):
        self._doCmdInt(AccountCommands.CMD_DEACTIVATE_CLAN_BOOSTERS, 0, callback)

    def makeDenunciation(self, violatorID, topicID, violatorKind):
        self._doCmdInt3(AccountCommands.CMD_MAKE_DENUNCIATION, violatorID, topicID, violatorKind, None)
        return

    def banUnbanUser(self, accountDBID, restrType, banPeriod, reason, isBan, callback=None):
        reason = reason.encode('utf8')
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, errorStr, ext)
        else:
            proxy = None
        intArr = [accountDBID,
         restrType,
         banPeriod,
         isBan]
        strArr = [reason]
        self._doCmdIntArrStrArr(AccountCommands.CMD_BAN_UNBAN_USER, intArr, strArr, proxy)
        return

    def flushArenaRelations(self, arenaUniqueID, callback=None):
        self._doCmdInt2(AccountCommands.CMD_FLUSH_ARENA_RELATIONS, arenaUniqueID, 0, callback)

    def chooseQuestReward(self, eventType, questID, rewardID, callback=None):
        if callback is not None:
            proxy = lambda requestID, resultID, errorCode: callback(resultID, errorCode)
        else:
            proxy = None
        strArr = [questID.encode('utf8'), rewardID.encode('utf8')]
        self._doCmdIntStrArr(AccountCommands.CMD_CHOOSE_QUEST_REWARD, eventType, strArr, proxy)
        return

    def changeEventEnqueueData(self, data, callback=None):
        if callback is not None:
            proxy = lambda requestID, resultID, errorCode: callback(resultID, errorCode)
        else:
            proxy = None
        argStr = cPickle.dumps(data, -1)
        self._doCmdStr(AccountCommands.CMD_CHANGE_EVENT_ENQUEUE_DATA, argStr, proxy)
        return

    def logUXEvents(self, intArr):
        if self.lobbyContext.needLogUXEvents:
            return
        else:
            self._doCmdIntArr(AccountCommands.CMD_LOG_CLIENT_UX_EVENTS, intArr, None)
            return

    def logXMPPEvents(self, intArr, strArr):
        self._doCmdIntArrStrArr(AccountCommands.CMD_LOG_CLIENT_XMPP_EVENTS, intArr, strArr, None)
        return

    def verifyFinPassword(self, finPassword, callback):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr: callback(resultID, errorStr)
        else:
            proxy = None
        self._doCmdStr(AccountCommands.CMD_VERIFY_FIN_PSWD, finPassword, proxy)
        return

    def requestWGMBalanceInfo(self, callback):
        if events.isPlayerEntityChanging:
            return
        proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, errorStr, ext)
        self._doCmdStr(AccountCommands.CMD_QUERY_BALANCE_INFO, '', proxy)

    def runQuest(self, questType, questIDs, callback):
        self._doCmdIntStrArr(AccountCommands.CMD_RUN_QUEST, questType, questIDs, lambda requestID, resultID, errorStr: callback(resultID))

    def pawnFreeAwardList(self, questType, questID, callback):
        args = [questType, questID]
        self._doCmdIntArr(AccountCommands.CMD_PAWN_FREE_AWARD_LIST, args, lambda requestID, resultID, errorStr: callback(resultID))

    def requestSingleToken(self, tokenName, callback=None):
        self._doCmdStr(AccountCommands.CMD_GET_SINGLE_TOKEN, tokenName, callback)

    def messenger_onActionByServer_chat2(self, actionID, reqID, args):
        from messenger_common_chat2 import MESSENGER_ACTION_IDS as actions
        LOG_DEBUG('messenger_onActionByServer', actions.getActionName(actionID), reqID, args)
        MessengerEntry.g_instance.protos.BW_CHAT2.onActionReceived(actionID, reqID, args)

    def addBlueprintFragment(self, fragmentTypeCD, requestedCount, other=-1):
        LOG_DEBUG('Account.addBlueprintFragment: fragmentTypeCD={}, count={}'.format(fragmentTypeCD, requestedCount))
        self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_BPF_ADD_FRAGMENTS_DEV, requestedCount, fragmentTypeCD, other)

    def getWishlist(self):
        self._doCmdIntArr(AccountCommands.CMD_WISHLIST_GET_DEV, [], lambda *args: LOG_DEBUG_DEV(args[3]))

    def processInvitations(self, invitations):
        self.prebattleInvitations.processInvitations(invitations, ClientInvitations.InvitationScope.ACCOUNT)

    def setEnhancement(self, vehicleInvID, slot, enhancementID, callback):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr: callback(resultID, errorStr)
        else:
            proxy = None
        self._doCmdInt3(AccountCommands.CMD_EQUIP_ENHANCEMENT, vehicleInvID, slot, enhancementID, proxy)
        return

    def setOfferBannerSeen(self, offerID, callback=None):
        return self._doCmdInt(AccountCommands.CMD_SET_OFFER_BANNER_SEEN, offerID, callback)

    def receiveOfferGift(self, offerID, giftID, callback=None):
        return self._doCmdInt2(AccountCommands.CMD_RECEIVE_OFFER_GIFT, offerID, giftID, callback)

    def receiveMultipleOfferGifts(self, chosenGifts, callback=None):
        return self._doCmdStr(AccountCommands.CMD_RECEIVE_OFFER_GIFT_MULTIPLE, chosenGifts, callback)

    def dismountEnhancement(self, vehicleInvID, slot, callback):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext=None: callback(resultID, errorStr, ext)
        else:
            proxy = None
        self._doCmdInt2(AccountCommands.CMD_DISMOUNT_ENHANCEMENT, vehicleInvID, slot, proxy)
        return

    def startWatchingReplay(self, filename, callback=None):
        if callback is not None:
            proxy = lambda requestID, resultID, errorCode: callback(resultID, errorCode)
        else:
            proxy = None
        self._doCmdStr(AccountCommands.CMD_WATCH_REPLAY, filename, proxy)
        return

    def exchangeBlueprintsSale(self, offerID, count=1, callback=None):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext=None: callback(resultID, errorStr)
        else:
            proxy = None
        self._doCmdInt2(AccountCommands.CMD_BLUEPRINTS_CONVERT_SALE, offerID, count, proxy)
        return

    def addEquipment(self, deviceID, count=1):
        self._doCmdInt2(AccountCommands.CMD_ADD_EQUIPMENT, int(deviceID), count, None)
        return

    def addCrewBooks(self, book, count=1):
        bookItem = tankmen.g_cache.crewBooks().books[int(book)]
        self._doCmdIntArr(AccountCommands.CMD_ADD_CREW_BOOK, [bookItem.compactDescr, count], None)
        return

    def removeEquipment(self, deviceID, count=-1):
        self._doCmdInt2(AccountCommands.CMD_ADD_EQUIPMENT, int(deviceID), count, None)
        return

    def doActions(self, doActionsData):
        from gui.shared.gui_items.items_actions import factory
        groupSize = len(doActionsData)
        groupID = int(BigWorld.serverTime())
        while doActionsData:
            factory.doAction(*(doActionsData.pop(0) + (groupID, groupSize)))

    def _doCmdNoArgs(self, cmd, callback):
        return self.__doCmd('doCmdNoArgs', cmd, callback)

    def _doCmdStr(self, cmd, s, callback):
        return self.__doCmd('doCmdStr', cmd, callback, s)

    def _doCmdIntStr(self, cmd, int1, s, callback):
        return self.__doCmd('doCmdIntStr', cmd, callback, int1, s)

    def _doCmdInt(self, cmd, int_, callback):
        return self.__doCmd('doCmdInt', cmd, callback, int_)

    def _doCmdInt2(self, cmd, int1, int2, callback):
        return self.__doCmd('doCmdInt2', cmd, callback, int1, int2)

    def _doCmdInt3(self, cmd, int1, int2, int3, callback):
        return self.__doCmd('doCmdInt3', cmd, callback, int1, int2, int3)

    def _doCmdInt3Str(self, cmd, int1, int2, int3, s, callback):
        return self.__doCmd('doCmdInt3Str', cmd, callback, int1, int2, int3, s)

    def _doCmdInt4(self, cmd, int1, int2, int3, int4, callback):
        return self.__doCmd('doCmdInt4', cmd, callback, int1, int2, int3, int4)

    def _doCmdInt2Str(self, cmd, int1, int2, s, callback):
        return self.__doCmd('doCmdInt2Str', cmd, callback, int1, int2, s)

    def _doCmdIntArr(self, cmd, arr, callback):
        return self.__doCmd('doCmdIntArr', cmd, callback, arr)

    def _doCmdIntStrArr(self, cmd, int1, strArr, callback):
        return self.__doCmd('doCmdIntStrArr', cmd, callback, int1, strArr)

    def _doCmdIntArrStrArr(self, cmd, intArr, strArr, callback):
        return self.__doCmd('doCmdIntArrStrArr', cmd, callback, intArr, strArr)

    def _doCmdStrArr(self, cmd, strArr, callback):
        return self.__doCmd('doCmdStrArr', cmd, callback, strArr)

    def _update(self, triggerEvents, diff):
        LOG_DEBUG_DEV('_update', diff if triggerEvents else 'full sync')
        isFullSync = AccountSyncData.isFullSyncDiff(diff)
        if not self.syncData.updatePersistentCache(diff, isFullSync):
            return False
        else:
            self.syncData.revision = diff.get('rev', 0)
            self.inventory.synchronize(isFullSync, diff)
            self.stats.synchronize(isFullSync, diff)
            self.questProgress.synchronize(isFullSync, diff)
            self.intUserSettings.synchronize(isFullSync, diff)
            self.goodies.synchronize(isFullSync, diff)
            self.vehicleRotation.synchronize(isFullSync, diff)
            self.recycleBin.synchronize(isFullSync, diff)
            self.ranked.synchronize(isFullSync, diff)
            self.battleRoyale.synchronize(isFullSync, diff)
            self.badges.synchronize(isFullSync, diff)
            self.tokens.synchronize(isFullSync, diff)
            self.epicMetaGame.synchronize(isFullSync, diff)
            self.blueprints.synchronize(isFullSync, diff)
            self.festivities.synchronize(isFullSync, diff)
            self.sessionStats.synchronize(isFullSync, diff)
            self.spaFlags.synchronize(diff)
            self.anonymizer.synchronize(isFullSync, diff)
            self.battlePass.synchronize(isFullSync, diff)
            self.offers.synchronize(isFullSync, diff)
            self.dogTags.synchronize(isFullSync, diff)
            self.mapsTraining.synchronize(isFullSync, diff)
            self.telecomRentals.synchronize(isFullSync, diff)
            self.giftSystem.synchronize(isFullSync, diff)
            self.gameRestrictions.synchronize(isFullSync, diff)
            self.resourceWell.synchronize(isFullSync, diff)
            self.achievements20.synchronize(isFullSync, diff)
            self._synchronizeServerSettings(diff)
            self._synchronizeDisabledPersonalMissions(diff)
            self._synchronizeEventNotifications(diff)
            self._synchronizeCacheDict(self.prebattleAutoInvites, diff.get('account', None), 'prebattleAutoInvites', 'replace', events.onPrebattleAutoInvitesChanged)
            self._synchronizeCacheDict(self.prebattleInvites, diff, 'prebattleInvites', 'update', lambda : events.onPrebattleInvitesChanged(diff))
            self._synchronizeCacheDict(self.clanMembers, diff.get('cache', None), 'clanMembers', 'replace', events.onClanMembersListChanged)
            self._synchronizeCacheDict(self.eventsData, diff, 'eventsData', 'replace', events.onEventsDataChanged)
            self._synchronizeCacheDict(self.personalMissionsLock, diff.get('cache', None), 'potapovQuestIDs', 'replace', events.onPMLocksChanged)
            self._synchronizeCacheDict(self.dailyQuests, diff, 'dailyQuests', 'replace', events.onDailyQuestsInfoChange)
            self._synchronizeCacheSimpleValue('globalRating', diff.get('account', None), 'globalRating', events.onAccountGlobalRatingChanged)
            self._synchronizeCacheDict(self.platformBlueprintsConvertSaleLimits, diff, 'platformBlueprintsConvertSaleLimits', 'replace', events.onPlatformBlueprintsConvertSaleLimits)
            if ENABLE_FREE_PREMIUM_CREW:
                synchronizeDicts(diff.get('freePremiumCrew', {}), self.freePremiumCrew)
            events.onClientUpdated(diff, not triggerEvents)
            if triggerEvents and not isFullSync:
                for vehTypeCompDescr in diff.get('stats', {}).get('eliteVehicles', ()):
                    events.onVehicleBecomeElite(vehTypeCompDescr)

                for vehInvID, lockReason in diff.get('cache', {}).get('vehsLock', {}).iteritems():
                    if lockReason is None:
                        lockReason = AccountCommands.LOCK_REASON.NONE
                    events.onVehicleLockChanged(vehInvID, lockReason)

            return True

    def _synchronizeCacheDict(self, repDict, diffDict, key, syncMode, event):
        if syncMode not in ('update', 'replace'):
            raise SoftException('Mode {} is not supported on the client'.format(syncMode))
        if diffDict is None:
            return
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
                        repDict.setdefault(k, {})
                        repDict[k].update(v)

                else:
                    LOG_WARNING('_synchronizeCacheDict: bad diff=%r for key=%r' % (diff, key))
            if repl is not None or diff is not None:
                event()
            return

    def _synchronizeCacheSimpleValue(self, accountPropName, diffDict, key, event):
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

    def _subscribeForStream(self, requestID, callback):
        self.__onStreamComplete[requestID] = callback

    def _initTimeCorrection(self, ctx):
        if 'serverUTC' in ctx:
            import helpers.time_utils as tm
            tm.setTimeCorrection(ctx['serverUTC'])

    def _synchronizeEventNotifications(self, diff):
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
                LOG_DEBUG_DEV('Account.__synchronizeEventNotifications, diff=%s' % (diffDict,))
            return

    def _synchronizeServerSettings(self, diffDict):
        if diffDict is None:
            return
        else:
            serverSettings = self.serverSettings
            fullServerSettings = diffDict.get(('serverSettings', '_r'), None)
            if fullServerSettings is not None:
                serverSettings.clear()
                serverSettings.update(fullServerSettings)
            serverSettingsDiff = diffDict.get('serverSettings', None)
            if serverSettingsDiff is not None:
                if isinstance(serverSettingsDiff, dict):
                    for key, value in serverSettingsDiff.iteritems():
                        if value is None:
                            serverSettings.pop(key, None)
                            continue
                        if isinstance(value, dict):
                            serverSettings.setdefault(key, {})
                            serverSettings[key].update(value)
                        serverSettings[key] = value

                else:
                    LOG_WARNING('_synchronizeCacheDict: bad diff=%r for key=%r' % (serverSettingsDiff, key))
            return

    def _synchronizeDisabledPersonalMissions(self, diffDict):
        if diffDict is None:
            return
        else:
            serverSettings = self.serverSettings
            disabledSectionKeys = ('disabledPersonalMissions', 'disabledPMOperations')
            serverSettingsDiff = diffDict.get('serverSettings', None)
            if serverSettingsDiff is not None:
                if isinstance(serverSettingsDiff, dict):
                    for sectionKey in disabledSectionKeys:
                        if sectionKey in serverSettingsDiff:
                            if isinstance(serverSettingsDiff[sectionKey], dict):
                                serverSettings.setdefault(sectionKey, {})
                                serverSettings[sectionKey] = serverSettingsDiff[sectionKey]
                            else:
                                LOG_WARNING('_synchronizeCacheDict: bad diff=%r for key=%r' % (serverSettingsDiff, sectionKey))

            return

    @prbEntityProperty
    def _prbEntity(self):
        return None

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
                callbackID = requestID
            else:
                callbackID = None
            getattr(self.base, doCmdMethod)(requestID, cmd, *args)
            return callbackID

    def __cancelCommands(self):
        for requestID, callback in self.__onCmdResponse.iteritems():
            try:
                callback(requestID, AccountCommands.RES_NON_PLAYER, 'NON_PLAYER')
            except Exception:
                LOG_CURRENT_EXCEPTION()

        self.__onCmdResponse.clear()
        for callback in self.__onStreamComplete.itervalues():
            try:
                callback(False, None)
            except Exception:
                LOG_CURRENT_EXCEPTION()

        self.__onStreamComplete.clear()
        return


Account = PlayerAccount

class AccountInputHandler(object):

    def handleKeyEvent(self, event):
        return False

    def handleMouseEvent(self, dx, dy, dz):
        return False


class _AccountRepository(object):

    def __init__(self, name, className, initialServerSettings):
        self.className = className
        self.contactInfo = ContactInfo()
        self.commandProxy = _ClientCommandProxy()
        self.serverSettings = copy.copy(initialServerSettings)
        self.syncData = AccountSyncData.AccountSyncData()
        self.inventory = Inventory.Inventory(self.syncData, self.commandProxy)
        self.stats = Stats.Stats(self.syncData, self.commandProxy)
        self.questProgress = QuestProgress.QuestProgress(self.syncData)
        self.shop = Shop.Shop()
        self.dossierCache = DossierCache.DossierCache(name, className)
        self.battleResultsCache = BattleResultsCache.BattleResultsCache()
        self.prebattleAutoInvites = {}
        self.prebattleInvites = {}
        self.clanMembers = {}
        self.eventsData = {}
        self.personalMissionsLock = {}
        self.customFilesCache = CustomFilesCache.CustomFilesCache('custom_data')
        self.eventNotifications = []
        self.intUserSettings = IntUserSettings.IntUserSettings()
        self.prebattleInvitations = ClientInvitations.ClientInvitations(events)
        self.goodies = ClientGoodies.ClientGoodies(self.syncData)
        self.vehicleRotation = vehicle_rotation.VehicleRotation(self.syncData)
        self.recycleBin = client_recycle_bin.ClientRecycleBin(self.syncData)
        self.ranked = client_ranked.ClientRanked(self.syncData)
        self.battleRoyale = ClientBattleRoyale.ClientBattleRoyale(self.syncData)
        self.badges = ClientBadges.ClientBadges(self.syncData)
        self.tokens = tokens.Tokens(self.syncData)
        self.epicMetaGame = client_epic_meta_game.ClientEpicMetaGame(self.syncData)
        self.blueprints = client_blueprints.ClientBlueprints(self.syncData)
        self.festivities = FestivityManager(self.syncData, self.commandProxy)
        self.sessionStats = SessionStatistics(self.syncData)
        self.spaFlags = SPAFlags(self.syncData)
        self.anonymizer = client_anonymizer.ClientAnonymizer(self.syncData)
        self.dailyQuests = {}
        self.battlePass = BattlePassManager(self.syncData, self.commandProxy)
        self.offers = OffersSyncData(self.syncData)
        self.dogTags = DogTags(self.syncData)
        self.mapsTraining = MapsTraining(self.syncData)
        self.telecomRentals = TelecomRentals(self.syncData)
        self.resourceWell = ResourceWell(self.syncData, self.commandProxy)
        self.winback = Winback(self.commandProxy)
        self.achievements20 = Achievements20(self.syncData, self.commandProxy)
        self.tradeIn = TradeIn()
        self.giftSystem = GiftSystem(self.syncData, self.commandProxy)
        self.gameRestrictions = GameRestrictions(self.syncData)
        self.platformBlueprintsConvertSaleLimits = {}
        self.freePremiumCrew = {}
        self.gMap = ClientGlobalMap()
        self.onTokenReceived = Event.Event()
        self.requestID = AccountCommands.REQUEST_ID_UNRESERVED_MIN

    @property
    def fileServerSettings(self):
        return self.serverSettings['file_server']


def delAccountRepository():
    global g_accountRepository
    LOG_DEBUG('delAccountRepository')
    if g_accountRepository is None:
        return
    else:
        g_accountRepository.customFilesCache.close()
        g_accountRepository.onTokenReceived.clear()
        g_accountRepository.prebattleInvitations.clear()
        g_accountRepository = None
        return


_CLIENT_SERVER_VERSION = readClientServerVersion()
g_accountRepository = None
