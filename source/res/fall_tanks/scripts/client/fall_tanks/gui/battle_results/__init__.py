# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/battle_results/__init__.py
from gui.shared.system_factory import registerPostbattleSquadFinder
from fun_random.gui.shared.fun_system_factory import registerFunBattleResultsPresenter
from fall_tanks_constants import ARENA_GUI_TYPE, FunSubModeImpl
from fall_tanks.gui.battle_results.fall_tanks_pbs_squad_finder import FallTanksPostbattleSquadFinder
from fall_tanks.gui.battle_results.fall_tanks_presenter import FallTanksBattleResultsPresenter

def registerFallTanksBattleResults():
    registerFunBattleResultsPresenter(FunSubModeImpl.FALL_TANKS, FallTanksBattleResultsPresenter)
    registerPostbattleSquadFinder(ARENA_GUI_TYPE.FALL_TANKS, FallTanksPostbattleSquadFinder)
