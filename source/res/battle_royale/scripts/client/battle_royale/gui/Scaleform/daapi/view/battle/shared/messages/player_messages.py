# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/shared/messages/player_messages.py
import logging
from gui.Scaleform.daapi.view.battle.shared.messages import player_messages
from items import vehicles
_logger = logging.getLogger(__name__)

class SHPlayerMessages(player_messages.PlayerMessages):

    def _onShowPlayerMessageByCode(self, code, postfix, targetID, attackerID, equipmentID, ignoreMessages):
        _logger.debug('onShowPlayerMessage %r %r %r %r %r', code, postfix, targetID, attackerID, equipmentID)
        if ignoreMessages:
            return
        else:
            if equipmentID:
                equipment = vehicles.g_cache.equipments().get(equipmentID)
                if equipment is not None:
                    postfix = '_'.join((postfix, equipment.name.split('_')[0].upper()))
            if postfix in ('ENEMY_ENEMY', 'ENEMY_ALLY') and self.__isVehicleBot(attackerID) and code.startswith('DEATH'):
                code = 'DEATH_BY_BOT'
            self.showMessage(code, {'target': self._getFullName(targetID),
             'attacker': self._getFullName(attackerID)}, extra=(('target', targetID), ('attacker', attackerID)), postfix=postfix)
            return

    def _getFullName(self, vehicleID):
        isBot = self.__isVehicleBot(vehicleID)
        getFullName = self.sessionProvider.getCtx().getPlayerFullName
        return self.sessionProvider.getCtx().getPlayerFullNameParts(vehicleID, showClan=False).vehicleName if isBot else getFullName(vehicleID, showClan=False)

    def __isVehicleBot(self, vehicleID):
        return self.sessionProvider.getArenaDP().getVehicleInfo(vehicleID).team == 21
