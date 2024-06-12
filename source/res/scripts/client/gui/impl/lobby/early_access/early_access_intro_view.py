# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/early_access/early_access_intro_view.py
from account_helpers.AccountSettings import AccountSettings, EarlyAccess
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.lobby.early_access.early_access_window_events import showEarlyAccessQuestsView, showEarlyAccessVehicleView
from gui.impl.gen.view_models.views.lobby.early_access.early_access_intro_view_model import EarlyAccessIntroViewModel
from gui.impl.lobby.early_access.sounds import EARLY_ACCESS_INTRO_SOUND_SPACE
from gui.impl.pub import ViewImpl, WindowImpl
from helpers import dependency
from skeletons.gui.game_control import IEarlyAccessController

class EarlyAccessIntroView(ViewImpl):
    __slots__ = ('__isNextVehicleView',)
    __earlyAccessController = dependency.descriptor(IEarlyAccessController)
    _COMMON_SOUND_SPACE = EARLY_ACCESS_INTRO_SOUND_SPACE

    def __init__(self, layoutID, isNextVehicleView=True):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = EarlyAccessIntroViewModel()
        self.__isNextVehicleView = isNextVehicleView
        super(EarlyAccessIntroView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EarlyAccessIntroView, self).getViewModel()

    def _onLoaded(self, *args, **kwargs):
        super(EarlyAccessIntroView, self)._onLoaded(*args, **kwargs)
        AccountSettings.setEarlyAccess(EarlyAccess.INTRO_SEEN, True)

    def _onLoading(self, *args, **kwargs):
        super(EarlyAccessIntroView, self)._onLoading(*args, **kwargs)
        self.__updateModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onCloseView), (self.viewModel.onContinue, self.__onGoToNextView))

    def __updateModel(self):
        with self.viewModel.transaction() as model:
            startDate, endDate = self.__earlyAccessController.getSeasonInterval()
            model.setStartDate(startDate)
            model.setEndDate(endDate)

    def __onCloseView(self):
        self.destroyWindow()
        self.__onGoToNextView()

    def __onGoToNextView(self):
        self.destroyWindow()
        if self.__isNextVehicleView:
            showEarlyAccessVehicleView()
        else:
            showEarlyAccessQuestsView()


class EarlyAccessIntroViewWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, isNextVehicleView, parent=None):
        super(EarlyAccessIntroViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=EarlyAccessIntroView(R.views.lobby.early_access.EarlyAccessIntroView(), isNextVehicleView), parent=parent)
