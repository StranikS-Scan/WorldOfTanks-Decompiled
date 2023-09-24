# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/winback_call_controller.py
import logging
from collections import OrderedDict
from collections import namedtuple
import typing
import wg_async
from Event import EventManager, Event
from adisp import adisp_process, adisp_async
from constants import Configs
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.winback_call.winback_call_friend_status import WinBackCallFriendState
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils import decorators
from gui.wgcg.winback_call.contexts import WinBackCallFriendListCtx, WinBackCallSendInviteCodeCtx
from helpers import dependency, time_utils
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from messenger.proto.bw.wrappers import ServiceChannelMessage
from skeletons.gui.game_control import IWinBackCallController, IBootcampController, IBattleRoyaleController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.system_messages import ISystemMessages
from skeletons.gui.web import IWebController
if typing.TYPE_CHECKING:
    from typing import Optional, Tuple, List
    from helpers.server_settings import _WinBackCallConfig
_logger = logging.getLogger(__name__)

class FriendsDataKeys(object):
    ROOT = u'data'
    STATUS = u'status'
    STATUS_SUCCESS = u'success'
    STATUS_FAILURE = u'failure'
    FRIENDS = u'friends'
    CALLER_INFO = u'caller_info'
    CALLER_NAME = u'caller_name'
    CALLER_CLAN = u'caller_clan'
    INVITE_HOST = u'lms_url'
    FRIENDS_WINBACK_COUNT = u'friends_winback_count'


_WinbackCallWebResponse = namedtuple('_WinbackCallWebResponse', ('isSuccess', 'status', 'data'))
_Record = namedtuple('_Record', ('name', 'value', 'compare'))
_MAX_FRIENDS = 20
_COMMON_SERVICE_RECORDS = (u'common_battles_count', u'common_wins_count', u'winback_damage_dealt', u'brothers_in_arms_medal_cnt', u'crucial_contribution_medal_cnt', u'in_caller_contacts_days', u'common_clan_days_cnt', u'common_event_battles_cnt')
_PERSONAL_SERVICE_RECORDS = (u'battles_count', u'wins_count', u'damage_dealt', u'frags_count', u'account_age_days', u'medals_count')
_SERVICE_RECORDS_LIMITS = {u'common_battles_count': 10.0,
 u'common_wins_count': 0.4,
 u'winback_damage_dealt': 10000.0,
 u'brothers_in_arms_medal_cnt': 20.0,
 u'crucial_contribution_medal_cnt': 20.0,
 u'in_caller_contacts_days': 365.0,
 u'common_clan_days_cnt': 30.0,
 u'common_event_battles_cnt': 3.0,
 u'battles_count': 1000.0,
 u'wins_count': 0.4,
 u'damage_dealt': 50000.0,
 u'frags_count': 1000.0,
 u'account_age_days': 1095.0,
 u'medals_count': 100.0}
_SERVICE_DEPENDENCY_PRC = {u'common_wins_count': u'common_battles_count',
 u'wins_count': u'battles_count'}

class _ServiceRecords(object):
    __slots__ = ('__records',)

    def __init__(self, data):
        self.__records = []
        self.__parse(data)

    def __parse(self, data):
        commonImpressive = self.__buildRecords(data, _COMMON_SERVICE_RECORDS, weather=lambda i: i.compare >= 1)
        personalImpressive = self.__buildRecords(data, _PERSONAL_SERVICE_RECORDS, weather=lambda i: i.compare >= 1)
        personalRecords = self.__buildRecords(data, _PERSONAL_SERVICE_RECORDS, weather=lambda i: i.compare < 1)
        self.__records = commonImpressive + personalImpressive + personalRecords

    def __buildRecords(self, data, recordsTypes, weather):
        records = filter(weather, [ self.__buildRecord(data, key, value) for key, value in data.iteritems() if key in recordsTypes ])
        return sorted(records, key=lambda r: r.compare, reverse=True)

    def __buildRecord(self, data, key, value):
        dependecy = _SERVICE_DEPENDENCY_PRC.get(key)
        hasValue = dependecy and dependecy in data and data[dependecy]
        compareValue = float(value) / data[dependecy] if hasValue else value
        return _Record(key, value, float(compareValue) / _SERVICE_RECORDS_LIMITS[key])

    def getRecords(self, count=3):
        return self.__records[:count]


class _Friend(object):
    __slots__ = ('__data', '__serviceRecords')

    def __init__(self, data):
        self.__data = data or {}
        self.__serviceRecords = None
        return

    @property
    def spaID(self):
        return self.__data.get(u'winback_spa_id', '')

    @property
    def userName(self):
        return self.__data.get(u'winback_name', '')

    @property
    def userClan(self):
        return self.__data.get(u'winback_clan', '')

    @property
    def lastLogin(self):
        return self.__data.get(u'last_login_dt', time_utils.getServerUTCTime())

    @property
    def vehicleName(self):
        return self.__data.get(u'preferable_vehicle_name', '')

    @property
    def inviteStatus(self):
        status = str(self.__data.get(u'invite_status', ''))
        if not self.hasEmail:
            return WinBackCallFriendState.HAS_NOT_EMAIL.value
        if status == WinBackCallFriendState.ACCEPTED.value and self.isAwarded:
            return WinBackCallFriendState.ROLLED_BACK.value
        return WinBackCallFriendState.ACCEPT_BY_ANOTHER.value if status == WinBackCallFriendState.NOT_SENT.value and self.wasNotifiedByEmail else status

    @property
    def isAwarded(self):
        return bool(self.__data.get(u'awarded', False))

    @property
    def hasEmail(self):
        return bool(self.__data.get(u'is_email', False))

    @property
    def wasNotifiedByEmail(self):
        return bool(self.__data.get(u'email_status', False))

    @property
    def inviteCode(self):
        return str(self.__data.get(u'invite_code', ''))

    @property
    def serviceRecords(self):
        if self.__serviceRecords is None:
            self.__serviceRecords = _ServiceRecords(self.__data)
        return self.__serviceRecords

    @property
    def isRolledBack(self):
        return self.inviteStatus == WinBackCallFriendState.ROLLED_BACK.value

    def updateStatus(self, status):
        if status in WinBackCallFriendState:
            self.__data.update({u'invite_status': status.value})
            return True
        return False

    def clear(self):
        self.__data.clear()
        self.__data = None
        if self.__serviceRecords is None:
            self.__serviceRecords = None
        return


class _FriendsCache(object):

    def __init__(self, data):
        self.__player = None
        self.__friends = None
        self.__inviteURL = None
        self.__parse(data)
        return

    @property
    def friends(self):
        return self.__friends.values() if self.__friends else []

    @property
    def inviteUrl(self):
        return self.__inviteURL

    @property
    def playerName(self):
        return self.__getStrValue(FriendsDataKeys.CALLER_NAME, '')

    @property
    def playerClan(self):
        return self.__getStrValue(FriendsDataKeys.CALLER_CLAN, '')

    @property
    def playerInvitedCount(self):
        return self.__getIntValue(FriendsDataKeys.FRIENDS_WINBACK_COUNT, 0)

    @property
    def canSendInvite(self):
        notSentState = WinBackCallFriendState.NOT_SENT.value
        return any((self.__friends[spaID].inviteStatus == notSentState for spaID in self.__friends))

    def canSendInviteToFriend(self, spaID):
        notSentState = WinBackCallFriendState.NOT_SENT.value
        return bool(spaID in self.__friends and self.__friends[spaID].inviteStatus == notSentState)

    def updateFrindStatus(self, spaID, status):
        if spaID in self.__friends:
            self.__friends[spaID].updateStatus(status)

    def clear(self):
        if self.__friends:
            for friend in self.__friends.values():
                friend.clear()

            self.__friends.clear()
            self.__friends = None
        if self.__player:
            self.__player.clear()
            self.__player = None
        if self.__inviteURL is not None:
            self.__inviteURL = None
        return

    def __parse(self, data):
        if not data:
            return
        else:
            self.__player = data.get(FriendsDataKeys.CALLER_INFO, {})
            friends = data.get(FriendsDataKeys.FRIENDS, [])[:_MAX_FRIENDS]
            self.__friends = OrderedDict()
            friend = None
            for friendData in friends:
                friend = _Friend(friendData)
                self.__friends[friend.spaID] = friend

            if friend:
                inviteHost = data.get(FriendsDataKeys.INVITE_HOST)
                inviteCode = friend.inviteCode
                if inviteHost and inviteCode:
                    self.__inviteURL = '{}?inv={}'.format(inviteHost, inviteCode)
            return

    def __getStrValue(self, key, default):
        return str(self.__player.get(key, default))

    def __getIntValue(self, key, default):
        return int(self.__player.get(key, default))


class WinBackCallController(IWinBackCallController, IGlobalListener):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __bootcampController = dependency.descriptor(IBootcampController)
    __systemMessages = dependency.descriptor(ISystemMessages)
    __itemsCache = dependency.descriptor(IItemsCache)
    __webCtrl = dependency.descriptor(IWebController)

    def __init__(self):
        super(WinBackCallController, self).__init__()
        self.__serverSettings = None
        self.__winBackCallConfig = None
        self.__isBattleRoyaleMode = False
        self.__isEnabled = False
        self.__showEntryPointBubble = False
        self.__friendsStorage = None
        self.__em = EventManager()
        self.onStateChanged = Event(self.__em)
        self.onConfigChanged = Event(self.__em)
        self.onFriendStatusUpdated = Event(self.__em)
        self.onFriendsUpdated = Event(self.__em)
        return

    def onConnected(self):
        super(WinBackCallController, self).onConnected()
        self.__showEntryPointBubble = True

    def fini(self):
        self.__em.clear()
        super(WinBackCallController, self).fini()

    def onAvatarBecomePlayer(self):
        self.__clear()

    def onDisconnected(self):
        self.__clear()

    def onLobbyInited(self, event):
        if self.__bootcampController.isInBootcamp():
            return
        self.__isBattleRoyaleMode = self.__battleRoyaleController.isBattleRoyaleMode()
        self.__subscribe()

    def onPrbEntitySwitched(self):
        isBattleRoyaleMode = self.__battleRoyaleController.isBattleRoyaleMode()
        if self.__isBattleRoyaleMode != isBattleRoyaleMode:
            self.__isBattleRoyaleMode = isBattleRoyaleMode
            self.__updateStatus()

    @property
    def isEnabled(self):
        return self.__isEnabled and self.__hasAccessToken()

    @property
    def inviteTokenQuestID(self):
        return self.__winBackCallConfig.inviteTokenQuest if self.__winBackCallConfig else None

    def eventPeriod(self):
        return (self.__winBackCallConfig.startTime, self.__winBackCallConfig.endTime) if self.__winBackCallConfig else (0, 0)

    @adisp_async
    @adisp_process
    def getFriendsList(self, callback=None):
        isSuccess = False
        status = FriendsDataKeys.STATUS_SUCCESS
        data = None
        if self.__webCtrl.isAvailable():
            result = yield wg_async.wg_await(self.__webCtrl.sendRequest(WinBackCallFriendListCtx()))
            responseData = result.getData() or {}
            status = responseData.get(FriendsDataKeys.STATUS, status)
            isSuccess = result.isSuccess() and status == FriendsDataKeys.STATUS_SUCCESS
            if isSuccess:
                data = responseData.get(FriendsDataKeys.ROOT, {})
            else:
                errorStr = responseData.get(u'error', {}).get(u'code', '')
                _logger.warning('Request error. Response code: %d, extraCode: %d, msg: %s, errStr: %s', result.getCode(), result.getExtraCode(), result.getTxtString(), errorStr)
                self.__showWebErrorSysMessage()
        self.__clearStorage()
        self.__friendsStorage = _FriendsCache(data)
        callback(_WinbackCallWebResponse(isSuccess, status, self.__friendsStorage))
        return

    @decorators.adisp_process('sendingInvite')
    def sendInviteCode(self, spaID):
        if self.__webCtrl.isAvailable():
            ctx = WinBackCallSendInviteCodeCtx(spaID=spaID)
            result = yield wg_async.wg_await(self.__webCtrl.sendRequest(ctx))
            if result.isSuccess():
                responseData = result.getData() or {}
                status = responseData.get(FriendsDataKeys.STATUS, FriendsDataKeys.STATUS_SUCCESS)
                if status == FriendsDataKeys.STATUS_FAILURE:
                    self.__invalidateFriends()
                else:
                    self.__updateFriendStatus(spaID, WinBackCallFriendState.IN_PROGRESS)

    def canSendInviteToFriend(self, spaID):
        return self.__friendsStorage and self.__friendsStorage.canSendInviteToFriend(spaID)

    @decorators.adisp_process('updatingFriendList', softStart=True)
    def __invalidateFriends(self):
        response = yield self.getFriendsList()
        if response.isSuccess:
            self.onFriendsUpdated(response.data)

    def __updateFriendStatus(self, spaID, status):
        if self.__friendsStorage:
            self.__friendsStorage.updateFrindStatus(spaID, status)
            self.onFriendStatusUpdated()

    def __subscribe(self):
        self.startGlobalListening()
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())
        self.__lobbyContext.onServerSettingsChanged += self.__onServerSettingsChanged
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})

    def __unsubscribe(self):
        self.stopGlobalListening()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__lobbyContext.onServerSettingsChanged -= self.__onServerSettingsChanged
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onUpdateWinBackCallSettings
        return

    def __updateStatus(self):
        isEnableState = self.__winBackCallConfig.isEnabled and self.__hasAccessToken() and not self.__bootcampController.isInBootcamp() and not self.__isBattleRoyaleMode
        if self.__isEnabled != isEnableState:
            self.__isEnabled = isEnableState
            self.onStateChanged()
        self.__updateEntryPoint()

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onUpdateWinBackCallSettings
        self.__serverSettings = serverSettings
        self.__serverSettings.onServerSettingsChange += self.__onUpdateWinBackCallSettings
        self.__updateConfig()
        return

    def __onUpdateWinBackCallSettings(self, diff):
        if Configs.WINBACK_CALL_CONFIG.value in diff:
            self.__updateConfig()

    def __updateConfig(self):
        self.__winBackCallConfig = self.__serverSettings.winBackCallConfig
        self.onConfigChanged()
        self.__updateStatus()

    def __onTokensUpdate(self, _):
        self.__updateStatus()

    def __updateEntryPoint(self):
        self.__showEntrySysMessage()

    def __clear(self):
        self.__unsubscribe()
        self.__serverSettings = None
        self.__showEntryPointBubble = False
        self.__clearStorage()
        return

    def __clearStorage(self):
        if self.__friendsStorage:
            self.__friendsStorage.clear()
            self.__friendsStorage = None
        return

    def __hasAccessToken(self):
        return self.__itemsCache.items.tokens.getToken(self.__winBackCallConfig.accessToken) is not None

    def __showEntrySysMessage(self):
        if self.isEnabled is False:
            return
        msgType = SCH_CLIENT_MSG_TYPE.WIN_BACK_CALL_NOTIFY_TYPE
        priority = NotificationPriorityLevel.MEDIUM if self.__showEntryPointBubble else NotificationPriorityLevel.LOW
        data = {'priority': priority}
        self.__showEntryPointBubble = False
        message = ServiceChannelMessage(type=msgType, data=data)
        self.__systemMessages.proto.serviceChannel.pushClientMessage(message, msgType)

    def __showWebErrorSysMessage(self):
        SystemMessages.pushMessage(backport.text(R.strings.winback_call.serviceChannelMessages.friendsListRequestError()), SystemMessages.SM_TYPE.ErrorSimple)
