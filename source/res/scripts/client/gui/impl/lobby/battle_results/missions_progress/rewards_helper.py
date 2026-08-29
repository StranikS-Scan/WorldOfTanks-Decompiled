# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_results/missions_progress/rewards_helper.py
from gui.Scaleform.daapi.view.lobby.server_events.token_converter_helper import getBonusDataFromOneOfBonuses, convertTokensInBonusData
from gui.server_events.bonuses import TokensBonus
from gui.shared.missions.packers.events import packQuestBonusModelAndTooltipData
_RANDOM_REWARD_PLACEHOLDER_SUFFIX = ':random'

def _isRandomRewardPlaceholder(bonus):
    return False if not isinstance(bonus, TokensBonus) else any((tokenID.endswith(_RANDOM_REWARD_PLACEHOLDER_SUFFIX) for tokenID in bonus.getTokens()))


def packBonusesWithActualTokensConvertion(pCur, model, event, questTokensConvertion, questTokensCount, tooltipData, bonusPacker):
    bonusData = getBonusDataFromOneOfBonuses(event, pCur)
    bonusData = convertTokensInBonusData(event=event, bonusData=bonusData, questTokensConvertion=questTokensConvertion, questTokensCount=questTokensCount)
    questBonuses = [ bonus for bonus in event.getBonuses(bonusData=bonusData) if not _isRandomRewardPlaceholder(bonus) ]
    bonuses = model.getBonuses()
    bonuses.clear()
    packQuestBonusModelAndTooltipData(bonusPacker, bonuses, event, questBonuses=questBonuses, tooltipData=tooltipData)


def packBonusesWithTokensConvertionIfCompleted(pCur, model, event, questTokensConvertion, questTokensCount, tooltipData, bonusPacker, complete):
    if complete:
        packBonusesWithActualTokensConvertion(pCur, model, event, questTokensConvertion, questTokensCount, tooltipData, bonusPacker)
    else:
        bonuses = model.getBonuses()
        bonuses.clear()
        packQuestBonusModelAndTooltipData(bonusPacker, bonuses, event, questBonuses=event.getBonuses(), tooltipData=tooltipData)
