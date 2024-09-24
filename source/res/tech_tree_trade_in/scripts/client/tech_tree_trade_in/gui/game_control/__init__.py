# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/game_control/__init__.py
from gui.shared.system_factory import registerGameControllers
from tech_tree_trade_in.skeletons.gui.game_control import ITechTreeTradeInController
from tech_tree_trade_in.gui.game_control.tech_tree_trade_in_controller import TechTreeTradeInController

def registerTradeInController():
    registerGameControllers([(ITechTreeTradeInController, TechTreeTradeInController, False)])
