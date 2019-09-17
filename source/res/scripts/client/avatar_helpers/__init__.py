# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_helpers/__init__.py
import BigWorld
import BattleReplay
from shared_utils.avatar_helpers import VehicleTelemetry
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from festival_race.FestivalRaceSettings import FestivalRaceSettings

def getAvatarDatabaseID():
    dbID = 0
    player = BigWorld.player()
    arena = getattr(player, 'arena', None)
    if arena is not None:
        vehID = getattr(player, 'playerVehicleID', None)
        if vehID is not None and vehID in arena.vehicles:
            dbID = arena.vehicles[vehID]['accountDBID']
    return dbID


def loadAndStartPlayerVSPlan(arenaBonusType):
    planID = 'player'
    isRace = BONUS_CAPS.checkAny(arenaBonusType, BONUS_CAPS.FESTIVAL_RACE)
    if isRace and not BattleReplay.g_replayCtrl.isPlaying:
        racePlans = FestivalRaceSettings().vsePlans
        plan = BigWorld.PyPlan()
        plan.load(racePlans.get(planID), ['CLIENT'])
        plan.start()
        return plan
    else:
        return None
