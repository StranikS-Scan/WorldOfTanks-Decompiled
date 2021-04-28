# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/weekend_brawl/battle_messages.py
from gui.battle_control.battle_constants import UNDEFINED_VEHICLE_ID
from gui.battle_control.controllers.points_of_interest_ctrl import IPointOfInterestListener
from helpers import dependency
from items.vehicles import getItemByCompactDescr
from skeletons.gui.battle_session import IBattleSessionProvider
_ALLY_USED_EQUIPMENT = 'ALLY_USED_EQUIPMENT'
_ENEMY_USED_EQUIPMENT = 'ENEMY_USED_EQUIPMENT'

class BattleMessagesPlayer(IPointOfInterestListener):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def usedAbility(self, equipmentCD, vehicleID):
        msgCtrl = self.__sessionProvider.shared.messages
        if msgCtrl is None:
            return
        else:
            battleCxt = self.__sessionProvider.getCtx()
            if battleCxt.isCurrentPlayer(vehicleID):
                return
            item = getItemByCompactDescr(equipmentCD)
            equipment = item.userString
            if vehicleID == UNDEFINED_VEHICLE_ID:
                msgKey = _ENEMY_USED_EQUIPMENT
                params = {'equipment': equipment}
            else:
                msgKey = _ALLY_USED_EQUIPMENT
                playerName = battleCxt.getPlayerFullName(vehicleID, showClan=False, showRegion=False)
                params = {'player': playerName,
                 'equipment': equipment}
            msgCtrl.onShowPlayerMessageByKey(msgKey, params)
            return
