# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/writers/gun_writers.py
from items import _xml
from items.writers import shared_writers

def writeRecoilEffect(item, section, cache):
    if item.effectName != 'none':
        _xml.rewriteString(section, 'recoilEffect', item.effectName)
        section.deleteSection('backoffTime')
        section.deleteSection('returnTime')
    else:
        _xml.rewriteFloat(section, 'backoffTime', item.backoffTime)
        _xml.rewriteFloat(section, 'returnTime', item.returnTime)
        section.deleteSection('recoilEffect')
    _xml.rewriteFloat(section, 'amplitude', item.amplitude)
    shared_writers.writeLodDist(item.lodDist, section, 'lodDist', cache)
