# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/__init__.py
from comp7_core.gui import comp7_core_constants
from gui.battle_control import battle_constants
from gui.prb_control.prb_utils import initBattleCtrlIDs

def _initBattleCtrlIDs(personality):
    for attr in comp7_core_constants.BATTLE_CTRL_ID.getExtraAttrs():
        if hasattr(battle_constants.BATTLE_CTRL_ID, attr):
            return

    initBattleCtrlIDs(comp7_core_constants, personality)


def initCoreGuiTypes(personality):
    _initBattleCtrlIDs(personality)
