# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/registrar.py
import inspect
from block import Block
from context import VScriptContext
__all__ = ['VSBlockRegistrar']

def _findVScriptConponentsInModule(module):
    return list((value for key, value in inspect.getmembers(module, inspect.isclass) if issubclass(value, Block) and value is not Block and inspect.getmodule(value) is module))


def _collectContextMetaData(cls):
    membersData = []
    for _, mem in inspect.getmembers(cls):
        if inspect.ismethod(mem) and hasattr(mem, 'vse_meta'):
            membersData.append(mem.vse_meta)

    return (cls.__name__, membersData)


class VSBlockRegistrar(object):

    def __init__(self, *aspect):
        self._aspects = set(aspect)
        self._domainBlocks = []
        self._domainContexts = {}
        self._isEngineLoadBlocks = False
        self._isEngineLoadContexts = False

    @property
    def aspects(self):
        return ' | '.join(self._aspects)

    def regBlock(self, block):
        if block not in self._domainBlocks:
            self._domainBlocks.append(block)

    def regBlocksFromModule(self, module):
        for block in _findVScriptConponentsInModule(module):
            self.regBlock(block)

    def getBlocks(self):
        self._isEngineLoadBlocks = True
        return self._domainBlocks

    def regContext(self, ctx):
        name, data = _collectContextMetaData(ctx)
        if name not in self._domainContexts:
            self._domainContexts[name] = data

    def getContexts(self):
        self._isEngineLoadContexts = True
        return self._domainContexts
