# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/messages/player_messages.py
import logging
from gui.Scaleform.daapi.view.battle.shared.messages import player_messages
from items import vehicles
from supply_shared import Supply
_logger = logging.getLogger(__name__)
_ATTAKER_SUPPLY = 'SUPPLY_'
_TARGET_SUPPLY = '_SUPPLY'

class EpicPlayerMessages(player_messages.PlayerMessages):

    def _onShowPlayerMessageByCode(self, code, postfix, targetID, attackerID, equipmentID, ignoreMessages):
        _logger.debug('onShowEpicPlayerMessage %r %r %r %r %r', code, postfix, targetID, attackerID, equipmentID)
        if ignoreMessages:
            return
        else:
            if equipmentID:
                equipment = vehicles.g_cache.equipments().get(equipmentID)
                if equipment is not None:
                    postfix = '_'.join((postfix, equipment.name.split('_')[0].upper()))
            attackerName, isAttackerSupply = self._getSupplyName(attackerID)
            targetName, isTargetSupply = self._getSupplyName(targetID)
            if isAttackerSupply:
                postfix = _ATTAKER_SUPPLY + postfix
            if isTargetSupply:
                postfix = postfix + _TARGET_SUPPLY
            self.showMessage(code, {'target': targetName,
             'attacker': attackerName}, extra=(('target', targetID), ('attacker', attackerID)), postfix=postfix)
            return

    def _getSupplyName(self, vehicleID):
        vehicleType = self.sessionProvider.getArenaDP().getVehicleInfo(vehicleID).vehicleType
        if Supply.isSupply(vehicleType.tags):
            return ('({})'.format(vehicleType.shortNameWithPrefix), True)
        getFullName = self.sessionProvider.getCtx().getPlayerFullName
        return (getFullName(vehicleID, showClan=False), False)
