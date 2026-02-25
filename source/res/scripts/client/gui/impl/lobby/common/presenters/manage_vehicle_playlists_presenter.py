# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/common/presenters/manage_vehicle_playlists_presenter.py
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.impl.gen.view_models.views.lobby.hangar.manageable_vehicle_playlists_model import ManageableVehiclePlaylistsModel
from gui.impl.gui_decorators import args2params
from gui.impl.pub.view_component import ViewComponent
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import HangarVehicleEvent
from helpers import dependency
from skeletons.gui.game_control import IVehiclePlaylistsController

class ManageableVehiclePlaylistsPresenter(ViewComponent[ManageableVehiclePlaylistsModel], EventSystemEntity):
    __vehiclePlaylistsCtrl = dependency.descriptor(IVehiclePlaylistsController)

    def __init__(self):
        super(ManageableVehiclePlaylistsPresenter, self).__init__(model=ManageableVehiclePlaylistsModel)

    @property
    def viewModel(self):
        return super(ManageableVehiclePlaylistsPresenter, self).getViewModel()

    def _getListeners(self):
        return ((HangarVehicleEvent.ON_CONTEXT_MENU_CLICKED, self.__handleContextMenuClicked, EVENT_BUS_SCOPE.LOBBY),)

    def _onLoading(self, *args, **kwargs):
        self.__updateModel(self.viewModel.INVALID_VEHICLE_INTCD)
        super(ManageableVehiclePlaylistsPresenter, self)._onLoading()

    def _getEvents(self):
        return ((self.viewModel.onReset, self.__onClose), (self.viewModel.onSelectVehicle, self.__onSelectVehicle))

    def __handleContextMenuClicked(self, event=None):
        self.__updateModel(event.ctx.get('vehicleIntCD'))

    def __onClose(self):
        self.__updateModel(self.viewModel.INVALID_VEHICLE_INTCD)

    @args2params(int)
    def __onSelectVehicle(self, id):
        self.__updateModel(id)

    def __updateModel(self, intCD):
        with self.viewModel as model:
            model.setIntCD(intCD if intCD else self.viewModel.INVALID_VEHICLE_INTCD)
