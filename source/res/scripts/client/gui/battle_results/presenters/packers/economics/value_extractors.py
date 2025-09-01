# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/economics/value_extractors.py
import typing
from constants import FairplayViolationType
from fairplay_violation_types import getViolationsByMask
from gui.battle_results.pbs_helpers.additional_bonuses import isGoldPiggyBankAvailaible
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from gui.battle_results.pbs_helpers.economics import FinancialRecordValues
    from gui.battle_results.presenters.packers.economics.currency_packers import CurrencyRecord
    from gui.battle_results.reusable.records import ReplayRecords
    from gui.battle_results.stats_ctrl import BattleResults

def getBaseAccountValue(records, recordConfig, _):
    return records.baseAccountValue.getRecord(*recordConfig.recordNames)


def getPremiumAccountValue(records, recordConfig, _):
    return records.premiumAccountValue.getRecord(*recordConfig.recordNames)


def getIncreasingBaseAccountFactor(records, recordConfig, _):
    factor = _getBaseAccountFactor(records, recordConfig)
    return factor if factor > 1 else 0


def getIncreasingPremiumAccountFactor(records, recordConfig, _):
    factor = _getPremiumAccountFactor(records, recordConfig)
    return factor if factor > 1 else 0


def getDecreasingBaseAccountFactor(records, recordConfig, _):
    factor = _getBaseAccountFactor(records, recordConfig)
    return factor if factor < 1 else None


def getDecreasingPremiumAccountFactor(records, recordConfig, _):
    factor = _getPremiumAccountFactor(records, recordConfig)
    return factor if factor < 1 else None


def getBaseAccountEarnedValue(records, recordConfig, _):
    records = records.baseAccountValue
    return records.getRecord(*recordConfig.recordNames) - records.getRecord(*recordConfig.subtractRecords)


def getPremiumAccountEarnedValue(records, recordConfig, _):
    records = records.premiumAccountValue
    return records.getRecord(*recordConfig.recordNames) - records.getRecord(*recordConfig.subtractRecords)


def getBaseAccountEventValue(records, recordConfig, _):
    records = records.baseAccountValue
    return sum([ records.findRecord(recordName) for recordName in recordConfig.recordNames ])


def getPremiumAccountEventValue(records, recordConfig, _):
    records = records.premiumAccountValue
    return sum([ records.findRecord(recordName) for recordName in recordConfig.recordNames ])


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getBaseAccountWotPlusCurrentBonusValue(records, recordConfig, battleResults, lobbyContext=None):
    return getBaseAccountValue(records, recordConfig, battleResults) if lobbyContext.getServerSettings().isWotPlusBattleBonusesEnabled() else 0


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getPremiumAccountWotPlusCurrentBonusValue(records, recordConfig, battleResults, lobbyContext=None):
    return getPremiumAccountValue(records, recordConfig, battleResults) if lobbyContext.getServerSettings().isWotPlusBattleBonusesEnabled() else 0


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getBaseAccountWotPlusBonusValue(records, recordConfig, battleResults, lobbyContext=None):
    if lobbyContext.getServerSettings().isWotPlusBattleBonusesEnabled():
        if not battleResults.reusable.personal.isWotPlus:
            return records.baseAccountValueWithWotPlus.getRecord(*recordConfig.recordNames)
        return getBaseAccountValue(records, recordConfig, battleResults)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getPremiumAccountWotPlusBonusValue(records, recordConfig, battleResults, lobbyContext=None):
    if lobbyContext.getServerSettings().isWotPlusBattleBonusesEnabled():
        if not battleResults.reusable.personal.isWotPlus:
            return records.premiumAccountValueWithWotPlus.getRecord(*recordConfig.recordNames)
        return getPremiumAccountValue(records, recordConfig, battleResults)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getBaseAccountTotalMoneyValue(records, recordConfig, battleResults, lobbyContext=None):
    showWotPlusBattleBonuses = lobbyContext.getServerSettings().isWotPlusBattleBonusesEnabled()
    if showWotPlusBattleBonuses and not battleResults.reusable.personal.isWotPlus and battleResults.reusable.personal.hasAnyPremium:
        baseAccountValue, additional = records.baseAccountValueWithWotPlus, records.additionalValue
    else:
        baseAccountValue, additional = records.baseAccountValue, records.additionalValue
    return baseAccountValue.getRecord(*recordConfig.recordNames) + additional.getRecord(*recordConfig.subtractRecords)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getPremiumAccountTotalMoneyValue(records, recordConfig, battleResults, lobbyContext=None):
    showWotPlusBattleBonuses = lobbyContext.getServerSettings().isWotPlusBattleBonusesEnabled()
    if showWotPlusBattleBonuses and not battleResults.reusable.personal.isWotPlus and not battleResults.reusable.personal.hasAnyPremium:
        premiumAccountValue, additional = records.premiumAccountValueWithWotPlus, records.additionalValue
    else:
        premiumAccountValue, additional = records.premiumAccountValue, records.additionalValue
    return premiumAccountValue.getRecord(*recordConfig.recordNames) + additional.getRecord(*recordConfig.subtractRecords)


def getCreditsFromAdditional(records, recordConfig, _):
    additionalRecords = records.additionalValue
    return additionalRecords.getRecord(*recordConfig.recordNames)


def getGoldEventValue(records, recordConfig, _):
    return sum([ records.extraValue.findRecord(recordName) for recordName in recordConfig.recordNames ])


def getIntermediateTotalGoldValue(records, recordConfig, _):
    return records.extraValue.getRecord(*recordConfig.recordNames)


def getTotalGoldValue(records, recordConfig, _):
    return records.extraValue.getRecord(*recordConfig.recordNames) + records.additionalValue.getRecord(*recordConfig.subtractRecords)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getGoldPiggyBank(_, __, battleResults, lobbyContext=None):
    reusable = battleResults.reusable
    return reusable.personal.getGoldBankGain() if lobbyContext.getServerSettings().isRenewableSubGoldReserveEnabled() and isGoldPiggyBankAvailaible(reusable) else 0


def getCrystalValue(records, recordConfig, _):
    return records.getRecord(*recordConfig.recordNames)


def getCrystalTotalValue(records, recordConfig, _):
    return records.getRecord(*recordConfig.recordNames) + records.getRecord(*recordConfig.subtractRecords)


def getBaseAccountSquadXp(records, recordConfig, _):
    value = records.baseAccountValue.getRecord(*recordConfig.recordNames)
    return value if value > 0 else 0


def getPremiumAccountSquadXp(records, recordConfig, _):
    value = records.premiumAccountValue.getRecord(*recordConfig.recordNames)
    return value if value > 0 else 0


def getBaseAccountSquadXpPenalty(records, recordConfig, _):
    value = records.baseAccountValue.getRecord(*recordConfig.recordNames)
    return value if value < 0 else 0


def getPremiumAccountSquadXpPenalty(records, recordConfig, _):
    value = records.premiumAccountValue.getRecord(*recordConfig.recordNames)
    return value if value < 0 else 0


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getBaseAccountTotalXPValue(records, recordConfig, battleResults, lobbyContext=None):
    showWotPlusBattleBonuses = lobbyContext.getServerSettings().isWotPlusBattleBonusesEnabled()
    if showWotPlusBattleBonuses and not battleResults.reusable.personal.isWotPlus and battleResults.reusable.personal.hasAnyPremium:
        baseAccountValue = records.baseAccountValueWithWotPlus
    else:
        baseAccountValue = records.baseAccountValue
    return baseAccountValue.getRecord(*recordConfig.recordNames)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getPremiumAccountTotalXPValue(records, recordConfig, battleResults, lobbyContext=None):
    showWotPlusBattleBonuses = lobbyContext.getServerSettings().isWotPlusBattleBonusesEnabled()
    if showWotPlusBattleBonuses and not battleResults.reusable.personal.isWotPlus and not battleResults.reusable.personal.hasAnyPremium:
        premiumAccountValue = records.premiumAccountValueWithWotPlus
    else:
        premiumAccountValue = records.premiumAccountValue
    return premiumAccountValue.getRecord(*recordConfig.recordNames)


def getDeserterViolation(_, __, battleResults):
    return _getViolationPercent(battleResults, FairplayViolationType.DESERTER)


def getAfkViolation(_, __, battleResults):
    return _getViolationPercent(battleResults, FairplayViolationType.AFK)


def getSuicideViolation(_, __, battleResults):
    return _getViolationPercent(battleResults, FairplayViolationType.SUICIDE)


def _getBaseAccountFactor(records, recordConfig):
    return records.baseAccountValue.getFactor(*recordConfig.recordNames)


def _getPremiumAccountFactor(records, recordConfig):
    return records.premiumAccountValue.getFactor(*recordConfig.recordNames)


def _getViolationPercent(battleResults, penaltyType):
    avatarInfo = battleResults.reusable.personal.avatar
    if avatarInfo.hasPenalties():
        names = getViolationsByMask(penaltyType)
        name, percent = avatarInfo.getPenaltyDetails()
        if names and name == names[0]:
            return percent
        return 0
