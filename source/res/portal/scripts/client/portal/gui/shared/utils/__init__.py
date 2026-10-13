# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/shared/utils/__init__.py
from gui.battle_control import avatar_getter
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from portal_common.portal_constants import PortalBossesID

def getBossVehicleName():
    sessionProvider = dependency.instance(IBattleSessionProvider)
    arenaDP = sessionProvider.getArenaDP()
    if arenaDP is None:
        return ''
    else:
        battleState = avatar_getter.getArenaInfo().portalBattleStateComponent
        boss = battleState.bossInfo[PortalBossesID.BOSS_ID]
        vInfo = arenaDP.getVehicleInfo(boss.vehicleID)
        return vInfo.vehicleType.shortName if vInfo else ''
