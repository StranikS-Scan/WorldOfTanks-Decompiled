# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/gsw_cards/reward_path_presenter.py
from __future__ import absolute_import
import typing
from gui.impl.gen import R
from gui.impl.lobby.user_missions.hangar_widget.presenters.base_child_presenter import UserMissionChildPresenter
from gui.impl.lobby.user_missions.hangar_widget.tooltip_positioner import TooltipPositionerMixin
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.reward_path_view_model import RewardPathViewModel
from last_stand.gui.impl.lobby.ls_helpers import fillRewardPathWidgetViewModel
from last_stand.gui.impl.lobby.tooltips.reward_path_tooltip import RewardPathTooltip
from last_stand.gui.impl.lobby.user_missions.hangar_widget.overlap_ctrl import LastStandOverlapCtrlMixin
from last_stand.gui.shared.event_dispatcher import showRewardPathView
from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewEvent, View

class RewardPathCardPresenter(UserMissionChildPresenter, TooltipPositionerMixin, LastStandOverlapCtrlMixin, ViewComponent[RewardPathViewModel]):
    lsArtefactsCtrl = dependency.descriptor(ILSArtefactsController)

    def __init__(self):
        super(RewardPathCardPresenter, self).__init__(model=RewardPathViewModel)

    def _onLoading(self, *args, **kwargs):
        self.initOverlapCtrl()
        super(RewardPathCardPresenter, self)._onLoading(*args, **kwargs)
        self.__fillMetaWidget()

    def _getEvents(self):
        return super(RewardPathCardPresenter, self)._getEvents() + ((self.lsArtefactsCtrl.onArtefactStatusUpdated, self.__onArtefactStatusUpdated), (self.lsArtefactsCtrl.onProgressPointsUpdated, self.__onPointsUpdated), (self.getViewModel().onClick, self.__onClick))

    def createToolTipContent(self, event, contentID):
        return RewardPathTooltip() if contentID == R.views.last_stand.mono.lobby.tooltips.reward_path_tooltip() else super(RewardPathCardPresenter, self).createToolTipContent(event, contentID)

    def __onClick(self):
        showRewardPathView()

    def __fillMetaWidget(self):
        lastUnopenedArtefactId = self.lsArtefactsCtrl.getLastUnopenedArtefactId()
        with self.getViewModel().transaction() as tx:
            fillRewardPathWidgetViewModel(tx, lastUnopenedArtefactId)

    def __onArtefactStatusUpdated(self, _):
        self.__fillMetaWidget()

    def __onPointsUpdated(self):
        self.__fillMetaWidget()
