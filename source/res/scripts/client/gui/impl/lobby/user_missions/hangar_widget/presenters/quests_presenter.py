# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/presenters/quests_presenter.py
from frameworks.wulf import Array
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.widget.quests_list_model import QuestsListModel
from gui.impl.gen.view_models.views.lobby.user_missions.widget.widget_quest_model import WidgetQuestModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.impl.lobby.user_missions.hangar_widget.overlap_ctrl import OverlapCtrlMixin
from gui.impl.lobby.user_missions.hangar_widget.providers.user_mission_item import MissionItem
from gui.impl.lobby.user_missions.hangar_widget.tooltip_positioner import TooltipPositionerMixin
from gui.impl.lobby.user_missions.hangar_widget.user_misson_controller import MissionController
from gui.impl.lobby.user_missions.hangar_widget.utils import getCountdown
from gui.impl.lobby.user_missions.tooltips.all_quests_done_tooltip import AllQuestsDoneTooltip
from gui.impl.lobby.user_missions.tooltips.quest_tooltip import DailyQuestTooltip, WeeklyQuestTooltip
from gui.impl.pub.view_component import ViewComponent
from gui.prb_control.entities.listener import IGlobalListener
from gui.server_events.events_dispatcher import showDailyQuests
from gui.shared.missions.packers.events import packQuestBonusModel
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.server_events import IEventsCache

class QuestsPresenter(TooltipPositionerMixin, OverlapCtrlMixin, ViewComponent[QuestsListModel], IGlobalListener):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        self._missionController = MissionController()
        super(QuestsPresenter, self).__init__(model=QuestsListModel)

    @property
    def viewModel(self):
        return super(QuestsPresenter, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.mono.user_missions.tooltips.daily_quest_tooltip():
            quest = self._getQuestFromEvent(event)
            self._updateCurrentMissionCountDown(quest)
            return DailyQuestTooltip(quest)
        if contentID == R.views.mono.user_missions.tooltips.weekly_quest_tooltip():
            quest = self._getQuestFromEvent(event)
            return WeeklyQuestTooltip(quest)
        if contentID == R.views.mono.user_missions.tooltips.all_quests_done_tooltip():
            return AllQuestsDoneTooltip()
        if contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)
        return super(QuestsPresenter, self).createToolTipContent(event=event, contentID=contentID)

    def _getQuestFromEvent(self, event):
        quests = self._missionController.getSortedQuests()
        quest = next((q for q in quests if q.itemId == event.getArgument('questID', '')), None)
        return quest

    def onPrbEntitySwitched(self):
        if self._isFinalized:
            return
        self._missionController.refresh()

    def _subscribe(self):
        super(QuestsPresenter, self)._subscribe()
        self.startGlobalListening()

    def _unsubscribe(self):
        super(QuestsPresenter, self)._unsubscribe()
        self.stopGlobalListening()

    def _getEvents(self):
        return super(QuestsPresenter, self)._getEvents() + ((self.viewModel.onMissionClick, self.__onMissionClick), (self.viewModel.onMarkAsViewed, self.__onMarkAsViewed), (self._missionController.onChanged, self._onChanged))

    def _onLoading(self, *args, **kwargs):
        self.initOverlapCtrl()
        super(QuestsPresenter, self)._onLoading(*args, **kwargs)
        self._updateViewModel()

    def _finalize(self):
        super(QuestsPresenter, self)._finalize()
        self._missionController.destroy()
        self._missionController = None
        return

    def _onChanged(self):
        self._updateViewModel()

    def _updateCurrentMissionCountDown(self, missionItem):
        if missionItem.itemType == 'bonus':
            with self.viewModel.transaction() as vm:
                modelQuests = vm.getQuests()
                item = findFirst(lambda i: i.getId() == missionItem.itemId, modelQuests)
                if item:
                    item.setCountdown(getCountdown(missionItem))
                    modelQuests.invalidate()

    def _rawUpdate(self):
        super(QuestsPresenter, self)._rawUpdate()
        with self.viewModel.transaction() as vm:
            quests = self._missionController.getSortedQuests()
            modelQuests = vm.getQuests()
            modelQuests.clear()
            modelQuests.reserve(len(quests))
            for quest in quests:
                modelQuests.addViewModel(self._getModel(quest))

            modelQuests.invalidate()

    def _updateViewModel(self):
        self.queueUpdate()

    def _getModel(self, data):
        model = WidgetQuestModel()
        model.setId(data.itemId)
        model.setAnimationId(data.getAnimationId())
        model.setMissionType(str(data.itemType))
        model.setCountdown(int(data.countdown))
        missionPacker = data.getMissionPacker()
        missionPacker.packMissionItem(model, data.rawData)
        missionPacker.packSpecificMissionItem(model, data)
        self._packBonuses(model, data.rawData, data.getBonusPacker(), data.getRewardsSortFunc())
        return model

    def _packBonuses(self, model, data, bonusPacker, sort):
        bonuses = model.getBonuses()
        bonuses.clear()
        packQuestBonusModel(quest=data, packer=bonusPacker, array=bonuses, sort=sort)

    @args2params(str)
    def __onMissionClick(self, questId):
        showDailyQuests(questId=questId)

    def __onMarkAsViewed(self):
        for quest in self._missionController.getSortedQuests():
            self.eventsCache.questsProgress.markQuestProgressAsViewed(quest.itemId)
