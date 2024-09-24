# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/pbs_helpers/common.py
from collections import namedtuple
import typing
from constants import FINISH_REASON
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.locale.BATTLE_RESULTS import BATTLE_RESULTS
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import _ReusableInfo
    from gui.battle_results.reusable.players import PlayerInfo
    from gui.battle_results.reusable.shared import VehicleSummarizeInfo
    from gui.battle_results.stats_ctrl import BattleResults
_PlayerNames = namedtuple('PlayerNames', ('displayedName', 'hiddenName', 'isFakeNameVisible'))

def isPersonalBattleResult(summarizeInfo, battleResult):
    return battleResult.reusable.getPlayerInfo().dbID == summarizeInfo.player.dbID


def isRealNameVisible(reusable, playerInfo):
    personalInfo = reusable.getPlayerInfo()
    isPersonalResult = personalInfo.dbID == playerInfo.dbID
    if isPersonalResult:
        return True
    personalPrebattleID = personalInfo.prebattleID if personalInfo.squadIndex else 0
    return personalPrebattleID != 0 and personalPrebattleID == playerInfo.prebattleID


def getArenaNameStr(reusable):
    return backport.text(R.strings.arenas.num(reusable.common.arenaType.getGeometryName()).name())


def getRegularFinishResultResource(finishReason, teamResult):
    isExtermination = finishReason == FINISH_REASON.EXTERMINATION
    reasonKey = 'c_{}{}'.format(finishReason, teamResult) if isExtermination else 'c_{}'.format(finishReason)
    return R.strings.battle_results.finish.reason.dyn(reasonKey)()


def getUserNames(playerInfo, isPlayerRealNameVisible):
    if not playerInfo.isAnonymized():
        return _PlayerNames(displayedName=playerInfo.realName, hiddenName=playerInfo.fakeName, isFakeNameVisible=False)
    if isPlayerRealNameVisible:
        displayedName = playerInfo.realName
        hiddenName = playerInfo.fakeName
    else:
        displayedName = playerInfo.fakeName
        hiddenName = playerInfo.realName
    return _PlayerNames(displayedName=displayedName, hiddenName=hiddenName, isFakeNameVisible=not isPlayerRealNameVisible)


def getEnemies(reusable, result):
    enemies = []
    for _, enemies in reusable.getPersonalDetailsIterator(result['personal']):
        continue

    return enemies


def pushNoBattleResultsDataMessage():
    SystemMessages.pushI18nMessage(BATTLE_RESULTS.NODATA, type=SystemMessages.SM_TYPE.Warning)
