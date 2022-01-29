# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lunar_ny/envelopes_history_view.py
from collections import namedtuple
import typing
from async import async, await_callback
from gui.Scaleform.Waiting import Waiting
from gui.impl.gen.view_models.views.lobby.lunar_ny.main_view.main_view_model import Tab
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from lunar_ny.envelopes_storage_users_helper import EnvelopesStorageUsersHelper
from lunar_ny.gift_system.lunar_ny_gift_history_requester import CountGiftHistoryRequester, GiftHistoryRequester
from lunar_ny.lunar_ny_constants import MAIN_VIEW_INIT_CONTEXT_TAB, EnvelopeTypes
from shared_utils import findFirst
from frameworks.wulf import ViewFlags, WindowFlags, ViewSettings, WindowLayer, ViewStatus
from gifts.gifts_common import GiftEventID, GIFT_HISTORY_PAGE_LEN
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lunar_ny.envelopes_history_view_model import EnvelopesHistoryViewModel, ColumnType, ColumnSortingOrder
from gui.impl.gen.view_models.views.lobby.lunar_ny.player_envelopes_history import PlayerEnvelopesHistory, PlayerStatus
from gui.impl.lobby.lunar_ny.lunar_ny_helpers import showEnvelopesSendView, showLunarNYMainView
from gui.impl.pub import ViewImpl, WindowImpl
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from lunar_ny import ILunarNYController
from messenger.m_constants import PROTO_TYPE, USER_TAG, USER_ACTION_ID
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
_ENVELOPE_TYPES = (EnvelopeTypes.PREMIUM_PAID, EnvelopeTypes.PAID, EnvelopeTypes.FREE)
_COLUMN_TYPES = (ColumnType.PLAYERNAME,
 ColumnType.RECEIVEDENVELOPES,
 ColumnType.RECEIVEDGOLD,
 ColumnType.SENTINRESPONSE)
_COLUMN_SORTING_ORDER = (ColumnSortingOrder.ASC, ColumnSortingOrder.DESC)
_DEFAULT_COLUMN_TYPES = ColumnType.RECEIVEDENVELOPES
PlayerGiftHistoryData = namedtuple('PlayerGiftHistoryData', ('playerID',
 'nickName',
 'isOnline',
 'clanTag',
 'receivedEnvelopesNumber',
 'receivedGoldNumber',
 'sentInResponseEnvelopesNumber',
 'status'))

def _nickNameSortKeyFun(nick):
    return tuple(((str.lower(c), str.isupper(c)) for c in nick))


if typing.TYPE_CHECKING:
    from messenger.proto.entities import LobbyUserEntity
    from gui.gift_system.wrappers import SelectGiftHistoryData

class EnvelopesHistoryView(ViewImpl):
    __slots__ = ('__window', '__blur', '__userInfoHelper', '__currentEnvelopeType', '__currentColumnType', '__currentSortingOrder', '__currentPageNumber', '__currentUsersInfo', '__countRequester', '__dataRequester', 'isBlurActive')
    __lunarNYController = dependency.descriptor(ILunarNYController)

    def __init__(self, layoutID, countRequester=None, dataRequester=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = EnvelopesHistoryViewModel()
        super(EnvelopesHistoryView, self).__init__(settings)
        self.__userInfoHelper = EnvelopesStorageUsersHelper()
        self.__currentEnvelopeType = _ENVELOPE_TYPES[0]
        self.__currentColumnType = _DEFAULT_COLUMN_TYPES
        self.__currentSortingOrder = _COLUMN_SORTING_ORDER[1]
        self.__currentPageNumber = 0
        self.__currentUsersInfo = []
        self.isBlurActive = True
        self.__countRequester = countRequester if countRequester is not None else CountGiftHistoryRequester()
        self.__dataRequester = dataRequester if dataRequester is not None else GiftHistoryRequester()
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    @proto_getter(PROTO_TYPE.MIGRATION)
    def proto(self):
        return None

    def _onLoaded(self, *args, **kwargs):
        if self.isBlurActive and self.__blur is not None:
            self.__blur.enable()
        return

    def _onLoading(self, *args, **kwargs):
        self.__updateDataFromServer()
        self.viewModel.setSelectedColumnType(self.__currentColumnType)
        self.viewModel.setCurrentColumnSortingOrder(self.__currentSortingOrder)
        self.__userInfoHelper.onNamesReceived += self.__onUserNameReceived
        g_messengerEvents.users.onUserActionReceived += self.__userActionReceived
        g_messengerEvents.users.onUserStatusUpdated += self.__onUserStatusUpdated
        g_messengerEvents.onPluginConnected += self.__onChatPluginConnected

    def _onClose(self):
        if self.isBlurActive and self.__blur is not None:
            self.__blur.fini()
            self.isBlurActive = False
        self.destroyWindow()
        return

    def _initialize(self, *args, **kwargs):
        super(EnvelopesHistoryView, self)._initialize()
        self.viewModel.onClose += self._onClose
        self.viewModel.onChangeEnvelopeTypeTab += self.__onChangeEnvelopeTypeTab
        self.viewModel.onSendEnvelopeInResponse += self.__onSendEnvelopeInResponse
        self.viewModel.onAddToFriends += self.__onAddToFriends
        self.viewModel.onChangeColumnType += self.__onChangeColumnType
        self.viewModel.onGoToEnvelopeSend += self.__onGoToEnvelopeSend
        self.viewModel.onChangeCurrentPageNumber += self.__onChangeCurrentPageNumber
        window = self.getParentWindow()
        if self.isBlurActive:
            self.__blur = CachedBlur(ownLayer=window.layer - 1)

    def _finalize(self):
        g_messengerEvents.onPluginConnected -= self.__onChatPluginConnected
        self.viewModel.onChangeCurrentPageNumber -= self.__onChangeCurrentPageNumber
        self.viewModel.onChangeColumnType -= self.__onChangeColumnType
        self.viewModel.onGoToEnvelopeSend -= self.__onGoToEnvelopeSend
        self.viewModel.onAddToFriends -= self.__onAddToFriends
        self.viewModel.onSendEnvelopeInResponse -= self.__onSendEnvelopeInResponse
        self.viewModel.onChangeEnvelopeTypeTab -= self.__onChangeEnvelopeTypeTab
        self.viewModel.onClose -= self._onClose
        g_messengerEvents.users.onUserStatusUpdated -= self.__onUserStatusUpdated
        g_messengerEvents.users.onUserActionReceived -= self.__userActionReceived
        self.__userInfoHelper.onNamesReceived -= self.__onUserNameReceived
        if self.isBlurActive and self.__blur is not None:
            self.__blur.fini()
            self.isBlurActive = False
        self.__currentUsersInfo = []
        self.__userInfoHelper.clearInvalidData()
        self.__countRequester.stop()
        self.__dataRequester.stop()
        super(EnvelopesHistoryView, self)._finalize()
        return

    def __setPagesNumber(self, envelopesReceived):
        self.viewModel.setPagesNumber(envelopesReceived // GIFT_HISTORY_PAGE_LEN + 1)

    def __setCountGiftHistory(self, countGiftHistory):
        if countGiftHistory is None:
            return
        else:
            lootBoxIDPremiumPaid = self.__lunarNYController.receivedEnvelopes.getLootBoxIDByEnvelopeType(EnvelopeTypes.PREMIUM_PAID)
            lootBoxIDPaid = self.__lunarNYController.receivedEnvelopes.getLootBoxIDByEnvelopeType(EnvelopeTypes.PAID)
            lootBoxIDFree = self.__lunarNYController.receivedEnvelopes.getLootBoxIDByEnvelopeType(EnvelopeTypes.FREE)
            for result in countGiftHistory:
                if result.lootboxID == lootBoxIDFree:
                    self.viewModel.setFreeEnvelopesNumber(result.envelopesReceived)
                    if self.__currentEnvelopeType == EnvelopeTypes.FREE:
                        self.__setPagesNumber(result.envelopesReceived)
                if result.lootboxID == lootBoxIDPaid:
                    self.viewModel.setPaidEnvelopesNumber(result.envelopesReceived)
                    if self.__currentEnvelopeType == EnvelopeTypes.PAID:
                        self.__setPagesNumber(result.envelopesReceived)
                if result.lootboxID == lootBoxIDPremiumPaid:
                    self.viewModel.setPremiumPaidEnvelopesNumber(result.envelopesReceived)
                    if self.__currentEnvelopeType == EnvelopeTypes.PREMIUM_PAID:
                        self.__setPagesNumber(result.envelopesReceived)

            return

    @async
    def __updateDataFromServer(self):
        Waiting.show('loadContent')
        countGiftHistoryResult = yield await_callback(self.__countRequester.request)(eventID=GiftEventID.LUNAR_NY)
        if self.viewStatus not in (ViewStatus.DESTROYING, ViewStatus.DESTROYED):
            if countGiftHistoryResult.success:
                self.__setCountGiftHistory(countGiftHistoryResult.data)
        if countGiftHistoryResult.success:
            lootboxID = self.__lunarNYController.receivedEnvelopes.getLootBoxIDByEnvelopeType(self.__currentEnvelopeType)
            giftHistoryResult = yield await_callback(self.__dataRequester.request)(lootboxID=lootboxID, pageNum=self.__currentPageNumber, column=max(self.__currentColumnType.value, _DEFAULT_COLUMN_TYPES.value), order=self.__currentSortingOrder.value)
        else:
            giftHistoryResult = None
        Waiting.hide('loadContent')
        if self.viewStatus not in (ViewStatus.DESTROYING, ViewStatus.DESTROYED):
            if giftHistoryResult is not None and giftHistoryResult.success:
                self.__setGiftHistory(giftHistoryResult.data)
                self.viewModel.setEnvelopeTypeTab(self.__currentEnvelopeType)
                self.viewModel.setCurrentPageNumber(self.__currentPageNumber)
                self.__updatePagesNumber()
            else:
                self.viewModel.setIsGiftHistoryAvailable(False)
        return

    def __setGiftHistory(self, giftHistoryResults):
        if giftHistoryResults is None:
            return
        else:
            self.__userInfoHelper.clearInvalidData()
            for giftHistory in giftHistoryResults:
                self.__setupUserInfo(giftHistory)

            if self.__currentColumnType == ColumnType.PLAYERNAME:
                self.__sortCurrentUsersByUserName()
            self.__fillPlayerHistoryModel()
            if self.__userInfoHelper.hasInvalidName() and self.__userInfoHelper.proto.isConnected():
                self.__userInfoHelper.syncUsersInfo()
            return

    def __onChangeEnvelopeTypeTab(self, args):
        newTabType = EnvelopeTypes(args.get('envelopeType', _ENVELOPE_TYPES[0].value))
        if newTabType != self.__currentEnvelopeType:
            self.__currentPageNumber = 0
            self.__currentEnvelopeType = newTabType
            self.__updateGiftHistory()

    def __updatePagesNumber(self):
        if self.__currentEnvelopeType == EnvelopeTypes.FREE:
            self.__setPagesNumber(self.viewModel.getFreeEnvelopesNumber())
        if self.__currentEnvelopeType == EnvelopeTypes.PAID:
            self.__setPagesNumber(self.viewModel.getPaidEnvelopesNumber())
        if self.__currentEnvelopeType == EnvelopeTypes.PREMIUM_PAID:
            self.__setPagesNumber(self.viewModel.getPremiumPaidEnvelopesNumber())

    def __onSendEnvelopeInResponse(self, args):
        self.destroyWindow()
        if self.__lunarNYController.giftSystem.getEnvelopesEntitlementCount() > 0:
            showEnvelopesSendView(envelopeType=self.__currentEnvelopeType, receiverID=args.get('senderID', 0))
        else:
            showLunarNYMainView(initCtx={MAIN_VIEW_INIT_CONTEXT_TAB: Tab.SENDENVELOPES})

    def __onAddToFriends(self, args):
        senderID = args.get('senderID', 0)
        contact = self.__userInfoHelper.getContact(senderID)
        if contact is None:
            return
        else:
            if contact.isFriend() and USER_TAG.SUB_NONE in contact.getTags() and self.proto.contacts.isBidiFriendshipSupported():
                self.proto.contacts.requestFriendship(senderID)
            else:
                self.proto.contacts.addFriend(senderID, contact.getName())
            with self.viewModel.transaction() as model:
                playerEnvelopesHistoryModel = model.getPlayersInfo()
                for player in playerEnvelopesHistoryModel:
                    if player.getPlayerID() == senderID:
                        player.setStatus(self.__getPlayerStatus(contact))

                playerEnvelopesHistoryModel.invalidate()
                self.__triggerSyncInitiator(model=model)
            return

    def __onChangeColumnType(self, args):
        newColumnType = ColumnType(args.get('newColumnType', _COLUMN_TYPES[1].value))
        if newColumnType not in _COLUMN_TYPES:
            return
        if self.__currentColumnType == newColumnType:
            if self.__currentSortingOrder == ColumnSortingOrder.ASC:
                self.__currentSortingOrder = ColumnSortingOrder.DESC
            else:
                self.__currentSortingOrder = ColumnSortingOrder.ASC
        else:
            self.viewModel.setSelectedColumnType(newColumnType)
            self.__currentColumnType = newColumnType
            if newColumnType == ColumnType.PLAYERNAME:
                self.__currentSortingOrder = ColumnSortingOrder.DESC
            else:
                self.__currentSortingOrder = ColumnSortingOrder.ASC
        self.viewModel.setCurrentColumnSortingOrder(self.__currentSortingOrder)
        if self.__currentColumnType == ColumnType.PLAYERNAME:
            self.__sortCurrentUsersByUserName()
            self.__fillPlayerHistoryModel()
        else:
            self.__updateGiftHistory()

    def __onGoToEnvelopeSend(self):
        self.destroyWindow()
        showLunarNYMainView({MAIN_VIEW_INIT_CONTEXT_TAB: Tab.SENDENVELOPES})

    def __sortCurrentUsersByUserName(self):
        sortingOrder = bool(self.__currentSortingOrder.value)
        if not sortingOrder:
            self.__currentUsersInfo = sorted(self.__currentUsersInfo, key=lambda user: (user['nickName'] is None or user['nickName'] == '', _nickNameSortKeyFun(user['nickName'])), reverse=sortingOrder)
        else:
            self.__currentUsersInfo = sorted(self.__currentUsersInfo, key=lambda user: _nickNameSortKeyFun(user['nickName']), reverse=sortingOrder)

    def __fillPlayerHistoryModel(self):
        with self.viewModel.transaction() as model:
            model.getPlayersInfo().clear()
            items = model.getPlayersInfo()
            for currentUserInfo in self.__currentUsersInfo:
                item = PlayerEnvelopesHistory()
                item.setPlayerID(currentUserInfo['playerID'])
                item.setNickname(currentUserInfo['nickName'])
                item.setIsOnline(currentUserInfo['isOnline'])
                item.setClanTag(currentUserInfo['clanTag'])
                item.setReceivedEnvelopesNumber(currentUserInfo['receivedEnvelopesNumber'])
                item.setReceivedGoldNumber(currentUserInfo['receivedGoldNumber'])
                item.setSentInResponseEnvelopesNumber(currentUserInfo['sentInResponseEnvelopesNumber'])
                item.setStatus(currentUserInfo['status'])
                items.addViewModel(item)

            items.invalidate()
            self.__triggerSyncInitiator(model=model)

    def __onChangeCurrentPageNumber(self, args):
        newPageNumber = int(args.get('newPageNumber', 0))
        if 0 <= newPageNumber <= self.viewModel.getPagesNumber():
            self.__currentPageNumber = newPageNumber
            self.__updateGiftHistory()

    def __updateGiftHistory(self):
        self.__currentUsersInfo = []
        self.__updateDataFromServer()

    def __onUserNameReceived(self, names):
        with self.viewModel.transaction() as model:
            playerEnvelopesHistoryModel = model.getPlayersInfo()
            for player in playerEnvelopesHistoryModel:
                playerId = player.getPlayerID()
                if playerId in names:
                    player.setNickname(names[playerId])

            for user in self.__currentUsersInfo:
                if user['playerID'] in names:
                    user['nickName'] = names[user['playerID']]

            playerEnvelopesHistoryModel.invalidate()
            self.__triggerSyncInitiator(model=model)

    def __getPlayerStatus(self, contact):
        if contact is None:
            return PlayerStatus.NOTFRIEND
        elif contact.isAnySub():
            return PlayerStatus.ISFRIEND
        else:
            return PlayerStatus.FRIENDREQUESTINPROGRESS if contact.isFriend() and USER_TAG.SUB_PENDING_OUT in contact.getTags() else PlayerStatus.NOTFRIEND

    def __userActionReceived(self, actionID, contact, _):
        if actionID in (USER_ACTION_ID.SUBSCRIPTION_CHANGED, USER_ACTION_ID.FRIEND_ADDED, USER_ACTION_ID.FRIEND_REMOVED):
            contactID = contact.getID()
            playerStatus = self.__getPlayerStatus(contact)
            with self.viewModel.transaction() as model:
                playerEnvelopesHistoryModel = model.getPlayersInfo()
                for player in playerEnvelopesHistoryModel:
                    if player.getPlayerID() == contactID:
                        player.setStatus(playerStatus)

                playerEnvelopesHistoryModel.invalidate()
                self.__triggerSyncInitiator(model=model)
                for user in self.__currentUsersInfo:
                    if user['playerID'] == contactID:
                        user['status'] = playerStatus

    def __onUserStatusUpdated(self, user):
        playerModel = findFirst(lambda x: x.getNickname() == user.getFullName(), self.viewModel.getPlayersInfo())
        if playerModel:
            playerModel.setIsOnline(user.isOnline())
            self.__triggerSyncInitiator()

    def __setupUserInfo(self, data):
        userID = data.senderID
        contact = self.__userInfoHelper.getContact(userID)
        clanTag = contact.getClanAbbrev() if contact is not None and contact.getClanAbbrev() is not None else ''
        self.__currentUsersInfo.append({'playerID': data.senderID,
         'nickName': self.__userInfoHelper.getUserName(userID, withEmptyName=True),
         'isOnline': contact.isOnline() if contact is not None else False,
         'clanTag': clanTag,
         'receivedEnvelopesNumber': data.envelopesReceived,
         'receivedGoldNumber': data.goldReceived,
         'sentInResponseEnvelopesNumber': data.envelopesSend,
         'status': self.__getPlayerStatus(contact)})
        return

    @replaceNoneKwargsModel
    def __triggerSyncInitiator(self, model=None):
        model.setSyncInitiator((model.getSyncInitiator() + 1) % 1000)

    def __onChatPluginConnected(self, _):
        if self.__userInfoHelper.proto.isConnected() and self.__userInfoHelper.hasInvalidName():
            self.__userInfoHelper.syncUsersInfo()


class EnvelopesHistoryViewWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None, countRequester=None, dataRequester=None):
        super(EnvelopesHistoryViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=EnvelopesHistoryView(R.views.lobby.lunar_ny.envelopes.EnvelopesHistoryView(), countRequester=countRequester, dataRequester=dataRequester), layer=WindowLayer.FULLSCREEN_WINDOW, parent=parent)
