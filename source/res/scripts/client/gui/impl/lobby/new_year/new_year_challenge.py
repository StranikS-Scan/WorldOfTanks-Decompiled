# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/new_year_challenge.py
import logging
import typing
from BWUtil import AsyncReturn
from messenger.proto.events import g_messengerEvents
from shared_utils import findFirst, first
import adisp
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_CELEBRITY_COMPLETED_QUESTS_ANIMATION_SHOWN_MASK, NY_CELEBRITY_QUESTS_VISITED_MASK, NY_CELEBRITY_QUESTS_COMPLETED_MASK
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from async import async, await
from constants import CURRENT_REALM
from gui import SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.missions.cards_formatters import MissionBonusAndPostBattleCondFormatter
from gui.Scaleform.framework.managers.view_lifecycle_watcher import ViewLifecycleWatcher
from gui.Scaleform.genConsts.MISSIONS_ALIASES import MISSIONS_ALIASES
from gui.impl import backport
from gui.impl.backport.backport_pop_over import createPopOverData, BackportPopOverContent
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.builders import NYInfoDialogBuilder
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.discount_bonus_model import DiscountBonusModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_model import NewYearChallengeModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_progress_model import NewYearChallengeProgressModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_quest_model import NewYearQuestModel
from gui.impl.lobby.new_year import DiscountPopoverHandler
from gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from gui.impl.lobby.new_year.tooltips.ny_vehicle_slot_tooltip import NyVehicleSlotTooltip
from gui.impl.new_year.navigation import NewYearNavigation, ViewAliases
from gui.impl.new_year.new_year_bonus_packer import getNewYearBonusPacker, packBonusModelAndTooltipData, getChallengeBonusPacker
from gui.impl.new_year.new_year_helper import backportTooltipDecorator, nyCreateToolTipContentDecorator
from gui.impl.new_year.sounds import NewYearSoundEvents, NewYearSoundsManager
from gui.impl.wrappers.user_format_string_arg_model import UserFormatStringArgModel as FmtArgs
from gui.shared import event_dispatcher, events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showStylePreview
from gui.shared.formatters import icons, text_styles
from gui.shared.lock_overlays import lockNotificationManager
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency, time_utils, uniprof
from items.components.ny_constants import CelebrityQuestLevels, CelebrityQuestTokenParts
from new_year.celebrity.celebrity_quests_helpers import getCelebrityQuestSimplificationCost, marathonTokenCountExtractor
from new_year.ny_constants import SyncDataKeys, AdditionalCameraObject, NyWidgetTopMenu
from new_year.ny_preview import getVehiclePreviewID
from new_year.ny_processor import SimplifyCelebrityQuestProcessor, isCelebrityQuestsSimplificationLocked
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import ICelebritySceneController
if typing.TYPE_CHECKING:
    from typing import Callable, Dict, Iterable, List, Optional, Tuple
    from gui.server_events.event_items import CelebrityQuest
_logger = logging.getLogger(__name__)
_MAX_SIMPLIFICATION_QUANTITY = 1
_QuestsParams = typing.NamedTuple('_QuestsParams', (('iconKey', str),
 ('isCumulative', bool),
 ('condCurrent', int),
 ('condTotal', int),
 ('levelConds', dict)))

def _parseFormattedArg(fmtArg):
    return int(filter(str.isdigit, fmtArg)) if isinstance(fmtArg, str) else fmtArg


class NewYearChallenge(HistorySubModelPresenter):
    _navigationAlias = ViewAliases.CELEBRITY_VIEW
    __itemsCache = dependency.descriptor(IItemsCache)
    __celebrityController = dependency.descriptor(ICelebritySceneController)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, viewModel, parentView, *args, **kwargs):
        super(NewYearChallenge, self).__init__(viewModel, parentView, *args, **kwargs)
        self._dayToQuest = {}
        self._tooltips = {}
        self._marathonQuests = []
        self.__viewLifecycleWatcher = ViewLifecycleWatcher()
        self.__blur = CachedBlur()
        self.__condFormatter = _ChallengeCondFormatter()
        self.__isOverlaysLocked = False
        self.__isChallengeCompleted = False
        self.__fullCompletedQuests = 0

    @property
    def viewModel(self):
        return self.getViewModel()

    @nyCreateToolTipContentDecorator
    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.NyVehicleSlotTooltip():
            tooltipData = self._tooltips.get(event.getArgument('tooltipId'))
            if tooltipData is None:
                return
            return NyVehicleSlotTooltip(*tooltipData.specialArgs)
        else:
            return super(NewYearChallenge, self).createToolTipContent(event, contentID)

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(NewYearChallenge, self).createToolTip(event)

    def createPopOverContent(self, event):
        if event.contentID == R.views.common.pop_over_window.backport_pop_over.BackportPopOverContent():
            if event.getArgument('popoverId') == DiscountBonusModel.NEW_YEAR_DISCOUNT_APPLY_POPOVER_ID:
                alias = VIEW_ALIAS.NY_SELECT_VEHICLE_FOR_DISCOUNT_POPOVER
                variadicID = event.getArgument('variadicID')
                data = createPopOverData(alias, {'variadicID': variadicID})
                return BackportPopOverContent(popOverData=data)
        return super(NewYearChallenge, self).createPopOverContent(event)

    def preLoad(self, *args, **kwargs):
        completedQuestsMask = AccountSettings.getUIFlag(NY_CELEBRITY_QUESTS_COMPLETED_MASK)
        completedQuestsAnimation = AccountSettings.getUIFlag(NY_CELEBRITY_COMPLETED_QUESTS_ANIMATION_SHOWN_MASK)
        self.__fullCompletedQuests = completedQuestsMask & completedQuestsAnimation
        self.__celebrityController.onEnterChallenge()
        self._marathonQuests = self.__celebrityController.marathonQuests.values()
        self._marathonQuests.sort(key=marathonTokenCountExtractor)
        super(NewYearChallenge, self).preLoad(*args, **kwargs)

    @uniprof.regionDecorator(label='ny.celebrity', scope='enter')
    def initialize(self, *args, **kwargs):
        super(NewYearChallenge, self).initialize()
        self.__isChallengeCompleted = self.__celebrityController.isChallengeCompleted
        with self.viewModel.transaction() as tx:
            self.__setDisplayIntro(tx, skipIntro=kwargs.get('skipIntro', False))
            self.__updateState(tx)
            tx.setRealm(CURRENT_REALM)
            self.viewModel.setIsAllQuestsVisible(False)
        self.__startLifeCycleWatcher()

    @uniprof.regionDecorator(label='ny.celebrity', scope='exit')
    def finalize(self):
        self.__stopLifeCycleWatcher()
        self._tooltips.clear()
        self._dayToQuest.clear()
        self.__lockOverlaysAndNotifications(False)
        if self.viewModel.getIsDisplayIntro():
            NewYearSoundsManager.playEvent(NewYearSoundEvents.CELEBRITY_INTRO_EXIT)
        self.__celebrityController.onExitChallenge()
        self.__toggleBlur(True)
        super(NewYearChallenge, self).finalize()

    def clear(self):
        if self.__blur is not None:
            self.__blur.fini()
            self.__blur = None
        super(NewYearChallenge, self).clear()
        return

    def _getInfoForHistory(self):
        return {}

    def _getCallbacks(self):
        return (('cache.vehsLock', self.__onLocksUpdate),)

    def _getListeners(self):
        return ((events.NewYearEvent.ON_PRE_SWITCH_VIEW, self.__onPreSwitchViewEvent, EVENT_BUS_SCOPE.LOBBY),)

    def _getEvents(self):
        return ((self.viewModel.onLeaveIntroScreen, self.__onLeaveIntroScreen),
         (self.viewModel.onOpenIntroScreen, self.__onOpenIntroScreen),
         (self.viewModel.onUpdateTimeTill, self.__onUpdateTimeTill),
         (self.viewModel.onChangeAllQuestsVisibility, self.__onChangeAllQuestsVisibility),
         (self.viewModel.onSimplify, self.__onSimplify),
         (self.viewModel.onVisited, self.__onVisited),
         (self.viewModel.onCompletedAnimationShown, self.__onCompletedAnimationShown),
         (self.viewModel.onSimplificationAnimationEnd, self.__onSimplificationAnimationEnd),
         (self.viewModel.onStylePreviewShow, self.__onStylePreviewShow),
         (self.__celebrityController.onQuestsUpdated, self.__onQuestsUpdated),
         (self._nyController.onDataUpdated, self.__onDataUpdated))

    def __startLifeCycleWatcher(self):
        self.__viewLifecycleWatcher.start(dependency.instance(IAppLoader).getApp().containerManager, [DiscountPopoverHandler(self.__onDiscountPopoverOpened, self.__onDiscountPopoverClosed)])

    def __stopLifeCycleWatcher(self):
        self.__viewLifecycleWatcher.stop()

    def __updateState(self, model):
        if self.__isChallengeCompleted:
            self.__setChallengeCompleted(model)
        else:
            self.__setChallengeInProgress(model)

    def __setChallengeCompleted(self, model):
        model.setIsChallengeCompleted(True)
        bonuses = []
        for quest in self._marathonQuests:
            bonuses.extend(quest.getBonuses())

        rewardsList = model.getFinalRewards()
        rewardsList.clear()
        packBonusModelAndTooltipData(bonuses, rewardsList, getNewYearBonusPacker(), self._tooltips)
        rewardsList.invalidate()
        self.__triggerSyncInitiator()

    def __setChallengeInProgress(self, model):
        model.setIsChallengeCompleted(False)
        self.__setQuestsInfo()
        model.setMaxQuestsQuantity(self.__celebrityController.questsCount)
        model.setQuestsCompleted(self.__celebrityController.completedQuestsCount)
        questsQuantityBeforeReward = 0
        for mq in reversed(self._marathonQuests):
            if findFirst(lambda bonus: bonus.getName() == 'tmanToken', mq.getBonuses()) is not None:
                questsQuantityBeforeReward = marathonTokenCountExtractor(mq)
                break

        model.setQuestsQuantityBeforeReward(questsQuantityBeforeReward)
        if not questsQuantityBeforeReward:
            _logger.error("Couldn't find a marathon quest with a tankman")
        model.setMaxSimplificationQuantity(_MAX_SIMPLIFICATION_QUANTITY)
        model.setTimeTill(time_utils.getDayTimeLeft())
        self.__triggerSyncInitiator()
        self.__setMarathonProgress()
        return

    def __setDisplayIntro(self, model, skipIntro=False):
        if skipIntro:
            self.__settingsCore.serverSettings.saveInNewYearStorage({NewYearStorageKeys.CELEBRITY_CHALLENGE_VISITED: True})
        isChallengeVisited = self.__celebrityController.isChallengeVisited
        model.setIsDisplayIntro(not isChallengeVisited)
        model.setIsChallengeVisited(isChallengeVisited)

    def __triggerSyncInitiator(self):
        self.viewModel.setSyncInitiator((self.viewModel.getSyncInitiator() + 1) % 1000)

    def __setMarathonProgress(self):
        with self.viewModel.transaction() as tx:
            rewards = tx.getProgressRewards()
            rewards.clear()
            for quest in self._marathonQuests:
                model = NewYearChallengeProgressModel()
                model.setRewardLevel(marathonTokenCountExtractor(quest))
                packBonusModelAndTooltipData(quest.getBonuses(), model.getRewards(), getChallengeBonusPacker(), self._tooltips)
                bonus = findFirst(lambda b: b.getName() == 'customizations', model.getRewards())
                if bonus and bonus.getIcon() == 'style':
                    model.setStyleRewardIdx(bonus.getIndex())
                rewards.addViewModel(model)

            rewards.invalidate()

    def __setQuestsInfo(self):
        visitedQuestsMask = AccountSettings.getUIFlag(NY_CELEBRITY_QUESTS_VISITED_MASK)
        completedQuestsAnimation = AccountSettings.getUIFlag(NY_CELEBRITY_COMPLETED_QUESTS_ANIMATION_SHOWN_MASK)
        bonusPacker = getNewYearBonusPacker()
        with self.viewModel.transaction() as tx:
            self.__setSimplificationsLock()
            quests = tx.getQuests()
            quests.clear()
            for dayNum, activeQuest, regularQuests, bonuses in self.__iterQuests():
                if activeQuest is None:
                    continue
                dayNumMask = 1 << dayNum - 1
                if bool(self.__fullCompletedQuests & dayNumMask):
                    continue
                model = NewYearQuestModel()
                model.setId(dayNum)
                self._dayToQuest[dayNum] = activeQuest
                params = self.__parseQuestsParams(activeQuest, regularQuests)
                model.setIsCompleted(activeQuest.isCompleted())
                model.setCurrentProgress(params.condCurrent)
                model.setFinalProgress(params.condTotal)
                model.setIsCumulative(params.isCumulative)
                model.setIcon(params.iconKey)
                model.setDescription(activeQuest.getDescription())
                model.setGoalValue(params.levelConds[activeQuest.level])
                model.setLevel(activeQuest.level)
                self.__setSimplification(model, params, activeQuest, regularQuests)
                for bonus in bonuses:
                    for bonusModel in bonusPacker.pack(bonus):
                        model.reward.addViewModel(bonusModel)

                model.setIsVisited(bool(visitedQuestsMask & dayNumMask))
                model.setIsCompletedAnimationShown(bool(completedQuestsAnimation & dayNumMask))
                quests.addViewModel(model)

            quests.invalidate()
        return

    def __setSimplification(self, model, questsParams, activeQuest, regularQuests):
        simplification = model.simplification
        quest = findFirst(lambda q: q.level == CelebrityQuestLevels.EASY, regularQuests)
        if quest is None:
            return
        else:
            simplification.setIcon(questsParams.iconKey)
            simplification.setGoalValue(questsParams.levelConds[CelebrityQuestLevels.EASY])
            simplification.setLevel(CelebrityQuestLevels.EASY)
            price = getCelebrityQuestSimplificationCost(activeQuest, CelebrityQuestLevels.EASY)
            if price is not None:
                simplification.setPrice(price)
                simplification.setInsufficientFunds(self.__itemsCache.items.festivity.getShardsCount() < price)
            return

    def __setSimplificationsLock(self):
        self.viewModel.setVehicleInBattle(isCelebrityQuestsSimplificationLocked())

    def __iterQuests(self):
        tokens = self.__celebrityController.tokens
        return sorted(((CelebrityQuestTokenParts.getDayNum(questId),
         group.getActiveQuest(tokens),
         group.regularQuests,
         group.bonusQuest.getBonuses()) for questId, group in self.__celebrityController.questGroups.items() if group.isValid))

    def __parseQuestsParams(self, activeQuest, regularQuests):
        levelConditions = {}
        diffIdx = activeQuestCurrent = activeQuestTotal = 0
        currConditions = first(self.__condFormatter.format(activeQuest))
        allConditions = {quest:first(self.__condFormatter.format(quest)) for quest in regularQuests}
        for conditions in (c for q, c in allConditions.iteritems() if q != activeQuest):
            for index, (condition, currCondition) in enumerate(zip(conditions, currConditions)):
                if condition != currCondition:
                    diffIdx = index
                    break

        isCurrCumulative = currConditions[diffIdx].progressType == MISSIONS_ALIASES.CUMULATIVE
        for quest, conditions in allConditions.iteritems():
            if isCurrCumulative:
                levelCondition = conditions[diffIdx].total
            else:
                levelCondition = _parseFormattedArg(conditions[diffIdx].titleData.args[0])
            levelConditions[quest.level] = levelCondition

        anyCumulative = findFirst(lambda c: c.progressType == MISSIONS_ALIASES.CUMULATIVE, currConditions)
        if anyCumulative is not None:
            activeQuestCurrent, activeQuestTotal = anyCumulative.current, anyCumulative.total
        iconKey = currConditions[diffIdx].iconKey
        if iconKey == 'battles' and len(currConditions) == 2 and any((c.iconKey == 'win' for c in currConditions)):
            iconKey = 'win'
        return _QuestsParams(iconKey, anyCumulative is not None, activeQuestCurrent, activeQuestTotal, levelConditions)

    def __toggleBlur(self, forceDisable=False):
        if self.viewModel.getIsAllQuestsVisible() and not forceDisable:
            self.__blur.enable()
        else:
            self.__blur.disable()

    def __onLeaveIntroScreen(self):
        self.viewModel.setIsDisplayIntro(False)
        self.__toggleBlur()
        self.__settingsCore.serverSettings.saveInNewYearStorage({NewYearStorageKeys.CELEBRITY_CHALLENGE_VISITED: True})
        NewYearSoundsManager.playEvent(NewYearSoundEvents.CELEBRITY_INTRO_EXIT)
        if not self.viewModel.getIsChallengeVisited():
            self.viewModel.setIsChallengeVisited(True)

    def __onOpenIntroScreen(self):
        self.__toggleBlur(True)
        NewYearSoundsManager.playEvent(NewYearSoundEvents.CELEBRITY_INTRO)
        self.viewModel.setIsDisplayIntro(True)

    def __onUpdateTimeTill(self):
        self.viewModel.setTimeTill(time_utils.getDayTimeLeft())

    def __onChangeAllQuestsVisibility(self):
        self.viewModel.setIsAllQuestsVisible(not self.viewModel.getIsAllQuestsVisible())
        self.__toggleBlur()

    def __onPreSwitchViewEvent(self, event):
        if event.ctx.menuName != NyWidgetTopMenu.CHALLENGE and self.viewModel.getIsAllQuestsVisible():
            self.__toggleBlur(True)

    def __onStylePreviewShow(self, args):
        rewardLevel = int(args['rewardLevel'])
        styleIdx = int(args['styleIdx'])
        rewardModel = findFirst(lambda m: m.getRewardLevel() == rewardLevel, self.viewModel.getProgressRewards())
        if rewardModel is None:
            return
        else:
            bonusModel = rewardModel.getRewards().getValue(styleIdx)
            tooltipData = self._tooltips.get(bonusModel.getTooltipId())
            if tooltipData is None or not tooltipData.specialArgs:
                return
            styleItem = self.__itemsCache.items.getItemByCD(tooltipData.specialArgs[0])

            def _backCallback():
                if not self._nyController.isEnabled():
                    event_dispatcher.showHangar()
                else:
                    NewYearNavigation.switchFromStyle(AdditionalCameraObject.CELEBRITY, viewAlias=ViewAliases.CELEBRITY_VIEW, forceShowMainView=True)

            NewYearNavigation.switchTo(None, True)
            showStylePreview(getVehiclePreviewID(styleItem), styleItem, styleItem.getDescription(), backCallback=_backCallback, backBtnDescrLabel=backport.text(R.strings.ny.celebrityChallenge.backLabel()))
            return

    def __onSimplify(self, args=None):
        NewYearSoundsManager.playEvent(NewYearSoundEvents.CELEBRITY_CARD_CLICK)
        self.__simplifyQuest(int(args['id']), int(args['level']))

    @async
    def __simplifyQuest(self, qId, level):
        quest = self._dayToQuest[qId]
        if quest is None:
            return
        else:
            cost = getCelebrityQuestSimplificationCost(quest, level)
            confirmed = yield await(self.__simplifyConfirmator(cost))
            if confirmed:
                self.__lockOverlaysAndNotifications(True)
                self.__requestSimplification(quest, level, cost)
            return

    @async
    def __simplifyConfirmator(self, price):
        formattedCount = '{}{}'.format(text_styles.superPromoTitle(backport.getIntegralFormat(price)), icons.makeImageTag(backport.image(R.images.gui.maps.icons.newYear.shards.c_24x24()), width=24, height=24, vSpace=-1))
        builder = NYInfoDialogBuilder()
        builder.setMessagesAndButtons(R.strings.ny.confirmSimplification, buttons=R.strings.ny.confirmSimplification)
        builder.setMessageArgs(fmtArgs=[FmtArgs(formattedCount, 'count', R.styles.SuperPromoTitleTextStyle())])
        builder.setShowBalance(True)
        result = yield await(dialogs.showSimple(builder.build(self)))
        raise AsyncReturn(result)

    @adisp.process
    def __requestSimplification(self, quest, level, price):
        result = yield SimplifyCelebrityQuestProcessor(quest.getID(), level).request()
        if result and result.success:
            self.__celebrityController.onSimplifyQuest()
            SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.newYear.celebrityChallenge.simplification.message(), value=price), type=SystemMessages.SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': backport.text(R.strings.system_messages.newYear.celebrityChallenge.simplification.title())})
        else:
            self.__lockOverlaysAndNotifications(False)

    def __onVisited(self, args=None):
        self.__maskQuestAction(args, NY_CELEBRITY_QUESTS_VISITED_MASK, lambda qModel, value: qModel.setIsVisited(value))

    def __onCompletedAnimationShown(self, args):
        self.__maskQuestAction(args, NY_CELEBRITY_COMPLETED_QUESTS_ANIMATION_SHOWN_MASK, lambda qModel, value: qModel.setIsCompletedAnimationShown(value))

    def __maskQuestAction(self, args, maskName, modelSetFunc):
        questId = int(args.get('id'))
        questsMask = AccountSettings.getUIFlag(maskName)
        dayNumMask = 1 << questId - 1
        questsMask |= dayNumMask
        with self.viewModel.transaction() as tx:
            quests = tx.getQuests()
            questModel = findFirst(lambda q: q.getId() == questId, quests, None)
            if questModel is not None:
                modelSetFunc(questModel, True)
                quests.invalidate()
                self.__triggerSyncInitiator()
        AccountSettings.setUIFlag(maskName, questsMask)
        return

    def __onSimplificationAnimationEnd(self):
        self.__lockOverlaysAndNotifications(False)

    def __lockOverlaysAndNotifications(self, lock):
        if lock != self.__isOverlaysLocked:
            self.__isOverlaysLocked = lock
            lockNotificationManager(lock, releasePostponed=not lock)
            if lock:
                g_messengerEvents.onLockPopUpMessages(key=self.__class__.__name__, lockHigh=True)
            else:
                g_messengerEvents.onUnlockPopUpMessages(key=self.__class__.__name__)

    def __onDiscountPopoverOpened(self):
        self.viewModel.setIsDiscountPopoverOpened(True)

    def __onDiscountPopoverClosed(self):
        self.viewModel.setIsDiscountPopoverOpened(False)

    def __onLocksUpdate(self, *_):
        self.__setSimplificationsLock()

    def __onDataUpdated(self, keys):
        if SyncDataKeys.TOY_FRAGMENTS in keys:
            self.__setQuestsInfo()
            self.__triggerSyncInitiator()

    def __onQuestsUpdated(self):
        with self.viewModel.transaction() as tx:
            self.__updateState(tx)


class _ChallengeCondFormatter(MissionBonusAndPostBattleCondFormatter):

    def _packCondition(self, *args, **kwargs):
        pass

    def _getFormattedField(self, *args, **kwargs):
        pass

    def _packSeparator(self, key):
        pass

    def _packConditions(self, *args, **kwargs):
        pass
