# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/impl/lobby/tank_academy/tank_academy_exchange_rewards.py
from functools import partial
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.pub.dialog_window import DialogButtons
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.tank_academy_exchange_rewards_model import TankAcademyExchangeRewardsModel

class TankAcademyExchangeRewards(FullScreenDialogBaseView):
    __slots__ = ()

    def __init__(self, vehicleName, vehicleUserName, vehiclesLevel):
        settings = ViewSettings(R.views.tank_academy.lobby.tank_academy.TankAcademyExchangeRewards())
        settings.model = TankAcademyExchangeRewardsModel()
        settings.args = (vehicleName, vehicleUserName, vehiclesLevel)
        super(TankAcademyExchangeRewards, self).__init__(settings)

    @property
    def viewModel(self):
        return super(TankAcademyExchangeRewards, self).getViewModel()

    def _onLoading(self, vehicleName, vehicleUserName, vehiclesLevel):
        super(TankAcademyExchangeRewards, self)._onLoading()
        with self.viewModel.transaction() as tx:
            tx.setVehicleName(vehicleName)
            tx.setVehicleUserName(vehicleUserName)
            tx.setLevel(vehiclesLevel)

    def _getEvents(self):
        return ((self.viewModel.onConfirm, partial(self._setResult, DialogButtons.SUBMIT)), (self.viewModel.onClose, partial(self._setResult, DialogButtons.CANCEL)))
