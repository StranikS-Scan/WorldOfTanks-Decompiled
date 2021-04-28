# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/commands/ability_panel_control.py
from AvatarInputHandler.commands.input_handler_command import InputHandlerCommand
import CommandMapping
from gui.battle_control import event_dispatcher
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class AbilityPanelControl(InputHandlerCommand):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def handleKeyEvent(self, isDown, key, mods, event=None):
        poiCtrl = self.__guiSessionProvider.dynamic.pointsOfInterest
        if poiCtrl is not None and poiCtrl.isAbilityAvailable():
            if isDown and CommandMapping.g_instance.isFired(CommandMapping.CMD_CM_ABILITY_PANEL, key):
                event_dispatcher.toggleWeekendBrawlAbilityOverlay()
                event_dispatcher.toggleFullStats(False)
                return True
        return False


class ChoiceAbilityControl(InputHandlerCommand):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    __VALID_KEYS = (CommandMapping.CMD_CM_ABILITY_PANEL_FIRE_KEY_1,
     CommandMapping.CMD_CM_ABILITY_PANEL_FIRE_KEY_2,
     CommandMapping.CMD_CM_ABILITY_PANEL_FIRE_KEY_3,
     CommandMapping.CMD_CM_ABILITY_PANEL_FIRE_KEY_4)

    def handleKeyEvent(self, isDown, key, mods, event=None):
        poiCtrl = self.__guiSessionProvider.dynamic.pointsOfInterest
        if poiCtrl is None or not poiCtrl.isAbilityAvailable():
            return False
        else:
            for idx, keyCode in enumerate(self.__VALID_KEYS):
                if self.__isKeySuitable(isDown, keyCode, key):
                    poiCtrl.selectAbility(idx)
                    return True

            return False

    @staticmethod
    def __isKeySuitable(isDown, keyCode, key):
        return isDown and CommandMapping.g_instance.isFired(keyCode, key)
