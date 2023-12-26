# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/dialogs/challenge/discount_dialog.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.dialogs.challenge.discount_dialog_model import DiscountDialogModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.pub.dialog_window import DialogButtons

class DiscountDialogView(FullScreenDialogBaseView):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.dialogs.challenge.DiscountDialog())
        settings.args = args
        settings.kwargs = kwargs
        settings.model = DiscountDialogModel()
        super(DiscountDialogView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(DiscountDialogView, self).getViewModel()

    def _onLoading(self, vehicle, discountValue, *args, **kwargs):
        super(DiscountDialogView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            tx.vehicleInfo.setIsElite(vehicle.isElite)
            tx.vehicleInfo.setVehicleName(vehicle.shortUserName)
            tx.vehicleInfo.setVehicleType(vehicle.type)
            tx.setDiscountInPercent(discountValue)

    def _getEvents(self):
        return ((self.viewModel.onAccept, self._onAccept), (self.viewModel.onCancel, self._onCancel))

    def _onAccept(self):
        self._setResult(DialogButtons.SUBMIT)

    def _onCancel(self):
        self._setResult(DialogButtons.CANCEL)
