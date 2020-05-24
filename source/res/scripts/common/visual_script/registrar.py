# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/registrar.py
import inspect
from constants import IS_CLIENT, IS_CELLAPP, IS_BASEAPP, IS_EDITOR
from block import Block, ASPECT
__all__ = ['regVScriptBlock',
 'regAllVScriptBlocksInModule',
 'getBlocks',
 'aspectActive',
 'anyAspectActive']
__PY_VISUAL_SCRIPT_BLOCKS = []
__VS_ENGINE_LOAD_BLOCKS = False

def __findVScriptConponentsInModule(module):
    return list((value for key, value in inspect.getmembers(module, inspect.isclass) if issubclass(value, Block) and value is not Block))


def aspectActive(aspect):
    if IS_EDITOR:
        return True
    if aspect is ASPECT.CLIENT:
        return IS_CLIENT
    return IS_CELLAPP if aspect is ASPECT.SERVER else False


def anyAspectActive(*aspects):
    return any(map(aspectActive, aspects))


def regVScriptBlock(value):
    if value not in __PY_VISUAL_SCRIPT_BLOCKS:
        __PY_VISUAL_SCRIPT_BLOCKS.append(value)


def regAllVScriptBlocksInModule(module):
    for block in __findVScriptConponentsInModule(module):
        regVScriptBlock(block)


def getBlocks():
    global __VS_ENGINE_LOAD_BLOCKS
    __VS_ENGINE_LOAD_BLOCKS = True
    return __PY_VISUAL_SCRIPT_BLOCKS
