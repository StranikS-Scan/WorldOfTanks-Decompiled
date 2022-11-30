# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/challenge/ny_challenge_tournament.py
import logging
from itertools import chain
import typing
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
import wg_async as future_async
from PlayerEvents import g_playerEvents
from account_helpers.AccountSettings import AccountSettings, NY_CELEBRITY_ADD_QUESTS_COMPLETED_MASK, NY_CELEBRITY_ADD_QUESTS_INFO_HIDDEN, NY_CELEBRITY_ADD_QUESTS_VISITED_MASK, NY_CELEBRITY_DAY_QUESTS_COMPLETED_MASK, NY_CELEBRITY_DAY_QUESTS_VISITED_MASK
from gui.Scaleform.daapi.view.lobby.missions.cards_formatters import MissionBonusAndPostBattleCondFormatter
from gui.Scaleform.genConsts.MISSIONS_ALIASES import MISSIONS_ALIASES
from gui.impl.backport.backport_pop_over import BackportPopOverContent, createPopOverData
from gui.impl import backport
from gui.impl.gen.view_models.common.missions.bonuses.discount_bonus_model import DiscountBonusModel
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.dialogs.challenge.challenge_confirm_dialog_model import DialogViews
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_card_model import CardState, NewYearChallengeCardModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_progress_model import NewYearChallengeProgressModel
from gui.impl.lobby.new_year.dialogs.dialogs import showCelebrityChallengeConfirmDialog
from gui.impl.lobby.new_year.ny_history_presenter import NyHistoryPresenter
from gui.impl.lobby.new_year.tooltips.ny_gift_machine_token_tooltip import NyGiftMachineTokenTooltip
from gui.impl.lobby.new_year.tooltips.ny_replacement_timer_tooltip import NyReplacementTimerTooltip
from gui.impl.new_year.navigation import NewYearNavigation, ViewAliases
from gui.impl.new_year.new_year_bonus_packer import getChallengeBonusPacker, packBonusModelAndTooltipData
from gui.impl.new_year.new_year_helper import backportTooltipDecorator, nyCreateToolTipContentDecorator
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared import event_dispatcher
from gui.shared.event_dispatcher import showStylePreview
from helpers import dependency, time_utils, uniprof
from items.components.ny_constants import CelebrityQuestTokenParts
from new_year.celebrity.celebrity_quests_helpers import getCelebrityMarathonQuests, getCelebrityQuestBonusesByFullQuestID, getCelebrityQuestByFullID, getRerollsCount, iterCelebrityActiveQuestsIDs, marathonTokenCountExtractor, getCelebrityAdditionalQuestsConfig, getRerollTokens
from new_year.ny_constants import AdditionalCameraObject
from new_year.ny_preview import getVehiclePreviewID
from new_year.ny_processor import isCelebrityQuestsRerollLockedByVehicle
from shared_utils import findFirst, first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.server_events import IEventsCache
from skeletons.new_year import ICelebritySceneController
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from typing import Dict
    from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_model import NewYearChallengeModel
    from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_tournament_celebrity_model import NewYearTournamentCelebrityModel
    from gui.server_events.event_items import CelebrityQuest
_QuestsParams = typing.NamedTuple('_QuestsParams', (('iconKey', str),
 ('isCumulative', bool),
 ('condCurrent', int),
 ('condTotal', int),
 ('levelCondition', int)))
_COMPLETED_MASK = {CelebrityQuestTokenParts.DAY: NY_CELEBRITY_DAY_QUESTS_COMPLETED_MASK,
 CelebrityQuestTokenParts.ADD: NY_CELEBRITY_ADD_QUESTS_COMPLETED_MASK}
_VISITED_MASK = {CelebrityQuestTokenParts.DAY: NY_CELEBRITY_DAY_QUESTS_VISITED_MASK,
 CelebrityQuestTokenParts.ADD: NY_CELEBRITY_ADD_QUESTS_VISITED_MASK}

class NewYearChallengeTournament(NyHistoryPresenter):
    __slots__ = ('_tooltips', '__condFormatter')
    __celebritySceneController = dependency.descriptor(ICelebritySceneController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, viewModel, parentView, soundConfig=None):
        super(NewYearChallengeTournament, self).__init__(viewModel, parentView, soundConfig)
        self._tooltips = {}
        self.__condFormatter = None
        return

    @property
    def viewModel(self):
        model = self.getViewModel()
        return model.tournamentCelebrityModel

    @uniprof.regionDecorator(label='ny_challenge_tournament', scope='enter')
    def initialize(self, *args, **kwargs):
        super(NewYearChallengeTournament, self).initialize(self, *args, **kwargs)
        self.__celebritySceneController.onEnterChallenge()
        if not self.__celebritySceneController.isChallengeVisited:
            self.__settingsCore.serverSettings.saveInNewYearStorage({NewYearStorageKeys.CELEBRITY_SCREEN_VISITED: True})
            NewYearSoundsManager.playEvent(NewYearSoundEvents.CELEBRITY_INTRO)
        with self.viewModel.transaction() as model:
            self.__updateModel(model)

    @uniprof.regionDecorator(label='ny_challenge_tournament', scope='exit')
    def finalize(self):
        super(NewYearChallengeTournament, self).finalize()
        self.__condFormatter = None
        return

    @nyCreateToolTipContentDecorator
    def createToolTipContent(self, event, contentID):
        if event.contentID == R.views.lobby.new_year.tooltips.NyReplacementTimerTooltip():
            return NyReplacementTimerTooltip()
        return NyGiftMachineTokenTooltip() if event.contentID == R.views.lobby.new_year.tooltips.NyGiftMachineTokenTooltip() else super(NewYearChallengeTournament, self).createToolTipContent(event, contentID)

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(NewYearChallengeTournament, self).createToolTip(event)

    def createPopOverContent(self, event):
        if event.contentID == R.views.common.pop_over_window.backport_pop_over.BackportPopOverContent():
            if event.getArgument('popoverId') == DiscountBonusModel.NEW_YEAR_DISCOUNT_APPLY_POPOVER_ID:
                alias = VIEW_ALIAS.NY_SELECT_VEHICLE_FOR_DISCOUNT_POPOVER
                variadicID = event.getArgument('variadicID')
                data = createPopOverData(alias, {'variadicID': variadicID,
                 'parentWindow': self.getParentWindow()})
                return BackportPopOverContent(popOverData=data)
        return super(NewYearChallengeTournament, self).createPopOverContent(event)

    def _getEvents(self):
        events = super(NewYearChallengeTournament, self)._getEvents()
        return events + ((self.viewModel.onUpdateTimeTill, self.__onUpdateTimeTill),
         (self.viewModel.onVisited, self.__onVisited),
         (self.viewModel.onReplace, self.__onReplace),
         (self.viewModel.onCloseAdditionalCard, self.__onCloseAdditionalCard),
         (self.viewModel.onStylePreviewShow, self.__onStylePreviewShow),
         (self.__celebritySceneController.onQuestsUpdated, self.__onQuestsUpdated),
         (g_playerEvents.onClientUpdated, self.__onClientUpdated))

    def _getCallbacks(self):
        return (('cache', self.__onCacheUpdated),)

    def __updateModel(self, model):
        model.setMaxQuestsQuantity(self.__celebritySceneController.questsCount)
        model.setRerollingQuests(len(getRerollTokens()))
        model.setCompletedQuestsQuantity(self.__celebritySceneController.completedQuestsCount)
        model.setTimeTill(time_utils.getDayTimeLeft())
        self.__setQuestsInfo()
        self.__fillProgression(model)

    def __setQuestsInfo(self):
        with self.viewModel.transaction() as tx:
            tx.setIsVehicleInBattle(isCelebrityQuestsRerollLockedByVehicle())
            tx.setReplacementsQuantity(getRerollsCount())
            tx.setHasTemporaryAdditionalCard(not AccountSettings.getUIFlag(NY_CELEBRITY_ADD_QUESTS_INFO_HIDDEN))
            dailyCardsModel = tx.getChallengeCards()
            additionalCardsModel = tx.getAdditionalChallengeCards()
            dailyCardsModel.clear()
            additionalCardsModel.clear()
            for token in sorted(iterCelebrityActiveQuestsIDs(), cmp=CelebrityQuestTokenParts.compareFullQuestsIDs):
                qType, qNum = CelebrityQuestTokenParts.getFullQuestOrderInfo(token)
                if qType not in CelebrityQuestTokenParts.QUEST_TYPES:
                    continue
                cardsModel = dailyCardsModel if qType == CelebrityQuestTokenParts.DAY else additionalCardsModel
                self.__makeAndFillChallengeCardModel(cardsModel, token, (qType, qNum))

            if not additionalCardsModel:
                for rewardType, additionalQuestInfo in getCelebrityAdditionalQuestsConfig().iteritems():
                    receivedRewardsTokens = additionalQuestInfo.getDependencies().getTokensDependencies()
                    if all((self._itemsCache.items.tokens.getTokenCount(token) for token in receivedRewardsTokens)):
                        continue
                    self.__makeAndFillBlockedAdditionalChallengeCardModel(additionalCardsModel, rewardType)

            dailyCardsModel.invalidate()
            additionalCardsModel.invalidate()

    def __makeAndFillChallengeCardModel(self, model, token, questInfo):
        quest = getCelebrityQuestByFullID(token)
        if quest is None:
            return
        else:
            params = self.__parseQuestsParams(quest)
            qType, qNum = questInfo
            cardModel = NewYearChallengeCardModel()
            cardModel.setToken(token)
            cardModel.setCurrentProgress(params.condCurrent)
            cardModel.setFinalProgress(params.condTotal)
            cardModel.setIsCumulative(params.isCumulative)
            cardModel.setIcon(params.iconKey)
            cardModel.setDescription(quest.getDescription())
            cardModel.setGoalValue(params.levelCondition)
            cardModel.setIsVisited(_getQuestVisited(*questInfo))
            cardModel.setState(CardState.ACTIVE if not quest.isCompleted() else (CardState.JUSTCOMPLETED if not _getQuestCompleted(*questInfo) else CardState.COMPLETED))
            _setQuestCompleted(qType, qNum, quest.isCompleted())
            packBonusModelAndTooltipData(getCelebrityQuestBonusesByFullQuestID(token), cardModel.getRewards(), getChallengeBonusPacker(), self._tooltips)
            model.addViewModel(cardModel)
            return

    def __makeAndFillBlockedAdditionalChallengeCardModel(self, model, rewardType):
        bonusQuestId = CelebrityQuestTokenParts.makeAdditionalBonusQuestID(rewardType)
        quest = self.__eventsCache.getQuestByID(bonusQuestId)
        if quest is None:
            return
        else:
            bonusQuestBonuses = quest.getBonuses()
            bonusPacker = getChallengeBonusPacker()
            cardModel = NewYearChallengeCardModel()
            packBonusModelAndTooltipData(bonusQuestBonuses, cardModel.getRewards(), bonusPacker, self._tooltips)
            model.addViewModel(cardModel)
            return

    def __fillProgression(self, model):
        marathonQuests = getCelebrityMarathonQuests()
        if not marathonQuests:
            _logger.warning("Can't find marathon quests")
            return
        sortedMarathonQIDs = sorted(marathonQuests.keys(), key=lambda qID: qID.split(CelebrityQuestTokenParts.SEPARATOR)[-1])
        progressiveRewards = model.getProgressRewards()
        progressiveRewards.clear()
        for qID in sortedMarathonQIDs:
            quest = marathonQuests[qID]
            progressModel = NewYearChallengeProgressModel()
            progressModel.setRewardLevel(marathonTokenCountExtractor(quest))
            packBonusModelAndTooltipData(quest.getBonuses(), progressModel.getRewards(), getChallengeBonusPacker(), self._tooltips)
            bonus = findFirst(lambda b: b.getName() == 'customizations', progressModel.getRewards())
            if bonus and bonus.getIcon() == 'style':
                progressModel.setStyleRewardIndex(bonus.getIndex())
            progressiveRewards.addViewModel(progressModel)

        progressiveRewards.invalidate()

    def __parseQuestsParams(self, quest):
        activeQuestCurrent = activeQuestTotal = levelCondition = 0
        currConditions = first(self.__getCondFormatter().format(quest))
        postBattleConditions = quest.postBattleCond.getConditions()
        anyCumulative = findFirst(lambda c: c.progressType == MISSIONS_ALIASES.CUMULATIVE, currConditions)
        if anyCumulative is not None:
            activeQuestCurrent, activeQuestTotal = anyCumulative.current, anyCumulative.total
            levelCondition = anyCumulative.total
        else:
            for item in postBattleConditions.items:
                if item.getData().get('max'):
                    levelCondition = item.getData().get('max')[0][1]
                if item.getData().get('greaterOrEqual'):
                    levelCondition = item.getData().get('greaterOrEqual')[0][1]

        iconKey = currConditions[0].iconKey
        if iconKey == 'battles' and len(currConditions) == 2 and any((c.iconKey == 'win' for c in currConditions)):
            iconKey = 'win'
        return _QuestsParams(iconKey, anyCumulative is not None, activeQuestCurrent, activeQuestTotal, levelCondition)

    def __onVisited(self, args=None):
        with self.viewModel.transaction() as tx:
            dailyCards, additionalCards = tx.getChallengeCards(), tx.getAdditionalChallengeCards()
            cardModel = findFirst(lambda c: c.getToken() == args.get('token'), chain(dailyCards, additionalCards), None)
            if cardModel is None:
                return
            qType, qNum = CelebrityQuestTokenParts.getFullQuestOrderInfo(cardModel.getToken())
            cardsModel = dailyCards if qType == CelebrityQuestTokenParts.DAY else additionalCards
            cardModel.setIsVisited(True)
            cardsModel.invalidate()
            _setQuestVisited(qType, qNum, True)
        return

    @future_async.wg_async
    def __onReplace(self, args):
        self.viewModel.setIsReplaceLocked(True)
        result = yield showCelebrityChallengeConfirmDialog(DialogViews.TASKSWITCH, parent=self.getParentWindow(), questID=args.get('token'))
        if result is None or result.result != DialogButtons.SUBMIT:
            self.viewModel.setIsReplaceLocked(False)
        return

    def __onCloseAdditionalCard(self, _=None):
        self.viewModel.setHasTemporaryAdditionalCard(False)
        AccountSettings.setUIFlag(NY_CELEBRITY_ADD_QUESTS_INFO_HIDDEN, True)

    def __onStylePreviewShow(self, args):
        styleIntCD = int(args.get('intCD'))
        styleItem = self._itemsCache.items.getItemByCD(styleIntCD)
        if styleItem is None:
            return
        else:
            NewYearNavigation.switchTo(None, True)
            backBtnDescrLabel = backport.text(R.strings.ny.tournament.backLabel())

            def _backCallback():
                if not self._nyController.isEnabled():
                    event_dispatcher.showHangar()
                else:
                    NewYearNavigation.switchFromStyle(viewAlias=ViewAliases.CELEBRITY_VIEW, objectName=AdditionalCameraObject.CHALLENGE, forceShowMainView=True)

            showStylePreview(getVehiclePreviewID(styleItem), styleItem, styleItem.getDescription(), backCallback=_backCallback, backBtnDescrLabel=backBtnDescrLabel)
            return

    def __onUpdateTimeTill(self):
        self.viewModel.setTimeTill(time_utils.getDayTimeLeft())

    def __onQuestsUpdated(self):
        with self.viewModel.transaction() as tx:
            self.__updateModel(tx)

    def __onCacheUpdated(self, cache):
        if 'vehsLock' in cache:
            self.viewModel.setIsVehicleInBattle(isCelebrityQuestsRerollLockedByVehicle())

    def __onClientUpdated(self, diff, _):
        for questID in diff.get('quests', {}).keys():
            if CelebrityQuestTokenParts.isRerollQuestsID(questID):
                self.viewModel.setIsReplaceLocked(False)

    def __getCondFormatter(self):
        if self.__condFormatter is not None:
            return self.__condFormatter
        else:
            self.__condFormatter = _ChallengeCondFormatter()
            return self.__condFormatter


class _ChallengeCondFormatter(MissionBonusAndPostBattleCondFormatter):

    def _packCondition(self, *args, **kwargs):
        pass

    def _getFormattedField(self, *args, **kwargs):
        pass

    def _packSeparator(self, key):
        pass

    def _packConditions(self, *args, **kwargs):
        pass


def _getQuestVisited(questType, questNum):
    return _getUIFlagBit(_VISITED_MASK[questType], questNum - 1)


def _setQuestVisited(questType, questNum, value):
    return _setUIFlagBit(_VISITED_MASK[questType], questNum - 1, value)


def _getQuestCompleted(questType, questNum):
    return _getUIFlagBit(_COMPLETED_MASK[questType], questNum - 1)


def _setQuestCompleted(questType, questNum, value):
    return _setUIFlagBit(_COMPLETED_MASK[questType], questNum - 1, value)


def _getUIFlagBit(name, bitNum):
    return bool(AccountSettings.getUIFlag(name) >> bitNum & 1)


def _setUIFlagBit(name, bitNum, value):
    AccountSettings.setUIFlag(name, AccountSettings.getUIFlag(name) & ~(1 << bitNum) | int(value) << bitNum)
