# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/hangar/presenters/fun_random_progression_quests_presenter.py
from __future__ import absolute_import
import typing
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin, FunProgressionWatcher
from fun_random.gui.feature.util.fun_wrappers import hasActiveProgression
from fun_random.gui.fun_account_settings import FunAccountSettings
from fun_random.gui.impl.gen.view_models.views.lobby.feature.fun_random_progression_quests_model import FunRandomProgressionQuestsModel
from fun_random.gui.impl.lobby.tooltips.fun_random_progression_quest_tooltip_view import FunRandomProgressionQuestTooltipView
from fun_random.gui.impl.lobby.tooltips.fun_random_no_quests_tooltip_view import FunRandomNoQuestsTooltipView
from fun_random.gui.impl.lobby.common.fun_view_helpers import defineProgressionStatus, packProgressionState, packFullProgressionConditions, packFullInfiniteProgressionConditions
from gui.impl.gen import R
from gui.impl.pub.view_component import ViewComponent
from fun_random.gui.impl.lobby.hangar.controllers.fun_random_overlap_controller import FunRandomOverlapCtrlMixin
from gui.impl.lobby.user_missions.hangar_widget.tooltip_positioner import TooltipPositionerMixin
if typing.TYPE_CHECKING:
    from frameworks.wulf import View, ViewEvent

class FunRandomProgressionQuestsPresenter(TooltipPositionerMixin, FunRandomOverlapCtrlMixin, ViewComponent[FunRandomProgressionQuestsModel], FunAssetPacksMixin, FunProgressionWatcher):

    def __init__(self):
        super(FunRandomProgressionQuestsPresenter, self).__init__(model=FunRandomProgressionQuestsModel)

    @property
    def viewModel(self):
        return super(FunRandomProgressionQuestsPresenter, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.fun_random.mono.lobby.tooltips.progression_quest_tooltip():
            return FunRandomProgressionQuestTooltipView(event.getArgument('triggerId'))
        return FunRandomNoQuestsTooltipView() if contentID == R.views.fun_random.mono.lobby.tooltips.base_quest_tooltip() else super(FunRandomProgressionQuestsPresenter, self).createToolTipContent(event, contentID)

    def setDisabledProgression(self):
        self.viewModel.state.setStatus(defineProgressionStatus(None))
        return

    def _onLoading(self, *args, **kwargs):
        self.initOverlapCtrl()
        super(FunRandomProgressionQuestsPresenter, self)._onLoading(*args, **kwargs)
        self.startProgressionListening(self._updateViewModel)
        self._updateViewModel()

    def _finalize(self):
        self.stopProgressionListening(self._updateViewModel)
        super(FunRandomProgressionQuestsPresenter, self)._finalize()

    def _getEvents(self):
        return super(FunRandomProgressionQuestsPresenter, self)._getEvents() + ((self.viewModel.onMissionClick, self.showActiveProgressionPage), (self.viewModel.onMarkAsViewed, self.__onMarkAsViewed))

    @hasActiveProgression()
    def __onMarkAsViewed(self):
        if not self.readyForAnimations:
            return
        progression = self.getActiveProgression()
        for trigger in progression.conditions.triggers:
            triggerId = trigger.getID()
            triggerCompletionSeen = FunAccountSettings.getIsTriggerCompletionSeen(triggerId)
            if trigger.isCompleted() and not triggerCompletionSeen:
                FunAccountSettings.setIsTriggerCompletionSeen(triggerId, True)

    @hasActiveProgression(abortAction='setDisabledProgression')
    def _rawUpdate(self):
        super(FunRandomProgressionQuestsPresenter, self)._rawUpdate()
        with self.viewModel.transaction() as model:
            modeName = self.getModeUserName()
            progression = self.getActiveProgression()
            model.setAssetsPointer(self.getModeAssetsPointer())
            packProgressionState(progression, model.state)
            packFullProgressionConditions(modeName, progression, model.condition)
            if progression.hasUnlimitedProgression:
                packFullInfiniteProgressionConditions(modeName, progression, model.infiniteCondition)
            if progression.isInUnlimitedProgression:
                model.condition.setPrevPoints(progression.conditions.maximumCounter)

    @hasActiveProgression(abortAction='setDisabledProgression')
    def _updateViewModel(self, *_):
        self.queueUpdate()
