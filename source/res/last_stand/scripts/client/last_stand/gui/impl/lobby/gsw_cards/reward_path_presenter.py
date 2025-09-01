# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/gsw_cards/reward_path_presenter.py
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.reward_path_view_model import RewardPathViewModel
from last_stand.gui.shared.event_dispatcher import showRewardPathView
from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController

class RewardPathCardPresenter(ViewComponent[RewardPathViewModel]):
    lsArtifactsCtrl = dependency.descriptor(ILSArtefactsController)

    def __init__(self):
        super(RewardPathCardPresenter, self).__init__(model=RewardPathViewModel)

    def _onLoading(self, *args, **kwargs):
        super(RewardPathCardPresenter, self)._onLoading()
        self.__fillMetaWidget()

    def _getEvents(self):
        return ((self.lsArtifactsCtrl.onArtefactStatusUpdated, self.__onArtefactStatusUpdated), (self.getViewModel().onClick, self.__onClick))

    def __onClick(self):
        showRewardPathView()

    def __fillMetaWidget(self):
        with self.getViewModel().transaction() as tx:
            maxProgress = self.lsArtifactsCtrl.getMaxArtefactsProgress()
            currentProgress = self.lsArtifactsCtrl.getCurrentArtefactProgress()
            tx.setMaxProgress(maxProgress)
            tx.setCurrentProgress(currentProgress)
            tx.setIsCompleted(currentProgress >= maxProgress)

    def __onArtefactStatusUpdated(self, _):
        self.__fillMetaWidget()
