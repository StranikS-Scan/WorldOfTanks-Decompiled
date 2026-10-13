# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/shared/messages/player_messages.py
import logging
from gui.doc_loaders import messages_panel_reader
from gui.Scaleform.daapi.view.battle.shared.messages import player_messages
from items import vehicles
_logger = logging.getLogger(__name__)
_PORTAL_PLAYER_MESSAGES_PATH = 'portal/gui/player_messages_panel.xml'
_SENTRY_GUN_EQUIPMENT_NAME = 'sentry_gun_portal'

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
        else:
            if equipmentID:
                equipment = vehicles.g_cache.equipments().get(equipmentID)
                if equipment is not None:
                    postfix = '_'.join((postfix, self.__getPostfixFromEquipment(equipment)))
            self.showMessage(code, {'target': self._getFullName(targetID),
             'attacker': self._getFullName(attackerID)}, extra=(('target', targetID), ('attacker', attackerID)), postfix=postfix)
            return

    def showMessage(self, key, args=None, extra=None, postfix=''):
        if key == 'ALLY_HIT' and args and extra:
            vehicleID = dict(extra).get('entity')
            if vehicleID is not None:
                sentryGunName = self.__getSentryGunFullName(vehicleID)
                if sentryGunName is not None:
                    args = dict(args, entity=sentryGunName)
        super(PortalPlayerMessages, self).showMessage(key, args, extra, postfix)
        return

    def _getFullName(self, vehicleID):
        avatarSessionID = self.sessionProvider.getArenaDP().getVehicleInfo(vehicleID).player.avatarSessionID
        getFullName = self.sessionProvider.getCtx().getPlayerFullName
        return self.sessionProvider.getCtx().getPlayerFullNameParts(vehicleID, showClan=False).vehicleName if not avatarSessionID else getFullName(vehicleID, showClan=False)

    def __getSentryGunFullName(self, vehicleID):
        equipment = vehicles.g_cache.getEquipmentByName(_SENTRY_GUN_EQUIPMENT_NAME)
        if equipment is None:
            return
        else:
            sentryGunVehicleCD = vehicles.makeVehicleTypeCompDescrByName(equipment.sentryGunVehicle)
            vInfo = self.sessionProvider.getArenaDP().getVehicleInfo(vehicleID)
            return None if vInfo.vehicleType.compactDescr != sentryGunVehicleCD else self.sessionProvider.getCtx().getPlayerFullNameParts(vehicleID, pName=equipment.userString, showClan=False).playerFullName

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
