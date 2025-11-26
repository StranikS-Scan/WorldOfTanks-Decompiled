# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/user_missions/hangar_widget/presenters/progression_presenter.py
from battle_royale.gui.impl.gen.view_models.views.lobby.views.widget.progression_model import ProgressionModel, ProgressionStatus
from battle_royale.gui.impl.lobby.tooltips.progression_widget_tooltip import ProgressionWidgetTooltipView
from battle_royale.gui.impl.lobby.views.user_missions.hangar_widget.overlap_ctrl import BattleRoyaleOverlapCtrlMixin
from battle_royale_progression.gui.shared.event_dispatcher import showProgressionView
from battle_royale_progression.skeletons.game_controller import IBRProgressionOnTokensController
from gui.impl.lobby.user_missions.hangar_widget.tooltip_positioner import TooltipPositionerMixin
from gui.impl.gen import R
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency

class BattleRoyaleProgressionPresenter(TooltipPositionerMixin, BattleRoyaleOverlapCtrlMixin, ViewComponent[ProgressionModel]):
    __brProgression = dependency.descriptor(IBRProgressionOnTokensController)

    def __init__(self):
        super(BattleRoyaleProgressionPresenter, self).__init__(model=ProgressionModel)

    @property
    def viewModel(self):
        return super(BattleRoyaleProgressionPresenter, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return ProgressionWidgetTooltipView() if contentID == R.views.battle_royale.mono.lobby.tooltips.progression_widget() else super(BattleRoyaleProgressionPresenter, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        self.initOverlapCtrl()
        super(BattleRoyaleProgressionPresenter, self)._onLoading(*args, **kwargs)
        self.__updateModel()

    def _getEvents(self):
        return super(BattleRoyaleProgressionPresenter, self)._getEvents() + ((self.viewModel.showProgression, self.__onShowProgressionClick),
         (self.viewModel.onProgressionAnimationCompleted, self.__onProgressionAnimationCompleted),
         (self.__brProgression.onProgressPointsUpdated, self.__updateModel),
         (self.__brProgression.onSettingsChanged, self.__updateModel))

    def __updateModel(self):
        with self.viewModel.transaction() as tx:
            if self.__brProgression.isEnabled:
                data = self.__brProgression.getProgessionPointsData()
                tx.setStage(data['stage'])
                tx.setPrevStage(data['prevStage'])
                tx.setCurPoints(data['curPoints'])
                tx.setPrevPoints(data['prevPoints'])
                tx.setStageProgress(data['stageProgress'])
                tx.setPrevStageProgress(data['prevStageProgress'])
                tx.setStagePoints(data['stagePoints'])
                tx.setPrevStagePoints(data['prevStagePoints'])
                tx.setIsCompleted(self.__brProgression.isFinished)
                status = ProgressionStatus.ACTIVE
            else:
                status = ProgressionStatus.DISABLED
            tx.setStatus(status)

    def __onProgressionAnimationCompleted(self):
        self.__brProgression.saveCurPoints()

    def __onShowProgressionClick(self):
        showProgressionView()
