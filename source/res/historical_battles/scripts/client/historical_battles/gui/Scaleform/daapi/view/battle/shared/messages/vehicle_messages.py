# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/shared/messages/vehicle_messages.py
from gui.Scaleform.daapi.view.battle.shared.messages import vehicle_messages

class HistoricalBattleVehicleMessages(vehicle_messages.VehicleMessages):

    def _formatEntity(self, entityID):
        ctx = self.sessionProvider.getCtx()
        vTypeInfoVO = ctx.getArenaDP().getVehicleInfo(entityID).vehicleType
        entityInfo = self._styleFormatter.format(vTypeInfoVO.shortNameWithPrefix)
        return entityInfo
