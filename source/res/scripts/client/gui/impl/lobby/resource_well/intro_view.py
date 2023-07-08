# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/resource_well/intro_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.resource_well.intro_view_model import IntroViewModel
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.resource_well.resource_well_helpers import setIntroShown
from gui.resource_well.sounds import RESOURCE_WELL_SOUND_SPACE
from gui.shared.event_dispatcher import showBrowserOverlayView, showResourceWellProgressionWindow, showHangar
from helpers import dependency
from skeletons.gui.game_control import IResourceWellController
from tutorial.control.game_vars import getVehicleByIntCD

class IntroView(ViewImpl):
    __slots__ = ('__backCallback',)
    _COMMON_SOUND_SPACE = RESOURCE_WELL_SOUND_SPACE
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self, layoutID, backCallback):
        settings = ViewSettings(R.views.lobby.resource_well.IntroView())
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = IntroViewModel()
        self.__backCallback = backCallback
        super(IntroView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(IntroView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(IntroView, self)._onLoading(*args, **kwargs)
        setIntroShown()
        with self.viewModel.transaction() as model:
            fillVehicleInfo(model.vehicleInfo, getVehicleByIntCD(self.__resourceWell.getRewardVehicle()))
            self.__fillEventInfo(model=model)

    def _onLoaded(self, *args, **kwargs):
        super(IntroView, self)._onLoaded(*args, **kwargs)
        self.__showVideo()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.viewModel.showVideo, self.__showVideo), (self.__resourceWell.onEventUpdated, self.__onEventStateUpdated))

    @replaceNoneKwargsModel
    def __fillEventInfo(self, model=None):
        model.setTopRewardPlayersCount(self.__resourceWell.getRewardLimit(isTop=True))
        model.setRegularRewardVehiclesCount(self.__resourceWell.getRewardLimit(isTop=False))

    def __showVideo(self):
        showBrowserOverlayView(GUI_SETTINGS.resourceWellIntroVideoUrl, VIEW_ALIAS.WEB_VIEW_TRANSPARENT)

    def __onClose(self):
        self.destroyWindow()
        showResourceWellProgressionWindow(backCallback=self.__backCallback)

    def __onEventStateUpdated(self):
        if not self.__resourceWell.isActive():
            self.destroyWindow()
            showHangar()
