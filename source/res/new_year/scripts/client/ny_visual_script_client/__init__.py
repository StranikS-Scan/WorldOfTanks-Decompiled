# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/ny_visual_script_client/__init__.py
import surprise_machine_block
from visual_script.misc import ASPECT
from visual_script.registrar import VSBlockRegistrar
g_blockRegistrar = VSBlockRegistrar(ASPECT.CLIENT, ASPECT.HANGAR)
g_blockRegistrar.regBlocksFromModule(surprise_machine_block)
