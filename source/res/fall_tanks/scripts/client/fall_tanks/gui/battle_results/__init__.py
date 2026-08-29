# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/battle_results/__init__.py
from __future__ import absolute_import
from gui.impl.gen import R
from gui.shared.system_factory import registerPostbattleSquadFinder
from gui.sounds.ambients import BattleResultsEnv
from fun_random_common.fun_constants import FunSubModeImpl
from fun_random.gui.shared.fun_system_factory import registerBattleResultsSubPresenter, registerBattleResultsSoundEnv
from fall_tanks_constants import ARENA_GUI_TYPE
from fall_tanks.gui.battle_results.fall_tanks_battle_results_sub_presenters import FallTanksBattleResultsSubPresenter
from fall_tanks.gui.battle_results.fall_tanks_pbs_squad_finder import FallTanksPostbattleSquadFinder

def registerFallTanksBattleResults():
    registerPostbattleSquadFinder(ARENA_GUI_TYPE.FALL_TANKS, FallTanksPostbattleSquadFinder)
    registerBattleResultsSubPresenter(FunSubModeImpl.FALL_TANKS, FallTanksBattleResultsSubPresenter, R.views.fun_random.mono.lobby.battle_results())
    registerBattleResultsSoundEnv(ARENA_GUI_TYPE.FALL_TANKS, BattleResultsEnv)
