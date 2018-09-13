# Embedded file name: scripts/client/gui/prb_control/restrictions/__init__.py
from prebattle_shared import decodeRoster

def createPermissions(functional, pID = None):
    clazz = functional._permClass
    rosterKey = functional.getRosterKey(pID=pID)
    if rosterKey is not None:
        team, _ = decodeRoster(rosterKey)
        pInfo = functional.getPlayerInfo(pID=pID, rosterKey=rosterKey)
        if pInfo is not None:
            return clazz(roles=functional.getRoles(pDatabaseID=pInfo.dbID, clanDBID=pInfo.clanDBID, team=team), pState=pInfo.state, teamState=functional.getTeamState(team=team))
    return clazz()
