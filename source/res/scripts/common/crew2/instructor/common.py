# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/instructor/common.py
import typing
from items import _xml
from items import perks
if typing.TYPE_CHECKING:
    import ResMgr

def loadPerksIDsList(xmlCtx, section, professionID):
    perksStr = _xml.readStringOrNone(xmlCtx, section, 'perksIDs')
    if perksStr is None:
        _xml.raiseWrongXml(xmlCtx, '', 'perks list must be init for profession')
    perksIDs = [ int(x) for x in perksStr.split() ]
    if not perksIDs:
        _xml.raiseWrongXml(xmlCtx, '', 'perks list must be init for profession')
    perksCache = perks.g_cache.perks()
    for perkID in perksIDs:
        if perkID not in perksCache.perks:
            _xml.raiseWrongXml(xmlCtx, '', 'invalidate perkID={} in profession:id={} settings'.format(perkID, professionID))

    return perksIDs
