# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/lobby/awards/confirm_selection_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.shared.view_helpers.blur_manager import CachedBlur
from one_time_gift.gui.impl.gen.view_models.views.lobby.confirm_selection_view_model import ConfirmSelectionViewModel
from gui.impl.pub.dialog_window import DialogButtons
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class ConfirmSelectionView(FullScreenDialogBaseView):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.one_time_gift.mono.lobby.confirm_selection_view(), model=ConfirmSelectionViewModel(), args=args, kwargs=kwargs)
        self.__blur = None
        super(ConfirmSelectionView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getEvents(self):
        return super(ConfirmSelectionView, self)._getEvents() + ((self.viewModel.onConfirm, self.__onConfirm), (self.viewModel.onClose, self.__onClose))

    def _finalize(self):
        if self.__blur is not None:
            self.__blur.fini()
            self.__blur = None
        super(ConfirmSelectionView, self)._finalize()
        return

    def _onLoading(self, vehCDs, *args, **kwargs):
        super(ConfirmSelectionView, self)._onLoading(*args, **kwargs)
        self.__blur = CachedBlur(enabled=True, ownLayer=self.getParentWindow().layer - 1, uiBlurRadius=40, blurAnimRepeatCount=20)
        vehicles = []
        for vehCD in vehCDs:
            vehicle = self.__itemsCache.items.getItemByCD(vehCD)
            if vehicle is not None:
                vehicles.append(vehicle)

        if not vehicles:
            return
        else:
            vehicles = sorted(vehicles, key=lambda v: v.level)
            with self.viewModel.transaction() as vm:
                obtainedVehicles = vm.getObtainedVehicles()
                obtainedVehicles.clear()
                creditedVehicles = vm.getCreditedVehicles()
                creditedVehicles.clear()
                for vehicle in vehicles:
                    vehicleModel = VehicleModel()
                    fillVehicleModel(vehicleModel, vehicle)
                    if vehicle.isPurchased:
                        obtainedVehicles.addViewModel(vehicleModel)
                    vehicleModel.setIsPremium(True)
                    creditedVehicles.addViewModel(vehicleModel)

                obtainedVehicles.invalidate()
                creditedVehicles.invalidate()
                vm.setBranchName(vehicles[-1].descriptor.type.shortUserString)
            return

    def __onConfirm(self):
        self._setResult(DialogButtons.SUBMIT)

    def __onClose(self):
        self._setResult(DialogButtons.CANCEL)
