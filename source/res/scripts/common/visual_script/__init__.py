# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/__init__.py
import sys
import constants
from debug_utils import LOG_ERROR
from visual_script.block import ASPECT
from visual_script.registrar import regAllVScriptBlocksInModule, regVScriptBlock, aspectActive, anyAspectActive
if anyAspectActive(ASPECT.CLIENT, ASPECT.SERVER):
    import example
    regAllVScriptBlocksInModule(example)
    import general
    regAllVScriptBlocksInModule(general)
if aspectActive(ASPECT.SERVER):
    try:
        from visual_script_cell import perk_blocks
        regAllVScriptBlocksInModule(perk_blocks)
    except ImportError:
        LOG_ERROR('Error import visual_script_cell.perk_blocks')

if aspectActive(ASPECT.CLIENT) and not constants.IS_EDITOR:
    from visual_script_client import client_perk_blocks
    regAllVScriptBlocksInModule(client_perk_blocks)
if aspectActive(ASPECT.SERVER):
    pass
