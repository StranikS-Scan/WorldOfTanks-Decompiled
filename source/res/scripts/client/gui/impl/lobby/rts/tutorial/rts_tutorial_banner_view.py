# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/tutorial/rts_tutorial_banner_view.py
from RTSShared import RTSBootcampMatchmakerState
from gui.impl.gen.view_models.views.lobby.rts.tutorial_banner_view_model import TutorialBannerViewModel
from helpers import dependency
from gui.impl.pub import ViewImpl
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from frameworks.wulf.gui_constants import ViewFlags
from skeletons.gui.game_control import IRTSBattlesController
from gui.impl.lobby.rts.tutorial.rts_tutorial_helpers import showInvitationDialog

class RTSTutorialBannerView(ViewImpl):
    __rtsController = dependency.descriptor(IRTSBattlesController)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.lobby.rts.Tutorial.Banner(), model=TutorialBannerViewModel(), flags=ViewFlags.COMPONENT)
        super(RTSTutorialBannerView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _initialize(self, *args, **kwargs):
        self.__addListeners()

    def _onLoading(self, *args, **kwargs):
        self.__updateViewModel()

    def _finalize(self):
        self.__removeListeners()

    def __addListeners(self):
        with self.viewModel.transaction() as model:
            model.onBannerClick += self.__handleBannerClick
        self.__rtsController.onRtsTutorialBannerUpdate += self.__updateViewModel

    def __removeListeners(self):
        with self.viewModel.transaction() as model:
            model.onBannerClick -= self.__handleBannerClick
        self.__rtsController.onRtsTutorialBannerUpdate -= self.__updateViewModel

    def __handleBannerClick(self):
        if not self.viewModel.getIsDisabled():
            showInvitationDialog()

    def __updateViewModel(self):
        rtsBootcampState = self.__rtsController.getModeSettings().getRTSBootcampMatchmakerState()
        temporaryDisabled = RTSBootcampMatchmakerState.DISABLED_TEMPORARY == rtsBootcampState
        with self.viewModel.transaction() as model:
            model.setIsDisabled(temporaryDisabled)
