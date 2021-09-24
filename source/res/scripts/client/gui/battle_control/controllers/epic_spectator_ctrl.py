# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/epic_spectator_ctrl.py
import Event
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.view_components import IViewComponentsController
from gui.Scaleform.genConsts.EPIC_CONSTS import EPIC_CONSTS

class SPECTATOR_MODE(object):
    FREECAM = EPIC_CONSTS.SPECTATOR_MODE_FREECAM
    FOLLOW = EPIC_CONSTS.SPECTATOR_MODE_FOLLOW
    DEATHCAM = EPIC_CONSTS.SPECTATOR_MODE_DEATHCAM


class SpectatorViewController(IViewComponentsController):

    def __init__(self, setup):
        super(SpectatorViewController, self).__init__()
        self.__plugins = {}
        self.__eManager = Event.EventManager()
        self.__mode = EPIC_CONSTS.SPECTATOR_MODE_DEATHCAM
        self.__vehicleID = None
        self.onSpectatorViewModeChanged = Event.Event(self.__eManager)
        self.onSpectatedVehicleChanged = Event.Event(self.__eManager)
        return

    def setViewComponents(self, *components):
        pass

    spectatorViewMode = property(lambda self: self.__getViewMode())
    spectatedVehicle = property(lambda self: self.__getVehicle())

    def spectatorViewModeChanged(self, mode):
        self.__mode = mode
        self.onSpectatorViewModeChanged(mode)

    def spectatedVehicleChanged(self, vehicleID):
        self.__vehicleID = vehicleID
        self.onSpectatedVehicleChanged(vehicleID)

    def clearViewComponents(self):
        pass

    def getControllerID(self):
        return BATTLE_CTRL_ID.SPECTATOR

    def startControl(self):
        pass

    def stopControl(self):
        self.__eManager.clear()
        self.__eManager = None
        return

    def __getViewMode(self):
        return self.__mode

    def __getVehicle(self):
        return self.__vehicleID
