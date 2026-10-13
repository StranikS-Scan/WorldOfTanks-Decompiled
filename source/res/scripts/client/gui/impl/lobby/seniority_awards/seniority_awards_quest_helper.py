# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/seniority_awards/seniority_awards_quest_helper.py
import typing
from copy import deepcopy
from paragons_common import PARAGONS_COINS_TOKEN
from shared_utils import first
if typing.TYPE_CHECKING:
    from gui.server_events.event_items import Quest
    from typing import Dict, Optional

def processSeniorityAwardsParagonsCoins(detailedRewards, quest):
    if not quest:
        return detailedRewards
    rewards = deepcopy(detailedRewards)
    tokens = rewards.get('tokens', {})
    paragonsCoinValue = first((x.getValue() for x in quest.getBonuses('tokens') if PARAGONS_COINS_TOKEN in x.getValue()))
    if paragonsCoinValue and PARAGONS_COINS_TOKEN in tokens:
        tokens.get(PARAGONS_COINS_TOKEN, {})['count'] = paragonsCoinValue.get(PARAGONS_COINS_TOKEN, {}).get('count', 0)
    return rewards
