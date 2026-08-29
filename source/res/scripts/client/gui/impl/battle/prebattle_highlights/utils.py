# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/prebattle_highlights/utils.py
from __future__ import absolute_import
from constants import ARENA_BONUS_TYPE
from gui.battle_control import avatar_getter
from gui.impl.battle.prebattle_highlights.prebattle_highlights_view import PrebattleHighlightsWindow
from gui.shared.system_factory import collectPrebattleHighlightsWindow, registerPrebattleHighlightsWindow

def getPrebattleHighlightsWindow():
    arena = avatar_getter.getArena()
    bonusType = None if not arena else arena.bonusType
    if not bonusType:
        return
    else:
        window = collectPrebattleHighlightsWindow(bonusType)
        return PrebattleHighlightsWindow if not window else window


registerPrebattleHighlightsWindow(ARENA_BONUS_TYPE.REGULAR, PrebattleHighlightsWindow)
registerPrebattleHighlightsWindow(ARENA_BONUS_TYPE.RANDOM_NP2, PrebattleHighlightsWindow)
