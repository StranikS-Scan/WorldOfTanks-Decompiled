# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lunar_ny/open_envelopes_award_view.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import IS_OPEN_ENVELOPES_ANIMATION_ENABLED
from adisp import process
from frameworks.wulf import ViewSettings, ViewFlags, WindowFlags, WindowLayer, ViewStatus
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lunar_ny.envelope_award_view_model import EnvelopeAwardViewModel, PlayerStatus
from gui.impl.gen.view_models.views.lobby.lunar_ny.main_view.main_view_model import Tab
from gui.impl.gen.view_models.views.lobby.lunar_ny.open_envelopes_award_view_model import OpenEnvelopesAwardViewModel, RequestStatus
from gui.impl.lobby.lunar_ny.lunar_ny_helpers import showLunarNYMainView, createRewardTooltip, showOpenEnvelopesAwardView, showEnvelopesSendView
from gui.impl.lobby.lunar_ny.lunar_ny_model_helpers import packBonusModelAndTooltipData
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import g_eventBus, events
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from lunar_ny import ILunarNYController
from lunar_ny.envelopes_storage_users_helper import EnvelopesStorageUsersHelper
from lunar_ny.lunar_ny_bonuses_packers import composeOpenLootBoxesBonuses
from lunar_ny.lunar_ny_constants import MAIN_VIEW_INIT_CONTEXT_TAB, EnvelopeTypes
from messenger.m_constants import PROTO_TYPE, USER_TAG, USER_ACTION_ID
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from shared_utils import first
from skeletons.gui.shared import IItemsCache

class OpenEnvelopesAwardView(ViewImpl):
    __slots__ = ('__rawData', '__envelopesType', '__userInfoHelper', '__toolTipsData', '__senderID')
    __lunarNYController = dependency.descriptor(ILunarNYController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *_, **kwargs):
        settings = ViewSettings(kwargs.get('layoutID', R.invalid()))
        settings.flags = ViewFlags.VIEW
        settings.model = OpenEnvelopesAwardViewModel()
        super(OpenEnvelopesAwardView, self).__init__(settings)
        self.__rawData = kwargs.get('rawData', {})
        self.__envelopesType = kwargs.get('envelopesType', EnvelopeTypes.PREMIUM_PAID)
        self.__userInfoHelper = EnvelopesStorageUsersHelper()
        self.__toolTipsData = {}
        self.__senderID = -1

    @property
    def viewModel(self):
        return self.getViewModel()

    @proto_getter(PROTO_TYPE.MIGRATION)
    def proto(self):
        return None

    def createToolTipContent(self, event, contentID):
        tooltipData = self.__toolTipsData.get(event.getArgument('tooltipID'), None)
        return createRewardTooltip(contentID, tooltipData)

    def _initialize(self, *args, **kwargs):
        super(OpenEnvelopesAwardView, self)._initialize()
        self.viewModel.onAddToFriend += self.__onAddToFriend
        self.viewModel.onAnimationEnabled += self.__onAnimationEnabled
        self.viewModel.onGoToStorage += self.__onGoToStorage
        self.viewModel.onOpenNext += self.__onOpenNext
        self.viewModel.onSendEnvelope += self.__onSendEnvelope
        self.viewModel.onClickInfoLink += self.__onClickInfoLink

    def _onLoading(self, *args, **kwargs):
        super(OpenEnvelopesAwardView, self)._onLoading()
        with self.viewModel.transaction() as model:
            model.setEnvelopesType(self.__envelopesType)
            model.setAnimationEnabled(AccountSettings.getSettings(IS_OPEN_ENVELOPES_ANIMATION_ENABLED))
            self.__updateEnvelopesCount(model=model)
            self.__setupEnvelopesData(model=model)
            self.__setupBonuses(model=model)
            model.setOpenEnvelopesRequestStatus(RequestStatus.SUCCESS)
        self.__userInfoHelper.onNamesReceived += self.__onNamesReceived
        self.__lunarNYController.receivedEnvelopes.onReceivedEnvelopesUpdated += self.__updateEnvelopesCount
        g_messengerEvents.users.onUserActionReceived += self.__onUserActionReceived
        g_messengerEvents.onPluginConnected += self.__onChatPluginConnected

    def _finalize(self):
        super(OpenEnvelopesAwardView, self)._finalize()
        g_messengerEvents.users.onUserActionReceived -= self.__onUserActionReceived
        self.__userInfoHelper.onNamesReceived -= self.__onNamesReceived
        g_messengerEvents.onPluginConnected -= self.__onChatPluginConnected
        self.__lunarNYController.receivedEnvelopes.onReceivedEnvelopesUpdated -= self.__updateEnvelopesCount
        self.viewModel.onAddToFriend -= self.__onAddToFriend
        self.viewModel.onAnimationEnabled -= self.__onAnimationEnabled
        self.viewModel.onGoToStorage -= self.__onGoToStorage
        self.viewModel.onOpenNext -= self.__onOpenNext
        self.viewModel.onSendEnvelope -= self.__onSendEnvelope
        self.viewModel.onClickInfoLink -= self.__onClickInfoLink
        self.__toolTipsData.clear()
        self.__userInfoHelper.clearInvalidData()
        self.__senderID = -1

    @replaceNoneKwargsModel
    def __setupEnvelopesData(self, model=None):
        giftsInfo = self.__rawData.get('giftsInfo', [])
        envelopesModel = model.getEnvelopes()
        envelopesModel.clear()
        self.__userInfoHelper.clearInvalidData()
        senderIDs = set()
        for senderID, giftInfo in giftsInfo:
            wishID = giftInfo.get('message_id', 0)
            envelopeModel = EnvelopeAwardViewModel()
            envelopeModel.setSenderID(senderID)
            envelopeModel.setWishID(wishID)
            if senderID > 0:
                senderName = self.__userInfoHelper.getUserName(senderID, withEmptyName=True)
                envelopeModel.setSenderName(senderName)
            envelopeModel.setSenderStatus(self.__getPlayerStatus(senderID))
            envelopesModel.addViewModel(envelopeModel)
            senderIDs.add(senderID)

        self.__senderID = first(senderIDs, 0) if len(senderIDs) == 1 else -1
        if self.__userInfoHelper.hasInvalidName() and self.__userInfoHelper.proto.isConnected():
            self.__userInfoHelper.syncUsersInfo()
        envelopesModel.invalidate()

    @replaceNoneKwargsModel
    def __setupBonuses(self, model=None):
        bonuses = composeOpenLootBoxesBonuses(self.__rawData.get('bonus', []))
        packBonusModelAndTooltipData(bonuses, model.getRewards(), self.__toolTipsData)

    @replaceNoneKwargsModel
    def __updateEnvelopesCount(self, model=None):
        model.setEnvelopesCount(self.__lunarNYController.receivedEnvelopes.getReceivedEnvelopesCountByType(self.__envelopesType))

    def __getPlayerStatus(self, senderID):
        contact = self.__userInfoHelper.getContact(senderID)
        if contact.isAnySub():
            return PlayerStatus.ISFRIEND
        return PlayerStatus.FRIENDREQUESTINPROGRESS if contact.isFriend() and USER_TAG.SUB_PENDING_OUT in contact.getTags() else PlayerStatus.NOTFRIEND

    def __onNamesReceived(self, names):
        with self.viewModel.transaction() as model:
            envelopesModel = model.getEnvelopes()
            for envelope in envelopesModel:
                playerID = envelope.getSenderID()
                if playerID in names:
                    envelope.setSenderName(names[playerID])

            envelopesModel.invalidate()

    def __onSendEnvelope(self, args):
        if self.__lunarNYController.giftSystem.getEnvelopesEntitlementCount() > 0:
            showEnvelopesSendView(envelopeType=self.__envelopesType, receiverID=args.get('senderID', 0))
        else:
            showLunarNYMainView(initCtx={MAIN_VIEW_INIT_CONTEXT_TAB: Tab.SENDENVELOPES})
        self.destroyWindow()

    @process
    def __onOpenNext(self, args):
        count = args.get('count', 1)
        lootBox = self.__lunarNYController.receivedEnvelopes.getLootBoxByEnvelopeType(self.__envelopesType)
        self.viewModel.setOpenEnvelopesRequestStatus(RequestStatus.INPROGRESS)
        if self.__lunarNYController.receivedEnvelopes.isOpenAvailability() and lootBox is not None:
            if self.__senderID != -1 and self.__hasEnvelopesFromSender(self.__senderID, count):
                senderID = self.__senderID
            else:
                senderID = -1
            result = yield LootBoxOpenProcessor(lootBox, count, senderID).request()
            if result.success:
                if self.viewStatus in (ViewStatus.DESTROYING, ViewStatus.DESTROYED):
                    showOpenEnvelopesAwardView(result.auxData, self.__envelopesType)
                else:
                    self.__updateRewardsData(result.auxData)
                    self.viewModel.setOpenEnvelopesRequestStatus(RequestStatus.SUCCESS)
                return
            self.__pushErrorSystemMessage()
        if self.viewStatus not in (ViewStatus.DESTROYING, ViewStatus.DESTROYED):
            self.viewModel.setOpenEnvelopesRequestStatus(RequestStatus.ERROR)
        return

    def __pushErrorSystemMessage(self):
        msg = backport.text(R.strings.lunar_ny.systemMessage.openEnvelopesAwards.error())
        SystemMessages.pushMessage(msg, SM_TYPE.ErrorSimple, NotificationPriorityLevel.MEDIUM)

    def __onGoToStorage(self, *_):
        showLunarNYMainView(initCtx={MAIN_VIEW_INIT_CONTEXT_TAB: Tab.STOREENVELOPES})
        self.destroyWindow()

    def __onAnimationEnabled(self, args):
        isEnabled = args.get('animationEnabled', True)
        AccountSettings.setSettings(IS_OPEN_ENVELOPES_ANIMATION_ENABLED, isEnabled)
        self.viewModel.setAnimationEnabled(isEnabled)

    def __onAddToFriend(self, args):
        senderID = args.get('senderID', 0)
        contact = self.__userInfoHelper.getContact(senderID)
        if contact.isFriend() and USER_TAG.SUB_NONE in contact.getTags() and self.proto.contacts.isBidiFriendshipSupported():
            self.proto.contacts.requestFriendship(senderID)
        else:
            self.proto.contacts.addFriend(senderID, contact.getName())
        with self.viewModel.transaction() as model:
            envelopesModel = model.getEnvelopes()
            for envelopeModel in envelopesModel:
                if envelopeModel.getSenderID() == senderID:
                    envelopeModel.setSenderStatus(self.__getPlayerStatus(senderID))

            envelopesModel.invalidate()

    def __onClickInfoLink(self, *_):
        g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.SPECIFIED, self.__lunarNYController.getAboutEnvelopesUrl()))

    def __onUserActionReceived(self, actionID, contact, _):
        if actionID in (USER_ACTION_ID.SUBSCRIPTION_CHANGED, USER_ACTION_ID.FRIEND_ADDED, USER_ACTION_ID.FRIEND_REMOVED):
            with self.viewModel.transaction() as model:
                envelopesModel = model.getEnvelopes()
                for envelopeModel in envelopesModel:
                    if envelopeModel.getSenderID() == contact.getID():
                        envelopeModel.setSenderStatus(self.__getPlayerStatus(contact.getID()))

                envelopesModel.invalidate()

    def __updateRewardsData(self, rawData):
        self.__rawData = rawData
        self.__toolTipsData.clear()
        with self.viewModel.transaction() as model:
            self.__updateEnvelopesCount(model=model)
            self.__setupEnvelopesData(model=model)
            self.__setupBonuses(model=model)

    def __onChatPluginConnected(self, _):
        if self.__userInfoHelper.proto.isConnected() and self.__userInfoHelper.hasInvalidName():
            self.__userInfoHelper.syncUsersInfo()

    def __hasEnvelopesFromSender(self, senderID, count):
        _, data = self.__itemsCache.items.giftSystem.findGiftBySenderID(self.__getGiftsID(), senderID)
        return data is not None and data.giftsCount >= count

    def __getGiftsID(self):
        return self.__lunarNYController.receivedEnvelopes.getLootBoxIDByEnvelopeType(self.__envelopesType)


class OpenEnvelopesAwardViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, rawData, envelopesType, parent=None):
        super(OpenEnvelopesAwardViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=OpenEnvelopesAwardView(layoutID=R.views.lobby.lunar_ny.OpenEnvelopesAwardView(), rawData=rawData, envelopesType=envelopesType), layer=WindowLayer.OVERLAY, parent=parent)
