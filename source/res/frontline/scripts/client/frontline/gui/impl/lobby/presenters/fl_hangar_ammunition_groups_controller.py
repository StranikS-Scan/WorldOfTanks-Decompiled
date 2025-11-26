# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/presenters/fl_hangar_ammunition_groups_controller.py
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from frontline.constants.common import FRONTLINE_GROUPS
from gui.impl.common.ammunition_panel.ammunition_groups_controller import RANDOM_GROUPS
from gui.impl.lobby.tank_setup.ammunition_panel.groups_controller import HangarAmmunitionGroupsController

class FLHangarAmmunitionGroupsController(HangarAmmunitionGroupsController):

    def _getGroups(self):
        if self._vehicle is None:
            return []
        else:
            return FRONTLINE_GROUPS if self.prbDispatcher is not None and (self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EPIC) or self.prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.EPIC)) and self._vehicle.level in self.__epicMetaGameCtrl.getValidVehicleLevels() else RANDOM_GROUPS
