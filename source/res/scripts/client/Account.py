# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Account.py
import cPickle
import zlib
import copy
from collections import namedtuple
import BigWorld
import Event
import AccountCommands
import ClientPrebattle
from account_helpers import AccountSyncData, Inventory, DossierCache, Shop, Stats, QuestProgress, CustomFilesCache, BattleResultsCache, ClientGoodies, client_recycle_bin, AccountSettings
from account_helpers import ClientRanked, ClientBadges, ClientNewYear
from account_helpers import ClientInvitations, vehicle_rotation
from PlayerEvents import g_playerEvents as events
from account_helpers.AccountSettings import CURRENT_VEHICLE
from account_helpers.settings_core import IntUserSettings
from account_helpers.settings_core import ISettingsCore
from adisp import process
from bootcamp.BootcampPreferences import BootcampPreferences
from constants import ARENA_BONUS_TYPE, QUEUE_TYPE, EVENT_CLIENT_DATA
from constants import PREBATTLE_INVITE_STATUS, PREBATTLE_TYPE
from debug_utils import LOG_DEBUG, LOG_CURRENT_EXCEPTION, LOG_ERROR, LOG_DEBUG_DEV, LOG_WARNING
from helpers import dependency
from gui.Scaleform.Waiting import Waiting
from messenger import MessengerEntry
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.lobby_context import ILobbyContext
from streamIDs import RangeStreamIDCallbacks, STREAM_ID_CHAT_MAX, STREAM_ID_CHAT_MIN
from ContactInfo import ContactInfo
from ClientChat import ClientChat
from ChatManager import chatManager
from account_shared import NotificationItem, readClientServerVersion
from OfflineMapCreator import g_offlineMapCreator
from ClientUnitMgr import ClientUnitMgr, ClientUnitBrowser
from gui.wgnc import g_wgncProvider
from gui.shared.ClanCache import g_clanCache
from ClientSelectableObject import ClientSelectableObject
from ClientGlobalMap import ClientGlobalMap
from bootcamp.Bootcamp import g_bootcamp
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
    lobbyContext = dependency.descriptor(ILobbyContext)
    connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self):
        global g_accountRepository
        LOG_DEBUG('client Account.init')
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
            self.connectionMgr.onDisconnected -= _delAccountRepository
            _delAccountRepository()
        if g_accountRepository is None:
            g_accountRepository = _AccountRepository(self.name, className, self.initialServerSettings)
            self.connectionMgr.onDisconnected += _delAccountRepository
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
        self.badges = g_accountRepository.badges
        self.customFilesCache = g_accountRepository.customFilesCache
        self.newYear = g_accountRepository.newYear
        self.syncData.setAccount(self)
        self.inventory.setAccount(self)
        self.stats.setAccount(self)
        self.questProgress.setAccount(self)
        self.shop.setAccount(self)
        self.dossierCache.setAccount(self)
        self.battleResultsCache.setAccount(self)
        self.intUserSettings.setProxy(self, self.syncData)
        self.prebattleInvitations.setProxy(self)
        self.gMap.setAccount(self)
        self.goodies.setAccount(self)
        self.vehicleRotation.setAccount(self)
        self.recycleBin.setAccount(self)
        self.ranked.setAccount(self)
        self.badges.setAccount(self)
        self.newYear.setAccount(self)
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
        self.personalMissionsLock = g_accountRepository.personalMissionsLock
        self.isInRandomQueue = False
        self.isInTutorialQueue = False
        self.isInBootcampQueue = False
        self.isInUnitAssembler = False
        self.isInEventBattles = False
        self.isInSandboxQueue = False
        self.isInFalloutClassic = False
        self.isInFalloutMultiteam = False
        self.isInRankedQueue = False
        self.selectedHangarEntityId = None
        self.__onCmdResponse = {}
        self.__onStreamComplete = {}
        return

    def onBecomePlayer(self):
        LOG_DEBUG('Account.onBecomePlayer()')
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
        self.badges.onAccountBecomePlayer()
        self.newYear.onAccountBecomePlayer()
        chatManager.switchPlayerProxy(self)
        events.onAccountBecomePlayer()
        BigWorld.target.source = BigWorld.MouseTargetingMatrix()
        BigWorld.target.maxDistance = 700
        BigWorld.target.skeletonCheckEnabled = True
        BigWorld.target.caps()
        BigWorld.target.isEnabled = True
        return

    def onBecomeNonPlayer(self):
        LOG_DEBUG('Account.onBecomeNonPlayer()')
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
        self.badges.onAccountBecomeNonPlayer()
        self.newYear.onAccountBecomeNonPlayer()
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
        self.badges.setAccount(None)
        self.newYear.setAccount(None)
        self.unitMgr.clear()
        self.unitBrowser.clear()
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

    def onKickedFromServer(self, reason, isBan, expiryTime):
        LOG_DEBUG('onKickedFromServer', reason, isBan, expiryTime)
        self.connectionMgr.setKickedFromServer(reason, isBan, expiryTime)

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
        elif queueType == QUEUE_TYPE.BOOTCAMP:
            pass
        elif queueType == QUEUE_TYPE.UNIT_ASSEMBLER:
            self.isInUnitAssembler = True
            events.onEnqueuedUnitAssembler()
        elif queueType == QUEUE_TYPE.EVENT_BATTLES:
            self.isInEventBattles = True
            events.onEnqueuedEventBattles()
        elif queueType == QUEUE_TYPE.FALLOUT_CLASSIC:
            self.isInFalloutClassic = True
            events.onEnqueuedFalloutClassic()
        elif queueType == QUEUE_TYPE.FALLOUT_MULTITEAM:
            self.isInFalloutMultiteam = True
            events.onEnqueuedFalloutMultiteam()
        elif queueType == QUEUE_TYPE.SANDBOX:
            self.isInSandboxQueue = True
            events.onEnqueuedSandbox()
        elif queueType == QUEUE_TYPE.RANKED:
            self.isInRankedQueue = True
            events.onEnqueuedRanked()

    def onEnqueueFailure(self, queueType, errorCode, errorStr):
        LOG_DEBUG('onEnqueueFailure', queueType, errorCode, errorStr)
        if queueType == QUEUE_TYPE.RANDOMS:
            events.onEnqueueRandomFailure(errorCode, errorStr)
        elif queueType == QUEUE_TYPE.TUTORIAL:
            events.onTutorialEnqueueFailure(errorCode, errorStr)
        elif queueType == QUEUE_TYPE.BOOTCAMP:
            events.onBootcampEnqueueFailure(errorCode, errorStr)
        elif queueType == QUEUE_TYPE.UNIT_ASSEMBLER:
            events.onEnqueueUnitAssemblerFailure(errorCode, errorStr)
        elif queueType == QUEUE_TYPE.EVENT_BATTLES:
            events.onEnqueueEventBattlesFailure(errorCode, errorStr)
        elif queueType == QUEUE_TYPE.FALLOUT_CLASSIC:
            events.onEnqueueFalloutClassicFailure(errorCode, errorStr)
        elif queueType == QUEUE_TYPE.FALLOUT_MULTITEAM:
            events.onEnqueueFalloutMultiteamFailure(errorCode, errorStr)
        elif queueType == QUEUE_TYPE.SANDBOX:
            events.onEnqueuedSandboxFailure(errorCode, errorStr)
        elif queueType == QUEUE_TYPE.RANKED:
            events.onEnqueuedRankedFailure(errorCode, errorStr)

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
        elif queueType == QUEUE_TYPE.EVENT_BATTLES:
            self.isInEventBattles = False
            events.onDequeuedEventBattles()
        elif queueType == QUEUE_TYPE.FALLOUT_CLASSIC:
            self.isInFalloutClassic = False
            events.onDequeuedFalloutClassic()
        elif queueType == QUEUE_TYPE.FALLOUT_MULTITEAM:
            self.isInFalloutMultiteam = False
            events.onDequeuedFalloutMultiteam()
        elif queueType == QUEUE_TYPE.SANDBOX:
            self.isInSandboxQueue = False
            events.onDequeuedSandbox()
        elif queueType == QUEUE_TYPE.RANKED:
            self.isInRankedQueue = False
            events.onDequeuedRanked()
        elif queueType == QUEUE_TYPE.BOOTCAMP:
            self.isInBootcampQueue = False
            events.onBootcampDequeued()

    def onTutorialEnqueued(self, number, queueLen, avgWaitingTime):
        LOG_DEBUG('onTutorialEnqueued', number, queueLen, avgWaitingTime)
        self.isInTutorialQueue = True
        events.onTutorialEnqueued(number, queueLen, avgWaitingTime)

    def debugSelectEntity(self, selectionId):
        entitiesIDs = BigWorld.entities.keys()
        for key in entitiesIDs:
            e = BigWorld.entities[key]
            if isinstance(e, ClientSelectableObject) and e.selectionId == selectionId:
                self.targetFocus(e)
                break
        else:
            LOG_DEBUG('No ClientSelectableObject with selectionID', selectionId)

    def debugUnselectEntity(self, selectionId):
        entitiesIDs = BigWorld.entities.keys()
        for key in entitiesIDs:
            e = BigWorld.entities[key]
            if isinstance(e, ClientSelectableObject) and e.selectionId == selectionId:
                self.targetBlur(e)
                break
        else:
            LOG_DEBUG('No ClientSelectableObject with selectionID', selectionId)

    def debugSelectAllEntities(self):
        count = 0
        entitiesIDs = BigWorld.entities.keys()
        for key in entitiesIDs:
            e = BigWorld.entities[key]
            if isinstance(e, ClientSelectableObject):
                self.targetFocus(e)
                count += 1

        if count == 0:
            LOG_DEBUG('No any ClientSelectableObject to select')

    def debugUnselectAllEntites(self):
        count = 0
        entitiesIDs = BigWorld.entities.keys()
        for key in entitiesIDs:
            e = BigWorld.entities[key]
            if isinstance(e, ClientSelectableObject):
                self.targetBlur(e)
                count += 1

        if count == 0:
            LOG_DEBUG('No any ClientSelectableObject to unselect')

    def targetFocus(self, entity):
        if isinstance(entity, ClientSelectableObject) and entity.enabled:
            from gui.shared.utils.HangarSpace import g_hangarSpace
            self.selectedHangarEntityId = entity.id
            g_hangarSpace.onObjectSelected(entity)

    def targetBlur(self, prevEntity):
        if isinstance(prevEntity, ClientSelectableObject):
            from gui.shared.utils.HangarSpace import g_hangarSpace
            self.selectedHangarEntityId = None
            g_hangarSpace.onObjectUnselected(prevEntity)
        return

    def onKickedFromQueue(self, queueType):
        LOG_DEBUG('onKickedFromQueue', queueType)
        if queueType == QUEUE_TYPE.RANDOMS:
            self.isInRandomQueue = False
            events.onKickedFromRandomQueue()
        elif queueType == QUEUE_TYPE.TUTORIAL:
            self.isInTutorialQueue = False
            events.onKickedFromTutorialQueue()
        elif queueType == QUEUE_TYPE.BOOTCAMP:
            self.isInBootcampQueue = False
            events.onKickedFromBootcampQueue()
        elif queueType == QUEUE_TYPE.UNIT_ASSEMBLER:
            self.isInUnitAssembler = False
            events.onKickedFromUnitAssembler()
        elif queueType == QUEUE_TYPE.UNITS:
            events.onKickedFromUnitsQueue()
        elif queueType == QUEUE_TYPE.EVENT_BATTLES:
            self.isInEventBattles = False
            events.onKickedFromEventBattles()
        elif queueType == QUEUE_TYPE.FALLOUT_CLASSIC:
            self.isInFalloutClassic = False
            events.onKickedFromFalloutClassic()
        elif queueType == QUEUE_TYPE.FALLOUT_MULTITEAM:
            self.isInFalloutMultiteam = False
            events.onKickedFromFalloutMultiteam()
        elif queueType == QUEUE_TYPE.SANDBOX:
            self.isInSandboxQueue = False
            events.onKickedFromSandboxQueue()
        elif queueType == QUEUE_TYPE.RANKED:
            self.isInRankedQueue = False
            events.onKickedFromRankedQueue()
        elif queueType == QUEUE_TYPE.BOOTCAMP:
            self.isInBootcampQueue = False
            events.onKickedFromBootcampQueue()

    def onArenaCreated(self):
        LOG_DEBUG('onArenaCreated')
        self.prebattle = None
        events.isPlayerEntityChanging = True
        events.onArenaCreated()
        events.onPlayerEntityChanging()
        return

    def onArenaJoinFailure(self, errorCode, errorStr):
        LOG_DEBUG('onArenaJoinFailure', errorCode, errorStr)
        self.isInRandomQueue = False
        self.isInTutorialQueue = False
        self.isInEventBattles = False
        self.isInFalloutClassic = False
        self.isInFalloutMultiteam = False
        self.isInSandboxQueue = False
        self.isInBootcampQueue = False
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

    def onUnitAssemblerSuccess(self, *args):
        self.unitBrowser.onSearchSuccess(*args)

    def onKickedFromArena(self, reasonCode):
        LOG_DEBUG('onKickedFromArena', reasonCode)
        self.isInRandomQueue = False
        self.isInTutorialQueue = False
        self.isInBootcampQueue = False
        self.isInEventBattles = False
        self.isInFalloutClassic = False
        self.isInFalloutMultiteam = False
        self.isInSandboxQueue = False
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
        LOG_DEBUG('showGUI', ctx)
        self.databaseID = ctx['databaseID']
        if 'prebattleID' in ctx:
            self.prebattle = ClientPrebattle.ClientPrebattle(ctx['prebattleID'])
        self.isInRandomQueue = ctx.get('isInRandomQueue', False)
        self.isInTutorialQueue = ctx.get('isInTutorialQueue', False)
        self.isInTutorialQueue = ctx.get('isInUnitAssembler', False)
        self._initTimeCorrection(ctx)
        if 'isLongDisconnectedFromCenter' in ctx:
            isLongDisconnectedFromCenter = ctx['isLongDisconnectedFromCenter']
            if self.isLongDisconnectedFromCenter != isLongDisconnectedFromCenter:
                self.isLongDisconnectedFromCenter = isLongDisconnectedFromCenter
                events.onCenterIsLongDisconnected(isLongDisconnectedFromCenter)
        g_bootcamp.setBootcampParams({'completed': ctx.get('bootcampCompletedCount', 0),
         'runCount': ctx.get('bootcampRunCount', 0),
         'needAwarding': ctx.get('bootcampNeedAwarding', False)})
        currentVehInvID = ctx.get('currentVehInvID', 0)
        if currentVehInvID > 0:
            AccountSettings.setFavorites(CURRENT_VEHICLE, currentVehInvID)
        events.isPlayerEntityChanging = False
        events.onAccountShowGUI(ctx)

    def receiveQueueInfo(self, queueInfo):
        events.onQueueInfoReceived(queueInfo)

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
        if self.isPlayer:
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

    def requestPrebattleRoster(self, prebattleID):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_PREBATTLE_ROSTER, AccountCommands.CMD_REQ_PREBATTLE_ROSTER, prebattleID, 0, 0)

    def requestServerStats(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_REQ_SERVER_STATS, 0, 0, 0)

    def requestPlayerInfo(self, databaseID, callback):
        if events.isPlayerEntityChanging:
            return
        proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, ext.get('databaseID', 0L), ext.get('dossier', ''), ext.get('clanDBID', 0), ext.get('clanInfo', None), ext.get('globalRating', 0), ext.get('eSportSeasons', {}), ext.get('ranked', {}))
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

    def enqueueRandom(self, vehInvID, gameplaysMask=65535, arenaTypeID=0):
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

    def startBootcampCmd(self):
        if events.isPlayerEntityChanging:
            return
        if g_bootcamp.isRunning():
            return
        self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_REQUEST_BOOTCAMP_START, 0, 0, 0)

    def quitBootcampCmd(self):
        if events.isPlayerEntityChanging:
            return
        self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_REQUEST_BOOTCAMP_QUIT, 0, 0, 0)

    def enqueueBootcamp(self, lessonId):
        if events.isPlayerEntityChanging:
            return
        self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_BOOTCAMP, lessonId, 0, 0)

    def dequeueBootcamp(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_BOOTCAMP, 0, 0, 0)

    def enqueueSandbox(self, vehInvID):
        if events.isPlayerEntityChanging:
            return
        self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_SANDBOX, vehInvID, 0, 0)

    def dequeueSandbox(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_SANDBOX, 0, 0, 0)

    def enqueueUnitAssembler(self, compactDescrs):
        if events.isPlayerEntityChanging:
            return
        args = list(compactDescrs)
        self.base.doCmdIntArr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_UNIT_ASSEMBLER, args)

    def dequeueUnitAssembler(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_UNIT_ASSEMBLER, 0, 0, 0)

    def enqueueEventBattles(self, vehInvIDs):
        if not events.isPlayerEntityChanging:
            arr = [len(vehInvIDs)] + vehInvIDs
            self.base.doCmdIntArr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_EVENT_BATTLES, arr)

    def dequeueEventBattles(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_EVENT_BATTLES, 0, 0, 0)

    def enqueueFalloutClassic(self, vehInvIDs, gameplaysMask=65535, canAddToSquad=False):
        if not events.isPlayerEntityChanging:
            arr = [len(vehInvIDs)] + vehInvIDs + [gameplaysMask, canAddToSquad]
            self.base.doCmdIntArr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_FALLOUT_CLASSIC, arr)

    def dequeueFalloutClassic(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_FALLOUT_CLASSIC, 0, 0, 0)

    def enqueueFalloutMultiteam(self, vehInvIDs, gameplaysMask=65535, canAddToSquad=True):
        if not events.isPlayerEntityChanging:
            arr = [len(vehInvIDs)] + vehInvIDs + [gameplaysMask, canAddToSquad]
            self.base.doCmdIntArr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_FALLOUT_MULTITEAM, arr)

    def dequeueFalloutMultiteam(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_FALLOUT_MULTITEAM, 0, 0, 0)

    def enqueueRanked(self, vehInvID):
        if events.isPlayerEntityChanging:
            return
        self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_RANKED_BATTLES, vehInvID, 0, 0)

    def dequeueRanked(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_RANKED_BATTLES, 0, 0, 0)

    def createArenaFromQueue(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_FORCE_QUEUE, 0, 0, 0)

    def prb_createTraining(self, arenaTypeID, roundLength, isOpened, comment):
        if events.isPlayerEntityChanging:
            return
        self.base.accountPrebattle_createTraining(arenaTypeID, roundLength, isOpened, comment)

    def prb_createDev(self, arenaTypeID, roundLength, comment, bonusType=ARENA_BONUS_TYPE.REGULAR):
        if events.isPlayerEntityChanging:
            return
        self.base.accountPrebattle_createDevPrebattle(bonusType, arenaTypeID, roundLength, comment)

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
        self._doCmdIntArr(AccountCommands.CMD_ACTIVATE_GOODIE, goodieID, lambda requestID, resultID, errorCode: callback(resultID, errorCode))

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

    def logUXEvents(self, intArr):
        if self.lobbyContext.needLogUXEvents:
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

    def messenger_onActionByServer_chat2(self, actionID, reqID, args):
        from messenger_common_chat2 import MESSENGER_ACTION_IDS as actions
        LOG_DEBUG('messenger_onActionByServer', actions.getActionName(actionID), reqID, args)
        MessengerEntry.g_instance.protos.BW_CHAT2.onActionReceived(actionID, reqID, args)

    def processInvitations(self, invitations):
        self.prebattleInvitations.processInvitations(invitations)

    def _doCmdStr(self, cmd, str, callback):
        return self.__doCmd('doCmdStr', cmd, callback, str)

    def _doCmdIntStr(self, cmd, int, str, callback):
        return self.__doCmd('doCmdIntStr', cmd, callback, int, str)

    def _doCmdInt3(self, cmd, int1, int2, int3, callback):
        return self.__doCmd('doCmdInt3', cmd, callback, int1, int2, int3)

    def _doCmdInt4(self, cmd, int1, int2, int3, int4, callback):
        return self.__doCmd('doCmdInt4', cmd, callback, int1, int2, int3, int4)

    def _doCmdInt2Str(self, cmd, int1, int2, str, callback):
        return self.__doCmd('doCmdInt2Str', cmd, callback, int1, int2, str)

    def _doCmdIntArr(self, cmd, arr, callback):
        return self.__doCmd('doCmdIntArr', cmd, callback, arr)

    def _doCmdIntStrArr(self, cmd, int1, strArr, callback):
        return self.__doCmd('doCmdIntStrArr', cmd, callback, int1, strArr)

    def _doCmdIntArrStrArr(self, cmd, intArr, strArr, callback):
        return self.__doCmd('doCmdIntArrStrArr', cmd, callback, intArr, strArr)

    def _update(self, triggerEvents, diff):
        LOG_DEBUG_DEV('_update', diff if triggerEvents else 'full sync')
        if not self.newYear.checkDiffSanity(diff):
            return True
        else:
            isFullSync = diff.get('prevRev', None) is None
            if not self.syncData.updatePersistentCache(diff, isFullSync):
                return False
            self.syncData.revision = diff.get('rev', 0)
            self.inventory.synchronize(isFullSync, diff)
            self.stats.synchronize(isFullSync, diff)
            self.questProgress.synchronize(isFullSync, diff)
            self.intUserSettings.synchronize(isFullSync, diff)
            self.goodies.synchronize(isFullSync, diff)
            self.vehicleRotation.synchronize(isFullSync, diff)
            self.recycleBin.synchronize(isFullSync, diff)
            self.ranked.synchronize(isFullSync, diff)
            self.badges.synchronize(isFullSync, diff)
            self.__synchronizeServerSettings(diff)
            self.__synchronizeEventNotifications(diff)
            self.__synchronizeCacheDict(self.prebattleAutoInvites, diff.get('account', None), 'prebattleAutoInvites', 'replace', events.onPrebattleAutoInvitesChanged)
            self.__synchronizeCacheDict(self.prebattleInvites, diff, 'prebattleInvites', 'update', lambda : events.onPrebattleInvitesChanged(diff))
            self.__synchronizeCacheDict(self.clanMembers, diff.get('cache', None), 'clanMembers', 'replace', events.onClanMembersListChanged)
            self.__synchronizeCacheDict(self.eventsData, diff, 'eventsData', 'replace', events.onEventsDataChanged)
            self.__synchronizeCacheDict(self.personalMissionsLock, diff.get('cache', None), 'potapovQuestIDs', 'replace', events.onPMLocksChanged)
            self.__synchronizeCacheSimpleValue('globalRating', diff.get('account', None), 'globalRating', events.onAccountGlobalRatingChanged)
            self.newYear.synchronize(isFullSync, diff)
            cacheDiff = diff.get('cache', {})
            events.onClientUpdated(diff, not triggerEvents)
            if triggerEvents and not isFullSync:
                for vehTypeCompDescr in diff.get('stats', {}).get('eliteVehicles', ()):
                    if g_bootcamp.isRunning():
                        continue
                    events.onVehicleBecomeElite(vehTypeCompDescr)

                for vehInvID, lockReason in diff.get('cache', {}).get('vehsLock', {}).iteritems():
                    if lockReason is None:
                        lockReason = AccountCommands.LOCK_REASON.NONE
                    events.onVehicleLockChanged(vehInvID, lockReason)

            return True

    def _subscribeForStream(self, requestID, callback):
        self.__onStreamComplete[requestID] = callback

    def _initTimeCorrection(self, ctx):
        if 'serverUTC' in ctx:
            import helpers.time_utils as tm
            tm.setTimeCorrection(ctx['serverUTC'])

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
                LOG_DEBUG_DEV('Account.__synchronizeEventNotifications, diff=%s' % (diffDict,))
            return

    def __synchronizeServerSettings(self, diffDict):
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
                    LOG_WARNING('__synchronizeCacheDict: bad diff=%r for key=%r' % (serverSettingsDiff, key))
            return

    def onEntityCheckOutEnqueued(self, queueNumber):
        Waiting.hide('login')
        events.onEntityCheckOutEnqueued(lambda : self.base.cancelEntityCheckOut())

    @process
    def onBootcampAccountMigrationComplete(self):
        events.onBootcampAccountMigrationComplete()
        settingsCore = dependency.instance(ISettingsCore)
        yield settingsCore.serverSettings.settingsCache.update()
        settingsCore.serverSettings.applySettings()


Account = PlayerAccount

class AccountInputHandler():

    def handleKeyEvent(self, event):
        return False

    def handleMouseEvent(self, dx, dy, dz):
        return False


class _AccountRepository(object):

    def __init__(self, name, className, initialServerSettings):
        self.className = className
        self.contactInfo = ContactInfo()
        self.serverSettings = copy.copy(initialServerSettings)
        self.syncData = AccountSyncData.AccountSyncData()
        self.inventory = Inventory.Inventory(self.syncData)
        self.stats = Stats.Stats(self.syncData)
        self.questProgress = QuestProgress.QuestProgress(self.syncData)
        self.shop = Shop.Shop()
        self.dossierCache = DossierCache.DossierCache(name, className)
        self.battleResultsCache = BattleResultsCache.BattleResultsCache()
        self.prebattleAutoInvites = {}
        self.prebattleInvites = {}
        self.clanMembers = {}
        self.eventsData = {}
        self.personalMissionsLock = {}
        self.customFilesCache = CustomFilesCache.CustomFilesCache()
        self.eventNotifications = []
        self.intUserSettings = IntUserSettings.IntUserSettings()
        self.prebattleInvitations = ClientInvitations.ClientInvitations(events)
        self.goodies = ClientGoodies.ClientGoodies(self.syncData)
        self.vehicleRotation = vehicle_rotation.VehicleRotation(self.syncData)
        self.recycleBin = client_recycle_bin.ClientRecycleBin(self.syncData)
        self.ranked = ClientRanked.ClientRanked(self.syncData)
        self.badges = ClientBadges.ClientBadges(self.syncData)
        self.gMap = ClientGlobalMap()
        self.newYear = ClientNewYear.ClientNewYear(self.syncData)
        self.onTokenReceived = Event.Event()
        self.requestID = AccountCommands.REQUEST_ID_UNRESERVED_MIN

    @property
    def fileServerSettings(self):
        return self.serverSettings['file_server']


def _delAccountRepository():
    global g_accountRepository
    LOG_DEBUG('_delAccountRepository')
    if g_accountRepository is None:
        return
    else:
        g_accountRepository.customFilesCache.close()
        g_accountRepository.onTokenReceived.clear()
        g_accountRepository.prebattleInvitations.clear()
        g_accountRepository.newYear.clear()
        g_accountRepository = None
        return


_CLIENT_SERVER_VERSION = readClientServerVersion()
g_accountRepository = None
