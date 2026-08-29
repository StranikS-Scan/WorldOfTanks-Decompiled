# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/extension_stubs/museum_of_glory_controller.py
import typing
import Event
from skeletons.gui.game_control import IMuseumOfGloryController

class MuseumOfGloryController(IMuseumOfGloryController):
    onConfigUpdate = Event.Event()

    @property
    def isEnabled(self):
        return False

    def getEpochMusics(self, year):
        return {}

    def getVehiclesDto(self):
        return []

    def getBackgroundImage(self, year):
        pass

    def getMinYear(self):
        pass
