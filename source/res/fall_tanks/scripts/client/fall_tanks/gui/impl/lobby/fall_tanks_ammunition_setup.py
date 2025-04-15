# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/impl/lobby/fall_tanks_ammunition_setup.py
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tank_setup.ammunition_setup.hangar import HangarAmmunitionSetupView
from fall_tanks.gui.impl.lobby.fall_tanks_ammunition_panel import FallTanksAmmunitionPanel

class FallTanksAmmunitionSetupView(HangarAmmunitionSetupView):
    __slots__ = ()

    def _createAmmunitionPanel(self):
        ctx = {'specializationClickable': True}
        return FallTanksAmmunitionPanel(self.viewModel.ammunitionPanel, self._vehItem.getItem(), ctx=ctx)

    def _onPanelSelected(self, args):
        if args.get('selectedSection') not in (TankSetupConstants.SHELLS, TankSetupConstants.CONSUMABLES):
            super(FallTanksAmmunitionSetupView, self)._onPanelSelected(args)
