# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/gift_system/ny_gift_system_view.py
import typing
import math_utils
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from gifts.gifts_common import GiftEventID
from gui import SystemMessages
from gui.gift_system.constants import NY_STAMP_CODE, GifterResponseState, HubUpdateReason
from gui.gift_system.mixins import GiftEventHubWatcher
from gui.gift_system.wrappers import hasGiftEventHub
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.gift_system.friend_model import FriendModel
from gui.impl.gen.view_models.views.lobby.new_year.views.gift_system.progression_stage_model import ProgressionStageModel
from gui.impl.gen.view_models.views.lobby.new_year.views.gift_system.ny_gift_system_view_model import State
from gui.impl.gen.view_models.views.lobby.new_year.views.gift_system.submission_form_model import SubmissionFormModel, SubmissionState
from gui.impl.lobby.missions.daily_quests_view import DailyTabs
from gui.impl.lobby.new_year.ny_views_helpers import giftsPogressQuestFilter, giftsSubprogressQuestFilter, getGiftsTokensCountByID, getTimerGameDayLeft
from gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from gui.impl.lobby.new_year.tooltips.ny_bro_token_tooltip import NyBroTokenTooltip
from gui.impl.lobby.new_year.tooltips.ny_post_stamp_tooltip import NyPostStampTooltip
from gui.impl.new_year.navigation import ViewAliases, NewYearNavigation
from gui.impl.new_year.new_year_bonus_packer import packBonusModelAndTooltipData, getNewYearBonusPacker
from gui.impl.new_year.new_year_helper import backportTooltipDecorator, getGiftSystemCongratulationResource, getGiftSystemRandomCongratulationID
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events import events_dispatcher
from gui.shared.event_dispatcher import showHangar, showStylePreview
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.missions.packers.bonus import BonusUIPacker
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers import dependency
from helpers.time_utils import getDayTimeLeft, ONE_MINUTE
from messenger.m_constants import USER_ACTION_ID as _ACTION_ID, USER_TAG
from messenger.proto.events import g_messengerEvents
from messenger.proto.entities import LobbyUserEntity
from messenger.proto.shared_find_criteria import AnySubFindCriteria
from messenger.storage import storage_getter
from new_year.ny_constants import NY_GIFT_SYSTEM_SUBPROGRESS_TOKEN, NY_GIFT_SYSTEM_PROGRESSION_TOKEN, CustomizationObjects
from new_year.ny_preview import getVehiclePreviewID
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IGiftSystemController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
from uilogging.ny.loggers import NyGiftSystemSendButtonLogger, NyGiftSystemIntroLogger, NyCelebrityButtonLogger, NyGiftSystemFlowLogger
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.gift_system.hubs.new_year.hub_core import GiftEventNYHub
    from gui.gift_system.wrappers import SendGiftResponse
    from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
    from gui.impl.gen.view_models.views.lobby.new_year.views.gift_system.ny_gift_system_view_model import NyGiftSystemViewModel
    from gui.server_events.event_items import TokenQuest
_NOT_SELECTED_SPA_ID = SubmissionFormModel.NOT_SELECTED_SPA_ID
_DEFAULT_SELECTED_USER = LobbyUserEntity(_NOT_SELECTED_SPA_ID, name='')
_LOCKED_STATES = {SubmissionState.GIFT_SENDING, SubmissionState.PREV_GIFT_SENDING, SubmissionState.BALANCE_UNAVAILABLE}

def _showDailyQuestsTab():
    events_dispatcher.showDailyQuests(subTab=DailyTabs.QUESTS)


class _ShowGiftSystemCallback(object):
    __giftsController = dependency.descriptor(IGiftSystemController)
    __nyController = dependency.descriptor(INewYearController)
    __slots__ = ('__objectName',)

    def __init__(self, objectName=None):
        self.__objectName = objectName or NewYearNavigation.getCurrentObject()

    def __call__(self, *args, **kwargs):
        if not self.__nyController.isEnabled():
            showHangar()
            return
        else:
            giftEventHub = self.__giftsController.getEventHub(GiftEventID.NY_HOLIDAYS)
            if giftEventHub is None or not giftEventHub.getSettings().isEnabled:
                NewYearNavigation.switchFromStyle(CustomizationObjects.FIR, viewAlias=ViewAliases.GLADE_VIEW, forceShowMainView=True)
                return
            NewYearNavigation.switchFromStyle(self.__objectName, viewAlias=ViewAliases.GIFT_SYSTEM_VIEW, forceShowMainView=True)
            return


class NyGiftSystemView(HistorySubModelPresenter, GiftEventHubWatcher):
    __slots__ = ('_tooltips', '_eventHub', '__notifier', '__forcedSending', '__messageID', '__targetSpaID')
    _GIFT_EVENT_ID = GiftEventID.NY_HOLIDAYS
    __eventsCache = dependency.descriptor(IEventsCache)
    __giftsController = dependency.descriptor(IGiftSystemController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __introLogger = NyGiftSystemIntroLogger()
    __sendButtonLogger = NyGiftSystemSendButtonLogger()

    def __init__(self, viewModel, parentView, soundConfig=None):
        super(NyGiftSystemView, self).__init__(viewModel, parentView, soundConfig)
        self._tooltips = {}
        self.__forcedSending = False
        self.__messageID = getGiftSystemRandomCongratulationID()
        self.__targetSpaID = _NOT_SELECTED_SPA_ID
        self.__notifier = PeriodicNotifier(getTimerGameDayLeft, self.__updateProgressionTimer, (ONE_MINUTE,))

    @property
    def viewModel(self):
        return self.getViewModel()

    @storage_getter('users')
    def usersStorage(self):
        return None

    def initialize(self, targetSpaID=_NOT_SELECTED_SPA_ID, forceShowIntro=False, *args, **kwargs):
        super(NyGiftSystemView, self).initialize(*args, **kwargs)
        self.__addListeners()
        self.__checkTargetConsistency(targetSpaID or self.__targetSpaID)
        with self.viewModel.transaction() as model:
            self.__updateIntro(model=model, force=forceShowIntro)
            self.__updateFriends(model=model)
            self.__updateProgression(model=model)
        self.__notifier.startNotification()
        self.__giftsController.requestWebState(GiftEventID.NY_HOLIDAYS)

    def finalize(self):
        self._tooltips.clear()
        self.__removeListeners()
        self.__forcedSending = False
        self.__notifier.stopNotification()
        self.__introLogger.onViewClosed()
        self.__sendButtonLogger.resetMessageChanged()
        super(NyGiftSystemView, self).finalize()

    def clear(self):
        self.__notifier.clear()
        super(NyGiftSystemView, self).clear()

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(NyGiftSystemView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if event.contentID == R.views.lobby.new_year.tooltips.NyPostStampTooltip():
            return NyPostStampTooltip()
        return NyBroTokenTooltip() if event.contentID == R.views.lobby.new_year.tooltips.NyBroTokenTooltip() else super(NyGiftSystemView, self).createToolTipContent(event, contentID)

    def _getInfoForHistory(self):
        return {}

    def _goToCelebrityView(self, *args, **kwargs):
        super(NyGiftSystemView, self)._goToCelebrityView(*args, **kwargs)
        NyCelebrityButtonLogger().logClickInGiftSystem()
        NyGiftSystemFlowLogger().logCelebrityClick()

    def _onGiftHubUpdate(self, reason, extraInfo=None):
        if reason == HubUpdateReason.OUTCOME_GIFT:
            self.__checkSendingComplete(extraInfo)
        elif reason == HubUpdateReason.INCOME_GIFT:
            self.__updateSubmission()
        elif reason == HubUpdateReason.STAMPER_UPDATE:
            self.__updateState()
            self.viewModel.submissionForm.setState(self.__getSubmissionState())
        elif reason == HubUpdateReason.KEEPER_CLEAR:
            self.__updateSubmission()
        elif reason == HubUpdateReason.HISTORY:
            self.__giftsController.requestWebState(GiftEventID.NY_HOLIDAYS)
        elif reason == HubUpdateReason.WEB_STATE:
            self.__checkTargetConsistency(self.__targetSpaID)
            self.__updateSubmission()

    def __addListeners(self):
        self.catchGiftEventHub()
        viewModel = self.viewModel
        viewModel.onIntroClose += self.__onCloseIntro
        viewModel.onQuestsBtnClick += _showDailyQuestsTab
        viewModel.onCelebrityBtnClick += self._goToCelebrityView
        viewModel.giftsProgression.onStylePreviewShow += self.__onPreviewStyleShow
        submission = viewModel.submissionForm
        submission.onRollCongrats += self.__onRollCongratsText
        submission.onSelectFriend += self.__onSelectFriend
        submission.onSendAnimationEnd += self.__onSendAnimationEnd
        submission.onSendGift += self.__onSendGift
        NewYearNavigation.onUpdateCurrentView += self.__onUpdateView
        g_messengerEvents.users.onUserActionReceived += self.__onUserActionReceived
        g_messengerEvents.users.onUsersListReceived += self.__onUsersListReceived
        self.__eventsCache.onSyncCompleted += self.__updateProgression

    def __removeListeners(self):
        self.releaseGiftEventHub()
        viewModel = self.viewModel
        viewModel.onIntroClose -= self.__onCloseIntro
        viewModel.onQuestsBtnClick -= _showDailyQuestsTab
        viewModel.onCelebrityBtnClick -= self._goToCelebrityView
        viewModel.giftsProgression.onStylePreviewShow -= self.__onPreviewStyleShow
        submission = viewModel.submissionForm
        submission.onRollCongrats -= self.__onRollCongratsText
        submission.onSelectFriend -= self.__onSelectFriend
        submission.onSendAnimationEnd -= self.__onSendAnimationEnd
        submission.onSendGift -= self.__onSendGift
        NewYearNavigation.onUpdateCurrentView -= self.__onUpdateView
        g_messengerEvents.users.onUserActionReceived -= self.__onUserActionReceived
        g_messengerEvents.users.onUsersListReceived -= self.__onUsersListReceived
        self.__eventsCache.onSyncCompleted -= self.__updateProgression

    def __getFriendsList(self):
        return self.usersStorage.getList(AnySubFindCriteria())

    def __getSubmissionState(self):
        resultState = SubmissionState.NONE
        if self.__forcedSending:
            resultState = SubmissionState.GIFT_SENDING
        elif self._eventHub.getGifter().getActiveRequest() is not None:
            resultState = SubmissionState.PREV_GIFT_SENDING
        elif not self._eventHub.isWebStateReceived():
            resultState = SubmissionState.LIMITS_LOADING
        elif not self._eventHub.getStamper().isBalanceAvailable():
            resultState = SubmissionState.BALANCE_UNAVAILABLE
        elif self.__targetSpaID != _NOT_SELECTED_SPA_ID:
            user = self.usersStorage.getUser(self.__targetSpaID) or _DEFAULT_SELECTED_USER
            resultState = SubmissionState.NO_LONGER_FRIEND if not user.isAnySub() else resultState
        return resultState

    def __onCloseIntro(self):
        self.__settingsCore.serverSettings.saveInNewYearStorage({NewYearStorageKeys.GIFT_SYSTEM_INTRO_VISITED: True})
        self.viewModel.setIsIntroOpened(False)
        self.__introLogger.onViewClosed()

    def __onPreviewStyleShow(self, args):
        backCallback = _ShowGiftSystemCallback()
        NewYearNavigation.switchTo(None, True)
        styleItem = self.__itemsCache.items.getItemByCD(int(args['styleID']))
        showStylePreview(getVehiclePreviewID(styleItem), styleItem, styleItem.getDescription(), backCallback=backCallback, backBtnDescrLabel=backport.text(R.strings.ny.giftSystem.backLabel()))
        return

    def __onRollCongratsText(self):
        self.__messageID = getGiftSystemRandomCongratulationID(self.__messageID)
        self.__invalidateSelectedCongrats(self.viewModel.submissionForm)
        self.__sendButtonLogger.onMessageChanged()

    @hasGiftEventHub
    @replaceNoneKwargsModel
    def __onSelectFriend(self, args, model=None):
        self.__checkTargetConsistency(int(args['spaID']))
        submissionState = self.__getSubmissionState()
        model.submissionForm.setState(submissionState)
        self.__invalidateSelectedFriend(model.submissionForm.selectedFriend, submissionState)

    @hasGiftEventHub
    def __onSendAnimationEnd(self):
        self.__forcedSending = False
        self.__checkSendingComplete()

    @hasGiftEventHub
    def __onSendGift(self):
        submissionState = self.__getSubmissionState()
        if submissionState in _LOCKED_STATES:
            return
        else:
            gifter = self._eventHub.getGifter()
            restriction = gifter.getRequestRestriction()
            if restriction is not None:
                defaultErrorRes = R.strings.ny.giftSystem.notification.error.defaultSending
                restrictErrorRes = R.strings.ny.giftSystem.notification.error.dyn(restriction.value, defaultErrorRes)
                SystemMessages.pushMessage(backport.text(restrictErrorRes()), type=SystemMessages.SM_TYPE.GiftSystemError)
                return
            self.__forcedSending = True
            self.__sendButtonLogger.logClick()
            self.__sendButtonLogger.resetMessageChanged()
            self.viewModel.submissionForm.setState(SubmissionState.GIFT_SENDING)
            gifter.sendGift(NY_STAMP_CODE, self.__targetSpaID, {'message_id': self.__messageID})(None)
            return

    def __onUpdateView(self, *_, **kwargs):
        spaID = kwargs.get('targetSpaID')
        if spaID is not None:
            self.__onSelectFriend({'spaID': spaID})
        return

    def __onUserActionReceived(self, actionID, *_):
        if actionID in (_ACTION_ID.FRIEND_ADDED, _ACTION_ID.FRIEND_REMOVED, _ACTION_ID.SUBSCRIPTION_CHANGED):
            self.__updateFriends()

    def __onUsersListReceived(self, tags):
        if USER_TAG.FRIEND in tags:
            self.__updateFriends()

    def __buildFriend(self, friend, friendModel=None):
        friendModel = friendModel or FriendModel()
        friendModel.setSpaID(friend.getID())
        friendModel.setName(friend.getName())
        friendModel.setClanAbbrev(friend.getClanAbbrev())
        return friendModel

    def __buildProgressionStage(self, packer, progressQuest, progressTokensRemains, prevStageTokensRequiered):
        maxCoinsCount = getGiftsTokensCountByID(progressQuest.getID()) - prevStageTokensRequiered
        currentCoinsCount = math_utils.clamp(0, maxCoinsCount, progressTokensRemains)
        stage = ProgressionStageModel()
        stage.setMaxCoinsCount(maxCoinsCount)
        stage.setCurrentCoinsCount(currentCoinsCount)
        stageBonuses, stageRewardsModels = progressQuest.getBonuses(), stage.getRewards()
        packBonusModelAndTooltipData(stageBonuses, stageRewardsModels, packer, self._tooltips)
        stageRewardsModels.invalidate()
        self.__invalidateStylesModel(stageRewardsModels, stage.getStyleIDs())
        return stage

    def __checkSendingComplete(self, webResponse=None):
        if webResponse is not None:
            self.__processSendResponse(webResponse)
        submissionState = self.__getSubmissionState()
        if submissionState in (SubmissionState.GIFT_SENDING, SubmissionState.PREV_GIFT_SENDING):
            return
        else:
            self.__updateFriends()
            return

    @hasGiftEventHub
    def __checkTargetConsistency(self, targetSpaID):
        user = self.usersStorage.getUser(targetSpaID)
        eventHub = self.getGiftEventHub()
        ifConsistentTarget = user and user.isAnySub() and not eventHub.getKeeper().isFullfilled(user.getID())
        self.__targetSpaID = user.getID() if ifConsistentTarget else _NOT_SELECTED_SPA_ID

    @hasGiftEventHub
    def __invalidateFriends(self, waiting, fullfilled, friends):
        waiting.clear()
        fullfilled.clear()
        income = self._eventHub.getKeeper().getIncomeRelations()
        outcome = self._eventHub.getKeeper().getOutcomeRelations()
        for friend in sorted(friends, key=lambda f: f.getName()):
            friendID = friend.getID()
            friendModel = self.__buildFriend(friend, FriendModel())
            friendModel.setIsGiftReceived(friendID in income and income[friendID])
            (fullfilled if friendID in outcome and outcome[friendID] else waiting).addViewModel(friendModel)

        fullfilled.invalidate()
        waiting.invalidate()

    def __invalidateProgressionStages(self, stages, progressQuests, progressTokensCount):
        stages.clear()
        prevStageRequiredAmount = 0
        packer = getNewYearBonusPacker()
        for quest in sorted(progressQuests.itervalues(), key=lambda q: q.getID()):
            stageModel = self.__buildProgressionStage(packer, quest, progressTokensCount, prevStageRequiredAmount)
            prevStageRequiredAmount = getGiftsTokensCountByID(quest.getID())
            progressTokensCount -= stageModel.getCurrentCoinsCount()
            stages.addViewModel(stageModel)

        stages.invalidate()

    @hasGiftEventHub
    def __invalidateSelectedCongrats(self, submission, submissionState=None):
        gifterCtx = self._eventHub.getGifter().getActiveRequest()
        submissionState = submissionState or self.__getSubmissionState()
        if submissionState in _LOCKED_STATES and gifterCtx is None:
            return
        else:
            messageID = gifterCtx.getMetaInfo()['message_id'] if gifterCtx else self.__messageID
            submission.setCongratsText(getGiftSystemCongratulationResource(messageID)())
            return

    @hasGiftEventHub
    def __invalidateSelectedFriend(self, selectedFriend, submissionState=None):
        gifterCtx = self._eventHub.getGifter().getActiveRequest()
        submissionState = submissionState or self.__getSubmissionState()
        if submissionState in _LOCKED_STATES and gifterCtx is None:
            return
        else:
            selectedUser = self.usersStorage.getUser(gifterCtx.getReceiverID() if gifterCtx else self.__targetSpaID)
            selectedUser, income = selectedUser or _DEFAULT_SELECTED_USER, self._eventHub.getKeeper().getIncomeRelations()
            selectedFriend.setIsGiftReceived(selectedUser.getID() in income and income[selectedUser.getID()])
            self.__buildFriend(selectedUser, selectedFriend)
            return

    def __invalidateStylesModel(self, stageRewardsModels, styleIDs):
        for rewardModel in stageRewardsModels:
            tooltipData = self._tooltips.get(rewardModel.getTooltipId())
            if tooltipData is None or not tooltipData.specialArgs:
                styleIDs.addNumber(0)
                continue
            possibleStyle = self.__itemsCache.items.getItemByCD(tooltipData.specialArgs[0])
            if possibleStyle is None or possibleStyle.itemTypeID != GUI_ITEM_TYPE.STYLE:
                styleIDs.addNumber(0)
                continue
            styleIDs.addNumber(possibleStyle.intCD)

        styleIDs.invalidate()
        return

    def __processSendResponse(self, webResponse):
        isSuccess = webResponse.state == GifterResponseState.WEB_SUCCESS
        receiverID, messageID = webResponse.receiverID, webResponse.meta['message_id']
        currentTarget = _NOT_SELECTED_SPA_ID if self.__targetSpaID == receiverID else self.__targetSpaID
        self.__messageID = getGiftSystemRandomCongratulationID(messageID) if isSuccess else messageID
        self.__targetSpaID = currentTarget if isSuccess else receiverID

    @replaceNoneKwargsModel
    def __updateIntro(self, model=None, force=False):
        isIntroVisited = self.__settingsCore.serverSettings.getNewYearStorage().get(NewYearStorageKeys.GIFT_SYSTEM_INTRO_VISITED, False)
        showIntro = not isIntroVisited or force
        model.setIsIntroOpened(showIntro)
        if showIntro:
            self.__introLogger.onViewOpened()

    @replaceNoneKwargsModel
    def __updateProgression(self, model=None):
        tokens = self.__itemsCache.items.tokens
        progressQuests = self.__eventsCache.getHiddenQuests(giftsPogressQuestFilter)
        progressTokensCount = tokens.getTokenCount(NY_GIFT_SYSTEM_PROGRESSION_TOKEN)
        subprogressTokensCount = tokens.getTokenCount(NY_GIFT_SYSTEM_SUBPROGRESS_TOKEN)
        subprogressQuests = self.__eventsCache.getHiddenQuests(giftsSubprogressQuestFilter)
        subprogressQuest = subprogressQuests.itervalues().next() if subprogressQuests else None
        self._tooltips.clear()
        progression = model.giftsProgression
        progression.setCurrentGiftsCount(subprogressTokensCount)
        progression.setMaxGiftsCount(getGiftsTokensCountByID(subprogressQuest.getID()) if subprogressQuest else 0)
        self.__invalidateProgressionStages(progression.getStages(), progressQuests, progressTokensCount)
        self.__updateProgressionTimer(model=model)
        return

    @replaceNoneKwargsModel
    def __updateProgressionTimer(self, model=None):
        model.giftsProgression.setResetDelta(getDayTimeLeft())

    @hasGiftEventHub
    @replaceNoneKwargsModel
    def __updateState(self, model=None, friends=None):
        stamper = self._eventHub.getStamper()
        stampsCount = stamper.getStampCount(NY_STAMP_CODE)
        friends = friends if friends is not None else self.__getFriendsList()
        state = State.NORMAL
        if not stamper.wasBalanceAvailable():
            state = State.NO_BALANCE
        elif stampsCount == 0:
            state = State.NO_POST_STAMPS
        elif not friends:
            state = State.NO_FRIENDS
        model.setState(State.NORMAL if self.__forcedSending else state)
        model.setPostStampsCount(stampsCount)
        return

    @hasGiftEventHub
    @replaceNoneKwargsModel
    def __updateSubmission(self, model=None, friends=None, submissionState=None):
        submissionState = submissionState or self.__getSubmissionState()
        submission = model.submissionForm
        submission.setState(submissionState)
        friends = friends if friends is not None else self.__getFriendsList()
        self.__invalidateFriends(submission.getWaitingFriends(), submission.getFullfilledFriends(), friends)
        self.__invalidateSelectedFriend(submission.selectedFriend, submissionState)
        self.__invalidateSelectedCongrats(submission, submissionState)
        return

    @replaceNoneKwargsModel
    def __updateFriends(self, model=None):
        friends = self.__getFriendsList()
        self.__updateState(model=model, friends=friends)
        self.__updateSubmission(model=model, friends=friends)
