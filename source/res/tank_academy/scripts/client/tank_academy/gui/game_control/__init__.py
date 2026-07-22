# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/game_control/__init__.py
from skeletons.gui.game_control import ITankAcademyController
from gui.shared.system_factory import registerGameControllers, registerAwardControllerHandlers
from tank_academy.gui.game_control.tank_academy_controller import TankAcademyController
from tank_academy.gui.game_control.awards_controller import TankAcademyQuestsHandler

def registerTAGameControllers():
    registerGameControllers([(ITankAcademyController, TankAcademyController, True)])


def registerTAAwardControllers():
    registerAwardControllerHandlers([TankAcademyQuestsHandler])
