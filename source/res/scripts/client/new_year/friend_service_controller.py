# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/friend_service_controller.py
import logging
from collections import OrderedDict
import typing
import Event
import wg_async
from copy import copy
from account_helpers.AccountSettings import AccountSettings
from account_helpers.AccountSettings import NY_HAS_BEST_FRIENDS
from account_helpers.AccountSettings import NY_FRIENDS_RESOURCES_COLLECT_DAY
from adisp import adisp_process, adisp_async
from gui.impl.new_year.sounds import NewYearSoundsManager
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.notifications import NotificationPriorityLevel
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.utils import decorators
from gui.wgcg.friends_service.contexts import FriendStateCtx, FriendListCtx, PutBestFriendCtx, DeleteBestFriendCtx, GatherFriendsResourcesCtx
from helpers import dependency, time_utils
from messenger.storage import storage_getter
from new_year.ny_constants import NewYearSysMessages
from new_year.ny_level_helper import getNYGeneralConfig
from new_year.ny_notifications_helpers import sendNYFriendResourceCollectingAvailableMessage
from new_year.ny_resource_collecting_helper import getAvgResourcesByCollecting, getNYResourceCollectingConfig
from ny_common.settings import NY_CONFIG_NAME, NYGeneralConsts
from skeletons.gui.game_control import IBootcampController, IBattleRoyaleController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.web import IWebController
from skeletons.new_year import IFriendServiceController, INewYearController
from gui import SystemMessages
if typing.TYPE_CHECKING:
    from typing import Optional
_logger = logging.getLogger(__name__)

class FriendListDataKeys(object):
    BEST_FRIENDS_MAX_COUNT = u'best_friends_max_count'


class BestFriendsDataKeys(object):
    SPA_ID = u'spa_id'
    RESOURCES_COOLDOWN = u'resources_gather_cooldown'
    IS_REMOVED = u'removed'


class FriendsDataKeys(object):
    SPA_ID = u'spa_id'
    NAME = u'name'
    ATM_POINTS = u'atmosphere_points'
    ATM_LEVEL = u'atmosphere_level'
    HANGAR_NAME = u'hangar_id'
    HANGAR_VISITS = u'hangar_visits'
    HANGAR_VISITS_BY_FRIEND = u'hangar_visits_by_friend'
    RESOURCES_GATHERED_BY_FRIEND = u'resources_gathered_by_friend'
    HIS_BEST_FRIEND = u'his_best'


class FriendHangarDataKeys(object):
    HANGAR_NAME = u'hangar_id'
    TOY_SLOTS = u'toy_slots'
    CUSTOMIZATION_OBJECTS = u'customization_objects'
    ATM_POINTS = u'atmosphere_points'
    ATM_LEVEL = u'atmosphere_level'
    RESOURCES = u'resources'
    RESOURCES_COOLDOWN = u'resources_cooldown'
    TOKENS = u'tokens'


_STATE_TRANSITION_SYS_MESSAGES = {(True, False): NewYearSysMessages(R.strings.ny.notification.friendService.disabled(), NotificationPriorityLevel.HIGH, SystemMessages.SM_TYPE.Error)}

class FriendServiceController(IFriendServiceController, IGlobalListener):
    __webController = dependency.descriptor(IWebController)
    __bootcampController = dependency.descriptor(IBootcampController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self):
        super(FriendServiceController, self).__init__()
        self.__em = Event.EventManager()
        self.__friendHangarState = None
        self.__friendHangarSpaId = None
        self.__lastFriendHangarSpaId = None
        self.__maxBestFriends = 0
        self.__friendList = {}
        self.__bestFriendList = OrderedDict()
        self.__isServiceEnabled = None
        self.__isBattleRoyaleMode = False
        self.onFriendHangarEnter = Event.Event(self.__em)
        self.onFriendHangarExit = Event.Event(self.__em)
        self.onFriendServiceStateChanged = Event.Event(self.__em)
        return

    def fini(self):
        self.__em.clear()

    def onLobbyInited(self, event):
        if self.__bootcampController.isInBootcamp():
            return
        self.__isBattleRoyaleMode = self.__battleRoyaleController.isBattleRoyaleMode()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.startGlobalListening()
        self.__updateState()
        self.__tryToSendBestFriendsResourceCollectingMessage()

    def onAvatarBecomePlayer(self):
        self.__clear()

    def onDisconnected(self):
        self.__clear()

    @property
    def friendHangarSpaId(self):
        return self.__friendHangarSpaId

    @property
    def isServiceEnabled(self):
        return self.__isServiceEnabled

    @property
    def maxBestFriendsCount(self):
        return self.__maxBestFriends

    @property
    def friendList(self):
        return self.__friendList

    @property
    def bestFriendList(self):
        return self.__bestFriendList

    @adisp_async
    @adisp_process
    def enterFriendHangar(self, spaId, callback=None):
        if spaId is None and self.__lastFriendHangarSpaId:
            spaId = self.__lastFriendHangarSpaId
        self.__friendHangarSpaId = None
        self.__lastFriendHangarSpaId = None
        isSuccess = yield self.__updateFriendHangarState(spaId)
        if isSuccess and self.__friendHangarState:
            self.onFriendHangarEnter(self.__friendHangarState)
            NewYearSoundsManager.setFriendHangarState(True)
        else:
            _logger.error("Entering friend's hangar fail. No hangar state info from service")
        callback(self.__friendHangarState)
        return

    def leaveFriendHangar(self):
        self.__doLeaveFriendHangar()
        self.onFriendHangarExit()

    def preLeaveFriendHangar(self):
        self.__doLeaveFriendHangar()

    def __doLeaveFriendHangar(self):
        if not self.__friendHangarSpaId:
            return
        else:
            self.__friendHangarState = None
            self.__updateSpaID(None)
            NewYearSoundsManager.setFriendHangarState(False)
            return

    def getFriendState(self):
        return None if not self.__friendHangarSpaId else copy(self.__friendHangarState)

    def getFriendCollectingCooldownTime(self):
        if not self.__friendHangarSpaId:
            return 0
        cooldown = self.__friendHangarState.get(FriendHangarDataKeys.RESOURCES_COOLDOWN) or 0
        return max(cooldown - time_utils.getServerUTCTime(), 0)

    def getFriendTokens(self):
        return {} if not self.__friendHangarSpaId else self.__friendHangarState.get(FriendHangarDataKeys.TOKENS, {})

    @adisp_async
    @adisp_process
    def updateFriendList(self, callback=None):
        response = yield self.__webController.sendRequest(FriendListCtx(), callback=None)
        if response.isSuccess():
            data = response.getData() or {}
            _logger.debug('updateFriendList data %s', response)
            if not data:
                _logger.warning('Empty data in response %s', response.getCode())
            self.__clearFriendList()
            self.__maxBestFriends = data[FriendListDataKeys.BEST_FRIENDS_MAX_COUNT]
            self.__updateFriends(data)
            self.__updateBestFriends(data)
        else:
            self.__showErrorSystemMessage()
            _logger.error('Failed to update friend list from the service. Response: %s.', response)
        callback(response.isSuccess())
        return

    @adisp_async
    @adisp_process
    def addBestFriend(self, spaId, callback=None):
        response = yield wg_async.wg_await(self.__webController.sendRequest(ctx=PutBestFriendCtx(spaId)))
        if response.isSuccess():
            self.__updateBestFriends(response.getData())
        else:
            self.__showErrorSystemMessage()
            _logger.error("Can't add best friend = %s, %s", spaId, response)
        callback(response.isSuccess())

    @adisp_async
    @adisp_process
    def deleteBestFriend(self, spaId, callback=None):
        response = yield wg_async.wg_await(self.__webController.sendRequest(ctx=DeleteBestFriendCtx(spaId)))
        if response.isSuccess():
            self.__updateBestFriends(response.getData())
        else:
            self.__showErrorSystemMessage()
            _logger.error("Can't remove best friend = %s, %s", spaId, response)
        callback(response.isSuccess())

    @adisp_async
    @adisp_process
    def collectFriendResources(self, callback=None):
        if not self.friendHangarSpaId:
            _logger.error("Must be in friend's hangar to collect it's resources")
            return
        response = yield self.__webController.sendRequest(ctx=GatherFriendsResourcesCtx(self.__friendHangarSpaId))
        if response.isSuccess():
            self.__friendHangarState = response.getData()
            friendName = self.getFriendName(self.__friendHangarSpaId)
            header = backport.text(R.strings.ny.notification.friendService.collectFriendResources.header(), friendName=friendName)
            body = []
            collectedResources = getNYResourceCollectingConfig().getFriendResources().items()
            for resource in ('ny_crystal', 'ny_emerald', 'ny_amber', 'ny_iron'):
                for resName, count in collectedResources:
                    if resource == resName:
                        body.append(backport.text(R.strings.system_messages.newYear.resources.dyn(resName)(), count=count))

            SystemMessages.pushMessage('\n'.join(body), type=SystemMessages.SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': header})
        else:
            SystemMessages.pushMessage(backport.text(R.strings.ny.notification.friendService.collectFriendResources.requestError()), type=SystemMessages.SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.MEDIUM)
            _logger.error("Can't collect resources for friend %s, %s", self.__friendHangarSpaId, response)
        callback(response.isSuccess())

    def getFriendName(self, spaId):
        contact = self.usersStorage.getUser(spaId)
        if not contact:
            _logger.error('No contact info in user storage')
            return ''
        return contact.getFullName()

    def isFriendOnline(self, spaId):
        contact = self.usersStorage.getUser(spaId)
        return contact.isOnline()

    @storage_getter('users')
    def usersStorage(self):
        return None

    def onPrbEntitySwitched(self):
        isBattleRoyaleMode = self.__battleRoyaleController.isBattleRoyaleMode()
        if self.__isBattleRoyaleMode != isBattleRoyaleMode:
            self.__isBattleRoyaleMode = isBattleRoyaleMode
            self.__updateState()

    def __clearFriendList(self):
        self.__friendList.clear()
        self.__bestFriendList.clear()
        self.__maxBestFriends = 0

    def __clear(self):
        self.stopGlobalListening()
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self.__friendHangarSpaId = None
        self.__friendHangarState = None
        self.__lastFriendHangarSpaId = None
        self.__maxBestFriends = 0
        self.__clearFriendList()
        return

    def __updateFriends(self, data):
        for v in data.get('friends', []):
            self.__friendList[int(v[FriendsDataKeys.SPA_ID])] = v

    def __updateBestFriends(self, data):
        self.__bestFriendList.clear()
        for v in data.get('best_friends', []):
            self.__bestFriendList[int(v[BestFriendsDataKeys.SPA_ID])] = v

        AccountSettings.setUIFlag(NY_HAS_BEST_FRIENDS, bool(self.__bestFriendList))

    def __onServerSettingsChange(self, diff):
        if diff.get(NY_CONFIG_NAME, {}).get(NYGeneralConsts.CONFIG_NAME) is None:
            return
        else:
            self.__updateState()
            return

    def __updateState(self):
        if self.__bootcampController.isInBootcamp() or self.__isBattleRoyaleMode:
            state = False
        else:
            generalConfig = getNYGeneralConfig()
            state = generalConfig.getFriendServiceEnabled()
        if state != self.__isServiceEnabled:
            self.__showSwitchOffSystemMessage(state)
            self.__isServiceEnabled = state
            self.onFriendServiceStateChanged()

    def __showSwitchOffSystemMessage(self, newState):
        msg = _STATE_TRANSITION_SYS_MESSAGES.get((self.__isServiceEnabled, newState))
        if msg is not None:
            SystemMessages.pushMessage(backport.text(msg.keyText), type=msg.type, priority=msg.priority)
        return

    def __showErrorSystemMessage(self):
        SystemMessages.pushMessage(backport.text(R.strings.ny.notification.friendService.requestError()), type=SystemMessages.SM_TYPE.Error, priority=NotificationPriorityLevel.HIGH)

    def __updateSpaID(self, spaId):
        self.__lastFriendHangarSpaId = self.__friendHangarSpaId
        self.__friendHangarSpaId = int(spaId) if spaId is not None else spaId
        return

    @adisp_async
    @adisp_process
    def __updateFriendHangarState(self, spaId, callback=None):
        response = yield self.__webController.sendRequest(ctx=FriendStateCtx(spaId))
        if response.isSuccess():
            self.__friendHangarState = response.getData()
            self.__updateSpaID(int(spaId))
        else:
            self.__showErrorSystemMessage()
            _logger.error("Can't get info about player's hangar spaId = %s", spaId)
        callback(response.isSuccess())

    @decorators.adisp_process()
    def __tryToSendBestFriendsResourceCollectingMessage(self):
        if not self.__isServiceEnabled or not self.__nyController.isEnabled():
            return
        hasBestFriends = AccountSettings.getUIFlag(NY_HAS_BEST_FRIENDS)
        if not hasBestFriends:
            return
        lastNotifyGameDay = AccountSettings.getUIFlag(NY_FRIENDS_RESOURCES_COLLECT_DAY)
        serverGameDay = time_utils.getServerGameDay()
        if lastNotifyGameDay == serverGameDay:
            return
        isSuccess = yield self.updateFriendList()
        if isSuccess:
            friendNames = []
            spaIdList = []
            for friendData in self.__bestFriendList.itervalues():
                isRemoved = friendData[BestFriendsDataKeys.IS_REMOVED]
                cooldown = max(friendData[BestFriendsDataKeys.RESOURCES_COOLDOWN] - time_utils.getServerUTCTime(), 0)
                if not isRemoved and cooldown <= 0:
                    spaId = int(friendData[BestFriendsDataKeys.SPA_ID])
                    spaIdList.append(spaId)
                    friendNames.append(self.__friendList[spaId][FriendsDataKeys.NAME])

            if friendNames:
                AccountSettings.setUIFlag(NY_FRIENDS_RESOURCES_COLLECT_DAY, serverGameDay)
                sendNYFriendResourceCollectingAvailableMessage(friendsNames=friendNames, resourcesCount=getAvgResourcesByCollecting(forceFriend=True), friendSpaIDs=spaIdList)
