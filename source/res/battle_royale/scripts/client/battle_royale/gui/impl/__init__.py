# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/__init__.py
from battle_royale.gui.impl.lobby.tank_setup.ammunition_panel import BattleRoyaleAmmunitionPanelView
from gui.shared.system_factory import registerAmmunitionPanelView

def registerBRViews():
    registerAmmunitionPanelView(BattleRoyaleAmmunitionPanelView)
