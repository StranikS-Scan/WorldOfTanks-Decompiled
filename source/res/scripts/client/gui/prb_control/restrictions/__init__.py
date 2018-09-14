# Embedded file name: scripts/client/gui/prb_control/restrictions/__init__.py
from constants import PREBATTLE_TYPE, FALLOUT_BATTLE_TYPE
from prebattle_shared import decodeRoster

def createPermissions(functional, pID = None):
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
        battleType = proxy.getExtra().eventType
        if battleType != FALLOUT_BATTLE_TYPE.UNDEFINED:
            validator = limits.FalloutSquadActionValidator(rosterSettings)
        else:
            validator = limits.SquadActionValidator(rosterSettings)
    else:
        validator = limits.UnitActionValidator(rosterSettings)
    return validator
