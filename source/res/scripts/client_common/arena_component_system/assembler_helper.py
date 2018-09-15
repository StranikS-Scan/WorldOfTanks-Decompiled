# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/arena_component_system/assembler_helper.py
from constants import ARENA_BONUS_TYPE
from arena_component_system.epic_random_battle_component_assembler import EpicRandomBattleComponentAssembler
COMPONENT_ASSEMBLER = {ARENA_BONUS_TYPE.EPIC_RANDOM: EpicRandomBattleComponentAssembler,
 ARENA_BONUS_TYPE.EPIC_RANDOM_TRAINING: EpicRandomBattleComponentAssembler}
ARENA_BONUS_TYPE_CAP_COMPONENTS = {}
