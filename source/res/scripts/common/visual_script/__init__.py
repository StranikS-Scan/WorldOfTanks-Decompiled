# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/__init__.py
from visual_script.misc import ASPECT
from visual_script.registrar import VSBlockRegistrar
from constants import IS_DEVELOPMENT
import example
import general
import vehicle_blocks
import qa_blocks
import qa_education_blocks
import balance
g_blockRegistrar = VSBlockRegistrar(ASPECT.CLIENT, ASPECT.SERVER)
if IS_DEVELOPMENT:
    g_blockRegistrar.regBlocksFromModule(example)
    g_blockRegistrar.regTypesFromModule(example)
    g_blockRegistrar.regBlocksFromModule(qa_blocks)
    g_blockRegistrar.regBlocksFromModule(qa_education_blocks)
    g_blockRegistrar.regBlocksFromModule(balance)
    g_blockRegistrar.regTypesFromModule(balance)
g_blockRegistrar.regBlocksFromModule(general)
g_blockRegistrar.regBlocksFromModule(vehicle_blocks)
