# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lunar_ny/envelopes/fill_envelope_view.py
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import LUNAR_NY_CONGRATULATIONS
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from frameworks.wulf import ViewStatus
from helpers import dependency
from lunar_ny import ILunarNYController
from lunar_ny.lunar_ny_constants import EnvelopeTypes, ALL_ENVELOPE_TYPES
from gui.impl import backport
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lunar_ny.reward_view_model import RewardViewModel, RewardType
from gui.impl.gen.view_models.views.lobby.lunar_ny.fill_envelope_view_model import FillEnvelopeViewModel, TabKeys
from gui.impl.gen.view_models.views.lobby.lunar_ny.friend_model import FriendModel, FriendStatus
from gui.impl.lobby.lunar_ny.lunar_ny_base_main_view_component import BaseLunarNYViewComponent
from gui.impl.lobby.lunar_ny.lunar_ny_model_helpers import getRewardsByEnvelopeType
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.gift_system.constants import GifterResponseState
from gui.shared import g_eventBus
from gui.shared.money import Currency
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import OpenLinkEvent, HasCtxEvent, TutorialEvent
from gui.shared.utils.functions import makeTooltip
from gui.server_events.bonuses import getSimpleTooltipData
from messenger.storage import storage_getter
from messenger.proto.shared_find_criteria import AnySubFindCriteria
from messenger.proto.events import g_messengerEvents
from skeletons.account_helpers.settings_core import ISettingsCore
from shared_utils import findFirst
from lunar_ny.lunar_ny_constants import MAIN_VIEW_INIT_CONTEXT_SEND_TO_PLAYER, MAIN_VIEW_INIT_CONTEXT_ENVELOPE_TYPE, SEND_TO_PLAYER_EVENT, SEND_TO_PLAYER_EVENT_IS_ENABLED
from external_strings_utils import textRestrictions
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from messenger.proto.entities import LobbyUserEntity
    from gui.gift_system.wrappers import SendGiftResponse

class FillEnvelopeView(BaseLunarNYViewComponent[FillEnvelopeViewModel]):
    __slots__ = ('__envelopeType', '__friends', '__receiverID', '__congratulationSettings', '__banned')
    __lunarNYController = dependency.descriptor(ILunarNYController)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, viewModel, view):
        super(FillEnvelopeView, self).__init__(viewModel, view)
        self.__friends = self.__userStorage.getList(AnySubFindCriteria())
        self.__congratulationSettings = AccountSettings.getSettings(LUNAR_NY_CONGRATULATIONS)
        self.__envelopeType = EnvelopeTypes.FREE
        self.__receiverID = -1
        self.__banned = set()

    def createToolTipContent(self, event, contentID):
        tooltipID = event.getArgument('tooltipID')
        if tooltipID is not None:
            if tooltipID == RewardType.CURRENCY.value:
                tooltip = makeTooltip(*getSimpleTooltipData(Currency.GOLD))
                return createBackportTooltipContent(tooltip=tooltip, isSpecial=False)
            if tooltipID == RewardType.CUSTOMIZATIONDECAL.value:
                header = backport.text(R.strings.item_types.customization.projectionDecal())
                body = backport.text(R.strings.tooltips.customization.tabs.projectionDecal.body())
                return createBackportTooltipContent(tooltip=makeTooltip(header=header, body=body), isSpecial=False)
            if tooltipID == RewardType.CHARMRARE.value:
                return createBackportTooltipContent(tooltip=makeTooltip(*getSimpleTooltipData('charmRare')), isSpecial=False)
            if tooltipID == RewardType.CHARMCOMMON.value:
                return createBackportTooltipContent(tooltip=makeTooltip(*getSimpleTooltipData('charmCommon')), isSpecial=False)
        return super(FillEnvelopeView, self).createToolTipContent(event, contentID)

    def onLoading(self, initCtx, isActive):
        super(FillEnvelopeView, self).onLoading(initCtx, isActive)
        if isActive:
            self.__updateViewModelByCtx(initCtx)
        self._viewModel.setAccountNameMaxLength(textRestrictions.ACCOUNT_NAME_MAX_LENGTH)

    def show(self, ctx):
        self.__banned.clear()
        self.__updateViewModelByCtx(ctx)

    def getViewModel(self):
        return self._viewModel

    def __updateViewModelByCtx(self, ctx):
        self.__receiverID = ctx.get(MAIN_VIEW_INIT_CONTEXT_SEND_TO_PLAYER, -1)
        self.__envelopeType = ctx.get(MAIN_VIEW_INIT_CONTEXT_ENVELOPE_TYPE)
        if self.__envelopeType is None:
            countByType = self.__lunarNYController.giftSystem.getEnvelopesEntitlementCountByType
            envelopes = [ (envType, countByType(envType)) for envType in ALL_ENVELOPE_TYPES ]
            envelopes.sort(key=lambda x: x[1])
            self.__envelopeType, _ = envelopes[-1]
        else:
            self.__envelopeType = EnvelopeTypes(self.__envelopeType)
        self.__addListeners()
        with self._viewModel.transaction() as model:
            model.setEnvelopeType(self.__envelopeType)
            model.setCountEnvelopes(self.__lunarNYController.giftSystem.getEnvelopesEntitlementCountByType(self.__envelopeType))
            model.setIsForRandomUser(len(self.__friends) == 0)
            self.__updateRewards(model)
            self.__updateFriends(model=model)
            if self.__receiverID > 0:
                friend = findFirst(lambda x: x.getID() == self.__receiverID, self.__friends)
                self.__updateFriendModel(model.selectedFriend, friend)
                model.setIsValidFriend(friend.getID() not in self.__banned)
            else:
                self.__setNotSelectedFriend(model.selectedFriend)
                self.getViewModel().setIsValidFriend(True)
            hintSettings = self.__settingsCore.serverSettings.getOnceOnlyHintsSettings()
            model.setHasDropdownBeenClicked(hintSettings[OnceOnlyHints.LUNAR_NY_DROPDOWN_HINT])
            model.setHasCongratulationBeenClicked(hintSettings[OnceOnlyHints.LUNAR_NY_CONGRATULATION_HINT])
        return

    def __updateCongratulation(self, model):
        congratulationIdx = 0
        envelopeValue = self.__envelopeType.value
        if envelopeValue in self.__congratulationSettings:
            congratulationIdx = self.__congratulationSettings[envelopeValue]
        model.setCongratulation(congratulationIdx)

    def __saveCongratulation(self):
        self.__congratulationSettings[self.__envelopeType.value] = self.getViewModel().getCongratulation()
        AccountSettings.setSettings(LUNAR_NY_CONGRATULATIONS, self.__congratulationSettings)

    def finalize(self):
        self.__saveCongratulation()
        self.__removeListeners()
        super(FillEnvelopeView, self).finalize()

    @storage_getter('users')
    def __userStorage(self):
        return None

    def __addListeners(self):
        g_messengerEvents.users.onUserStatusUpdated += self.__onUserStatusUpdated
        g_messengerEvents.users.onUserActionReceived += self.__onUserActionReceived
        vm = self.getViewModel()
        vm.onSendBtnClick += self.__onSendBtnClick
        vm.onSelectFriend += self.__onSelectFriend
        vm.gotoEnvelopesInfo += self.__gotoEnvelopesInfo
        vm.onClose += self.__onClose
        vm.onTabChange += self.__onTabChange
        vm.onCongratulationSelect += self.__onCongratulationSelect
        vm.onDropdownClick += self.__onDropdownClick
        self.__lunarNYController.giftSystem.onEnvelopesEntitlementUpdated += self.__onEnvelopesEntitlementUpdated

    def __removeListeners(self):
        g_messengerEvents.users.onUserStatusUpdated -= self.__onUserStatusUpdated
        g_messengerEvents.users.onUserActionReceived -= self.__onUserActionReceived
        vm = self.getViewModel()
        vm.onSendBtnClick -= self.__onSendBtnClick
        vm.onSelectFriend -= self.__onSelectFriend
        vm.gotoEnvelopesInfo -= self.__gotoEnvelopesInfo
        vm.onClose -= self.__onClose
        vm.onTabChange -= self.__onTabChange
        vm.onCongratulationSelect -= self.__onCongratulationSelect
        vm.onDropdownClick -= self.__onDropdownClick
        self.__lunarNYController.giftSystem.onEnvelopesEntitlementUpdated -= self.__onEnvelopesEntitlementUpdated

    def __updateRewards(self, model):
        self.__packRewardsByType(self.__envelopeType, model.getRewards())

    def __packRewardsByType(self, envelopeType, rewardsModel):
        rewardsModel.clear()
        if envelopeType in (EnvelopeTypes.FREE, EnvelopeTypes.PAID):
            charmType = RewardType.CHARMCOMMON
        else:
            charmType = RewardType.CHARMRARE
        rewardsModel.addViewModel(self.__createRewardModel(charmType, 'charm', 1))
        lootboxRewards = getRewardsByEnvelopeType(envelopeType)
        gold = lootboxRewards.get(Currency.GOLD)
        if gold is not None:
            rewardsModel.addViewModel(self.__createRewardModel(RewardType.CURRENCY, Currency.GOLD, gold))
        if envelopeType == EnvelopeTypes.PREMIUM_PAID:
            rewardsModel.addViewModel(self.__createRewardModel(RewardType.CUSTOMIZATIONDECAL, 'decal', 1))
        rewardsModel.invalidate()
        return

    def __createRewardModel(self, rewardType, rewardName, value):
        model = RewardViewModel()
        model.setRewardType(rewardType)
        model.setRewardID(rewardName)
        model.setCount(value)
        model.setTooltipID(rewardType.value)
        model.setTooltipContentID(R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent())
        return model

    @replaceNoneKwargsModel
    def __updateFriends(self, model=None):
        friendsArray = model.getFriends()
        friendsArray.clear()
        for friend in self.__friends:
            friendModel = FriendModel()
            self.__updateFriendModel(friendModel, friend)
            friendsArray.addViewModel(friendModel)

        friendsArray.invalidate()

    def __updateFriendModel(self, friendModel, friend):
        friendModel.setSpaID(friend.getID())
        friendModel.setName(friend.getFullName())
        friendModel.setStatus(FriendStatus.ONLINE if friend.isOnline() else FriendStatus.OFFLINE)
        friendModel.setClan(friend.getClanAbbrev())

    def __onSendBtnClick(self):
        isRandomUser = self.getViewModel().getIsForRandomUser()
        selectedFriend = self.getViewModel().selectedFriend
        selectedUserID = -1 if isRandomUser else selectedFriend.getSpaID()
        self.__lunarNYController.giftSystem.sendGift(self.__envelopeType, selectedUserID, self.getViewModel().getCongratulation(), self.__onSendComplete)
        g_eventBus.handleEvent(TutorialEvent(TutorialEvent.ON_COMPONENT_LOST, targetID='LunarNYCongratulation'), scope=EVENT_BUS_SCOPE.GLOBAL)

    def __onSendComplete(self, result):
        isSuccess = result is not None and result.state == GifterResponseState.WEB_SUCCESS
        if self._mainViewRef.viewStatus != ViewStatus.LOADED:
            return
        else:
            if isSuccess:
                self.getViewModel().setSendingComplete(True)
            elif result.state == GifterResponseState.WEB_ACCOUNT_FAILURE:
                self.__banned.add(self.getViewModel().selectedFriend.getSpaID())
                self.getViewModel().setIsValidFriend(False)
                self.getViewModel().setIsErrorState(True)
            else:
                self.getViewModel().setIsErrorState(True)
            return

    def __onEnvelopesEntitlementUpdated(self):
        self.getViewModel().setCountEnvelopes(self.__lunarNYController.giftSystem.getEnvelopesEntitlementCountByType(self.__envelopeType))

    def __onUserStatusUpdated(self, user):
        friendModel = findFirst(lambda x: x.getName() == user.getFullName(), self.getViewModel().getFriends())
        if friendModel:
            friendModel.setStatus(FriendStatus.ONLINE if user.isOnline() else FriendStatus.OFFLINE)

    def __onUserActionReceived(self, _, user, __):
        isFriend = user.isAnySub()
        updatedUserName = user.getFullName()
        existsInFriends = findFirst(lambda x: x.getFullName() == updatedUserName, self.__friends) is not None
        if isFriend and not existsInFriends:
            self.__friends.append(user)
            self.__updateFriends()
        elif not isFriend and existsInFriends:
            self.getViewModel().setIsValidFriend(existsInFriends)
            self.__friends = self.__userStorage.getList(AnySubFindCriteria())
            self.__updateFriends()
        return

    def __gotoEnvelopesInfo(self):
        g_eventBus.handleEvent(OpenLinkEvent(OpenLinkEvent.SPECIFIED, self.__lunarNYController.getAboutEnvelopesUrl()))

    def __onClose(self):
        with self._viewModel.transaction() as tx:
            tx.setSendingComplete(False)
            tx.setIsErrorState(False)
        g_eventBus.handleEvent(HasCtxEvent(SEND_TO_PLAYER_EVENT, {SEND_TO_PLAYER_EVENT_IS_ENABLED: False}))

    def __onTabChange(self, args):
        tabName = args.get('tab')
        if tabName:
            tabName = TabKeys(tabName)
            self.getViewModel().setIsForRandomUser(tabName == TabKeys.SENDTORANDOMUSER)

    def __onSelectFriend(self, args):
        spaID = args.get('spaID')
        if spaID:
            friend = findFirst(lambda x: x.getID() == spaID, self.__friends)
            if friend:
                with self.getViewModel().selectedFriend.transaction() as model:
                    self.__updateFriendModel(model, friend)
            self.__friends = self.__userStorage.getList(AnySubFindCriteria())
            friend = findFirst(lambda x: x.getID() == spaID, self.__friends)
            self.getViewModel().setIsValidFriend(friend is not None and friend.getID() not in self.__banned)
        else:
            self.__setNotSelectedFriend(self.getViewModel().selectedFriend)
            self.getViewModel().setIsValidFriend(True)
        return

    def __onCongratulationSelect(self, args):
        congratulation = args.get('congratulation')
        if congratulation is not None:
            self.getViewModel().setCongratulation(congratulation)
        if not self.__settingsCore.serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.LUNAR_NY_CONGRATULATION_HINT, False):
            self.__settingsCore.serverSettings.setOnceOnlyHintsSettings({OnceOnlyHints.LUNAR_NY_CONGRATULATION_HINT: True})
            self._viewModel.setHasCongratulationBeenClicked(True)
        return

    def __onDropdownClick(self):
        if not self.__settingsCore.serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.LUNAR_NY_DROPDOWN_HINT, False):
            self.__settingsCore.serverSettings.setOnceOnlyHintsSettings({OnceOnlyHints.LUNAR_NY_DROPDOWN_HINT: True})
            self._viewModel.setHasDropdownBeenClicked(True)

    def __setNotSelectedFriend(self, friendModel):
        with friendModel.transaction() as tx:
            tx.setSpaID(FriendModel.NOT_SELECTED_SPA_ID)
            tx.setName('')
            tx.setStatus(FriendStatus.OFFLINE)
            tx.setClan('')
