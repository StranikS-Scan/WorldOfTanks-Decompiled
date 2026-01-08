# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_results/missions_progress/rewards_helper.py
from gui.Scaleform.daapi.view.lobby.server_events.token_converter_helper import getBonusDataFromOneOfBonuses, convertTokensInBonusData
from gui.shared.missions.packers.events import packQuestBonusModelAndTooltipData

def packBonusesWithActualTokensConvertion(pCur, model, event, questTokensConvertion, questTokensCount, tooltipData, bonusPacker):
    bonusData = getBonusDataFromOneOfBonuses(event, pCur)
    bonusData = convertTokensInBonusData(event=event, bonusData=bonusData, questTokensConvertion=questTokensConvertion, questTokensCount=questTokensCount)
    questBonuses = event.getBonuses(bonusData=bonusData)
    bonuses = model.getBonuses()
    bonuses.clear()
    packQuestBonusModelAndTooltipData(bonusPacker, bonuses, event, questBonuses=questBonuses, tooltipData=tooltipData)
