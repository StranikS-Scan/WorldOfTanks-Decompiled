# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/game_control/__init__.py
from fun_random.gui.game_control.awards_controller import FunProgressionQuestsHandler
from fun_random.gui.game_control.fun_random_controller import FunRandomController
from skeletons.gui.game_control import IFunRandomController
from gui.shared.system_factory import registerGameControllers, registerAwardControllerHandler

def registerFunRandomGameControllers():
    registerGameControllers(((IFunRandomController, FunRandomController, True),))
    registerAwardControllerHandler(FunProgressionQuestsHandler)
