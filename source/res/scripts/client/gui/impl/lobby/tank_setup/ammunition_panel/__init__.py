# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/ammunition_panel/__init__.py
from gui.Scaleform.daapi.view.lobby.bob.bob_ammunition_panel_view import BobAmmunitionPanelView
from gui.shared.system_factory import registerAmmunitionPanelView
from gui.impl.lobby.tank_setup.comp7.ammunition_panel import Comp7AmmunitionPanelView
registerAmmunitionPanelView(Comp7AmmunitionPanelView)
registerAmmunitionPanelView(BobAmmunitionPanelView)
