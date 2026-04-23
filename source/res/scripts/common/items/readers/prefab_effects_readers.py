# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/readers/prefab_effects_readers.py
import typing
import ResMgr
from constants import SHELL_TYPES_INDICES
from debug_utils import LOG_ERROR
from items import _xml
from items.components import component_constants
EffectDesc = typing.NamedTuple('EffectDesc', (('prefab', str),))
ShotEffectItemDesc = typing.NamedTuple('ShotEffectItemDesc', (('prefab', str), ('decal', int)))
EffectDescMap = typing.Dict[str, EffectDesc]
ShotEffectGroups = typing.Dict[str, ShotEffectItemDesc]
GunEffectDesc = typing.NamedTuple('GunEffectDesc', (('idx', int), ('explosion', EffectDesc), ('groundwave', EffectDesc)))
GunEffectDescMap = typing.Dict[str, GunEffectDesc]
ShotEffectDesc = typing.NamedTuple('ShotEffectDesc', (('idx', int),
 ('defaultHit', ShotEffectItemDesc),
 ('defaultVehicleHit', ShotEffectItemDesc),
 ('defaultSceneHit', ShotEffectItemDesc),
 ('groups', ShotEffectGroups)))
ShotEffects = typing.NamedTuple('ShotEffects', (('effects', typing.Sequence[ShotEffectDesc]), ('indexes', typing.Dict[str, int])))
DecalDesc = typing.NamedTuple('DecalDesc', (('idx', int), ('priority', int), ('prefab', str)))
Decals = typing.NamedTuple('Decals', (('effects', typing.Sequence[DecalDesc]), ('indexes', typing.Dict[str, int])))
ShotDefaults = typing.NamedTuple('ShotDefaults', (('default', str), ('shellTypeEffects', typing.Dict[str, str])))
Defaults = typing.NamedTuple('Defaults', (('gun', str), ('shot', ShotDefaults)))

def readDefaultPrefabEffects(xmlCtx, section, subsectionName):
    section = _xml.getSubsection(xmlCtx, section, subsectionName)
    gunDefault = _xml.readStringOrEmpty(xmlCtx, section, 'gun').strip()
    shotDefault = ''
    shotShellTypeEffects = {}
    shotSection = section['shot']
    if shotSection is not None:
        for sectionName, subsection in shotSection.items():
            if sectionName == 'default':
                shotDefault = subsection.asString.strip() or shotDefault
            if sectionName in SHELL_TYPES_INDICES:
                shotShellTypeEffects[sectionName] = subsection.asString.strip()
            LOG_ERROR('Unrecognized shell type name when reading defaultPrefabEffects: {}'.format(sectionName))

    return Defaults(gunDefault, ShotDefaults(shotDefault, shotShellTypeEffects))


def readGunEffects(xmlPath):
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    res = {}
    xmlCtx = (None, xmlPath)
    idx = 0
    for sname, subsection in section.items():
        ctx = (xmlCtx, sname)
        res[sname] = _readGunEffect(ctx, subsection, idx)
        idx += 1

    return res


def readShotEffects(xmlPath, decals):
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    effects = []
    indexes = {}
    xmlCtx = (None, xmlPath)
    for sname, subsection in section.items():
        ctx = (xmlCtx, sname)
        indexes[sname] = len(effects)
        effects.append(_readShotEffect(ctx, subsection, decals, len(effects)))

    return ShotEffects(effects, indexes)


def readDecals(xmlPath):
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    decals = []
    indexes = {}
    xmlCtx = (None, xmlPath)
    for sname, subsection in section.items():
        ctx = (xmlCtx, sname)
        indexes[sname] = len(decals)
        decals.append(_readDecal(ctx, subsection, len(decals)))

    return Decals(decals, indexes)


def _readEffect(xmlCtx, section):
    prefabPath = _xml.readString(xmlCtx, section, 'prefab')
    return EffectDesc(prefabPath)


def _readGunEffect(xmlCtx, section, idx):
    explosionEffect = _readEffect(xmlCtx, section['explosion'])
    if section.has_key('groundwave'):
        groundWaveEffect = _readEffect(xmlCtx, section['groundwave'])
    else:
        groundWaveEffect = EffectDesc('')
    return GunEffectDesc(idx, explosionEffect, groundWaveEffect)


def _readShotEffectItem(xmlCtx, section, decals):
    prefabPath = _xml.readString(xmlCtx, section, 'prefab')
    decal = _xml.readStringOrEmpty(xmlCtx, section, 'decal')
    decalId = decals.indexes[decal] if decal else component_constants.INVALID_EFFECT_INDEX
    return ShotEffectItemDesc(prefabPath, decalId)


def _readShotEffect(xmlCtx, section, decals, idx):
    res = {}
    defaultHit = ShotEffectItemDesc('', component_constants.INVALID_EFFECT_INDEX)
    defaultVehicleHit = ShotEffectItemDesc('', component_constants.INVALID_EFFECT_INDEX)
    defaultSceneHit = ShotEffectItemDesc('', component_constants.INVALID_EFFECT_INDEX)
    for sname, subsection in section.items():
        xmlCtx = (xmlCtx, sname)
        shotEffectItem = _readShotEffectItem(xmlCtx, subsection, decals)
        if sname == 'defaultHit':
            defaultHit = shotEffectItem
        if sname == 'defaultVehicleHit':
            defaultVehicleHit = shotEffectItem
        if sname == 'defaultSceneHit':
            defaultSceneHit = shotEffectItem
        res[sname] = shotEffectItem

    return ShotEffectDesc(idx, defaultHit, defaultVehicleHit, defaultSceneHit, res)


def _readDecal(xmlCtx, section, idx):
    priority = _xml.readNonNegativeInt(xmlCtx, section, 'priority')
    prefabPath = _xml.readString(xmlCtx, section, 'prefab')
    return DecalDesc(idx, priority, prefabPath)
