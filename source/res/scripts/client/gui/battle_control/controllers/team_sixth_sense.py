# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/team_sixth_sense.py
import functools
import logging
import BigWorld
from gui.battle_control.arena_info.interfaces import ITeamSixthSenseController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, VEHICLE_VIEW_STATE
from gui.battle_control.view_components import ViewComponentsController
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_DURATION = 6.0
_logger = logging.getLogger(__name__)

class ITeamSixthSenseView(object):

    def sixthSenseActive(self, vehicleID):
        pass

    def sixthSenseNotActive(self, vehicleID):
        pass


class TeamSixthSenseController(ViewComponentsController, ITeamSixthSenseController):
    __slots__ = ('__vehicleToCB',)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(TeamSixthSenseController, self).__init__()
        self.__vehicleToCB = {}

    def startControl(self, *args):
        ctrl = self.__sessionProvider.shared.vehicleState
        ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated

    def stopControl(self):
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        for cbID in self.__vehicleToCB.itervalues():
            if cbID:
                try:
                    BigWorld.cancelCallback(cbID)
                except ValueError:
                    _logger.warning("Couldn't cancel callbackID = %s", cbID)

        self.__vehicleToCB = None
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.TEAM_SIXTH_SENSE

    def setViewComponents(self, *components):
        self._viewComponents = list(components)

    def addRuntimeView(self, view):
        self._viewComponents.append(view)
        for vID in self.__vehicleToCB:
            view.sixthSenseActive(vID)

    def removeRuntimeView(self, view):
        if view in self._viewComponents:
            self._viewComponents.remove(view)

    def isVehicleObserved(self, vehicleID):
        return self.__vehicleToCB.get(vehicleID) is not None

    def __onVehicleStateUpdated(self, state, vehicleID):
        if state == VEHICLE_VIEW_STATE.OBSERVED_BY_ENEMY:
            if vehicleID and not self.isVehicleObserved(vehicleID):
                self.__vehicleToCB[vehicleID] = BigWorld.callback(_DURATION, functools.partial(self.__hideVehicle, vehicleID))
                for view in self._viewComponents:
                    view.sixthSenseActive(vehicleID)

    def __hideVehicle(self, vehicleID):
        cb = self.__vehicleToCB.get(vehicleID)
        if cb:
            del self.__vehicleToCB[vehicleID]
            for view in self._viewComponents:
                view.sixthSenseNotActive(vehicleID)

        else:
            _logger.warning('Unable to find callback be vehicleID=%s', vehicleID)
