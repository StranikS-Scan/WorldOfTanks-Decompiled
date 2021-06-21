# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/ammunition_panel/groups_controller.py
from constants import QUEUE_TYPE, PREBATTLE_TYPE
from gui.prb_control import prbDispatcherProperty
from gui.impl.common.ammunition_panel.ammunition_groups_controller import AmmunitionGroupsController, FRONTLINE_GROUPS, RANDOM_GROUPS

class HangarAmmunitionGroupsController(AmmunitionGroupsController):
    __slots__ = ()

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def _getGroups(self):
        if self._vehicle is None:
            return []
        else:
            return FRONTLINE_GROUPS if self.prbDispatcher is not None and (self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EPIC) or self.prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.EPIC)) else RANDOM_GROUPS
