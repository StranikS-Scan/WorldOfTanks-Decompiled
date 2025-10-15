# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/shared/messages/player_messages.py
import logging
from gui.doc_loaders import messages_panel_reader
from gui.Scaleform.daapi.view.battle.shared.messages import player_messages
_logger = logging.getLogger(__name__)
_PORTAL_PLAYER_MESSAGES_PATH = 'portal/gui/player_messages_panel.xml'

class PortalPlayerMessages(player_messages.PlayerMessages):

    def _addGameListeners(self):
        super(PortalPlayerMessages, self)._addGameListeners()
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentUpdated += self.__onEquipmentUpdated
        return

    def _removeGameListeners(self):
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentUpdated -= self.__onEquipmentUpdated
        super(PortalPlayerMessages, self)._removeGameListeners()
        return

    def _populate(self):
        super(PortalPlayerMessages, self)._populate()
        _, _, messages = messages_panel_reader.readXML(_PORTAL_PLAYER_MESSAGES_PATH)
        self._messages.update(messages)

    def _onShowPlayerMessageByCode(self, code, postfix, targetID, attackerID, equipmentID, ignoreMessages):
        _logger.debug('onShowPlayerMessage %r %r %r %r %r', code, postfix, targetID, attackerID, equipmentID)
        if ignoreMessages:
            return
        self.showMessage(code, {'target': self._getFullName(targetID),
         'attacker': self._getFullName(attackerID)}, extra=(('target', targetID), ('attacker', attackerID)), postfix=postfix)

    def _getFullName(self, vehicleID):
        avatarSessionID = self.sessionProvider.getArenaDP().getVehicleInfo(vehicleID).player.avatarSessionID
        getFullName = self.sessionProvider.getCtx().getPlayerFullName
        return self.sessionProvider.getCtx().getPlayerFullNameParts(vehicleID, showClan=False).vehicleName if not avatarSessionID else getFullName(vehicleID, showClan=False)

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
        if hasattr(equipment, 'becomeAppointed'):
            return equipment.becomeAppointed
        return equipment.becomeActive if hasattr(equipment, 'becomeActive') else False
