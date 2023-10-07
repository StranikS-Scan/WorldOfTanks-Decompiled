# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/views/welcome_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from frontline.gui.impl.gen.view_models.views.lobby.views.welcome_view_model import WelcomeViewModel

class WelcomeView(ViewImpl):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self):
        settings = ViewSettings(R.views.frontline.lobby.WelcomeView(), ViewFlags.VIEW, WelcomeViewModel())
        super(WelcomeView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WelcomeView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WelcomeView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as vm:
            self.__updateVehiclesSlide(vm.vehiclesSlide)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onViewClose),)

    def __onViewClose(self):
        self.destroyWindow()

    def __updateVehiclesSlide(self, vehicleSlideModel):
        validVehicleLevels = self.__epicController.getValidVehicleLevels()
        validVehicleLevels.sort()
        vehicleSlideModel.setFromLevel(validVehicleLevels[0])
        vehicleSlideModel.setToLevel(validVehicleLevels[-1])


class WelcomeViewWindow(WindowImpl):

    def __init__(self):
        super(WelcomeViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.FULLSCREEN_WINDOW, content=WelcomeView())
