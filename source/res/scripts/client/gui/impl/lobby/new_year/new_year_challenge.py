# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/new_year_challenge.py
import logging
from enum import IntEnum
import typing
import BigWorld
from BWUtil import AsyncReturn
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_CELEBRITY_QUESTS_VISITED_MASK, NY_CELEBRITY_CHALLENGE_VISITED, NY_CELEBRITY_COMPLETED_QUESTS_ANIMATION_SHOWN_MASK
import adisp
from async import await, async
from frameworks.wulf import ViewSettings
from constants import CURRENT_REALM
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.framework.managers.view_lifecycle_watcher import ViewLifecycleWatcher
from gui.impl import backport
from gui.Scaleform.daapi.view.lobby.missions.cards_formatters import MissionBonusAndPostBattleCondFormatter
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.builders import InfoDialogBuilderEx
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_progress_model import NewYearChallengeProgressModel
from gui.impl.lobby.new_year import DiscountPopoverHandler
from gui.impl.new_year.new_year_bonus_packer import getNewYearBonusPacker
from gui.impl.new_year.new_year_helper import backportTooltipDecorator, nyCreateToolTipContentDecorator
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.impl.wrappers.user_format_string_arg_model import UserFormatStringArgModel as FmtArgs
from gui.Scaleform.genConsts.MISSIONS_ALIASES import MISSIONS_ALIASES
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_model import NewYearChallengeModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_quest_model import NewYearQuestModel
from gui.impl.lobby.loot_box.loot_box_bonuses_helpers import packBonusModelAndTooltipData
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.quest_simplification_model import QuestSimplificationModel
from gui.impl.new_year.history_navigation import NewYearHistoryNavigation
from gui.server_events.conditions import BattleResults
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles, icons
from gui.shared.lock_overlays import lockOverlays
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils.functions import getAbsoluteUrl
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import time_utils, dependency, uniprof
from items.components.ny_constants import CelebrityQuestTokenParts, CelebrityQuestLevels
from new_year.celebrity.celebrity_quests_helpers import marathonTokenCountExtractor, getCelebrityQuestSimplificationCost
from new_year.ny_constants import NyWidgetTopMenu, NyTabBarMainView, SyncDataKeys
from new_year.ny_processor import SimplifyCelebrityQuestProcessor, isCelebrityQuestsSimplificationLocked
from shared_utils import findFirst
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared import IItemsCache
from gui.server_events.formatters import getConditionIcon128
from skeletons.new_year import ICelebritySceneController
from soft_exception import SoftException
from uilogging.decorators import loggerTarget, loggerEntry, simpleLog, logOnMatch
from uilogging.ny.constants import NY_LOG_KEYS, NY_LOG_ACTIONS
from uilogging.ny.loggers import NYLogger
if typing.TYPE_CHECKING:
    from gui.server_events.formatters import PreFormattedCondition
    from gui.shared.event_dispatcher import NYTabCtx
_MAX_SIMPLIFICATION_QUANTITY = 2
_logger = logging.getLogger(__name__)

@loggerTarget(logKey=NY_LOG_KEYS.NY_CELEBRITY_CHALLENGE, loggerCls=NYLogger)
class NewYearChallenge(NewYearHistoryNavigation):
    _itemsCache = dependency.descriptor(IItemsCache)
    _celebrityController = dependency.descriptor(ICelebritySceneController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.NewYearChallenge())
        settings.model = NewYearChallengeModel()
        settings.args = args
        settings.kwargs = kwargs
        self._dayToQuest = {}
        self._tooltips = {}
        self.__condFormatter = _ChallengeCondFormatter()
        self.__isOverlaysLocked = False
        self.__isChallengeCompleted = self._celebrityController.isChallengeCompleted
        self.__blur = CachedBlur()
        self.__onEnterChallengeCallbackId = None
        self.__viewLifecycleWatcher = ViewLifecycleWatcher()
        super(NewYearChallenge, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(NewYearChallenge, self).getViewModel()

    @nyCreateToolTipContentDecorator
    def createToolTipContent(self, event, contentID):
        return super(NewYearChallenge, self).createToolTipContent(event, contentID)

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(NewYearChallenge, self).createToolTip(event)

    @loggerEntry
    @uniprof.regionDecorator(label='ny.celebrity', scope='enter')
    def _initialize(self, *args, **kwargs):
        super(NewYearChallenge, self)._initialize()
        self.__onEnterChallenge()
        self.__updateState()
        self.__addListeners()

    def _onLoading(self, *args, **kwargs):
        super(NewYearChallenge, self)._onLoading()
        with self.viewModel.transaction() as model:
            model.setRealm(CURRENT_REALM)

    @uniprof.regionDecorator(label='ny.celebrity', scope='exit')
    def _finalize(self):
        if self.__onEnterChallengeCallbackId is not None:
            BigWorld.cancelCallback(self.__onEnterChallengeCallbackId)
            self.__onEnterChallengeCallbackId = None
        self.__removeListeners()
        self._tooltips.clear()
        self._dayToQuest.clear()
        self.__lockOverlays(False)
        if self.__blur is not None:
            self.__blur.fini()
        if self.viewModel.getIsDisplayIntro():
            NewYearSoundsManager.playEvent(NewYearSoundEvents.CELEBRITY_INTRO_EXIT)
        self._celebrityController.onExitChallenge()
        return

    def _getDisplayIntro(self):
        return not self._celebrityController.isChallengeVisited

    def _getAllQuestsVisible(self):
        return self.viewModel.getIsAllQuestsVisible()

    def __onEnterChallenge(self):
        self.__onEnterChallengeCallbackId = None
        view = self._app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.NY_MAIN_VIEW))
        if view is None:
            _logger.error('Missing NYMainView.')
            return
        else:
            if not view.isViewOpened:
                self.__onEnterChallengeCallbackId = BigWorld.callback(0.1, self.__onEnterChallenge)
            else:
                self._celebrityController.onEnterChallenge()
            return

    def __updateState(self):
        self._marathonQuests = self._celebrityController.marathonQuests.values()
        self._marathonQuests.sort(key=marathonTokenCountExtractor)
        if self.__isChallengeCompleted:
            self.__setChallengeCompleted()
        else:
            self.__setChallengeInProgress(self._celebrityController.completedQuestsCount)

    def __setChallengeCompleted(self):
        with self.viewModel.transaction() as vm:
            vm.setIsChallengeCompleted(True)
            self.__setDisplayIntro(vm)
            bonuses = []
            for quest in self._marathonQuests:
                bonuses.extend(quest.getBonuses())

            rewardsList = vm.getFinalRewards()
            rewardsList.clear()
            packBonusModelAndTooltipData(bonuses, rewardsList, getNewYearBonusPacker(), self._tooltips)
            rewardsList.invalidate()
            self.__triggerSyncInitiator()

    def __setChallengeInProgress(self, completedCount):
        with self.viewModel.transaction() as vm:
            vm.setIsChallengeCompleted(False)
            self.__setDisplayIntro(vm)
            self.__setQuestsInfo()
            vm.setMaxQuestsQuantity(self._celebrityController.questsCount)
            vm.setQuestsCompleted(completedCount)
            questsQuantityBeforeReward = 0
            for mq in reversed(self._marathonQuests):
                if findFirst(lambda bonus: bonus.getName() == 'tmanToken', mq.getBonuses()) is not None:
                    questsQuantityBeforeReward = marathonTokenCountExtractor(mq)
                    break

            vm.setQuestsQuantityBeforeReward(questsQuantityBeforeReward)
            if questsQuantityBeforeReward == 0:
                _logger.error("Couldn't found marathon quest with tankman")
            vm.setMaxSimplificationQuantity(_MAX_SIMPLIFICATION_QUANTITY)
            vm.setTimeTill(time_utils.getDayTimeLeft())
            self.__triggerSyncInitiator()
            self.__setMarathonProgress()
        return

    @logOnMatch(objProperty='_getDisplayIntro', needCall=True, matches={True: NY_LOG_ACTIONS.NY_CELEBRITY_INFO_SCREEN_AUTO_OPEN})
    def __setDisplayIntro(self, model):
        model.setIsDisplayIntro(self._getDisplayIntro())
        model.setIsChallengeVisited(self._celebrityController.isChallengeVisited)

    def __triggerSyncInitiator(self):
        self.viewModel.setSyncInitiator((self.viewModel.getSyncInitiator() + 1) % 1000)

    def __addListeners(self):
        model = self.viewModel
        model.onLeaveIntroScreen += self.__onLeaveIntroScreen
        model.onOpenIntroScreen += self.__onOpenIntroScreen
        model.onUpdateTimeTill += self.__onUpdateTimeTill
        model.onChangeAllQuestsVisibility += self.__onChangeAllQuestsVisibility
        model.onSimplify += self.__onSimplify
        model.onVisited += self.__onVisited
        model.onCompletedAnimationShown += self.__onCompletedAnimationShown
        model.onSimplificationAnimationEnd += self.__onSimplificationAnimationEnd
        g_clientUpdateManager.addCallbacks({'cache.vehsLock': self.__onLocksUpdate})
        g_eventBus.addListener(events.NewYearEvent.ON_SIDEBAR_SELECTED, self.__onSideBarSelected, scope=EVENT_BUS_SCOPE.LOBBY)
        self._celebrityController.onQuestsUpdated += self.__updateState
        self._celebrityController.onExitIntroScreen += self.__onLeaveIntroScreen
        self._nyController.onDataUpdated += self.__onDataUpdated
        appLoader = dependency.instance(IAppLoader)
        app = appLoader.getApp()
        self.__viewLifecycleWatcher.start(app.containerManager, [DiscountPopoverHandler(self.__onDiscountPopoverOpened, self.__onDiscountPopoverClosed)])

    def __removeListeners(self):
        model = self.viewModel
        model.onLeaveIntroScreen -= self.__onLeaveIntroScreen
        model.onUpdateTimeTill -= self.__onUpdateTimeTill
        model.onChangeAllQuestsVisibility -= self.__onChangeAllQuestsVisibility
        model.onSimplify -= self.__onSimplify
        model.onVisited -= self.__onVisited
        model.onCompletedAnimationShown -= self.__onCompletedAnimationShown
        model.onSimplificationAnimationEnd -= self.__onSimplificationAnimationEnd
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_eventBus.removeListener(events.NewYearEvent.ON_SIDEBAR_SELECTED, self.__onSideBarSelected, scope=EVENT_BUS_SCOPE.LOBBY)
        self._celebrityController.onQuestsUpdated -= self.__updateState
        self._celebrityController.onExitIntroScreen -= self.__onLeaveIntroScreen
        self._nyController.onDataUpdated -= self.__onDataUpdated
        self.__viewLifecycleWatcher.stop()

    def __setMarathonProgress(self):
        with self.viewModel.transaction() as vm:
            pr = vm.getProgressRewards()
            pr.clear()
            for q in self._marathonQuests:
                model = NewYearChallengeProgressModel()
                model.setRewardLevel(marathonTokenCountExtractor(q))
                packBonusModelAndTooltipData(q.getBonuses(), model.getRewards(), getNewYearBonusPacker(), self._tooltips)
                pr.addViewModel(model)

            pr.invalidate()

    def __setQuestsInfo(self):
        visitedQuestsMask = AccountSettings.getUIFlag(NY_CELEBRITY_QUESTS_VISITED_MASK)
        completedQuestsAnimation = AccountSettings.getUIFlag(NY_CELEBRITY_COMPLETED_QUESTS_ANIMATION_SHOWN_MASK)
        bonusPacker = getNewYearBonusPacker()
        with self.viewModel.transaction() as vm:
            self.__setSimplificationsLock()
            q = vm.getQuests()
            q.clear()
            for qGroupId, celebrityGroup in sorted(self._celebrityController.questGroups.items(), key=lambda i: CelebrityQuestTokenParts.getDayNum(i[0])):
                if not celebrityGroup.isValid:
                    continue
                model = NewYearQuestModel()
                dayNum = CelebrityQuestTokenParts.getDayNum(qGroupId)
                model.setId(dayNum)
                activeQuest = celebrityGroup.getActiveQuest(self._celebrityController.tokens)
                regularQuests = celebrityGroup.regularQuests
                self._dayToQuest[dayNum] = activeQuest
                if activeQuest is None:
                    continue
                questsParams = self.__parseQuestsChangeableParams(activeQuest, regularQuests)
                model.setIsCompleted(activeQuest.isCompleted())
                model.setCurrentProgress(questsParams.condCurrent)
                model.setFinalProgress(questsParams.condTotal)
                model.setIsCumulative(questsParams.isCumulative)
                model.setIcon(getAbsoluteUrl(getConditionIcon128(questsParams.iconKey)))
                model.setDescription(activeQuest.getDescription())
                model.setGoalValue(questsParams.levelConds[activeQuest.level])
                model.setLevel(activeQuest.level)
                self.__setSimplifications(model.getSimplifications(), questsParams, activeQuest, regularQuests)
                for bonus in celebrityGroup.bonusQuest.getBonuses():
                    for bonusModel in bonusPacker.pack(bonus):
                        model.reward.addViewModel(bonusModel)

                dayNumMask = 1 << dayNum - 1
                model.setIsVisited(bool(visitedQuestsMask & dayNumMask))
                model.setIsCompletedAnimationShown(bool(completedQuestsAnimation & dayNumMask))
                q.addViewModel(model)

            q.invalidate()
        return

    def __setSimplifications(self, simplificationsModel, questsParams, activeQuest, regularQuests):
        with self.viewModel.transaction():
            simplificationsModel.clear()
            for level in xrange(CelebrityQuestLevels.MEDIUM, -1, -1):
                quest = self.__getQuestFromGroup(regularQuests, level)
                if quest is not None:
                    model = QuestSimplificationModel()
                    model.setIcon(questsParams.iconKey)
                    descrRes = R.strings.ny.newYear.celebrityChallenge.questShortDescr.dyn(questsParams.shortDescrKey)()
                    model.setDescription(backport.text(descrRes))
                    model.setGoalValue(questsParams.levelConds[level])
                    price = getCelebrityQuestSimplificationCost(activeQuest, level)
                    if price is not None:
                        model.setPrice(price)
                        model.setInsufficientFunds(self._itemsCache.items.festivity.getShardsCount() < price)
                    model.setLevel(level)
                    simplificationsModel.addViewModel(model)

            simplificationsModel.invalidate()
        return

    def __setSimplificationsLock(self):
        isSimplificationLocked = isCelebrityQuestsSimplificationLocked()
        self.viewModel.setVehicleInBattle(isSimplificationLocked)

    @staticmethod
    def __getQuestFromGroup(regularQuests, level):
        return findFirst(lambda q: q.level == level, regularQuests, None)

    def __toggleBlur(self, forceDisable=False):
        if self.viewModel.getIsAllQuestsVisible() and not forceDisable:
            self.__blur.enable()
        else:
            self.__blur.disable()

    @simpleLog(action=NY_LOG_ACTIONS.NY_CELEBRITY_INFO_SCREEN_CLOSE)
    def __onLeaveIntroScreen(self):
        self.viewModel.setIsDisplayIntro(False)
        self.__toggleBlur()
        AccountSettings.setUIFlag(NY_CELEBRITY_CHALLENGE_VISITED, True)
        NewYearSoundsManager.playEvent(NewYearSoundEvents.CELEBRITY_INTRO_EXIT)
        if not self.viewModel.getIsChallengeVisited():
            self.viewModel.setIsChallengeVisited(True)

    @simpleLog(action=NY_LOG_ACTIONS.NY_CELEBRITY_INFO_SCREEN_OPEN)
    def __onOpenIntroScreen(self):
        self.__toggleBlur(True)
        self.viewModel.setIsDisplayIntro(True)

    def __onUpdateTimeTill(self):
        self.viewModel.setTimeTill(time_utils.getDayTimeLeft())

    @logOnMatch(objProperty='_getAllQuestsVisible', needCall=True, matches={True: NY_LOG_ACTIONS.NY_CHALLENGE_QUESTS_HIDE,
     False: NY_LOG_ACTIONS.NY_CHALLENGE_QUESTS_SHOW})
    def __onChangeAllQuestsVisibility(self):
        self.viewModel.setIsAllQuestsVisible(not self.viewModel.getIsAllQuestsVisible())
        self.__toggleBlur()

    def __onSideBarSelected(self, event):
        ctx = event.ctx
        if ctx.menuName != NyWidgetTopMenu.GLADE:
            return
        tabName = ctx.tabName
        if tabName != self.getCurrentObject():
            if tabName != NyTabBarMainView.CELEBRITY:
                self.switchByObjectName(tabName)
            self._newYearSounds.onExitView()

    def __onSimplify(self, args=None):
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
                self.__lockOverlays(True)
                self.__requestSimplification(quest, level, cost)
            return

    @async
    def __simplifyConfirmator(self, price):
        formattedCount = '{}{}'.format(text_styles.grandTitle(backport.getIntegralFormat(price)), icons.makeImageTag(backport.image(R.images.gui.maps.icons.new_year.icons.parts_24x24()), width=24, height=24, vSpace=1))
        builder = InfoDialogBuilderEx()
        builder.setMessagesAndButtons(R.strings.ny.confirmSimplification, buttons=R.strings.ny.confirmSimplification)
        builder.setMessageArgs(fmtArgs=[FmtArgs(formattedCount, 'count', R.styles.GrandTitleTextStyle())])
        result = yield await(dialogs.showSimple(builder.build(self)))
        raise AsyncReturn(result)

    @adisp.process
    def __requestSimplification(self, quest, level, price):
        result = yield SimplifyCelebrityQuestProcessor(quest.getID(), level).request()
        if result and result.success:
            self._celebrityController.onSimplifyQuest()
            SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.newYear.celebrityChallenge.simplification.message(), value=price), type=SystemMessages.SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': backport.text(R.strings.system_messages.newYear.celebrityChallenge.simplification.title())})
        else:
            self.__lockOverlays(False)

    def __onVisited(self, args=None):
        self.__maskQuestAction(args, NY_CELEBRITY_QUESTS_VISITED_MASK, lambda qModel, value: qModel.setIsVisited(value))

    def __onCompletedAnimationShown(self, args=None):
        self.__maskQuestAction(args, NY_CELEBRITY_COMPLETED_QUESTS_ANIMATION_SHOWN_MASK, lambda qModel, value: qModel.setIsCompletedAnimationShown(value))

    def __maskQuestAction(self, args, maskName, modelSetFunc):
        qId = int(args.get('id'))
        questsMask = AccountSettings.getUIFlag(maskName)
        dayNumMask = 1 << qId - 1
        questsMask |= dayNumMask
        with self.viewModel.transaction() as vm:
            quests = vm.getQuests()
            questModel = findFirst(lambda q: q.getId() == qId, quests, None)
            modelSetFunc(questModel, True)
            quests.invalidate()
            self.__triggerSyncInitiator()
        AccountSettings.setUIFlag(maskName, questsMask)
        return

    def __parseQuestsChangeableParams(self, activeQuest, regularQuests):
        questsParams = _QuestsParams()
        goalByLevel = questsParams.levelConds
        simplificationParamType = _SimplificationParamType.UNSUPPORTED
        topValue = None
        battleResultCond = [ i for i in activeQuest.postBattleCond.getConditions().items if isinstance(i, BattleResults) ]
        if battleResultCond:
            maxValue = battleResultCond[0].getMaxRange()[-1]
            topValue = maxValue if maxValue != BattleResults.TOP_RANGE_LOWEST else None
        preformattedCond = self.__condFormatter.format(activeQuest)[0]
        if topValue is not None and len(preformattedCond) == 2:
            simplificationParamType = _SimplificationParamType.TWO_COND_REPEAT_TOP_BATTLE_RESULTS
            questsParams.isCumulative = True
            cumulativeCond = findFirst(lambda c: c.progressType == MISSIONS_ALIASES.CUMULATIVE, preformattedCond, None)
            questsParams.condCurrent = cumulativeCond.current
            questsParams.condTotal = cumulativeCond.total
            questsParams.shortDescrKey = 'top' + str(topValue)
            goalByLevel[activeQuest.level] = cumulativeCond.total
            nonCumulativeCond = findFirst(lambda c: c.progressType != MISSIONS_ALIASES.CUMULATIVE, preformattedCond, None)
            questsParams.iconKey = nonCumulativeCond.iconKey
        elif len(preformattedCond) == 1:
            cond = preformattedCond[0]
            if cond.progressType == MISSIONS_ALIASES.CUMULATIVE:
                goalByLevel[activeQuest.level] = cond.total
                questsParams.isCumulative = True
                questsParams.condCurrent = cond.current
                questsParams.condTotal = cond.total
                simplificationParamType = _SimplificationParamType.ONE_COND_CUMULATIVE
            else:
                goalByLevel[activeQuest.level] = cond.titleData.args[0]
                questsParams.isCumulative = False
                simplificationParamType = _SimplificationParamType.ONE_COND_BATTLE_RESULTS
            questsParams.iconKey = cond.iconKey
            if questsParams.iconKey == 'damage_block':
                questsParams.shortDescrKey = activeQuest.bonusCond.getConditions().items[0].keyName
            else:
                questsParams.shortDescrKey = cond.iconKey
        elif len(preformattedCond) == 2:
            otherQuest = regularQuests[0] if regularQuests[0] is not activeQuest else regularQuests[1]
            otherPreformattedCond = self.__condFormatter.format(otherQuest)[0]
            cumulativeCond = findFirst(lambda c: c.progressType == MISSIONS_ALIASES.CUMULATIVE, preformattedCond, None)
            nonCumulativeCond = findFirst(lambda c: c.progressType != MISSIONS_ALIASES.CUMULATIVE, preformattedCond, None)
            if cumulativeCond is not None:
                otherTotalGoal = findFirst(lambda c: c.progressType == MISSIONS_ALIASES.CUMULATIVE, otherPreformattedCond, 0).total
                winCond = findFirst(lambda c: c.iconKey == 'win', preformattedCond, None)
                questsParams.condCurrent = cumulativeCond.current
                questsParams.condTotal = cumulativeCond.total
                questsParams.isCumulative = True
                if winCond is not None:
                    simplificationParamType = _SimplificationParamType.TWO_COND_WIN
                    questsParams.shortDescrKey = winCond.iconKey
                    questsParams.iconKey = winCond.iconKey
                    goalByLevel[activeQuest.level] = cumulativeCond.total
                elif cumulativeCond.total == otherTotalGoal:
                    simplificationParamType = _SimplificationParamType.TWO_COND_BATTLE_RESULTS
                    questsParams.shortDescrKey = nonCumulativeCond.iconKey
                    questsParams.iconKey = nonCumulativeCond.iconKey
                    goalByLevel[activeQuest.level] = nonCumulativeCond.titleData.args[0]
                else:
                    simplificationParamType = _SimplificationParamType.TWO_COND_REPEAT_BATTLE_RESULTS
                    questsParams.shortDescrKey = cumulativeCond.iconKey
                    questsParams.iconKey = nonCumulativeCond.iconKey
                    goalByLevel[activeQuest.level] = cumulativeCond.total
            else:
                cond = findFirst(lambda c: c.iconKey != 'win', preformattedCond, 0)
                if cond is not None:
                    simplificationParamType = _SimplificationParamType.TWO_COND_WIN_AND_BATTLE_RESULT
                    questsParams.shortDescrKey = cond.iconKey
                    questsParams.iconKey = cond.iconKey
                    questsParams.isCumulative = False
                    goalByLevel[activeQuest.level] = cond.titleData.args[0]
        elif len(preformattedCond) == 3:
            winCond = findFirst(lambda c: c.iconKey == 'win', preformattedCond, None)
            cumulativeCond = findFirst(lambda c: c.progressType == MISSIONS_ALIASES.CUMULATIVE, preformattedCond, None)
            if winCond is not None and cumulativeCond is not None:
                simplificationParamType = _SimplificationParamType.THREE_COND_WIN_REPEAT_AND_BATTLE_RESULT
                questsParams.condCurrent = cumulativeCond.current
                questsParams.condTotal = cumulativeCond.total
                questsParams.isCumulative = True
                questsParams.shortDescrKey = winCond.iconKey
                questsParams.iconKey = winCond.iconKey
                goalByLevel[activeQuest.level] = cumulativeCond.total
        if simplificationParamType == _SimplificationParamType.UNSUPPORTED:
            raise SoftException('Not supported celebrity condition in quest of day {}'.format(activeQuest.getID()))
        for quest in regularQuests:
            if quest is activeQuest:
                continue
            preformattedCond = self.__condFormatter.format(quest)[0]
            if simplificationParamType == _SimplificationParamType.ONE_COND_BATTLE_RESULTS:
                goalByLevel[quest.level] = preformattedCond[0].titleData.args[0]
            if simplificationParamType == _SimplificationParamType.ONE_COND_CUMULATIVE:
                goalByLevel[quest.level] = preformattedCond[0].total
            if simplificationParamType in (_SimplificationParamType.TWO_COND_REPEAT_BATTLE_RESULTS,
             _SimplificationParamType.TWO_COND_REPEAT_TOP_BATTLE_RESULTS,
             _SimplificationParamType.TWO_COND_WIN,
             _SimplificationParamType.THREE_COND_WIN_REPEAT_AND_BATTLE_RESULT):
                goalByLevel[quest.level] = findFirst(lambda c: c.progressType == MISSIONS_ALIASES.CUMULATIVE, preformattedCond, 0).total
            if simplificationParamType == _SimplificationParamType.TWO_COND_BATTLE_RESULTS:
                goalByLevel[quest.level] = findFirst(lambda c: c.iconKey == questsParams.shortDescrKey, preformattedCond, 0).titleData.args[0]
            if simplificationParamType == _SimplificationParamType.TWO_COND_WIN_AND_BATTLE_RESULT:
                goalByLevel[quest.level] = findFirst(lambda c: c.iconKey != 'win', preformattedCond, 0).titleData.args[0]

        return questsParams

    def __onSimplificationAnimationEnd(self):
        self.__lockOverlays(False)

    def __lockOverlays(self, lock):
        if lock != self.__isOverlaysLocked:
            self.__isOverlaysLocked = lock
            lockOverlays(lock)

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


class _SimplificationParamType(IntEnum):
    UNSUPPORTED = 0
    ONE_COND_BATTLE_RESULTS = 1
    ONE_COND_CUMULATIVE = 2
    TWO_COND_BATTLE_RESULTS = 3
    TWO_COND_REPEAT_BATTLE_RESULTS = 4
    TWO_COND_REPEAT_TOP_BATTLE_RESULTS = 5
    TWO_COND_WIN_AND_BATTLE_RESULT = 6
    TWO_COND_WIN = 7
    THREE_COND_WIN_REPEAT_AND_BATTLE_RESULT = 8


class _QuestsParams(object):
    __slots__ = ('isCumulative', 'iconKey', 'shortDescrKey', 'condCurrent', 'condTotal', 'levelConds')

    def __init__(self):
        self.isCumulative = False
        self.iconKey = ''
        self.shortDescrKey = ''
        self.condCurrent = 0
        self.condTotal = 0
        self.levelConds = {}


class _ChallengeCondFormatter(MissionBonusAndPostBattleCondFormatter):

    def _packCondition(self, *args, **kwargs):
        pass

    def _getFormattedField(self, *args, **kwargs):
        pass

    def _packSeparator(self, key):
        pass

    def _packConditions(self, *args, **kwargs):
        pass
