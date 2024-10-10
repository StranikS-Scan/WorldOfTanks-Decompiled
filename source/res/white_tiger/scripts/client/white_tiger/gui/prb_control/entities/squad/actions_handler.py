# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/prb_control/entities/squad/actions_handler.py
from gui.prb_control.entities.base.squad.actions_handler import SquadActionsHandler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from prebattle_vehicle import IPrebattleVehicle
from helpers import dependency
from constants import IS_DEVELOPMENT

class WhiteTigerBattleSquadActionsHandler(SquadActionsHandler):
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)

    @classmethod
    def _loadBattleQueue(cls):
        g_eventDispatcher.loadEventBattleQueue()

    def _getActiveVehicleItem(self):
        if IS_DEVELOPMENT:
            pass
        return self.__prebattleVehicle.item
