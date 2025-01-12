# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/common/player_satisfaction_rating/player_satisfaction_sound.py
import logging
from enum import Enum
import SoundGroups
from constants import PlayerSatisfactionRating
_logger = logging.getLogger(__name__)

class SoundEvents(Enum):
    BETTER = 'post_battle_voting_better'
    USUAL = 'post_battle_voting_usual'
    WORSE = 'post_battle_voting_worse'


_RATING_TO_SOUND_MAP = {PlayerSatisfactionRating.USUAL: SoundEvents.USUAL,
 PlayerSatisfactionRating.BETTER: SoundEvents.BETTER,
 PlayerSatisfactionRating.WORSE: SoundEvents.WORSE}

def playSoundForRating(rating):
    SoundGroups.g_instance.playSound2D(_RATING_TO_SOUND_MAP[rating].value)
