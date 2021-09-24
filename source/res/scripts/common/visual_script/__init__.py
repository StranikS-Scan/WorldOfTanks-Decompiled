# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/__init__.py
from visual_script.misc import ASPECT
from visual_script.registrar import VSBlockRegistrar
import example
import general
import vehicle_blocks
import qa_blocks
import entity_blocks
import ability_common
import all_vstypes
g_blockRegistrar = VSBlockRegistrar(ASPECT.CLIENT, ASPECT.SERVER)
g_blockRegistrar.regBlocksFromModule(general)
g_blockRegistrar.regBlocksFromModule(vehicle_blocks)
g_blockRegistrar.regBlocksFromModule(qa_blocks)
g_blockRegistrar.regBlocksFromModule(entity_blocks)
g_blockRegistrar.regTypesFromModule(all_vstypes)
g_blockRegistrar.regType(ability_common.Stage)
