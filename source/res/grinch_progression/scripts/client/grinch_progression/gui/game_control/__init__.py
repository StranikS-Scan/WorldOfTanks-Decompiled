# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/game_control/__init__.py
from gui.shared.system_factory import registerGameControllers
from grinch_progression.gui.game_control.grinch_progression_controller import GrinchProgressionController

def registerGrinchProgressionGameControllers():
    from grinch_progression.skeletons.game_controller import IGrinchProgressionController
    registerGameControllers([(IGrinchProgressionController, GrinchProgressionController, False)])
