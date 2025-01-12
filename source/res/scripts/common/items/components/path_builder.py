# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/path_builder.py
import persistent_data_cache_common as pdc
__all__ = ('makeIndexes', 'makePath')
_SEPARATOR = '/'
_chains = []

def makeIndexes(path):
    global _chains
    chains = path.split(_SEPARATOR)
    for chain in chains:
        if chain not in _chains:
            yield len(_chains)
            _chains.append(chain)
        yield _chains.index(chain)


def makePath(*indexes):
    chains = []
    for index in indexes:
        chains.append(_chains[index])

    return _SEPARATOR.join(chains)


def init():
    global _chains
    _chains = pdc.load('path_builder', list)
