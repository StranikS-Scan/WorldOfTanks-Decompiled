# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/shared/messages/player_messages.py
import logging
from gui.doc_loaders import messages_panel_reader
from gui.Scaleform.daapi.view.battle.shared.messages import player_messages
_logger = logging.getLogger(__name__)
_HB_PLAYER_MESSAGES_PATH = 'historical_battles/gui/player_messages_panel.xml'
_HB_EQUIPMENT_NAME_TO_POSTFIX_KEY = {'arcade_teamRepairKit_historical_battles': 'REGENERATION_KIT_EPIC',
 'arcade_artillery_historical_battles': 'ARCADE_ARTILLERY_HISTORICAL_BATTLES',
 'super_shot_1': 'SUPER_SHOT'}

class HistoricalBattlePlayerMessages(player_messages.PlayerMessages):

    def _addGameListeners(self):
        super(HistoricalBattlePlayerMessages, self)._addGameListeners()
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentUpdated += self.__onEquipmentUpdated
        return

    def _removeGameListeners(self):
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentUpdated -= self.__onEquipmentUpdated
        super(HistoricalBattlePlayerMessages, self)._removeGameListeners()
        return

    def showMessage(self, key, args=None, extra=None, postfix=''):
        if key == 'DEATH_FROM_DEATH_ZONE':
            key = 'EVENT_DEATH_FROM_DEATH_ZONE'
        elif postfix == 'SELF_ENEMY':
            key = 'EVENT_DEATH'
        super(HistoricalBattlePlayerMessages, self).showMessage(key, args=args, extra=extra, postfix=postfix)

    def _populate(self):
        super(HistoricalBattlePlayerMessages, self)._populate()
        _, _, messages = messages_panel_reader.readXML(_HB_PLAYER_MESSAGES_PATH)
        self._messages.update(messages)

    def _onShowPlayerMessageByCode(self, code, postfix, targetID, attackerID, equipmentID, ignoreMessages):
        _logger.debug('onShowPlayerMessage %r %r %r %r %r', code, postfix, targetID, attackerID, equipmentID)
        if ignoreMessages:
            return
        self.showMessage(code, {'target': self._getFullName(targetID),
         'attacker': self._getFullName(attackerID)}, extra=(('target', targetID), ('attacker', attackerID)), postfix=postfix)

    def _getFullName(self, vehicleID):
        isBot = self.sessionProvider.getArenaDP().getVehicleInfo(vehicleID).isBot
        getFullName = self.sessionProvider.getCtx().getPlayerFullName
        return getFullName(vehicleID, showClan=False, showName=False) if isBot else getFullName(vehicleID, showClan=False)

    def __onEquipmentUpdated(self, _, item):
        if not item or not self.__isEquipmentBecomeActive(item):
            return
        itemDescriptor = item.getDescriptor()
        self.showMessage('COMBAT_EQUIPMENT_ACTIVATED', {}, postfix=self.__getPostfixFromEquipment(itemDescriptor))

    @staticmethod
    def __getPostfixFromEquipment(equipment):
        postfix = equipment.playerMessagesKey
        if postfix is None:
            postfix = equipment.name.split('_')[0].upper()
        return postfix

    @staticmethod
    def __isEquipmentBecomeActive(equipment):
        if hasattr(equipment, 'becomeActive'):
            return equipment.becomeActive
        return equipment.becomeAppointed if hasattr(equipment, 'becomeAppointed') else False
