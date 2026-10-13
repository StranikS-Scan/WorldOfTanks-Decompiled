# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/lobby/presenters/fort_rush_progression_presenter.py
from __future__ import absolute_import
from future.utils import viewvalues
import logging
from typing import TYPE_CHECKING
from fort_rush.account_helpers.account_settings import getLastSeenProgressionPoints, setLastSeenProgressionPoints
from fort_rush.gui.impl.gen.view_models.views.progression.milestone_model import MilestoneModel
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.impl.gen import R
from gui.impl.backport import BackportTooltipWindow, TooltipData
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from fort_rush.gui.impl.gen.view_models.views.progression.progression_view_model import ProgressionViewModel
from fort_rush.gui.impl.gen.view_models.views.progression.mission_model import MissionModel
from gui.shared.missions.packers.bonus import getDefaultBonusPacker
from gui.shared.missions.packers.events import packQuestBonusModelAndTooltipData
from helpers import dependency
from fort_rush.skeletons.battle_controller import IFortRushBattleController
from helpers.time_utils import getTimestampFromUTC, utcToLocalDatetime
from gui.shared.items_cache import CACHE_SYNC_REASON
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.shared import IItemsCache
from fort_rush.gui.impl.lobby.quest_packers import FortRushDailyQuestUIDataPacker
from fort_rush_common.configs.fort_rush_battles_config import fortRushBattlesConfigGameParamsSchema
from gui.impl.lobby.missions.missions_helpers import markQuestProgressAsViewed
from PlayerEvents import g_playerEvents
if TYPE_CHECKING:
    from frameworks.wulf import Array, ViewEvent
    from fort_rush_common.configs.fort_rush_battles_config import FortRushBattlesConfigModel
_logger = logging.getLogger(__name__)

class _MissionDecoration(object):
    WIN = 1
    KILL_VEHICLES = 2
    DAMAGE = 3
    BASE_CAPTURE = 4
    RAM = 5
    TOP3 = 6


class FortRushProgressionPresenter(SubModelPresenter):
    __gameSession = dependency.descriptor(IGameSessionController)
    __ctrl = dependency.descriptor(IFortRushBattleController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, viewModel, parentView):
        super(FortRushProgressionPresenter, self).__init__(viewModel, parentView)
        self.__tooltipData = {}

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def tokens(self):
        return self.__itemsCache.items.tokens

    @property
    def config(self):
        return self.__ctrl.getConfig()

    def createToolTip(self, event):
        tooltipData = self.__getTooltipData(event)
        if not tooltipData:
            return super(FortRushProgressionPresenter, self).createToolTip(event)
        else:
            window = None
            if tooltipData and isinstance(tooltipData, TooltipData):
                window = BackportTooltipWindow(tooltipData, self.getParentWindow(), event) if tooltipData is not None else None
                if window is not None:
                    window.load()
            return window

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)
        return super(FortRushProgressionPresenter, self).createToolTipContent(event=event, contentID=contentID)

    def packModel(self):
        _logger.debug('[FortRush] FortRushProgressionPresenter packing model')
        self._updateModel()

    def saveSeenProgress(self):
        config = self.__ctrl.getConfig()
        setLastSeenProgressionPoints(self.tokens.getTokenCount(config.baseProgressionToken))

    def _getEvents(self):
        return super(FortRushProgressionPresenter, self)._getEvents() + ((self.__gameSession.onNewDayNotify, self._updateModel),
         (self.__eventsCache.onSyncCompleted, self._updateModel),
         (self.__itemsCache.onSyncCompleted, self.__onSyncCompleted),
         (g_playerEvents.onConfigModelUpdated, self.__onConfigModelUpdated))

    def _getCallbacks(self):
        return super(FortRushProgressionPresenter, self)._getCallbacks() + (('tokens', self.__onTokensUpdate),)

    def finalize(self):
        self.__tooltipData.clear()
        self.__tooltipData = None
        super(FortRushProgressionPresenter, self).finalize()
        return

    def _updateModel(self):
        _logger.debug('[FortRush] FortRushProgressionPresenter updating model')
        if not self.__ctrl.isWithinActiveTimeframe():
            return
        self._fillTimers()
        self._fillDailyMissions()
        self._fillProgressionPoints()
        self._fillMilestones()

    def _fillTimers(self):
        self.viewModel.setEventStartDateTime(getTimestampFromUTC(utcToLocalDatetime(self.config.startDatetime).timetuple()))
        self.viewModel.setEventEndDateTime(getTimestampFromUTC(utcToLocalDatetime(self.config.endDatetime).timetuple()))
        self.viewModel.setNewMissionsDateTime(self.__ctrl.getNewDailyMissionsTimestamp())

    def _fillDailyMissions(self):
        dailyQuestsConfig = self.config.dailyMissionsConfig
        missions = self.viewModel.getMissions()
        missions.clear()
        self._fillMissions(missions, dailyQuestsConfig.dailyMissionQuestPrefix)
        self._fillMissions(missions, dailyQuestsConfig.hardDailyMissionQuestPrefix)

    def _fillMissions(self, missionModelArray, questPrefix):
        quests = self.__eventsCache.getAllQuests(lambda q: q.getID().startswith(questPrefix))
        dailyTokens = self.tokens.getTokensByPrefixAndPostfix(self.config.dailyMissionsConfig.dailyMissionTokenPrefix)
        if not dailyTokens:
            return
        filteredQuests = self.filterQuestsByTokenRequirement(quests, dailyTokens.keys().pop())
        for quest in filteredQuests:
            missionModel = MissionModel()
            packer = FortRushDailyQuestUIDataPacker(quest)
            packer.pack(missionModel)
            missionModelArray.addViewModel(missionModel)

        markQuestProgressAsViewed(filteredQuests)
        missionModelArray.invalidate()

    @staticmethod
    def filterQuestsByTokenRequirement(quests, token):

        def hasToken(q):
            return any((t.getID() == token for t in q.accountReqs.getTokens()))

        return list(filter(hasToken, viewvalues(quests)))

    def _fillProgressionPoints(self):
        self.viewModel.setCurrentEventPoints(self.tokens.getTokenCount(self.config.baseProgressionToken))
        self.viewModel.setPreviousEventPoints(getLastSeenProgressionPoints())

    def _fillMilestones(self):
        bonusPacker = getDefaultBonusPacker()
        progressionToken = self.config.baseProgressionToken
        progressionQuests = self.__eventsCache.getAllQuests(lambda q: q.getID().startswith(self.config.progressionQuestPrefix))
        milestones = self.viewModel.getMilestones()
        milestones.clear()
        self.__tooltipData = {}
        for stage in self.config.progression.stage:
            quest = progressionQuests.get(stage.quest)
            milestoneModel = MilestoneModel()
            threshold = 0
            if quest is not None:
                for tokenCond in quest.accountReqs.getTokens():
                    if tokenCond.getID() == progressionToken:
                        threshold = tokenCond.getNeededCount()
                        break

                rewardsList = milestoneModel.getRewards()
                packQuestBonusModelAndTooltipData(bonusPacker, rewardsList, quest, self.__tooltipData)
                rewardsList.invalidate()
            milestoneModel.setEventPoints(threshold)
            milestones.addViewModel(milestoneModel)

        milestones.invalidate()
        return

    def __onConfigModelUpdated(self, gpKey):
        if fortRushBattlesConfigGameParamsSchema.gpKey == gpKey:
            self._updateModel()

    def __onSyncCompleted(self, reason, diff):
        if reason != CACHE_SYNC_REASON.CLIENT_UPDATE:
            return
        self._updateModel()

    def __onTokensUpdate(self, diff):
        _logger.debug('[FortRush] FortRushProgressionPresenter updating tokens: %s', diff)
        if self.config.completedProgressionToken in diff:
            self._updateModel()
            self.saveSeenProgress()
            return
        if self.config.baseProgressionToken in diff:
            self._fillProgressionPoints()
            self._fillMilestones()
            self.saveSeenProgress()

    def __getTooltipData(self, event):
        tooltipIdx = event.getArgument('tooltipId', '')
        return self.__tooltipData.get(tooltipIdx)
