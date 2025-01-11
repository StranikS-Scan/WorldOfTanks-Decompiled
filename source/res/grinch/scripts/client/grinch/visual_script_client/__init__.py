# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/visual_script_client/__init__.py
from visual_script.misc import ASPECT
from visual_script.registrar import VSBlockRegistrar
from grinch.visual_script_client import arena_blocks
from grinch.visual_script_client.ability_context import StackableAbilityContextClient
g_blockRegistrar = VSBlockRegistrar(ASPECT.CLIENT)
g_blockRegistrar.regBlocksFromModule(arena_blocks)
g_blockRegistrar.regContext(StackableAbilityContextClient)
