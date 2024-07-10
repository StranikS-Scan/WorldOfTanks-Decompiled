# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/tank_setup/qfg_ammunition_panel.py
from frameworks.wulf import ViewFlags
from fun_random.gui.impl.gen.view_models.views.lobby.feature.fun_random_qfg_ammunition_panel_view_model import FunRandomQfgAmmunitionPanelViewModel
from gui.impl.gen import R
from gui.impl.lobby.tank_setup.ammunition_panel.hangar_view import HangarAmmunitionPanelView
FUN_RANDOM_QUICK_FIRE_GUNS = 'FunRandomQuickFireGuns'

class FunRandomQuickFireGunsAmmunitionPanelView(HangarAmmunitionPanelView):

    def __init__(self, layoutID=None, flags=ViewFlags.VIEW, model=None):
        super(FunRandomQuickFireGunsAmmunitionPanelView, self).__init__(layoutID=layoutID or R.views.fun_random.lobby.feature.FunRandomQuickFireGunsAmmunitionPanelView(), flags=flags, model=model or FunRandomQfgAmmunitionPanelViewModel())

    def _onLoaded(self, *args, **kwargs):
        super(FunRandomQuickFireGunsAmmunitionPanelView, self)._onLoaded(*args, **kwargs)
        self.viewModel.setModeName(FUN_RANDOM_QUICK_FIRE_GUNS)
