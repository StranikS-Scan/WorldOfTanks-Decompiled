# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/widget_view.py
from battle_royale.gui.impl.gen.view_models.views.lobby.views.widget_view_model import WidgetViewModel, BattleStatus
from battle_royale_progression.skeletons.game_controller import IBRProgressionOnTokensController
from frameworks.wulf import ViewSettings, ViewFlags
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController

class WidgetView(ViewImpl):
    brProgression = dependency.descriptor(IBRProgressionOnTokensController)
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.battle_royale.lobby.views.WidgetView())
        settings.flags = ViewFlags.VIEW
        settings.model = WidgetViewModel()
        super(WidgetView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WidgetView, self).getViewModel()

    def updateModel(self):
        isInProgress = self.brProgression.isEnabled and not self.brProgression.isFinished
        isPrimeTime = self.__battleRoyaleController.isEnabled() and self.__battleRoyaleController.isInPrimeTime()
        currentStage = 0
        if isInProgress:
            currentStage = self.brProgression.getCurrentStageData().get('currentStage')
        with self.viewModel.transaction() as model:
            model.setCurrentProgression(currentStage)
            model.setBattleStatus(BattleStatus.INPROGRESS if isInProgress or not isPrimeTime else BattleStatus.COMPLETED)

    def _onLoading(self, *args, **kwargs):
        super(WidgetView, self)._onLoading(args, kwargs)
        self.brProgression.onProgressPointsUpdated += self.__onProgressionUpdated
        self.brProgression.onSettingsChanged += self.__onProgressionUpdated
        self.__battleRoyaleController.onPrimeTimeStatusUpdated += self.__onPrimeTimeStatusUpdated
        self.updateModel()

    def _finalize(self):
        self.brProgression.onProgressPointsUpdated -= self.__onProgressionUpdated
        self.brProgression.onSettingsChanged -= self.__onProgressionUpdated
        self.__battleRoyaleController.onPrimeTimeStatusUpdated -= self.__onPrimeTimeStatusUpdated
        super(WidgetView, self)._finalize()

    def __onPrimeTimeStatusUpdated(self, *args):
        self.updateModel()

    def __onProgressionUpdated(self):
        self.updateModel()
