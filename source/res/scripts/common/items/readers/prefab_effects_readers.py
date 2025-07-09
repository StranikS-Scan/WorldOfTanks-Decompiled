# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/readers/prefab_effects_readers.py
import typing
import ResMgr
from items import _xml
EffectDesc = typing.NamedTuple('EffectDesc', (('prefab', str),))
EffectDescMap = typing.Dict[str, EffectDesc]
ShotEffectDesc = typing.NamedTuple('ShotEffectDesc', (('groups', EffectDescMap),))
ShotEffects = typing.NamedTuple('ShotEffects', (('effects', typing.Sequence[ShotEffectDesc]), ('indexes', typing.Dict[str, int])))

def readEffects(xmlPath):
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    res = {}
    xmlCtx = (None, xmlPath)
    for sname, subsection in section.items():
        ctx = (xmlCtx, sname)
        res[sname] = _readEffect(ctx, subsection)

    return res


def readShotEffects(xmlPath):
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    effects = []
    indexes = {}
    xmlCtx = (None, xmlPath)
    for sname, subsection in section.items():
        ctx = (xmlCtx, sname)
        indexes[sname] = len(effects)
        effects.append(_readShotEffect(ctx, subsection))

    return ShotEffects(effects, indexes)


def _readEffect(xmlCtx, section):
    prefabPath = _xml.readNonEmptyString(xmlCtx, section, 'prefab')
    return EffectDesc(prefabPath)


def _readShotEffect(xmlCtx, section):
    res = {}
    for sname, subsection in section.items():
        xmlCtx = (xmlCtx, sname)
        res[sname] = _readEffect(xmlCtx, subsection)

    return ShotEffectDesc(res)
