# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/progression_quests_presenter.py
from comp7.gui.impl.lobby.comp7_helpers.comp7_bonus_packer import packQuestBonuses
from comp7_light.gui.impl.gen.view_models.views.lobby.progression_quests_model import ProgressionQuestsModel
from comp7_light.gui.impl.lobby.comp7_light_helpers.account_settings import getLastSeenQuestData, setLastSeenQuestData
from comp7_light.gui.impl.lobby.comp7_light_helpers.comp7_light_mission_packer import packMissionItem
from comp7_light.gui.impl.lobby.comp7_light_helpers.comp7_light_packers import getComp7LightBonusPacker
from comp7_light.gui.impl.lobby.tooltips.battle_quest_tooltip import BattleQuestTooltip
from comp7_light.gui.impl.lobby.tooltips.battle_quests_done_tooltip import BattleQuestsDoneTooltip
from comp7_light.gui.impl.lobby.user_missions.hangar_widget.overlap_ctrl import Comp7LightOverlapCtrlMixin
from frameworks.wulf import Array
from comp7_light.gui.shared.event_dispatcher import showComp7LightProgressionView
from comp7_light.skeletons.gui.game_control import IComp7LightProgressionController
from frameworks.wulf.view.array import fillViewModelsArray
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.widget.widget_quest_model import WidgetQuestModel
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.impl.lobby.user_missions.hangar_widget.tooltip_positioner import TooltipPositionerMixin
from gui.impl.pub.view_component import ViewComponent
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.missions.packers.events import DailyQuestUIDataPacker
from helpers import dependency
from skeletons.gui.game_control import IComp7LightController
from skeletons.gui.server_events import IEventsCache

class ProgressionQuestsPresenter(TooltipPositionerMixin, Comp7LightOverlapCtrlMixin, ViewComponent[ProgressionQuestsModel], IGlobalListener):
    __eventsCache = dependency.descriptor(IEventsCache)
    __comp7LightController = dependency.descriptor(IComp7LightController)
    __comp7LightProgressionController = dependency.descriptor(IComp7LightProgressionController)

    def __init__(self):
        super(ProgressionQuestsPresenter, self).__init__(model=ProgressionQuestsModel)

    @property
    def viewModel(self):
        return super(ProgressionQuestsPresenter, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        self.initOverlapCtrl()
        super(ProgressionQuestsPresenter, self)._onLoading(*args, **kwargs)
        self._updateViewModel()

    def _getEvents(self):
        return super(ProgressionQuestsPresenter, self)._getEvents() + ((self.viewModel.onMarkAsViewed, self.__onMarkAsViewed),
         (self.__eventsCache.onSyncCompleted, self._updateViewModel),
         (self.viewModel.onMissionClick, self.__onOpenProgression),
         (self.__comp7LightProgressionController.onProgressPointsUpdated, self._updateViewModel))

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.comp7_light.mono.lobby.tooltips.battle_quest_tooltip():
            questId = event.getArgument('questID', '')
            battleQuest = self.__comp7LightProgressionController.getProgressionData()['battleQuests'].get(questId)
            return BattleQuestTooltip(battleQuest)
        if contentID == R.views.comp7_light.mono.lobby.tooltips.all_quests_done_tooltip():
            return BattleQuestsDoneTooltip()
        if contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)
        return super(ProgressionQuestsPresenter, self).createToolTipContent(event=event, contentID=contentID)

    def _finalize(self):
        super(ProgressionQuestsPresenter, self)._finalize()
        self.stopGlobalListening()

    def _updateViewModel(self):
        self.queueUpdate()

    def _rawUpdate(self):
        super(ProgressionQuestsPresenter, self)._rawUpdate()
        with self.viewModel.transaction() as vm:
            battleQuests = self.__comp7LightProgressionController.getProgressionData()
            modelQuests = vm.getQuests()
            modelQuests.clear()
            for questId in battleQuests['questsOrder']:
                modelQuests.addViewModel(self.__updateBattleQuestData(battleQuests['battleQuests'][questId]))

            modelQuests.invalidate()

    def __updateBattleQuestData(self, quest):
        model = WidgetQuestModel()
        model.setId(quest.getID())
        model.setMissionType('battleQuest')
        bonusPacker = getComp7LightBonusPacker()
        packedBonuses, _ = packQuestBonuses(quest.getBonuses(), bonusPacker)
        fillViewModelsArray(packedBonuses, model.getBonuses())
        packMissionItem(model, quest, DailyQuestUIDataPacker)
        lastSeenProgress, isQuestAnimationSeen = getLastSeenQuestData(quest.getID())
        model.setAnimateCompletion(not isQuestAnimationSeen and model.getIsCompleted())
        if not isQuestAnimationSeen:
            model.setEarned(model.getCurrentProgress() - lastSeenProgress)
        return model

    def __onMarkAsViewed(self):
        battleQuests = self.__comp7LightProgressionController.getProgressionData()
        for questID in battleQuests['questsOrder']:
            model = WidgetQuestModel()
            isCompleted, lastSeenProgress = packMissionItem(model, battleQuests['battleQuests'][questID], DailyQuestUIDataPacker)
            setLastSeenQuestData(questID, (lastSeenProgress, True))
            _, showCompletedAnimation = getLastSeenQuestData(questID)
            if showCompletedAnimation and not isCompleted:
                setLastSeenQuestData(questID, (lastSeenProgress, False))

    def __onOpenProgression(self):
        return showComp7LightProgressionView()
