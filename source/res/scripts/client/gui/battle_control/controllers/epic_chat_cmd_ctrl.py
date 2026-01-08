# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/epic_chat_cmd_ctrl.py
import Vehicle
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES, ReplyState
from gui.battle_control.controllers.chat_cmd_ctrl import ChatCommandsController, CONTEXTCOMMAND, CONTEXTCOMMAND2
from supply_shared import Supply
from gui.Scaleform.genConsts.RADIAL_MENU_CONSTS import RADIAL_MENU_CONSTS
_COMMAND_MAP = {RADIAL_MENU_CONSTS.TARGET_STATE_SUPPLY_ENEMY: {CONTEXTCOMMAND: BATTLE_CHAT_COMMAND_NAMES.ATTACK_SUPPLY,
                                                CONTEXTCOMMAND2: BATTLE_CHAT_COMMAND_NAMES.ATTACKING_SUPPLY},
 RADIAL_MENU_CONSTS.TARGET_STATE_SUPPLY_ALLY: {CONTEXTCOMMAND: BATTLE_CHAT_COMMAND_NAMES.DEFEND_SUPPLY,
                                               CONTEXTCOMMAND2: BATTLE_CHAT_COMMAND_NAMES.DEFENDING_SUPPLY},
 RADIAL_MENU_CONSTS.TARGET_STATE_SELF_REPAIR_SUPPLY: {CONTEXTCOMMAND: BATTLE_CHAT_COMMAND_NAMES.SELF_REPAIR_SUPPLY}}

class EpicChatCommandsController(ChatCommandsController):

    def _isTargetCorrect(self, player, target):
        if target is not None and isinstance(target, Vehicle.Vehicle):
            vInfo = self._arenaDP.getVehicleInfo(target.id)
            if Supply.isSupply(vInfo.vehicleType.tags):
                if target.publicInfo['team'] == player.team:
                    return True
                if target.isAlive():
                    return True
                return False
        return super(EpicChatCommandsController, self)._isTargetCorrect(player, target)

    def _handleContextChatCommandForMappedKey(self, chatCmd, key, advChatCmp):
        targetID, _, _, replyState, _ = self.getAimedAtTargetData()
        if replyState == ReplyState.NO_REPLY:
            vInfo = self._arenaDP.getVehicleInfo(targetID)
            if Supply.isSupply(vInfo.vehicleType.tags):
                viewState = self._getSupplyViewState(vInfo)
                action = _COMMAND_MAP.get(viewState, {}).get(chatCmd)
                if action:
                    self.handleChatCommand(action, targetID=targetID)
                    return
        super(EpicChatCommandsController, self)._handleContextChatCommandForMappedKey(chatCmd, key, advChatCmp)

    def _getSupplyViewState(self, vInfo):
        if vInfo.isEnemy():
            return RADIAL_MENU_CONSTS.TARGET_STATE_SUPPLY_ENEMY
        if vInfo.isAlive():
            return RADIAL_MENU_CONSTS.TARGET_STATE_SUPPLY_ALLY
        return RADIAL_MENU_CONSTS.TARGET_STATE_SELF_REPAIR_SUPPLY if Supply.isSelfRepair(vInfo.vehicleType) else None

    def sendTargetedCommand(self, cmdName, targetID, isInRadialMenu=False):
        vInfo = self._arenaDP.getVehicleInfo(targetID)
        if Supply.isSupply(vInfo.vehicleType.tags):
            command = self.proto.battleCmd.createByNameTarget(cmdName, targetID)
            self._sendChatCommand(command, cmdName)
            return
        super(EpicChatCommandsController, self).sendTargetedCommand(cmdName, targetID, isInRadialMenu)
