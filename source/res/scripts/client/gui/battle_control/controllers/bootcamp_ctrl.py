# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/bootcamp_ctrl.py
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from helpers import dependency
from skeletons.gui.game_control import IGameSessionController
from bootcamp.BootCampEvents import g_bootcampEvents

class BootcampController(IArenaVehiclesController):
    gameSession = dependency.descriptor(IGameSessionController)

    def __init__(self):
        super(BootcampController, self).__init__()

    def getControllerID(self):
        return None

    def arenaLoadCompleted(self):
        g_bootcampEvents.onArenaLoadCompleted()
