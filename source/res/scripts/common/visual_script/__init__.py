# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/__init__.py
from visual_script.misc import ASPECT
from visual_script.registrar import VSBlockRegistrar
from visual_script.contexts.perks_context import PerkContext, CrewContext, PerkNotifyState
import ability_common
import example
import general
import vehicle_blocks
import qa_blocks
import qa_education_blocks
import balance
import entity_blocks
import arena_blocks
import bitmask_blocks_common
g_blockRegistrar = VSBlockRegistrar(ASPECT.CLIENT, ASPECT.SERVER)
g_blockRegistrar.regBlocksFromModule(example)
g_blockRegistrar.regTypesFromModule(example)
g_blockRegistrar.regBlocksFromModule(qa_blocks)
g_blockRegistrar.regBlocksFromModule(qa_education_blocks)
g_blockRegistrar.regBlocksFromModule(balance)
g_blockRegistrar.regTypesFromModule(balance)
g_blockRegistrar.regBlocksFromModule(general)
g_blockRegistrar.regBlocksFromModule(vehicle_blocks)
g_blockRegistrar.regBlocksFromModule(ability_common)
g_blockRegistrar.regType(ability_common.Stage)
g_blockRegistrar.regType(ability_common.EquipmentErrorState)
g_blockRegistrar.regBlock(bitmask_blocks_common.BitwiseNOT)
g_blockRegistrar.regBlock(bitmask_blocks_common.BitwiseAND)
g_blockRegistrar.regBlock(bitmask_blocks_common.BitwiseOR)
g_blockRegistrar.regBlock(bitmask_blocks_common.BitwiseXOR)
g_blockRegistrar.regBlock(bitmask_blocks_common.BitwiseEQUAL)
g_blockRegistrar.regBlocksFromModule(entity_blocks)
g_blockRegistrar.regBlock(arena_blocks.GetFlyDirection)
g_blockRegistrar.regContext(PerkContext)
g_blockRegistrar.regContext(CrewContext)
g_blockRegistrar.regType(PerkNotifyState)
