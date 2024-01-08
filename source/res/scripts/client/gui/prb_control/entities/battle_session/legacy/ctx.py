# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/battle_session/legacy/ctx.py
from CurrentVehicle import g_currentVehicle
from constants import OBSERVER_VEH_INVENTORY_ID, OBSERVER_VEH_NAME, ARENA_BONUS_TYPE
from gui.prb_control.entities.base.legacy.ctx import JoinLegacyCtx, SetPlayerStateCtx
from gui.prb_control.prb_getters import getPrebattleSettings
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.withParent(('getID', 'prbID'), ('getPrbTypeName', 'type'), ('getWaitingID', 'waitingID'))
class JoinBattleSessionCtx(JoinLegacyCtx):
    __slots__ = ()

    def __init__(self, prbID, prbType, waitingID='', flags=FUNCTIONAL_FLAG.UNDEFINED):
        super(JoinBattleSessionCtx, self).__init__(prbID, prbType, waitingID=waitingID, flags=flags)


class BattleSessionSetPlayerStateCtx(SetPlayerStateCtx):

    def getVehicleInventoryID(self):
        bonusType = getPrebattleSettings()['bonusType']
        return OBSERVER_VEH_INVENTORY_ID if g_currentVehicle.item.name == OBSERVER_VEH_NAME and bonusType == ARENA_BONUS_TYPE.TOURNAMENT_COMP7 else super(BattleSessionSetPlayerStateCtx, self).getVehicleInventoryID()
