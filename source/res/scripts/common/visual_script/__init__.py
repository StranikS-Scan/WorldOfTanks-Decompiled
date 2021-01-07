# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/__init__.py
from visual_script.misc import ASPECT
from visual_script.registrar import VSBlockRegistrar
import example
import general
import vehicle_blocks
import arena_blocks
g_blockRegistrar = VSBlockRegistrar(ASPECT.CLIENT, ASPECT.SERVER)
g_blockRegistrar.regBlocksFromModule(example)
g_blockRegistrar.regBlocksFromModule(general)
g_blockRegistrar.regBlocksFromModule(vehicle_blocks)
g_blockRegistrar.regBlocksFromModule(arena_blocks)
