# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/visual_script_client/__init__.py
from visual_script.misc import ASPECT
from visual_script.registrar import VSBlockRegistrar
from grinch_progression.visual_script_client import grinch_progression_blocks
g_blockRegistrar = VSBlockRegistrar(ASPECT.CLIENT, ASPECT.HANGAR)
g_blockRegistrar.regBlocksFromModule(grinch_progression_blocks)
