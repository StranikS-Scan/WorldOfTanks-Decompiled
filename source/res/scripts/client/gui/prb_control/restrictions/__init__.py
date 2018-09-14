# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/restrictions/__init__.py
from constants import PREBATTLE_TYPE
from prebattle_shared import decodeRoster
from gui.server_events import g_eventsCache

def createPermissions(functional, pID=None):
    clazz = functional._permClass
    rosterKey = functional.getRosterKey(pID=pID)
    if rosterKey is not None:
        team, _ = decodeRoster(rosterKey)
        pInfo = functional.getPlayerInfo(pID=pID, rosterKey=rosterKey)
        if pInfo is not None:
            return clazz(roles=functional.getRoles(pDatabaseID=pInfo.dbID, clanDBID=pInfo.clanDBID, team=team), pState=pInfo.state, teamState=functional.getTeamState(team=team), hasLockedState=functional.hasLockedState())
    return clazz()


def createUnitActionValidator(prbType, rosterSettings, proxy):
    from gui.prb_control.restrictions import limits
    if prbType == PREBATTLE_TYPE.SORTIE:
        validator = limits.SortieActionValidator(rosterSettings)
    elif prbType == PREBATTLE_TYPE.FORT_BATTLE:
        validator = limits.FortBattleActionValidator(rosterSettings)
    elif prbType == PREBATTLE_TYPE.CLUBS:
        validator = limits.ClubsActionValidator(rosterSettings, proxy)
    elif prbType == PREBATTLE_TYPE.SQUAD:
        if g_eventsCache.isBalancedSquadEnabled():
            validator = limits.BalancedSquadActionValidator(rosterSettings)
        else:
            validator = limits.SquadActionValidator(rosterSettings)
    elif prbType == PREBATTLE_TYPE.EVENT:
        validator = limits.EventSquadActionValidator(rosterSettings)
    elif prbType == PREBATTLE_TYPE.FALLOUT:
        validator = limits.FalloutSquadActionValidator(rosterSettings)
    else:
        validator = limits.UnitActionValidator(rosterSettings)
    return validator
