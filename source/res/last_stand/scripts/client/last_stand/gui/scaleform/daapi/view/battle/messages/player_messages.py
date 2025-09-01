# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/messages/player_messages.py
from gui.Scaleform.daapi.view.battle.shared.messages import player_messages
from items import vehicles

class LSPlayerMessages(player_messages.PlayerMessages):
    _SKIP_MESSAGES = ('DEATH_FROM_WORLD_COLLISION_SELF_SUICIDE',)

    def showMessage(self, key, args=None, extra=None, postfix=''):
        if postfix:
            extKey = u'{0}_{1}'.format(key, postfix)
            if extKey in self._SKIP_MESSAGES:
                return
        if args is not None and extra is not None:
            for argName, vehId in extra:
                self.__replaceVehicleName(argName, vehId, args)

        super(LSPlayerMessages, self).showMessage(key, args, extra, postfix)
        return

    def _onCombatEquipmentUsed(self, shooterID, eqID):
        super(LSPlayerMessages, self)._onCombatEquipmentUsed(shooterID, eqID)
        battleCxt = self.sessionProvider.getCtx()
        equipment = vehicles.g_cache.equipments().get(eqID)
        if equipment and battleCxt.isCurrentPlayer(shooterID):
            self.showMessage('COMBAT_EQUIPMENT_USED_SELF', postfix=self._getPostfixFromEquipment(equipment))

    def __replaceVehicleName(self, argName, vehId, args):
        if vehId <= 0:
            return
        vInfo = self.sessionProvider.getArenaDP().getVehicleInfo(vehId)
        if not vInfo.isEnemy():
            return
        pName = vInfo.vehicleType.name
        spCtx = self.sessionProvider.getCtx()
        args[argName] = spCtx.getPlayerFullName(vehId, pName=pName, showVehShortName=False, showClan=False)

    @staticmethod
    def _getPostfixFromEquipment(equipment):
        postfix = equipment.playerMessagesKey
        if postfix is None:
            postfix = equipment.name.upper()
        return postfix
