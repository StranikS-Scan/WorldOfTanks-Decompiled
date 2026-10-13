# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/lobby/user_missions/fort_rush_quests_presenter.py
from __future__ import absolute_import
import typing
from fort_rush.gui.impl.lobby.bonus_packers import getFortRushMissionBonusPacker
from fort_rush.gui.impl.lobby.quest_packers import FortRushDailyQuestUIDataPacker
from fort_rush.gui.impl.lobby.tooltips.fort_rush_daily_quest_tooltip import FortRushProgressionQuestTooltip
from fort_rush.gui.shared.event_dispatcher import showProgressionView
from fort_rush.gui.impl.lobby.user_missions.fort_rush_overlap_ctrl import FortRushOverlapCtrlMixin
from fort_rush.skeletons.battle_controller import IFortRushBattleController
from fort_rush_common.fort_rush_constants import ARENA_BONUS_TYPE
from gui.Scaleform.genConsts.MISSIONS_STATES import MISSIONS_STATES
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.widget.quests_list_model import QuestsListModel
from gui.impl.gen.view_models.views.lobby.user_missions.widget.widget_quest_model import WidgetQuestModel
from gui.impl.lobby.missions.missions_helpers import needToUpdateQuestsInModel
from gui.impl.lobby.user_missions.hangar_widget.presenters.base_child_presenter import UserMissionChildPresenter
from gui.impl.lobby.user_missions.hangar_widget.presenters.constants import UserMissionGroups
from gui.impl.lobby.user_missions.hangar_widget.tooltip_positioner import TooltipPositionerMixin
from gui.impl.lobby.user_missions.tooltips.all_quests_done_tooltip import AllQuestsDoneTooltip
from gui.impl.pub.view_component import ViewComponent
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.missions.packers.events import findFirstConditionModel, packQuestBonusModelAndTooltipData
from helpers import dependency
from helpers.time_utils import getServerRegionalTime
from shared_utils import findFirst
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array, View, ViewEvent
    from gui.server_events.event_items import Quest

class FortRushQuestsPresenter(UserMissionChildPresenter, TooltipPositionerMixin, FortRushOverlapCtrlMixin, ViewComponent[QuestsListModel], IGlobalListener):
    GROUP = UserMissionGroups.MISSIONS
    __battleResults = dependency.descriptor(IBattleResultsService)
    __gameSession = dependency.descriptor(IGameSessionController)
    __ctrl = dependency.descriptor(IFortRushBattleController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(FortRushQuestsPresenter, self).__init__(model=QuestsListModel)
        self.__quests = []
        self.__isModelInited = False
        self.__battleResultsArenaUniqueID = None
        return

    @property
    def viewModel(self):
        return super(FortRushQuestsPresenter, self).getViewModel()

    def isVisible(self):
        return self.__ctrl.isEnabled()

    @property
    def hasDeferModelUpdate(self):
        isDeferUpdate = super(FortRushQuestsPresenter, self).hasDeferModelUpdate
        return isDeferUpdate and not self.__getAvailability()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.mono.user_missions.tooltips.daily_quest_tooltip():
            quest = self._getQuestFromEvent(event)
            self._updateCurrentMissionCountDown(quest)
            return FortRushProgressionQuestTooltip(quest)
        return AllQuestsDoneTooltip(questTimerLeft=self.__getTimeLeft()) if contentID == R.views.mono.user_missions.tooltips.all_quests_done_tooltip() else super(FortRushQuestsPresenter, self).createToolTipContent(event=event, contentID=contentID)

    def _finalize(self):
        super(FortRushQuestsPresenter, self)._finalize()
        self.__quests = None
        return

    def _getEvents(self):
        return super(FortRushQuestsPresenter, self)._getEvents() + ((self.viewModel.onMissionClick, self.__onMissionClick),
         (self.viewModel.onMarkAsViewed, self.__onMarkAsViewed),
         (self.__eventsCache.onSyncCompleted, self.__onSyncCompleted),
         (self.__hangarSpace.onVehicleChanged, self.__onVehicleLoaded),
         (self.__battleResults.onResultPosted, self.__handleBattleResultsPosted))

    def _getCallbacks(self):
        return super(FortRushQuestsPresenter, self)._getCallbacks() + (('tokens', self.__onTokensUpdate),)

    def _onLoading(self, *args, **kwargs):
        self.initOverlapCtrl()
        super(FortRushQuestsPresenter, self)._onLoading(*args, **kwargs)
        if self.__getAvailability():
            self.__refresh()
        else:
            self._notifyVisibilityChanged()

    def _rawUpdate(self):
        if self.__quests is None:
            return
        else:
            super(FortRushQuestsPresenter, self)._rawUpdate()
            with self.viewModel.transaction() as vm:
                modelQuests = vm.getQuests()
                modelQuests.clear()
                modelQuests.reserve(len(self.__quests))
                for quest in self.__quests:
                    modelQuests.addViewModel(self._getModel(quest))

                modelQuests.invalidate()
            self.__isModelInited = True
            return

    def _getModel(self, quest):
        questID = quest.getID()
        model = WidgetQuestModel()
        model.setId(questID)
        model.setMissionType('battleQuest')
        model.setAnimationId('fort_rush_daily::%s' % questID)
        packer = FortRushDailyQuestUIDataPacker(quest)
        fullQuestModel = packer.pack()
        isCompleted = fullQuestModel.getStatus().value == MISSIONS_STATES.COMPLETED
        hasPendingAnimateCompletion = self.__eventsCache.questsProgress.getQuestCompletionChanged(questID)
        model.setIsCompleted(isCompleted)
        model.setAnimateCompletion(hasPendingAnimateCompletion and isCompleted)
        model.setIcon(fullQuestModel.getIcon())
        model.setIsLocked(quest.getData().get('meta', {}).get('locked', False))
        model.setDescription(fullQuestModel.getDescription())
        conditionModel = self.__getFirstConditionModel(fullQuestModel)
        if conditionModel is not None:
            model.setCurrentProgress(conditionModel.getCurrent())
            model.setTotalProgress(conditionModel.getTotal())
            model.setEarned(conditionModel.getEarned())
        packQuestBonusModelAndTooltipData(getFortRushMissionBonusPacker(), model.getBonuses(), quest)
        model.setCountdown(self.__getTimeLeft())
        return model

    def _getQuestFromEvent(self, event):
        questId = event.getArgument('questID', '')
        quest = self.__eventsCache.getQuestByID(questId)
        return quest

    def _updateCurrentMissionCountDown(self, missionItem):
        with self.viewModel.transaction() as vm:
            modelQuests = vm.getQuests()
            item = findFirst(lambda i: i.getId() == missionItem.getID(), modelQuests)
            if item:
                item.setCountdown(self.__getTimeLeft())
                modelQuests.invalidate()

    @staticmethod
    def __getFirstConditionModel(questModel):
        postBattleModel = findFirstConditionModel(questModel.postBattleCondition)
        bonusConditionModel = findFirstConditionModel(questModel.bonusCondition)
        return postBattleModel if postBattleModel else bonusConditionModel

    def __getAvailability(self):
        isSpaceInited = self.__hangarSpace.spaceInited
        vehicleInited = self.__hangarSpace.isModelLoaded
        isInAwaitingBattleResult = self.__battleResults.areResultsPosted(self.__battleResultsArenaUniqueID)
        return isSpaceInited and vehicleInited and not isInAwaitingBattleResult

    def __onTokensUpdate(self, diff):
        if not self.__ctrl.isEnabled():
            return
        dailyMissionsConfig = self.__ctrl.getConfig().dailyMissionsConfig
        prefixes = (dailyMissionsConfig.dailyMissionTokenPrefix, dailyMissionsConfig.dailyMissionQuestPrefix, dailyMissionsConfig.hardDailyMissionQuestPrefix)
        if any((token.startswith(prefixes) for token in diff)):
            self.__refresh()

    def __handleBattleResultsPosted(self, reusableInfo, _, __):
        if reusableInfo.bonusType == ARENA_BONUS_TYPE.FORT_RUSH:
            self.__battleResultsArenaUniqueID = reusableInfo.arenaUniqueID

    def __onVehicleLoaded(self):
        self.__initModel()

    def _onSpaceCreate(self):
        self.__initModel()

    def __onSyncCompleted(self, *_):
        self.__refresh()

    def __initModel(self):
        if self._isFinalized or self.__isModelInited:
            return
        self.__refresh()

    def __onMissionClick(self, *args):
        showProgressionView()

    def __onMarkAsViewed(self):
        if not self.viewModel.getQuests():
            return
        for quest in self.__quests:
            self.__eventsCache.questsProgress.markQuestProgressAsViewed(quest.getID())

        self._rawUpdate()

    def __refresh(self):
        self._notifyVisibilityChanged()
        isAvailable = self.__getAvailability()
        self.setEnabled(isAvailable)
        if not isAvailable:
            return
        battleQuests = self.__ctrl.getFortRushDailyQuests()
        if not needToUpdateQuestsInModel(battleQuests, self.viewModel.getQuests()):
            return
        self.__quests = battleQuests
        self.queueUpdate()

    def __getTimeLeft(self):
        return int(self.__ctrl.getNewDailyMissionsTimestamp() - getServerRegionalTime())
