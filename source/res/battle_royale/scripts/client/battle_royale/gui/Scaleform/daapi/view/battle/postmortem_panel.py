# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/postmortem_panel.py
from gui.Scaleform.daapi.view.battle.shared.postmortem_panel import PostmortemPanel, _ALLOWED_EQUIPMENT_DEATH_CODES
from gui.Scaleform.daapi.view.meta.BattleRoyalePostmortemPanelMeta import BattleRoyalePostmortemPanelMeta
from gui.shared.gui_items import Vehicle
from items import vehicles

class BattleRoyalePostmortemPanel(PostmortemPanel, BattleRoyalePostmortemPanelMeta):

    def _onShowVehicleMessageByCode(self, code, postfix, entityID, extra, equipmentID, ignoreMessages):
        if equipmentID:
            equipment = vehicles.g_cache.equipments().get(equipmentID)
            if code not in _ALLOWED_EQUIPMENT_DEATH_CODES and equipment:
                code = '_'.join((code, equipment.name.upper()))
                self._prepareMessage(code, entityID, self._getDevice(extra))
                return
        super(BattleRoyalePostmortemPanel, self)._onShowVehicleMessageByCode(code, postfix, entityID, extra, equipmentID, ignoreMessages)

    def _showOwnDeathInfo(self):
        if not self._deathAlreadySet:
            deathInfo = self.getDeathInfo()
            if deathInfo is not None and self.__isBattleRoyaleBotVehicle(deathInfo['killerVehicle']):
                killerInfo = self.sessionProvider.getCtx().getArenaDP().getVehicleInfo(deathInfo['killerVehicle'])
                reason = self._makeReasonInfo(deathInfo)
                vehicleType = Vehicle.getTypeVPanelIconPath(killerInfo.vehicleType.classTag)
                vehicleName = killerInfo.vehicleType.shortNameWithPrefix
                self.as_setDeadReasonInfoS(reason, True, '', '', vehicleType, vehicleName, None)
                return
        super(BattleRoyalePostmortemPanel, self)._showOwnDeathInfo()
        return

    def _prepareMessage(self, code, killerVehID, device=None):
        if self.__isBattleRoyaleBotVehicle(killerVehID):
            msgText, colors = self._messages['DEATH_FROM_BR_BOT']
            self._deathInfo = {'text': msgText,
             'colors': colors,
             'killerVehicle': killerVehID,
             'device': device}
            self._deathInfoReceived()
        else:
            super(BattleRoyalePostmortemPanel, self)._prepareMessage(code, killerVehID, device)

    def __isBattleRoyaleBotVehicle(self, vehicleID):
        if vehicleID is None:
            return False
        else:
            vehicleInfoVO = self.sessionProvider.getCtx().getArenaDP().getVehicleInfo(vehicleID)
            return vehicleInfoVO.team == 21
