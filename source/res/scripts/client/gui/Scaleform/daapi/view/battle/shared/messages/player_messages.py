# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/messages/player_messages.py
import logging
from typing import TYPE_CHECKING
from constants import EQUIPMENT_STAGES, ARENA_GUI_TYPE
from battle_royale.gui.constants import BR_EQUIPMENTS_WITH_MESSAGES
from gui.Scaleform.daapi.view.battle.shared.messages import fading_messages
from items import vehicles
if TYPE_CHECKING:
    from items.artefacts import Equipment
_logger = logging.getLogger(__name__)
_ID_TO_DESTRUCTIBLE_ENTITY_NAME = {1: '1',
 2: '2',
 3: '3',
 4: '4',
 5: '5'}

class PlayerMessages(fading_messages.FadingMessages):

    def __init__(self):
        super(PlayerMessages, self).__init__('PlayerMessagesPanel', 'player_messages_panel.xml')

    def __del__(self):
        _logger.debug('PlayerMessages panel is deleted')

    def _addGameListeners(self):
        super(PlayerMessages, self)._addGameListeners()
        ctrl = self.sessionProvider.shared.messages
        if ctrl is not None:
            ctrl.onShowPlayerMessageByCode += self._onShowPlayerMessageByCode
            ctrl.onShowPlayerMessageByKey += self.__onShowPlayerMessageByKey
            ctrl.onShowDestructibleEntityMessageByCode += self.__onShowDestructibleEntityMessageByCode
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentUpdated += self.__onCombatEquipmentUpdated
            ctrl.onCombatEquipmentUsed += self.__onCombatEquipmentUsed
        return

    def _removeGameListeners(self):
        ctrl = self.sessionProvider.shared.messages
        if ctrl is not None:
            ctrl.onShowPlayerMessageByCode -= self._onShowPlayerMessageByCode
            ctrl.onShowPlayerMessageByKey -= self.__onShowPlayerMessageByKey
            ctrl.onShowDestructibleEntityMessageByCode -= self.__onShowDestructibleEntityMessageByCode
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentUpdated -= self.__onCombatEquipmentUpdated
            ctrl.onCombatEquipmentUsed -= self.__onCombatEquipmentUsed
        super(PlayerMessages, self)._removeGameListeners()
        return

    def __onShowDestructibleEntityMessageByCode(self, code, entityID, attackerID):
        _logger.debug('onShowDestructibleEntityMessage %r %r %r', code, entityID, attackerID)
        getFullName = self.sessionProvider.getCtx().getPlayerFullName
        self.showMessage(code, {'target': _ID_TO_DESTRUCTIBLE_ENTITY_NAME[entityID],
         'attacker': getFullName(attackerID, showClan=False)})

    def _onShowPlayerMessageByCode(self, code, postfix, targetID, attackerID, equipmentID, ignoreMessages):
        _logger.debug('onShowPlayerMessage %r %r %r %r %r', code, postfix, targetID, attackerID, equipmentID)
        if ignoreMessages:
            return
        else:
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
        if not item.becomeReady:
            return
        itemDescriptor = item.getDescriptor()
        if itemDescriptor.name in BR_EQUIPMENTS_WITH_MESSAGES:
            if item.getPrevStage() == EQUIPMENT_STAGES.COOLDOWN and item.getQuantity() == 0:
                return
            self.showMessage('COMBAT_BR_EQUIPMENT_READY', {'equipment': itemDescriptor.userString})
        else:
            self.showMessage('COMBAT_EQUIPMENT_READY', {}, postfix=self.__getPostfixFromEquipment(itemDescriptor))

    def __onCombatEquipmentUsed(self, shooterID, eqID):
        if self.sessionProvider.arenaVisitor.getArenaGuiType() in ARENA_GUI_TYPE.EPIC_RANGE:
            return
        else:
            battleCxt = self.sessionProvider.getCtx()
            if not battleCxt.isCurrentPlayer(shooterID):
                equipment = vehicles.g_cache.equipments().get(eqID)
                getFullName = battleCxt.getPlayerFullName
                if equipment is None:
                    return
                self.showMessage('COMBAT_EQUIPMENT_USED', {'player': getFullName(shooterID, showClan=False)}, extra=(('player', shooterID),), postfix=self.__getPostfixFromEquipment(equipment))
            return

    @staticmethod
    def __getPostfixFromEquipment(equipment):
        postfix = equipment.playerMessagesKey
        if postfix is None:
            postfix = equipment.name.split('_')[0].upper()
        return postfix
