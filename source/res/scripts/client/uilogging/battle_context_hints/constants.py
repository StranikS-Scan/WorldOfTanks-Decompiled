# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/battle_context_hints/constants.py
from enum import Enum
FEATURE = 'battle_context_hints'

class BattleContextHintsLogActions(Enum):
    HINT_ACTIVATED = 'hint_activated'
    HINT_SHOWED = 'hint_showed'
    HINT_APPLIED = 'hint_applied'
    HINT_MAX_VIEWS_REACHED = 'hint_max_views_reached'
