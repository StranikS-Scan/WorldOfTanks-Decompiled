# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/resource_well/no_vehicles_confirm.py
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.resource_well.no_vehicles_confirm_model import NoVehiclesConfirmModel
from gui.impl.pub import ViewImpl, WindowImpl
from gui.resource_well.sounds import RESOURCE_WELL_SOUND_SPACE
from gui.shared.event_dispatcher import showHangar
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.sounds.filters import switchHangarFilteredFilter
from helpers import dependency
from skeletons.gui.game_control import IResourceWellController

class NoVehiclesConfirm(ViewImpl):
    __slots__ = ()
    _COMMON_SOUND_SPACE = RESOURCE_WELL_SOUND_SPACE
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.resource_well.NoVehiclesConfirm())
        settings.model = NoVehiclesConfirmModel()
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
        return ((self.viewModel.showHangar, self.__showHangar),)

    def __showHangar(self):
        showHangar()
        self.destroyWindow()

    def __onEventStateUpdated(self):
        if not self.__resourceWell.isActive():
            showHangar()
            self.destroyWindow()


class NoVehiclesConfirmWindow(WindowImpl):
    __slots__ = ('__blur',)

    def __init__(self, parent=None):
        super(NoVehiclesConfirmWindow, self).__init__(wndFlags=WindowFlags.DIALOG | WindowFlags.WINDOW_FULLSCREEN, content=NoVehiclesConfirm(), parent=parent)
        self.__blur = CachedBlur(enabled=True, ownLayer=self.layer)

    def _finalize(self):
        self.__blur.fini()
        super(NoVehiclesConfirmWindow, self)._finalize()
