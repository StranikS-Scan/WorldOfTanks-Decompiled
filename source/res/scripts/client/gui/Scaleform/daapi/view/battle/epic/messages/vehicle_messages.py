# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/messages/vehicle_messages.py
from gui.Scaleform.daapi.view.battle.shared import messages
from supply_shared import Supply

class EpicVehicleMessages(messages.VehicleMessages):

    def _getPlayerInfo(self, playerName, vTypeInfoVO):
        return vTypeInfoVO.shortNameWithPrefix if Supply.isSupply(vTypeInfoVO.tags) else super(EpicVehicleMessages, self)._getPlayerInfo(playerName, vTypeInfoVO)
