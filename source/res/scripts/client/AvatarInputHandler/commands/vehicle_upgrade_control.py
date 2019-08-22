# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/commands/vehicle_upgrade_control.py
from AvatarInputHandler.commands.input_handler_command import InputHandlerCommand
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
import CommandMapping
from gui.battle_control import event_dispatcher

class VehicleUpdateControl(InputHandlerCommand):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def handleKeyEvent(self, isDown, key, mods, event=None):
        progressionCtrl = self.__guiSessionProvider.dynamic.progression
        if progressionCtrl and progressionCtrl.isVehicleReady():
            if isDown and CommandMapping.g_instance.isFired(CommandMapping.CMD_UPGRADE_PANEL_SHOW, key):
                event_dispatcher.showBattleVehicleConfigurator()
                event_dispatcher.toggleFullStats(False)
                return True
        return False


class VehicleUpgradePanelControl(InputHandlerCommand):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def handleKeyEvent(self, isDown, key, mods, event=None):
        progressionCtrl = self.__guiSessionProvider.dynamic.progression
        if progressionCtrl:
            if isDown and CommandMapping.g_instance.isFiredList([CommandMapping.CMD_CM_VEHICLE_UPGRADE_PANEL_LEFT, CommandMapping.CMD_CM_VEHICLE_UPGRADE_PANEL_ALTERNATIVE_LEFT], key):
                progressionCtrl.selectVehicleModule(0)
                return True
            if isDown and CommandMapping.g_instance.isFiredList([CommandMapping.CMD_CM_VEHICLE_UPGRADE_PANEL_RIGHT, CommandMapping.CMD_CM_VEHICLE_UPGRADE_PANEL_ALTERNATIVE_RIGHT], key):
                progressionCtrl.selectVehicleModule(1)
                return True
        return False
