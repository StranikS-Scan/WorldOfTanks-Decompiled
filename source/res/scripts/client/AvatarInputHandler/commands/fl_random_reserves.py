# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/commands/fl_random_reserves.py
from AvatarInputHandler.commands.input_handler_command import InputHandlerCommand
from ReservesEvents import randomReservesEvents
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
import CommandMapping

class FLRandomReserves(InputHandlerCommand):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    __FIRST_RESERVE_INDEX = 0
    __SECOND_RESERVE_INDEX = 1

    def handleKeyEvent(self, isDown, key, mods, event=None):
        if CommandMapping.g_instance.isFiredList([CommandMapping.CMD_CM_VEHICLE_UPGRADE_PANEL_LEFT, CommandMapping.CMD_CM_VEHICLE_UPGRADE_PANEL_ALTERNATIVE_LEFT], key):
            randomReservesEvents.onSelectedReserve(self.__FIRST_RESERVE_INDEX)
            return True
        if CommandMapping.g_instance.isFiredList([CommandMapping.CMD_CM_VEHICLE_UPGRADE_PANEL_RIGHT, CommandMapping.CMD_CM_VEHICLE_UPGRADE_PANEL_ALTERNATIVE_RIGHT], key):
            randomReservesEvents.onSelectedReserve(self.__SECOND_RESERVE_INDEX)
            return True
        return False
