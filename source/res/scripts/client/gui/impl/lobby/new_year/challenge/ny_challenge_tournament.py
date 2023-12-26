# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/challenge/ny_challenge_tournament.py
import logging
import typing
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from constants import SECONDS_IN_DAY
from gui import SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from PlayerEvents import g_playerEvents
from account_helpers.AccountSettings import AccountSettings, NY_CELEBRITY_ADD_QUESTS_COMPLETED_MASK, NY_CELEBRITY_ADD_QUESTS_VISITED_MASK, NY_CELEBRITY_DAY_QUESTS_COMPLETED_MASK, NY_CELEBRITY_DAY_QUESTS_VISITED_MASK
from gui.Scaleform.daapi.view.lobby.missions.cards_formatters import MissionBonusAndPostBattleCondFormatter
from gui.Scaleform.genConsts.MISSIONS_ALIASES import MISSIONS_ALIASES
from gui.impl.backport.backport_pop_over import BackportPopOverContent, createPopOverData
from gui.impl import backport
from gui.impl.gen.view_models.common.missions.bonuses.discount_bonus_model import DiscountBonusModel
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_card_model import CardState, NewYearChallengeCardModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_progress_model import NewYearChallengeProgressModel
from gui.impl.lobby.new_year.ny_history_presenter import NyHistoryPresenter
from gui.impl.lobby.new_year.tooltips.ny_gift_machine_token_tooltip import NyGiftMachineTokenTooltip
from gui.impl.lobby.new_year.tooltips.ny_replacement_timer_tooltip import NyReplacementTimerTooltip
from gui.impl.new_year.navigation import NewYearNavigation, ViewAliases
from gui.impl.new_year.new_year_bonus_packer import getChallengeBonusPacker, packBonusModelAndTooltipData
from gui.impl.new_year.new_year_helper import backportTooltipDecorator, nyCreateToolTipContentDecorator
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.shared import event_dispatcher
from gui.shared.event_dispatcher import showStylePreview
from helpers import dependency, time_utils
from items.components.ny_constants import CelebrityQuestTokenParts
from new_year.celebrity.celebrity_quests_helpers import getCelebrityMarathonQuests, getCelebrityQuestBonusesByFullQuestID, getCelebrityQuestByFullID, getRerollsCount, iterCelebrityActiveQuestsIDs, marathonTokenCountExtractor
from new_year.ny_constants import NYObjects
from new_year.ny_preview import getVehiclePreviewID
from new_year.ny_processor import isCelebrityQuestsRerollLockedByVehicle, RerollCelebrityQuestProcessor
from shared_utils import findFirst, first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from gui.shared.utils import decorators
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
    __slots__ = ('_tooltips', '__condFormatter', '__rerollQuestName')
    __celebritySceneController = dependency.descriptor(ICelebritySceneController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, viewModel, parentView, soundConfig=None):
        super(NewYearChallengeTournament, self).__init__(viewModel, parentView, soundConfig)
        self._tooltips = {}
        self.__condFormatter = None
        self.__rerollQuestName = None
        return

    @property
    def viewModel(self):
        model = self.getViewModel()
        return model.tournamentCelebrityModel if model else None

    def initialize(self, *args, **kwargs):
        super(NewYearChallengeTournament, self).initialize(self, *args, **kwargs)
        self.__celebritySceneController.onEnterChallenge()
        if not self.__celebritySceneController.isChallengeVisited:
            self.__settingsCore.serverSettings.saveInNewYearStorage({NewYearStorageKeys.CELEBRITY_SCREEN_VISITED: True})
            NewYearSoundsManager.playEvent(NewYearSoundEvents.CELEBRITY_INTRO)
        with self.viewModel.transaction() as model:
            self.__updateModel(model)

    def finalize(self):
        super(NewYearChallengeTournament, self).finalize()
        self.__celebritySceneController.onExitChallenge()
        self.__condFormatter = None
        self.__rerollQuestName = None
        return

    @nyCreateToolTipContentDecorator
    def createToolTipContent(self, event, contentID):
        if event.contentID == R.views.lobby.new_year.tooltips.NyReplacementTimerTooltip():
            isAvailable = event.getArgument('isAvailable', False)
            return NyReplacementTimerTooltip(isAvailable, self.__isRerollFinished())
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
         (self.viewModel.onStylePreviewShow, self.__onStylePreviewShow),
         (self.__celebritySceneController.onQuestsUpdated, self.__onQuestsUpdated),
         (g_playerEvents.onClientUpdated, self.__onClientUpdated))

    def _getCallbacks(self):
        return (('cache', self.__onCacheUpdated),)

    @dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
    def __isRerollFinished(self, lobbyCtx=None):
        serverDay = time_utils.getServerGameDay()
        eventEndDay, rest = divmod(lobbyCtx.getServerSettings().getNewYearGeneralConfig().getEventEndTime() - time_utils.getStartOfNewGameDayOffset(), SECONDS_IN_DAY)
        lastDayOfReroll = eventEndDay + (rest > 0)
        isFinished = lastDayOfReroll - serverDay <= 1
        return isFinished

    def __updateModel(self, model):
        model.setMaxQuestsQuantity(self.__celebritySceneController.questsCount)
        model.setCompletedQuestsQuantity(self.__celebritySceneController.completedQuestsCount)
        model.setTimeTill(time_utils.getDayTimeLeft())
        if self.__rerollQuestName is None:
            self.__setQuestsInfo()
        else:
            self.__updateQuestsInfoOnReroll()
        self.__fillProgression(model)
        return

    def __setQuestsInfo(self):
        if not self.viewModel:
            return
        with self.viewModel.transaction() as tx:
            tx.setIsVehicleInBattle(isCelebrityQuestsRerollLockedByVehicle())
            tx.setReplacementsQuantity(getRerollsCount())
            dailyCardsModel = tx.getChallengeCards()
            dailyCardsModel.clear()
            for token in sorted(iterCelebrityActiveQuestsIDs(), cmp=CelebrityQuestTokenParts.compareFullQuestsIDs):
                qType, qNum = CelebrityQuestTokenParts.getFullQuestOrderInfo(token)
                if qType not in CelebrityQuestTokenParts.QUEST_TYPES:
                    continue
                self.__makeAndFillChallengeCardModel(dailyCardsModel, token, (qType, qNum))

            dailyCardsModel.invalidate()

    def __updateQuestsInfoOnReroll(self):
        with self.viewModel.transaction() as tx:
            tx.setIsVehicleInBattle(isCelebrityQuestsRerollLockedByVehicle())
            tx.setReplacementsQuantity(getRerollsCount())
            dailyCardsModel = tx.getChallengeCards()
            for card in dailyCardsModel:
                if card.getToken() == self.__rerollQuestName:
                    card.setState(CardState.INTRANSITION)

            dailyCardsModel.invalidate()

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

    def __fillProgression(self, model):
        marathonQuests = getCelebrityMarathonQuests()
        if not marathonQuests:
            _logger.warning("Can't find marathon quests")
            return
        sortedMarathonQIDs = sorted(marathonQuests.keys(), key=lambda qID: int(qID.split(CelebrityQuestTokenParts.SEPARATOR)[-1]))
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
            dailyCards = tx.getChallengeCards()
            cardModel = findFirst(lambda c: c.getToken() == args.get('token'), dailyCards, None)
            if cardModel is None:
                return
            qType, qNum = CelebrityQuestTokenParts.getFullQuestOrderInfo(cardModel.getToken())
            cardModel.setIsVisited(True)
            dailyCards.invalidate()
            _setQuestVisited(qType, qNum, True)
        return

    @decorators.adisp_process('newYear/replacement')
    def __onReplace(self, args):
        questID = str(args.get('token', ''))
        if not questID:
            return
        else:
            self.viewModel.setIsReplaceLocked(True)
            if self.__rerollQuestName is None:
                self.__rerollQuestName = questID
            result = yield RerollCelebrityQuestProcessor(questID).request()
            self.__rerollQuestName = None
            model = self.viewModel
            if model:
                model.setIsReplaceLocked(False)
            if result and result.userMsg:
                SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType, priority=result.msgPriority)
            if result and not result.success:
                self.__setQuestsInfo()
            return

    def __onStylePreviewShow(self, args):
        styleIntCD = int(args.get('intCD'))
        styleItem = self._itemsCache.items.getItemByCD(styleIntCD)
        if styleItem is None:
            return
        else:
            backBtnDescrLabel = backport.text(R.strings.ny.tournament.backLabel())

            def _backCallback():
                if not self._nyController.isEnabled():
                    event_dispatcher.showHangar()
                else:
                    NewYearNavigation.switchFromStyle(viewAlias=ViewAliases.CELEBRITY_VIEW, objectName=NYObjects.CHALLENGE, forceShowMainView=True)

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
