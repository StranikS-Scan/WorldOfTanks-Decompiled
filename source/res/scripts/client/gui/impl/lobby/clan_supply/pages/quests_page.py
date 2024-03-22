# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/clan_supply/pages/quests_page.py
import json
import logging
import typing
import SoundGroups
from adisp import adisp_process
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui import SystemMessages
from gui.clans.clan_cache import g_clanCache
from gui.clans.data_wrapper.clan_supply import QuestStatus as DataQuestStatus, ConditionRuleType, ConditionSquadState, DataNames
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.clan_supply.pages.quest_model import QuestModel, QuestStatus, QuestCondition, QuestSquadState
from gui.impl.gen.view_models.views.lobby.clan_supply.pages.quests_model import ScreenStatus
from gui.impl.lobby.clan_supply.bonus_packers import composeBonuses, getCurrencyReward
from gui.impl.lobby.clan_supply.sound_helper import SOUNDS
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.shared.event_dispatcher import showStrongholds
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from gui.wgcg.clan_supply.contexts import ClaimRewardsCtx
from helpers import dependency, time_utils
from shared_utils import first, nextTick
from skeletons.gui.game_control import IClanNotificationController
from skeletons.gui.web import IWebController
if typing.TYPE_CHECKING:
    from typing import Optional, Dict, List, Tuple
    from gui.clans.data_wrapper import clan_supply
    from gui.impl.backport import TooltipData
    from gui.impl.gen.view_models.views.lobby.clan_supply.pages.quests_model import QuestsModel
_logger = logging.getLogger(__name__)
BUBBLES_ALIAS = 'clansupply_hangar_bubble'
_QuestDataStatusToModelStatus = {DataQuestStatus.INCOMPLETE: QuestStatus.IN_PROGRESS,
 DataQuestStatus.REWARD_AVAILABLE: QuestStatus.REWARD_AVAILABLE,
 DataQuestStatus.REWARD_PENDING: QuestStatus.REWARD_PENDING,
 DataQuestStatus.COMPLETE: QuestStatus.COMPLETE}
_QuestDataConditionToModelCondition = {ConditionRuleType.FRAGS: QuestCondition.FRAGS,
 ConditionRuleType.FULL_DAMAGE: QuestCondition.FULL_DAMAGE,
 ConditionRuleType.EXP: QuestCondition.EXP,
 ConditionRuleType.WIN: QuestCondition.WIN}
_QuestDataSquadStateToModelSquadState = {ConditionSquadState.SOLO: QuestSquadState.SOLO,
 ConditionSquadState.PLATOON: QuestSquadState.PLATOON,
 ConditionSquadState.DETACHMENT: QuestSquadState.DETACHMENT,
 (ConditionSquadState.SOLO, ConditionSquadState.PLATOON): QuestSquadState.SOLO_AND_PLATOON}
_ExistMainSquadStateLocalizationKeys = (QuestSquadState.PLATOON, QuestSquadState.SOLO_AND_PLATOON)
_ExistMainConditionLocalizationKeys = (QuestCondition.FRAGS, QuestCondition.FULL_DAMAGE, QuestCondition.EXP)
_ExistAlternativeSquadStateLocalizationKeys = (QuestSquadState.DETACHMENT,)
_ExistAlternativeConditionLocalizationKeys = (QuestCondition.WIN,)

class QuestsPage(SubModelPresenter):
    __slots__ = ('__tooltips', '__cachedQuestData', '__notifier')
    __webController = dependency.descriptor(IWebController)
    __notificationCtrl = dependency.descriptor(IClanNotificationController)

    def __init__(self, viewModel, parentView):
        self.__tooltips = {}
        self.__cachedQuestData = None
        self.__notifier = None
        super(QuestsPage, self).__init__(viewModel, parentView)
        return

    @property
    def viewModel(self):
        return super(QuestsPage, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(QuestsPage, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltips.get(tooltipId)

    def initialize(self, *args, **kwargs):
        super(QuestsPage, self).initialize(*args, **kwargs)
        self.__updateState()
        SoundGroups.g_instance.setState(SOUNDS.STATE_HANGAR_FILTERED, SOUNDS.STATE_HANGAR_FILTERED_ON)

    def finalize(self):
        SoundGroups.g_instance.setState(SOUNDS.STATE_HANGAR_FILTERED, SOUNDS.STATE_HANGAR_FILTERED_OFF)
        self.__cachedQuestData = None
        if self.__notifier is not None:
            self.__notifier.stopNotification()
            self.__notifier.clear()
            self.__notifier = None
        super(QuestsPage, self).finalize()
        return

    def _getEvents(self):
        return super(QuestsPage, self)._getEvents() + ((g_clanCache.clanSupplyProvider.onDataReceived, self.__onDataReceived),
         (g_clanCache.clanSupplyProvider.onDataFailed, self.__onDataFailed),
         (self.viewModel.onRefresh, self.__onRefresh),
         (self.viewModel.onClaimReward, self.__onClaimReward),
         (self.viewModel.onGoToClans, self.__onGoToClans))

    def _getCallbacks(self):
        return (('stats.clanInfo', self.__updateClanInfo),)

    def __updateState(self):
        questsObj = g_clanCache.clanSupplyProvider.getQuestsInfo()
        if questsObj.isWaitingResponse:
            self.viewModel.setStatus(ScreenStatus.PENDING)
            return
        else:
            quests = questsObj.data
            if quests is None:
                self.viewModel.setStatus(ScreenStatus.ERROR)
                return
            self.__cachedQuestData = quests
            self.__updateQuests(self.__cachedQuestData)
            return

    def __updateQuests(self, questsInfo):
        if not questsInfo.enabled or not questsInfo.quests:
            self.viewModel.setStatus(ScreenStatus.ERROR)
            return
        else:
            isPrevRewardsEmpty = self.__isPreviousRewardsEmpty(questsInfo.previous_rewards)
            with self.viewModel.transaction() as tx:
                if not g_clanCache.isInClan:
                    status = ScreenStatus.PLAYER_NOT_IN_CLAN
                elif not isPrevRewardsEmpty:
                    status = ScreenStatus.PREVIOUS_REWARDS
                elif any([ q for q in questsInfo.quests if q.status == DataQuestStatus.REWARD_AVAILABLE ]):
                    status = ScreenStatus.REWARD_AVAILABLE
                else:
                    status = ScreenStatus.IN_PROGRESS
                    if sum(self.__notificationCtrl.getCounters((BUBBLES_ALIAS,)).values()):
                        self.__notificationCtrl.setCounters(BUBBLES_ALIAS, 0)
                tx.setStatus(status)
                tx.setUpdateTime(questsInfo.cycle_end)
                tx.setCycleDuration(questsInfo.cycle_duration)
                self.__restartNotifier(questsInfo.cycle_end - time_utils.getServerUTCTime())
                quests = tx.getQuests()
                quests.clear()
                prevQuestData = None
                hasError = False
                for questData in questsInfo.quests:
                    questModel, questHasError = self.__fillQuestModel(questData, prevQuestData, status)
                    quests.addViewModel(questModel)
                    prevQuestData = questData
                    hasError |= questHasError

                quests.invalidate()
                if hasError:
                    self.viewModel.setStatus(ScreenStatus.ERROR)
                    return
                previousRewards = tx.getPreviousRewards()
                previousRewards.clear()
                if not isPrevRewardsEmpty:
                    packBonusModelAndTooltipData(composeBonuses(getCurrencyReward(questsInfo.previous_rewards)), previousRewards)
                previousRewards.invalidate()
            return

    def __fillQuestModel(self, questData, prevQuestData, screenStatus):
        hasError = False
        isQuestDisabled = screenStatus == ScreenStatus.PREVIOUS_REWARDS
        isPrevQuestIncomplete = prevQuestData is not None and prevQuestData.status == DataQuestStatus.INCOMPLETE
        if isQuestDisabled or isPrevQuestIncomplete:
            status = QuestStatus.DISABLED
        else:
            status = _QuestDataStatusToModelStatus.get(questData.status, QuestStatus.DISABLED)
        questModel = QuestModel()
        questModel.setLevel(questData.level)
        questModel.setCurrentProgress(questData.current_progress)
        questModel.setRequiredProgress(questData.required_progress)
        questModel.setStatus(status)
        mainCondition = _QuestDataConditionToModelCondition.get(questData.conditions.main.rule.type)
        hasError |= mainCondition not in _ExistMainConditionLocalizationKeys
        questModel.setMainCondition(mainCondition)
        mainSquadState = self.__getQuestSquadState(questData.conditions.main)
        hasError |= mainSquadState not in _ExistMainSquadStateLocalizationKeys
        questModel.setMainSquadState(mainSquadState)
        altCondition = _QuestDataConditionToModelCondition.get(questData.conditions.alternative.rule.type)
        hasError |= altCondition not in _ExistAlternativeConditionLocalizationKeys
        questModel.setAlternativeCondition(altCondition)
        altSquadState = self.__getQuestSquadState(questData.conditions.alternative)
        hasError |= altSquadState not in _ExistAlternativeSquadStateLocalizationKeys
        questModel.setAlternativeSquadState(altSquadState)
        questModel.setConditionParams(self.__getConditionParams([questData.conditions.main.rule, questData.conditions.alternative.rule]))
        rewards = getCurrencyReward(questData.rewards)
        packBonusModelAndTooltipData(composeBonuses(rewards), questModel.getRewards(), self.__tooltips)
        return (questModel, hasError)

    def __onDataReceived(self, dataName, data):
        if dataName not in (DataNames.QUESTS_INFO, DataNames.QUESTS_INFO_POST):
            return
        self.__cachedQuestData = data
        self.__updateQuests(data)

    def __onDataFailed(self, dataName):
        if dataName not in (DataNames.QUESTS_INFO, DataNames.QUESTS_INFO_POST):
            return
        self.viewModel.setStatus(ScreenStatus.ERROR)

    def __onRefresh(self):
        self.__updateState()

    def __updateClanInfo(self, *_):
        self.__updateState()

    @adisp_process
    def __onClaimReward(self):
        self.viewModel.setIsRewardsLoading(True)
        response = yield self.__webController.sendRequest(ctx=ClaimRewardsCtx())
        if self.viewModel is None:
            return
        else:
            self.viewModel.setIsRewardsLoading(False)
            if not response.isSuccess():
                SystemMessages.pushMessage(backport.text(R.strings.clan_supply.messages.claimRewards.error()), type=SystemMessages.SM_TYPE.Error)
                _logger.warning('Failed to claim rewards. Code: %s.', response.getCode())
                return
            self.__notificationCtrl.setCounters(BUBBLES_ALIAS, 0)
            quests = self.viewModel.getQuests()
            for quest in quests:
                if quest.getStatus() == QuestStatus.REWARD_AVAILABLE:
                    quest.setStatus(QuestStatus.REWARD_PENDING)

            currentScreenStatus = self.viewModel.getStatus()
            if currentScreenStatus == ScreenStatus.REWARD_AVAILABLE:
                self.viewModel.setStatus(ScreenStatus.IN_PROGRESS)
            elif currentScreenStatus == ScreenStatus.PREVIOUS_REWARDS:
                nextTick(self.__updateState)()
            return

    def __onGoToClans(self):
        showStrongholds()

    def __restartNotifier(self, timeUntilUpdateState):
        if self.__notifier is not None:
            self.__notifier.stopNotification()
            self.__notifier.clear()
            self.__notifier = None
        self.__notifier = SimpleNotifier(lambda : timeUntilUpdateState, self.__updateState)
        self.__notifier.startNotification()
        return

    @staticmethod
    def __getQuestSquadState(conditionData):
        if len(conditionData.squad_states) > 1:
            key = tuple(conditionData.squad_states)
        else:
            key = first(conditionData.squad_states)
        if key not in _QuestDataSquadStateToModelSquadState:
            _logger.error('Does not have key - %s for the mapping to the model.', key)
            return QuestSquadState.SOLO
        return _QuestDataSquadStateToModelSquadState[key]

    @staticmethod
    def __getConditionParams(rules):
        params = {}
        for rule in rules:
            ruleAsDict = rule._asdict()
            ruleAsDict.pop('type')
            params.update(ruleAsDict)

        return json.dumps(params)

    @staticmethod
    def __isPreviousRewardsEmpty(rewards):
        return not any(rewards.values())
