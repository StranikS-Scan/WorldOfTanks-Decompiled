# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/rest_bonus.py
import typing
from gui.game_control.rest_bonus_controller import REST_BONUS_BASE_FACTOR, REST_BONUS_XP_FACTOR_BONUS
if typing.TYPE_CHECKING:
    from typing import Dict, List, Tuple
    from gui.server_events.event_items import Quest

def getRestBonusData(questsProgress, restBonusQuests):
    factor = 0.0
    questIDs = []
    for questID in questsProgress:
        quest = restBonusQuests.get(questID)
        if quest is None:
            continue
        for bonus in quest.getBonuses(REST_BONUS_XP_FACTOR_BONUS):
            factor += bonus.getValue() - REST_BONUS_BASE_FACTOR

        questIDs.append(questID)

    return (factor, questIDs)
