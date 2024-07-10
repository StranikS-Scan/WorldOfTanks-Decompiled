# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/economics/value_extractors.py
import typing
from constants import FairplayViolationType
from fairplay_violation_types import getViolationsByMask
from gui.battle_results.pbs_helpers.additional_bonuses import isGoldPiggyBankAvailaible
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from gui.battle_results.pbs_helpers.economics import FinancialRecords
    from gui.battle_results.presenters.packers.economics.base_currency_packer import CurrencyRecord
    from gui.battle_results.reusable.records import ReplayRecords
    from gui.battle_results.stats_ctrl import BattleResults

def getMainValue(records, recordConfig, _):
    return records.main.getRecord(*recordConfig.recordNames)


def getIncreasingMainFactor(records, recordConfig, _):
    factor = _getMainFactor(records, recordConfig)
    return factor if factor > 1 else 0


def getDecreasingMainFactor(records, recordConfig, _):
    factor = _getMainFactor(records, recordConfig)
    return factor if factor < 1 else None


def getMainEarnedValue(records, recordConfig, _):
    records = records.main
    return records.getRecord(*recordConfig.recordNames) + records.getRecord(*recordConfig.subtractRecords)


def getEventValue(records, recordConfig, _):
    records = records.main
    return sum([ records.findRecord(recordName) for recordName in recordConfig.recordNames ])


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getWotPlusBonusValue(records, recordConfig, battleResults, lobbyContext=None):
    return getMainValue(records, recordConfig, battleResults) if lobbyContext.getServerSettings().isWotPlusBattleBonusesEnabled() else 0


def getTotalCreditsValue(records, recordConfig, _):
    main, additional = records.main, records.additional
    return main.getRecord(*recordConfig.recordNames) + additional.getRecord(*recordConfig.subtractRecords)


def getCreditsFromAdditional(records, recordConfig, _):
    additionalRecords = records.additional
    return additionalRecords.getRecord(*recordConfig.recordNames)


def getGoldEventValue(records, recordConfig, _):
    records = records.extra
    return sum([ records.findRecord(recordName) for recordName in recordConfig.recordNames ])


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getGoldPiggyBank(_, __, battleResults, lobbyContext=None):
    reusable = battleResults.reusable
    return reusable.personal.getGoldBankGain() if lobbyContext.getServerSettings().isRenewableSubGoldReserveEnabled() and isGoldPiggyBankAvailaible(reusable) else 0


def getCrystalValue(records, recordConfig, _):
    return records.getRecord(*recordConfig.recordNames)


def getCrystalTotalValue(records, recordConfig, _):
    return records.getRecord(*recordConfig.recordNames) + records.getRecord(*recordConfig.subtractRecords)


def getSquadXp(records, recordConfig, _):
    value = records.main.getRecord(*recordConfig.recordNames)
    return value if value > 0 else 0


def getSquadXpPenalty(records, recordConfig, _):
    value = records.main.getRecord(*recordConfig.recordNames)
    return value if value < 0 else 0


def getDeserterViolation(_, __, battleResults):
    return _getViolationPercent(battleResults, FairplayViolationType.DESERTER)


def getAfkViolation(_, __, battleResults):
    return _getViolationPercent(battleResults, FairplayViolationType.AFK)


def getSuicideViolation(_, __, battleResults):
    return _getViolationPercent(battleResults, FairplayViolationType.SUICIDE)


def _getMainFactor(records, recordConfig):
    return records.main.getFactor(*recordConfig.recordNames)


def _getViolationPercent(battleResults, penaltyType):
    avatarInfo = battleResults.reusable.personal.avatar
    if avatarInfo.hasPenalties():
        names = getViolationsByMask(penaltyType)
        name, percent = avatarInfo.getPenaltyDetails()
        if names and name == names[0]:
            return percent
        return 0
