# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/epic_game_controllers.py
from frontline.battle_controller import EpicBattleController
from gui.shared.system_factory import registerGameControllers
from skeletons.gui.game_control import IEpicBattleController

def register():
    registerGameControllers([(IEpicBattleController, EpicBattleController, False)])
