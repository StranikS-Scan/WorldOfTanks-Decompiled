# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/game_control/__init__.py
from gui.shared.system_factory import registerGameControllers
from mt_birthday.gui.game_control.last_battles_players_controller import LastBattlesPlayersController
from mt_birthday.gui.game_control.mt_birthday_controller import TanksBirthdayController
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController, ILastBattlesPlayersController

def registerTanksBirthdayControllers():
    registerGameControllers([(ITanksBirthdayController, TanksBirthdayController, False), (ILastBattlesPlayersController, LastBattlesPlayersController, False)])
