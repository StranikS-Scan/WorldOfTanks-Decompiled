# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/lobby/feature/no_vehicles_confirm.py
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.event_dispatcher import showHangar
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.sounds.filters import switchHangarFilteredFilter
from helpers import dependency
from resource_well.gui.impl.gen.view_models.views.lobby.no_vehicles_confirm_model import NoVehiclesConfirmModel
from resource_well.gui.impl.lobby.feature.sounds import RESOURCE_WELL_SOUND_SPACE
from skeletons.gui.resource_well import IResourceWellController

class NoVehiclesConfirm(ViewImpl):
    __slots__ = ()
    _COMMON_SOUND_SPACE = RESOURCE_WELL_SOUND_SPACE
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self):
        settings = ViewSettings(R.views.resource_well.lobby.feature.NoVehiclesConfirm(), model=NoVehiclesConfirmModel())
        super(NoVehiclesConfirm, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NoVehiclesConfirm, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(NoVehiclesConfirm, self)._onLoading(*args, **kwargs)
        switchHangarFilteredFilter(on=True)

    def _finalize(self):
        switchHangarFilteredFilter(on=False)
        super(NoVehiclesConfirm, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.showHangar, self.__showHangar), (self.__resourceWell.onEventUpdated, self.__onEventStateUpdated), (self.__resourceWell.onSettingsChanged, self.__onEventStateUpdated))

    def __showHangar(self):
        self.destroyWindow()
        showHangar()

    def __onEventStateUpdated(self):
        if not self.__resourceWell.isActive():
            self.destroyWindow()
            showHangar()


class NoVehiclesConfirmWindow(LobbyWindow):

    def __init__(self, parent=None):
        super(NoVehiclesConfirmWindow, self).__init__(wndFlags=WindowFlags.DIALOG | WindowFlags.WINDOW_FULLSCREEN, content=NoVehiclesConfirm(), parent=parent)
        self.__blur = CachedBlur(enabled=True, ownLayer=self.layer)

    def _finalize(self):
        self.__blur.fini()
        super(NoVehiclesConfirmWindow, self)._finalize()
