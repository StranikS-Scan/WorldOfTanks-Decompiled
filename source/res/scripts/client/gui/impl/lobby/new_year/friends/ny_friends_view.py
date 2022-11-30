# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/friends/ny_friends_view.py
import logging
import typing
import AnimationSequence
import WebBrowser
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_FRIENDS_BANNER_SHOWN
from adisp import adisp_process
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.friends.friend_model import FriendModel, UserStatus, FriendshipStatus
from gui.impl.lobby.new_year.friends.resource_box_presenter import ResourceBoxPresenter
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.lobby.new_year.ny_history_presenter import NyHistoryPresenter
from gui.impl.new_year.navigation import ViewAliases
from gui.impl.lobby.new_year.tooltips.ny_friends_tooltip import NyFriendsTooltip
from gui.impl.lobby.new_year.tooltips.ny_resource_box_tooltip import NyResourceBoxTooltip
from gui.shared.utils import decorators
from helpers import dependency, time_utils
from helpers.CallbackDelayer import CallbacksSetByID
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter
from new_year import parseHangarNameMask
from new_year.ny_constants import NyTabBarFriendGladeView, AdditionalCameraObject
from new_year.ny_level_helper import getNYGeneralConfig
from realm import CURRENT_REALM
from skeletons.gui.lobby_context import ILobbyContext
from new_year.friend_service_controller import BestFriendsDataKeys, FriendsDataKeys
from gui.impl.gen.view_models.views.lobby.new_year.views.friends.ny_friends_view_model import LoadingState
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.new_year.views.friends.ny_friends_view_model import NyFriendsViewModel
    from messenger.proto.xmpp.entities import XMPPUserEntity
_logger = logging.getLogger(__name__)
_FRIENDSHIP_DELAY_ID = 1
_PERIODICAL_UPDATE_ID = 2
_PERIODICAL_UPDATE_TIMEOUT = time_utils.ONE_MINUTE * 5

class NyFriendsView(NyHistoryPresenter):
    __slots__ = ('__resourceBoxPresenter', '__delayer')
    _navigationAlias = ViewAliases.FRIENDS_VIEW
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, viewModel, parentView, soundConfig=None):
        super(NyFriendsView, self).__init__(viewModel, parentView, soundConfig=soundConfig)
        self.__resourceBoxPresenter = None
        self.__delayer = CallbacksSetByID()
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    @storage_getter('users')
    def usersStorage(self):
        return None

    def initialize(self, *args, **kwargs):
        super(NyFriendsView, self).initialize(*args, **kwargs)
        self.__requestFriendList()
        self.__resourceBoxPresenter = ResourceBoxPresenter(self.viewModel.resourceBoxModel, self)
        self.__resourceBoxPresenter.initialize()
        self.__delayer.delayCallback(_PERIODICAL_UPDATE_ID, _PERIODICAL_UPDATE_TIMEOUT, self.__periodicalUpdate)
        AnimationSequence.setEnableAnimationSequenceUpdate(False)
        WebBrowser.pauseExternalCache(True)

    def finalize(self):
        if self.__resourceBoxPresenter is not None:
            self.__resourceBoxPresenter.finalize()
            self.__resourceBoxPresenter = None
        self.__delayer.clear()
        AnimationSequence.setEnableAnimationSequenceUpdate(True)
        WebBrowser.pauseExternalCache(False)
        super(NyFriendsView, self).finalize()
        return

    def createToolTipContent(self, event, contentID):
        if event.contentID == R.views.lobby.new_year.tooltips.NyFriendsTooltips():
            return NyFriendsTooltip(kind=event.getArgument('type'), payload=event.getArgument('payload'))
        return NyResourceBoxTooltip(event.getArgument('isFriendsList')) if event.contentID == R.views.lobby.new_year.tooltips.NyResourceBoxTooltip() else super(NyFriendsView, self).createToolTipContent(event, contentID)

    def createToolTip(self, event):
        if self.__resourceBoxPresenter is None:
            super(NyFriendsView, self).createToolTip(event)
        return self.__resourceBoxPresenter.createToolTip(event) or super(NyFriendsView, self).createToolTip(event)

    def _getEvents(self):
        return super(NyFriendsView, self)._getEvents() + ((self.viewModel.onGoToFriend, self.__goToFriend),
         (self.viewModel.onChooseBestFriend, self.__addBestFriend),
         (self.viewModel.onDeleteBestFriend, self.__deleteBestFriend),
         (self.viewModel.onBannerChangeDisplay, self.__onBannerChangeDisplay),
         (self._friendsService.onFriendServiceStateChanged, self.__onChangeFriendService),
         (g_messengerEvents.users.onUserActionReceived, self.__delayedRequestFriendList),
         (g_messengerEvents.users.onUserStatusUpdated, self.__updateFriendOnlineStatus))

    @decorators.adisp_process()
    def __requestFriendList(self):
        if self.viewModel is None:
            return
        else:
            self.viewModel.setFriendListLoadingState(LoadingState.PENDING)
            isSuccess = yield self._friendsService.updateFriendList()
            if self.viewModel is None:
                return
            if isSuccess:
                self.__updateAll()
                self.viewModel.setFriendListLoadingState(LoadingState.LOADED)
            else:
                self.viewModel.setFriendListLoadingState(LoadingState.FAILURE)
            return

    def __delayedRequestFriendList(self, *args, **kwargs):
        delay = getNYGeneralConfig().getFriendServiceEnabled()
        if delay:
            self.__delayer.delayCallback(_FRIENDSHIP_DELAY_ID, delay, self.__requestFriendList)

    @adisp_process
    def __goToFriend(self, spaId):
        spaId = spaId.get('id')
        if spaId is None:
            _logger.error('account id is not provided from ui')
            return
        else:
            yield self._friendsService.enterFriendHangar(spaId)
            if self._friendsService.friendHangarSpaId:
                NewYearNavigation.switchToView(ViewAliases.FRIEND_GLADE_VIEW, tabName=NyTabBarFriendGladeView.TOWN, showGreetings=True)
            return

    @decorators.adisp_process()
    def __addBestFriend(self, spaId):
        spaId = spaId.get('id')
        if spaId is None:
            _logger.error('account id is not provided from ui')
            return
        else:
            isSuccess = yield self._friendsService.addBestFriend(spaId)
            if isSuccess:
                self.__updateAll()
            return

    @decorators.adisp_process()
    def __deleteBestFriend(self, spaId):
        spaId = spaId.get('id')
        if spaId is None:
            _logger.error('account id is not provided from ui')
            return
        else:
            isSuccess = yield self._friendsService.deleteBestFriend(spaId)
            if isSuccess:
                self.__updateAll()
            return

    def __onChangeFriendService(self):
        if self._friendsService.isServiceEnabled is False:
            self._goToMainView(tabName=AdditionalCameraObject.UNDER_SPACE)

    def __updateAll(self):
        with self.viewModel.transaction() as model:
            if self._friendsService.friendList:
                self.__updateBestFriends(model)
                self.__updateFriendList(model)
            model.setRealm(CURRENT_REALM)
            model.setShowBanner(AccountSettings.getUIFlag(NY_FRIENDS_BANNER_SHOWN) is False)

    def __updateFriendList(self, model):
        friendList = sorted(self._friendsService.friendList.itervalues(), key=lambda data: (-data.get(FriendsDataKeys.HANGAR_VISITS, 0), -data.get(FriendsDataKeys.ATM_POINTS, 0), data.get(FriendsDataKeys.NAME, 0)))
        count = len(friendList)
        model.setTotalFriendsCount(count)
        friends = model.getFriends()
        friends.clear()
        friends.reserve(count)
        existedFriendIds = set()
        for info in friendList:
            friendInfo = self.__makeFriendInfo(info)
            if friendInfo is not None:
                friends.addViewModel(friendInfo)
                existedFriendIds.add(friendInfo.getId())

        for spaId, bestFriendInfo in self._friendsService.bestFriendList.iteritems():
            if bestFriendInfo[BestFriendsDataKeys.IS_REMOVED] or spaId not in existedFriendIds:
                if not bestFriendInfo[BestFriendsDataKeys.IS_REMOVED]:
                    _logger.warning('Something wrong with friend service, player %s not in friend list, but exist in best friend list with "removed" field == False', spaId)
                friend = FriendModel()
                friend.setId(spaId)
                friend.setIsRemoved(True)
                friend.setUserStatus(UserStatus.OFFLINE)
                friend.setCanCollectResourcesTime(bestFriendInfo[BestFriendsDataKeys.RESOURCES_COOLDOWN])
                friends.addViewModel(friend)

        friends.invalidate()
        return

    def __updateBestFriends(self, model):
        bestFriendList = self._friendsService.bestFriendList
        bestFriends = model.getBestFriends()
        bestFriends.clear()
        bestFriends.reserve(len(bestFriendList))
        for info in bestFriendList.itervalues():
            bestFriends.addNumber(info[BestFriendsDataKeys.SPA_ID])

        bestFriends.invalidate()

    def __makeFriendInfo(self, serviceData):
        friend = FriendModel()
        spaId = serviceData[FriendsDataKeys.SPA_ID]
        if spaId is None:
            return
        else:
            friend.setId(spaId)
            friend.setNickname(self._friendsService.getFriendName(spaId) or '')
            friend.setUserStatus(UserStatus.ONLINE if self._friendsService.isFriendOnline(spaId) else UserStatus.OFFLINE)
            friend.setServerName(self.__lobbyContext.getRegionCode(spaId) or '')
            friend.setLevel(serviceData.get(FriendsDataKeys.ATM_LEVEL, 1))
            currentPoints, toPoints = getNYGeneralConfig().getAtmosphereProgress(serviceData.get(FriendsDataKeys.ATM_POINTS, 0))
            if toPoints > 0:
                friend.setLevelProgress(float(currentPoints))
            else:
                friend.setLevelProgress(0)
            friend.setMaxLevelProgress(toPoints)
            friend.setAmountOfCollectedResources(serviceData.get(FriendsDataKeys.RESOURCES_GATHERED_BY_FRIEND, 0))
            friend.setAmountOfVisits(serviceData.get(FriendsDataKeys.HANGAR_VISITS_BY_FRIEND, 0))
            titleIdx, descriptionIdx = parseHangarNameMask(serviceData.get(FriendsDataKeys.HANGAR_NAME, 0))
            friend.hangarName.setTitle(titleIdx)
            friend.hangarName.setDescription(descriptionIdx)
            bestFriendInfo = self._friendsService.bestFriendList.get(spaId, None)
            if bestFriendInfo is not None:
                friend.setCanCollectResourcesTime(bestFriendInfo[BestFriendsDataKeys.RESOURCES_COOLDOWN])
                cooldown = max(bestFriendInfo[BestFriendsDataKeys.RESOURCES_COOLDOWN] - time_utils.getServerUTCTime(), 0)
                if cooldown > 0:
                    self.__delayer.delayCallback(spaId, cooldown + time_utils.ONE_SECOND, self.__requestFriendList)
                if serviceData[FriendsDataKeys.HIS_BEST_FRIEND]:
                    friend.setFriendshipStatus(FriendshipStatus.BOTHBEST)
                else:
                    friend.setFriendshipStatus(FriendshipStatus.BEST)
            elif serviceData[FriendsDataKeys.HIS_BEST_FRIEND]:
                friend.setFriendshipStatus(FriendshipStatus.YOUBEST)
            else:
                friend.setFriendshipStatus(FriendshipStatus.DEFAULT)
            return friend

    def __onBannerChangeDisplay(self, spaId):
        display = spaId.get('display')
        AccountSettings.setUIFlag(NY_FRIENDS_BANNER_SHOWN, display is False)
        self.viewModel.setShowBanner(display)

    def __periodicalUpdate(self):
        self.__requestFriendList()
        self.__delayer.delayCallback(_PERIODICAL_UPDATE_ID, _PERIODICAL_UPDATE_TIMEOUT, self.__periodicalUpdate)

    def __updateFriendOnlineStatus(self, user):
        friends = self.viewModel.getFriends()
        for friendModel in friends:
            if friendModel.getId() == user.getID():
                friendModel.setUserStatus(UserStatus.ONLINE if user.isOnline() else UserStatus.OFFLINE)

        friends.invalidate()
