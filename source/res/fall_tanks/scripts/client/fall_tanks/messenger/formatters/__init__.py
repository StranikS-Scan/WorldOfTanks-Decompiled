# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/messenger/formatters/__init__.py
from fun_random.gui.shared.fun_system_factory import registerBattleResultsMessageSubFormatter
from fall_tanks_constants import ARENA_GUI_TYPE
from fall_tanks.messenger.formatters.battle_results_formatter import FallTanksBattleResultsSubFormatter

def registerFallTanksFormatters():
    registerBattleResultsMessageSubFormatter(ARENA_GUI_TYPE.FALL_TANKS, FallTanksBattleResultsSubFormatter)
