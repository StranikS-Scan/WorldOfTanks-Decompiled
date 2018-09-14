# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/messages/player_messages.py
from constants import EQUIPMENT_STAGES
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.battle.shared.messages import fading_messages
from gui.battle_control import avatar_getter
from items import vehicles

class PlayerMessages(fading_messages.FadingMessages):

    def __init__(self):
        super(PlayerMessages, self).__init__('PlayerMessagesPanel', 'player_messages_panel.xml')

    def __del__(self):
        LOG_DEBUG('PlayerMessages panel is deleted')

    def _addGameListeners(self):
        super(PlayerMessages, self)._addGameListeners()
        ctrl = self.sessionProvider.shared.messages
        if ctrl is not None:
            ctrl.onShowPlayerMessageByCode += self.__onShowPlayerMessageByCode
            ctrl.onShowPlayerMessageByKey += self.__onShowPlayerMessageByKey
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentUpdated += self.__onCombatEquipmentUpdated
        arena = avatar_getter.getArena()
        if arena:
            arena.onCombatEquipmentUsed += self.__onCombatEquipmentUsed
        return

    def _removeGameListeners(self):
        ctrl = self.sessionProvider.shared.messages
        if ctrl is not None:
            ctrl.onShowPlayerMessageByCode -= self.__onShowPlayerMessageByCode
            ctrl.onShowPlayerMessageByKey -= self.__onShowPlayerMessageByKey
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentUpdated -= self.__onCombatEquipmentUpdated
        arena = avatar_getter.getArena()
        if arena:
            arena.onCombatEquipmentUsed -= self.__onCombatEquipmentUsed
        super(PlayerMessages, self)._removeGameListeners()
        return

    def __onShowPlayerMessageByCode(self, code, postfix, targetID, attackerID, equipmentID):
        LOG_DEBUG('onShowPlayerMessage', code, postfix, targetID, attackerID, equipmentID)
        getFullName = self.sessionProvider.getCtx().getPlayerFullName
        if equipmentID:
            equipment = vehicles.g_cache.equipments().get(equipmentID)
            if equipment is not None:
                postfix = '_'.join((postfix, equipment.name.split('_')[0].upper()))
        self.showMessage(code, {'target': getFullName(targetID, showClan=False),
         'attacker': getFullName(attackerID, showClan=False)}, extra=(('target', targetID), ('attacker', attackerID)), postfix=postfix)
        return

    def __onShowPlayerMessageByKey(self, key, args=None, extra=None):
        self.showMessage(key, args, extra)

    def __onCombatEquipmentUpdated(self, _, item):
        if item.getPrevStage() in (EQUIPMENT_STAGES.DEPLOYING, EQUIPMENT_STAGES.UNAVAILABLE, EQUIPMENT_STAGES.COOLDOWN) and item.getStage() == EQUIPMENT_STAGES.READY:
            postfix = item.getDescriptor().name.split('_')[0].upper()
            self.showMessage('COMBAT_EQUIPMENT_READY', {}, postfix=postfix)

    def __onCombatEquipmentUsed(self, shooterID, eqID):
        battleCxt = self.sessionProvider.getCtx()
        if not battleCxt.isCurrentPlayer(shooterID):
            equipment = vehicles.g_cache.equipments().get(eqID)
            getFullName = battleCxt.getPlayerFullName
            if equipment is not None:
                postfix = equipment.name.split('_')[0].upper()
                self.showMessage('COMBAT_EQUIPMENT_USED', {'player': getFullName(shooterID, showClan=False)}, extra=(('player', shooterID),), postfix=postfix)
        return
