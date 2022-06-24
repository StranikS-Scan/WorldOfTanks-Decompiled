# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/resource_well/no_serial_vehicles_confirm.py
from frameworks.wulf import ViewSettings
from gui.impl.auxiliary.resource_well_helper import fillVehicleCounter
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.resource_well.no_serial_vehicles_confirm_model import NoSerialVehiclesConfirmModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.resource_well.sounds import RESOURCE_WELL_SOUND_SPACE
from gui.sounds.filters import switchHangarFilteredFilter
from helpers import dependency
from skeletons.gui.game_control import IResourceWellController

class NoSerialVehiclesConfirm(FullScreenDialogView):
    __slots__ = ('__additionalData',)
    _COMMON_SOUND_SPACE = RESOURCE_WELL_SOUND_SPACE
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.resource_well.NoSerialVehiclesConfirm())
        settings.model = NoSerialVehiclesConfirmModel()
        super(NoSerialVehiclesConfirm, self).__init__(settings)
        self.__additionalData = {}

    @property
    def viewModel(self):
        return super(NoSerialVehiclesConfirm, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(NoSerialVehiclesConfirm, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            fillVehicleCounter(vehicleCounterModel=model.vehicleCounter, resourceWell=self.__resourceWell)
            vehicle = self._itemsCache.items.getItemByCD(self.__resourceWell.getRewardVehicle())
            model.setVehicleName(vehicle.userName)
        switchHangarFilteredFilter(on=True)

    def _finalize(self):
        switchHangarFilteredFilter(on=False)
        super(NoSerialVehiclesConfirm, self)._finalize()

    def _addListeners(self):
        self.viewModel.confirm += self._onAccept
        self.viewModel.cancel += self.__onCancelAction
        self.viewModel.close += self.__onCancelAction
        self.__resourceWell.onNumberRequesterUpdated += self.__onNumberRequesterUpdated
        self.__resourceWell.onEventUpdated += self.__onEventStateUpdated

    def _removeListeners(self):
        self.viewModel.confirm -= self._onAccept
        self.viewModel.cancel -= self.__onCancelAction
        self.viewModel.close -= self.__onCancelAction
        self.__resourceWell.onNumberRequesterUpdated -= self.__onNumberRequesterUpdated
        self.__resourceWell.onEventUpdated -= self.__onEventStateUpdated

    def _getAdditionalData(self):
        return self.__additionalData

    def _setBaseParams(self, model):
        pass

    def __onNumberRequesterUpdated(self):
        with self.viewModel.transaction() as model:
            fillVehicleCounter(vehicleCounterModel=model.vehicleCounter, resourceWell=self.__resourceWell)

    def __onEventStateUpdated(self):
        if not self.__resourceWell.isActive():
            self._onCancel()

    def __onCancelAction(self):
        self.__additionalData['isUserCancelAction'] = True
        self._onCancel()
