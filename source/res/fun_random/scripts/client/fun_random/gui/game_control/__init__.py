# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/game_control/__init__.py
from fun_random.gui.game_control.awards_controller import FunProgressionQuestsHandler, FunRandomLootBoxAutoOpenHandler
from gui.shared.system_factory import registerAwardControllerHandler

def registerFunRandomAwardControllers():
    registerAwardControllerHandler(FunProgressionQuestsHandler)
    registerAwardControllerHandler(FunRandomLootBoxAutoOpenHandler)
