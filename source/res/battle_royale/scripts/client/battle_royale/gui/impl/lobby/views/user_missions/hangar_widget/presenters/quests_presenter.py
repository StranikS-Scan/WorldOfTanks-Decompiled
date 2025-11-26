# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/user_missions/hangar_widget/presenters/quests_presenter.py
import typing
from battle_royale.gui.impl.lobby.tooltips.progression_quest_tooltip import BattleRoyaleProgressionQuestTooltip
from constants import ARENA_BONUS_TYPE
from gui.impl.gen import R
from battle_royale.gui.impl.lobby.br_helpers.account_settings import setLastSeenQuestData, getLastSeenQuestData
from battle_royale.gui.impl.lobby.views.user_missions.hangar_widget.overlap_ctrl import BattleRoyaleOverlapCtrlMixin
from battle_royale_progression.gui.impl.lobby.views.bonus_packer import getBonusPacker, packQuestBonuses, packMissionItem
from battle_royale_progression.gui.shared.event_dispatcher import showProgressionView
from battle_royale_progression.skeletons.game_controller import IBRProgressionOnTokensController
from frameworks.wulf.view.array import fillViewModelsArray
from gui.impl.gen.view_models.views.lobby.user_missions.widget.quests_list_model import QuestsListModel
from gui.impl.gen.view_models.views.lobby.user_missions.widget.widget_quest_model import WidgetQuestModel
from gui.impl.lobby.user_missions.tooltips.all_quests_done_tooltip import AllQuestsDoneTooltip
from gui.impl.lobby.missions.missions_helpers import needToUpdateQuestsInModel
from gui.impl.lobby.user_missions.hangar_widget.tooltip_positioner import TooltipPositionerMixin
from gui.impl.pub.view_component import ViewComponent
from gui.shared.missions.packers.events import DailyQuestUIDataPacker
from helpers import dependency, time_utils
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IBattleRoyaleController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared.utils import IHangarSpace
from shared_utils import findFirst
from helpers.time_utils import ONE_DAY
from gui.server_events.events_helpers import EventInfoModel
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array, ViewEvent
    from gui.server_events.event_items import Quest

class BattleRoayaleQuestsPresenter(TooltipPositionerMixin, BattleRoyaleOverlapCtrlMixin, ViewComponent[QuestsListModel]):
    __battleRoyale = dependency.descriptor(IBattleRoyaleController)
    __brProgression = dependency.descriptor(IBRProgressionOnTokensController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __battleResults = dependency.descriptor(IBattleResultsService)

    def __init__(self):
        super(BattleRoayaleQuestsPresenter, self).__init__(model=QuestsListModel, enabled=False)
        self.__quests = []
        self.__isModelInited = False
        self.__battleResultsArenaUniqueID = None
        return

    @property
    def viewModel(self):
        return super(BattleRoayaleQuestsPresenter, self).getViewModel()

    @property
    def hasDeferModelUpdate(self):
        isDeferUpdate = super(BattleRoayaleQuestsPresenter, self).hasDeferModelUpdate
        return isDeferUpdate and not self.__getAvailability()

    def _onLoading(self, *args, **kwargs):
        super(BattleRoayaleQuestsPresenter, self)._onLoading(*args, **kwargs)
        self.__refresh()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.mono.user_missions.tooltips.daily_quest_tooltip():
            quest = self._getQuestFromEvent(event)
            return BattleRoyaleProgressionQuestTooltip(quest)
        return AllQuestsDoneTooltip(layoutID=R.views.battle_royale.mono.lobby.tooltips.all_quests_done_tooltip(), questTimerLeft=self.__getTimeLeft()) if contentID == R.views.mono.user_missions.tooltips.all_quests_done_tooltip() else super(BattleRoayaleQuestsPresenter, self).createToolTipContent(event=event, contentID=contentID)

    def prepare(self):
        super(BattleRoayaleQuestsPresenter, self).prepare()
        self.initOverlapCtrl()
        self.__brProgression.onProgressPointsUpdated += self.__refresh
        self.__brProgression.onSettingsChanged += self.__onProgressSettingsChanged
        self.__eventsCache.onSyncCompleted += self.__onSyncCompleted
        self.__hangarSpace.onSpaceCreate += self.__onSpaceCreate
        self.__hangarSpace.onVehicleChanged += self.__onVehicleLoaded
        self.__battleResults.onResultPosted += self.__handleBattleResultsPosted

    def _finalize(self):
        super(BattleRoayaleQuestsPresenter, self)._finalize()
        self.__brProgression.onProgressPointsUpdated -= self.__refresh
        self.__brProgression.onSettingsChanged -= self.__onProgressSettingsChanged
        self.__eventsCache.onSyncCompleted -= self.__onSyncCompleted
        self.__hangarSpace.onSpaceCreate -= self.__onSpaceCreate
        self.__hangarSpace.onVehicleChanged -= self.__onVehicleLoaded
        self.__battleResults.onResultPosted -= self.__handleBattleResultsPosted
        self.__quests = None
        return

    def _getEvents(self):
        return super(BattleRoayaleQuestsPresenter, self)._getEvents() + ((self.viewModel.onMissionClick, self.__onMissionClick), (self.viewModel.onMarkAsViewed, self.__onMarkAsViewed))

    def __getAvailability(self):
        isSpaceInited = self.__hangarSpace.spaceInited
        vehicleInited = self.__hangarSpace.isModelLoaded
        isInAwaitingBattleResult = self.__battleResults.areResultsPosted(self.__battleResultsArenaUniqueID)
        return isSpaceInited and vehicleInited and not isInAwaitingBattleResult

    def _rawUpdate(self):
        super(BattleRoayaleQuestsPresenter, self)._rawUpdate()
        with self.viewModel.transaction() as vm:
            modelQuests = vm.getQuests()
            modelQuests.clear()
            modelQuests.reserve(len(self.__quests))
            for quest in self.__quests:
                modelQuests.addViewModel(self._getModel(quest))

            modelQuests.invalidate()
        self.__isModelInited = True

    def _getModel(self, quest):
        questID = quest.getID()
        model = WidgetQuestModel()
        model.setId(questID)
        model.setMissionType('battleQuest')
        model.setAnimationId(questID)
        bonusPacker = getBonusPacker()
        packedBonuses, _ = packQuestBonuses(quest.getBonuses(), bonusPacker)
        fillViewModelsArray(packedBonuses, model.getBonuses())
        packMissionItem(model, quest, DailyQuestUIDataPacker)
        lastSeenProgress, isQuestAnimationSeen = getLastSeenQuestData(quest.getID())
        model.setAnimateCompletion(not isQuestAnimationSeen and model.getIsCompleted())
        if not isQuestAnimationSeen:
            model.setEarned(model.getCurrentProgress() - lastSeenProgress)
        return model

    def _getQuestFromEvent(self, event):
        questID = event.getArgument('questID', '')
        quest = findFirst(lambda q: q.getID() == questID, self.__quests)
        return quest

    def __handleBattleResultsPosted(self, reusableInfo, _, __):
        if reusableInfo.bonusType in ARENA_BONUS_TYPE.BATTLE_ROYALE_RANGE:
            self.__battleResultsArenaUniqueID = reusableInfo.arenaUniqueID

    def __onVehicleLoaded(self):
        self.__initModel()

    def __onSpaceCreate(self):
        self.__initModel()

    def __onProgressSettingsChanged(self):
        self.__refresh()

    def __onSyncCompleted(self, *_):
        self.__refresh()

    def __initModel(self):
        if self._isFinalized or self.__isModelInited:
            return
        self.__refresh()

    def __refresh(self):
        isAvailable = self.__getAvailability()
        self.setEnabled(isAvailable)
        if not isAvailable:
            return
        battleQuests = self.__getQuests()
        isNeedToUpdate = needToUpdateQuestsInModel(battleQuests, self.viewModel.getQuests())
        if not isNeedToUpdate:
            return
        self.__quests = battleQuests
        self.queueUpdate()

    def __getQuests(self):
        if not self.__brProgression.isEnabled:
            return []
        data = self.__brProgression.getProgressionData()
        return data.get('battleQuests', {}).values()

    def __onMissionClick(self, *args):
        showProgressionView()

    def __onMarkAsViewed(self):
        if not self.viewModel.getQuests():
            return
        for quest in self.__quests:
            model = WidgetQuestModel()
            questID = quest.getID()
            isCompleted, lastSeenProgress = packMissionItem(model, quest, DailyQuestUIDataPacker)
            setLastSeenQuestData(questID, (lastSeenProgress, True))
            _, showCompletedAnimation = getLastSeenQuestData(questID)
            if showCompletedAnimation and not isCompleted:
                setLastSeenQuestData(questID, (lastSeenProgress, False))

    def __getTimeLeft(self):
        dailyQuestProgressDelta = EventInfoModel.getDailyProgressResetTimeDelta()
        currentCycleEndTime = self.__battleRoyale.getEndTime()
        currServerTime = time_utils.getCurrentLocalServerTimestamp()
        cycleTimeLeft = currentCycleEndTime - currServerTime
        return 0 if cycleTimeLeft < ONE_DAY and cycleTimeLeft < dailyQuestProgressDelta else dailyQuestProgressDelta
