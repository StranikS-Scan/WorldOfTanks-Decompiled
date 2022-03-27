# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/commander/six_sence_proxy.py
import logging
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from helpers import dependency
from gui.battle_control.controllers.team_sixth_sense import ITeamSixthSenseView
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class SixSenseCommanderVehiclesProxy(ITeamSixthSenseView):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def sixthSenseActive(self, vehicleID):
        self.__updateObservedStatus(vehicleID, True)

    def sixthSenseNotActive(self, vehicleID):
        self.__updateObservedStatus(vehicleID, False)

    def __updateObservedStatus(self, vehicleID, isObserved):
        rtsCommander = self.__sessionProvider.dynamic.rtsCommander
        if rtsCommander:
            rtsCommander.invalidateControlledVehicleState(vehicleID, VEHICLE_VIEW_STATE.OBSERVED_BY_ENEMY, isObserved)
        else:
            _logger.warning("Couldn't find RTS commander controller!")
