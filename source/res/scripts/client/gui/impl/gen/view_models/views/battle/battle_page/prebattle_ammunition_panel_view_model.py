# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/battle_page/prebattle_ammunition_panel_view_model.py
from gui.impl.gen.view_models.views.battle.battle_page.prebattle_ammunition_panel_model import PrebattleAmmunitionPanelModel
from gui.impl.gen.view_models.views.lobby.tank_setup.ammunition_panel_view_model import AmmunitionPanelViewModel

class PrebattleAmmunitionPanelViewModel(AmmunitionPanelViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=1):
        super(PrebattleAmmunitionPanelViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def ammunitionPanel(self):
        return self._getViewModel(6)

    def _initialize(self):
        super(PrebattleAmmunitionPanelViewModel, self)._initialize()
        self._addViewModelProperty('ammunitionPanel', PrebattleAmmunitionPanelModel())
