# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/lobby/feature/no_serial_vehicles_confirm.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.sounds.filters import switchHangarFilteredFilter
from helpers import dependency
from resource_well.gui.feature.resource_well_helpers import fillVehicleCounter
from resource_well.gui.impl.gen.view_models.views.lobby.no_serial_vehicles_confirm_model import NoSerialVehiclesConfirmModel
from resource_well.gui.impl.lobby.feature.sounds import RESOURCE_WELL_SOUND_SPACE
from skeletons.gui.resource_well import IResourceWellController

class NoSerialVehiclesConfirm(FullScreenDialogView):
    _COMMON_SOUND_SPACE = RESOURCE_WELL_SOUND_SPACE
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self, rewardID, *args, **kwargs):
        settings = ViewSettings(R.views.resource_well.lobby.feature.NoSerialVehiclesConfirm(), model=NoSerialVehiclesConfirmModel(), args=args, kwargs=kwargs)
        super(NoSerialVehiclesConfirm, self).__init__(settings)
        self.__rewardID = rewardID
        self.__additionalData = {}

    @property
    def viewModel(self):
        return super(NoSerialVehiclesConfirm, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(NoSerialVehiclesConfirm, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            fillVehicleCounter(self.__rewardID, vehicleCounterModel=model.vehicleCounter, resourceWell=self.__resourceWell)
            model.setVehicleName(self.__resourceWell.getRewardVehicle(self.__rewardID).shortUserName)
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
        self.__resourceWell.onSettingsChanged += self.__onEventStateUpdated

    def _removeListeners(self):
        self.viewModel.confirm -= self._onAccept
        self.viewModel.cancel -= self.__onCancelAction
        self.viewModel.close -= self.__onCancelAction
        self.__resourceWell.onNumberRequesterUpdated -= self.__onNumberRequesterUpdated
        self.__resourceWell.onEventUpdated -= self.__onEventStateUpdated
        self.__resourceWell.onSettingsChanged -= self.__onEventStateUpdated

    def _getAdditionalData(self):
        return self.__additionalData

    def _setBaseParams(self, model):
        pass

    def __onNumberRequesterUpdated(self):
        with self.viewModel.transaction() as model:
            fillVehicleCounter(self.__rewardID, vehicleCounterModel=model.vehicleCounter, resourceWell=self.__resourceWell)

    def __onEventStateUpdated(self):
        if not self.__resourceWell.isActive():
            self._onCancel()

    def __onCancelAction(self):
        self.__additionalData['isUserCancelAction'] = True
        self._onCancel()
