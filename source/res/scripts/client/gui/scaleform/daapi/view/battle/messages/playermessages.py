# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/messages/PlayerMessages.py
from constants import EQUIPMENT_STAGES
from gui.battle_control import g_sessionProvider, avatar_getter
from gui.Scaleform.daapi.view.battle.messages.FadingMessages import FadingMessages
from debug_utils import LOG_DEBUG
from items import vehicles

class PlayerMessages(FadingMessages):

    def __init__(self, parentUI):
        super(PlayerMessages, self).__init__(parentUI, 'PlayerMessagesPanel', 'gui/player_messages_panel.xml')

    def __del__(self):
        LOG_DEBUG('PlayerMessages panel is deleted')

    def _addGameListeners(self):
        super(PlayerMessages, self)._addGameListeners()
        ctrl = g_sessionProvider.getBattleMessagesCtrl()
        if ctrl:
            ctrl.onShowPlayerMessageByCode += self.__onShowPlayerMessageByCode
            ctrl.onShowPlayerMessageByKey += self.__onShowPlayerMessageByKey
        ctrl = g_sessionProvider.getEquipmentsCtrl()
        if ctrl:
            ctrl.onEquipmentUpdated += self.__onCombatEquipmentUpdated
        arena = avatar_getter.getArena()
        if arena:
            arena.onCombatEquipmentUsed += self.__onCombatEquipmentUsed

    def _removeGameListeners(self):
        ctrl = g_sessionProvider.getBattleMessagesCtrl()
        if ctrl:
            ctrl.onShowPlayerMessageByCode -= self.__onShowPlayerMessageByCode
            ctrl.onShowPlayerMessageByKey -= self.__onShowPlayerMessageByKey
        ctrl = g_sessionProvider.getEquipmentsCtrl()
        if ctrl:
            ctrl.onEquipmentUpdated -= self.__onCombatEquipmentUpdated
        arena = avatar_getter.getArena()
        if arena:
            arena.onCombatEquipmentUsed -= self.__onCombatEquipmentUsed
        super(PlayerMessages, self)._removeGameListeners()

    def __onShowPlayerMessageByCode(self, code, postfix, targetID, attackerID, equipmentID):
        LOG_DEBUG('onShowPlayerMessage', code, postfix, targetID, attackerID, equipmentID)
        getFullName = g_sessionProvider.getCtx().getFullPlayerName
        if equipmentID:
            equipment = vehicles.g_cache.equipments().get(equipmentID)
            if equipment is not None:
                postfix = '_'.join((postfix, equipment.name.split('_')[0].upper()))
        self.showMessage(code, {'target': getFullName(targetID, showClan=False),
         'attacker': getFullName(attackerID, showClan=False)}, extra=(('target', targetID), ('attacker', attackerID)), postfix=postfix)
        return

    def __onShowPlayerMessageByKey(self, key, args = None, extra = None):
        self.showMessage(key, args, extra)

    def __onCombatEquipmentUpdated(self, intCD, item):
        if item.getPrevStage() in (EQUIPMENT_STAGES.DEPLOYING, EQUIPMENT_STAGES.UNAVAILABLE, EQUIPMENT_STAGES.COOLDOWN) and item.getStage() == EQUIPMENT_STAGES.READY:
            postfix = item.getDescriptor().name.split('_')[0].upper()
            self.showMessage('COMBAT_EQUIPMENT_READY', {}, postfix=postfix)

    def __onCombatEquipmentUsed(self, shooterID, eqID):
        battleCxt = g_sessionProvider.getCtx()
        if not battleCxt.isCurrentPlayer(shooterID):
            equipment = vehicles.g_cache.equipments().get(eqID)
            getFullName = battleCxt.getFullPlayerName
            if equipment is not None:
                postfix = equipment.name.split('_')[0].upper()
                self.showMessage('COMBAT_EQUIPMENT_USED', {'player': getFullName(shooterID, showClan=False)}, extra=(('player', shooterID),), postfix=postfix)
        return
