# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/DestructiblesCache.py
import ResMgr
import BigWorld
import Math
import math
from constants import TREE_TAG, CUSTOM_DESTRUCTIBLE_TAGS
import string
from material_kinds import EFFECT_MATERIALS, EFFECT_MATERIAL_INDEXES_BY_NAMES
from constants import IS_CLIENT, IS_CELLAPP, IS_DEVELOPMENT, DESTRUCTIBLE_MATKIND
from debug_utils import *
import items
if IS_CLIENT:
    from helpers import EffectsList
if IS_CLIENT or IS_CELLAPP:
    from WoT import packAngleToUint, unpackAngleFromUint
SEARCH_AD_RADIUS = 5.0
RADIUS_FOR_LOCATION_AD = SEARCH_AD_RADIUS - 0.5
DESTRUCTIBLES_CONFIG_FILE = 'scripts/destructibles.xml'
DESTRUCTIBLES_EFFECTS_FILE = 'scripts/destructibles_effects.xml'
SPT_MATKIND_SOLID = 71
DESTR_TYPE_TREE = 0
DESTR_TYPE_FALLING_ATOM = 1
DESTR_TYPE_FRAGILE = 2
DESTR_TYPE_STRUCTURE = 3
DESTR_STATE_NAME_DESTROYED = 'destroyed'
DESTR_STATE_NAME_UNDAMAGED = 'undamaged'
DESTR_STATE_NAME_FALLEN = 'fallen'
STATIC_OBSTACLE_ID = 10000
_INV_CHUNK_RANGE = 0.01
PI = math.pi
FALLING_DESTRUCTIBLES_IGNORE_ANGLE = PI / 4.0
FALLING_DESTRUCTIBLES_IGNORE_SIN = math.sin(FALLING_DESTRUCTIBLES_IGNORE_ANGLE)
GLOBAL_CHUNK_ID = 127 + 127 << 8 | 127 + 127

class DestructiblesCache():

    def __init__(self):
        if IS_CLIENT:
            sec = ResMgr.openSection(DESTRUCTIBLES_EFFECTS_FILE)
            if not sec:
                raise Exception("Fail to read '%s'" % DESTRUCTIBLES_EFFECTS_FILE)
            self.__effects = _readDestructiblesEffects(sec)
            ResMgr.purge(DESTRUCTIBLES_EFFECTS_FILE, True)
        sec = ResMgr.openSection(DESTRUCTIBLES_CONFIG_FILE)
        if not sec:
            raise Exception("Fail to read '%s'" % DESTRUCTIBLES_CONFIG_FILE)
        self.__defaultLifetimeEffectChance = sec.readFloat('defaultLifetimeEffectChance')
        self.__unitVehicleMass = sec.readFloat('unitVehicleMass')
        if not IS_CLIENT or IS_DEVELOPMENT:
            self.__maxHpForShootingThrough = sec.readFloat('maxHpForShootingThrough')
            self.__projectilePiercingPowerReduction = _readProjectilePiercingPowerReduction(sec['projectilePiercingPowerReduction'])
        descs = []
        for fragileSec in sec['fragiles'].values():
            desc = self.__readFragile(fragileSec)
            descs.append(desc)

        for fallingSec in sec['fallingAtoms'].values():
            desc = self.__readFallingAtom(fallingSec)
            descs.append(desc)

        for treeSec in sec['trees'].values():
            desc = self.__readTree(treeSec)
            descs.append(desc)

        for structSec in sec['structures'].values():
            desc = self.__readStructure(structSec)
            descs.append(desc)

        self.__descs = descs
        self.__descIDs = dict(((desc['filename'], i) for i, desc in enumerate(descs)))
        ResMgr.purge(DESTRUCTIBLES_CONFIG_FILE, True)

    @property
    def unitVehicleMass(self):
        return self.__unitVehicleMass

    @property
    def maxHpForShootingThrough(self):
        return self.__maxHpForShootingThrough

    @property
    def projectilePiercingPowerReduction(self):
        return self.__projectilePiercingPowerReduction

    def getDescByID(self, descID):
        return self.__descs[descID] if descID < len(self.__descs) else None

    def getDescIDByFilename(self, filename):
        return self.__descIDs.get(filename)

    def getDescByFilename(self, filename):
        id = self.getDescIDByFilename(filename)
        return self.__descs[id] if id is not None else None

    def __readStructure(self, structSec):
        filename = structSec.readString('filename')
        ids = []
        idMap = {}
        for moduleSec in structSec['modules'].values():
            module = {'health': moduleSec.readInt('health')}
            matName = moduleSec.readString('matName')
            res = _parseMaterialName(matName, filename)
            if res:
                type, surface, id, depends = res
            else:
                continue
            effectMtrlIdx = EFFECT_MATERIAL_INDEXES_BY_NAMES.get(surface)
            if effectMtrlIdx is not None:
                module['effectMtrlIdx'] = effectMtrlIdx
            else:
                LOG_ERROR('Wrong effect material in structure %s' % filename)
            if IS_CLIENT:
                _readAndMapEffect(module, moduleSec, 'ramEffect', self.__effects['structures'], filename)
                _readAndMapEffect(module, moduleSec, 'hitEffect', self.__effects['structures'], filename)
                _readAndMapEffect(module, moduleSec, 'decayEffect', self.__effects['structures'], filename)
                module['effectHP'] = intern(moduleSec.readString('effectHP'))
                module['effectScale'] = moduleSec.readFloat('effectScale')
            ids.append(id)
            idMap[id] = (module, depends)

        destrMatkindCnt = DESTRUCTIBLE_MATKIND.NORMAL_MAX - DESTRUCTIBLE_MATKIND.NORMAL_MIN
        if len(ids) > destrMatkindCnt:
            LOG_ERROR('Number of modules in structure %s exceeds destructibles material kinds range' % filename)
            ids = ids[:destrMatkindCnt]
        ids.sort()
        map = {}
        modules = {}
        matkindNMin = DESTRUCTIBLE_MATKIND.NORMAL_MIN
        matkindDMin = DESTRUCTIBLE_MATKIND.DAMAGED_MIN
        matkindsNormal = []
        for i, id in enumerate(ids):
            module, depends = idMap[id]
            destroyedMat = matkindDMin + i
            module['destroyedMat'] = destroyedMat
            normalMat = matkindNMin + i
            matkindsNormal.append(normalMat)
            modules[normalMat] = module
            map[normalMat] = tuple((ids.index(id) + matkindNMin for id in depends))

        destroyDepends = {}
        for root in map.iterkeys():
            rootDepends = set()
            stack = [root]
            while len(stack) > 0:
                cur = stack.pop()
                if cur in rootDepends:
                    continue
                rootDepends.add(cur)
                depends = map.get(cur)
                if depends is None:
                    continue
                stack += depends

            rootDepends.remove(root)
            if len(rootDepends) > 0:
                destroyDepends[root] = rootDepends

        inversedDestroyDepends = {}
        for keyMat, depends in destroyDepends.iteritems():
            for mat in depends:
                inversedDestroyDepends.setdefault(mat, set()).add(keyMat)

        statePresets = {DESTR_STATE_NAME_UNDAMAGED: [],
         DESTR_STATE_NAME_DESTROYED: matkindsNormal}
        if structSec.has_key('states'):
            for stateSec in structSec['states'].values():
                name = stateSec.readString('name').strip()
                matNames = stateSec.readString('destroyedMaterials').split(' ')
                matKinds = []
                for matName in matNames:
                    res = _parseMaterialName(matName, filename)
                    if res:
                        type, surface, id, depends = res
                    else:
                        continue
                    matKinds.append(ids.index(id) + matkindNMin)

                statePresets[name] = matKinds

        desc = {'filename': filename,
         'type': DESTR_TYPE_STRUCTURE,
         'modules': modules,
         'destroyDepends': destroyDepends,
         'inversedDestroyDepends': inversedDestroyDepends,
         'statePresets': statePresets}
        self.__readAchievementTag(structSec, desc)
        return desc

    def __readExplosive(self, fragileSec, desc):
        explosiveSec = fragileSec['explosive']
        if explosiveSec:
            effName = explosiveSec.readString('effects', 'smallArmorPiercing')
            desc['explosive'] = {'radius': explosiveSec.readFloat('explosionRadius', 0),
             'armorDamage': explosiveSec.readFloat('damage/armor', 0),
             'devicesDamage': explosiveSec.readFloat('damage/devices', 0),
             'effect': items.vehicles.g_cache.shotEffectsIndexes.get(effName),
             'fireRadius': explosiveSec.readFloat('fireRadius', 0)}

    def __readFragile(self, fragileSec):
        filename = fragileSec.readString('filename')
        kineticDamageCorrection = fragileSec.readFloat('kineticDamageCorrection', 0.0)
        desc = {'filename': filename,
         'health': fragileSec.readInt('health'),
         'kineticDamageCorrection': kineticDamageCorrection,
         'type': DESTR_TYPE_FRAGILE}
        self.__readAchievementTag(fragileSec, desc)
        self.__readExplosive(fragileSec, desc)
        matName = fragileSec.readString('matName')
        if matName:
            surface = _parseFragileMaterialName(matName, filename)
            effectMtrlIdx = EFFECT_MATERIAL_INDEXES_BY_NAMES.get(surface)
            if effectMtrlIdx is not None:
                desc['effectMtrlIdx'] = effectMtrlIdx
        if IS_CLIENT:
            _readAndMapEffect(desc, fragileSec, 'effect', self.__effects['fragiles'], filename)
            _readAndMapEffect(desc, fragileSec, 'hitEffect', self.__effects['fragiles'], filename, False)
            _readAndMapEffect(desc, fragileSec, 'decayEffect', self.__effects['fragiles'], filename)
            desc['effectHP'] = fragileSec.readString('effectHP')
            desc['effectScale'] = fragileSec.readFloat('effectScale')
            _readAndMapEffect(desc, fragileSec, 'lifetimeEffect', self.__effects['fragiles'], filename)
            if fragileSec.has_key('lifetimeEffectChance'):
                desc['lifetimeEffectChance'] = fragileSec.readFloat('lifetimeEffectChance')
            else:
                desc['lifetimeEffectChance'] = self.__defaultLifetimeEffectChance
        return desc

    def __readTree(self, treeSec):
        filename = treeSec.readString('filename')
        kineticDamageCorrection = treeSec.readFloat('kineticDamageCorrection', 0.0)
        desc = {'filename': filename,
         'health': treeSec.readInt('health'),
         'density': treeSec.readFloat('density'),
         'kineticDamageCorrection': kineticDamageCorrection,
         'type': DESTR_TYPE_TREE,
         'achievementTag': TREE_TAG}
        physParams = _readDestructiblePhysicParams(treeSec)
        desc.update(physParams)
        if IS_CLIENT:
            _readAndMapEffect(desc, treeSec, 'fractureEffect', self.__effects['trees'], filename)
            _readAndMapEffect(desc, treeSec, 'touchdownEffect', self.__effects['trees'], filename)
            _readAndMapEffect(desc, treeSec, 'lifetimeEffect', self.__effects['trees'], filename)
            if treeSec.has_key('lifetimeEffectChance'):
                desc['lifetimeEffectChance'] = treeSec.readFloat('lifetimeEffectChance')
            else:
                desc['lifetimeEffectChance'] = self.__defaultLifetimeEffectChance
        return desc

    def __readFallingAtom(self, fallingSec):
        filename = fallingSec.readString('filename')
        kineticDamageCorrection = fallingSec.readFloat('kineticDamageCorrection', 0.0)
        desc = {'filename': filename,
         'health': fallingSec.readInt('health'),
         'kineticDamageCorrection': kineticDamageCorrection,
         'type': DESTR_TYPE_FALLING_ATOM}
        self.__readAchievementTag(fallingSec, desc)
        physParams = _readDestructiblePhysicParams(fallingSec)
        desc.update(physParams)
        preferredTiltDirections = _readPreferredTiltDirections(fallingSec)
        if preferredTiltDirections:
            desc['preferredTiltDirections'] = preferredTiltDirections
        if IS_CLIENT:
            _readAndMapEffect(desc, fallingSec, 'fractureEffect', self.__effects['fallingAtoms'], filename)
            _readAndMapEffect(desc, fallingSec, 'touchdownEffect', self.__effects['fallingAtoms'], filename)
            _readAndMapEffect(desc, fallingSec, 'touchdownBreakEffect', self.__effects['fallingAtoms'], filename, False)
            _readAndMapEffect(desc, fallingSec, 'lifetimeEffect', self.__effects['fallingAtoms'], filename)
            if fallingSec.has_key('lifetimeEffectChance'):
                desc['lifetimeEffectChance'] = fallingSec.readFloat('lifetimeEffectChance')
            else:
                desc['lifetimeEffectChance'] = self.__defaultLifetimeEffectChance
            desc['effectScale'] = fallingSec.readFloat('effectScale')
        return desc

    def __readAchievementTag(self, section, desc):
        tag = section.readString('achievementTag')
        if tag:
            if tag in CUSTOM_DESTRUCTIBLE_TAGS:
                desc['achievementTag'] = tag
            else:
                raise Exception("Wrong achievement tag '%s' in destructible '%s'" % (tag, section.readString('filename')))

    def _getEffect(self, effectName, effectCategory, needLogErrors=True):
        if not effectName:
            if needLogErrors:
                LOG_WARNING('Failed to read %s name in %s' % (effectName, effectCategory))
            return
        elif string.lower(effectName) == 'none':
            return
        effects = self.__effects[effectCategory]
        effect = effects.get(effectName)
        if effect is None:
            if needLogErrors:
                LOG_ERROR('Destructibles effect %s is not found' % effectName)
            return
        else:
            return effect


def _parseFragileMaterialName(matName, filename):
    try:
        arr = matName.split('_')
        res = filter(str.isalpha, arr[1])
    except:
        LOG_ERROR('Fail to parse material name %s in fragile %s' % (matName, filename))
        res = None

    return res


def _parseMaterialName(matName, filename):
    try:
        arr = matName.split('_')
        type = intern(arr[0])
        surface = intern(filter(str.isalpha, arr[1]))
        id = int(arr[2])
        depends = map(int, arr[3:])
        res = (type,
         surface,
         id,
         depends)
    except:
        LOG_ERROR('Fail to parse material name %s in structure %s' % (matName, filename))
        res = None

    return res


def _readAndMapEffect(cfg, sec, effectKey, effects, destrFilename, needLogErrors=True):
    effectName = sec.readString(effectKey)
    if not effectName:
        if needLogErrors:
            LOG_WARNING('Failed to read %s name in %s' % (effectKey, destrFilename))
            return
    if string.lower(effectName) == 'none':
        return
    else:
        effect = effects.get(effectName)
        if effect is None:
            if needLogErrors:
                LOG_ERROR('Destructibles effect %s is not found' % effectName)
            return
        cfg[effectKey] = effect
        return


def _readDestructiblesEffects(sec):
    effects = {}
    for groupName, groupSec in sec.items():
        groupEffects = {}
        for effName, effSec in groupSec.items():
            variants = []
            try:
                for varSec in effSec.values():
                    variants.append(_readEffectsTimeLine(varSec))

            except Exception:
                print Exception, groupName, groupSec, effName
                LOG_CURRENT_EXCEPTION()

            groupEffects[effName] = tuple(variants)

        effects[groupName] = groupEffects

    return effects


def _readEffectsTimeLine(section):
    effectsTimeLine = EffectsList.effectsFromSection(section)
    return effectsTimeLine


def _readDestructiblePhysicParams(section):
    params = _readFloatArray(section['physicParams'], 7)
    cfg = {'mass': params[0],
     'height': params[1],
     'springAngle': params[2],
     'springStiffnes': params[3],
     'springResist': params[4],
     'airResist': params[5],
     'buryDepth': params[6]}
    return cfg


def _readPreferredTiltDirections(section):
    angles = _readFloatArray(section['preferredTiltDirections']) if section.has_key('preferredTiltDirections') else tuple()
    if angles:
        angles = map(lambda a: (a + 180.0) % 360.0 - 180.0, angles)
        angles.append(max(angles) - 360)
        angles.append(min(angles) + 360)
        angles = map(math.radians, angles)
    return angles


def _readProjectilePiercingPowerReduction(section):
    res = []
    for matName in EFFECT_MATERIALS:
        val = section.readString(matName, '').split(None, 2)
        try:
            reductionFactor = float(val[0])
            minReduction = float(val[1])
        except:
            raise Exception('Wrong of missing value of %s/%s' % (section.name, matName))

        res.append((reductionFactor, minReduction))

    return tuple(res)


def _readFloatArray(sec, count=None):
    arrayStr = sec.readString('')
    strArr = arrayStr.split()
    if count is not None and len(strArr) != count:
        raise Exception('Error reading float array from section %s' % sec.name)
    return tuple(map(float, strArr))


def _readIntArray(sec, count):
    arrayStr = sec.readString('')
    strArr = arrayStr.split()
    if len(strArr) != count:
        raise Exception('Error reading int array from section %s' % sec.name)
    return tuple(map(int, strArr))


def _readStringArray(sec, count):
    arrayStr = sec.readString('')
    strArr = arrayStr.split()
    if len(strArr) != count:
        raise Exception('Error reading int array from section %s' % sec.name)
    return strArr


def scaledDestructibleHealth(scale, refHealth):
    return int(math.ceil(scale * scale * refHealth))


def chunkIDFromChunkPosition(position):
    chunkX = int(round(position.x * 0.01))
    chunkZ = int(round(position.z * 0.01))
    return chunkX + 127 << 8 | chunkZ + 127


def controllerPositionFromChunkID(chunkID):
    x = ((chunkID >> 8) - 127) * 100.0 + 50.0
    z = ((chunkID & 255) - 127) * 100.0 + 50.0
    return Math.Vector3(x, 0, z)


def chunkIndexesFromPosition(position):
    chunkX = int(math.floor(position[0] * _INV_CHUNK_RANGE))
    chunkZ = int(math.floor(position[2] * _INV_CHUNK_RANGE))
    return (chunkX, chunkZ)


def chunkIDFromPosition(position):
    return chunkIDFromChunkIndexes(*chunkIndexesFromPosition(position))


def chunkIDFromChunkIndexes(gridX, gridZ):
    return gridX + 127 << 8 | gridZ + 127


def chunkIndexesFromChunkID(id):
    return ((id >> 8) - 127, (id & 255) - 127)


def areaDestructiblesPositionFromChunkID(chunkID):
    gridX, gridZ = chunkIndexesFromChunkID(chunkID)
    pos = controllerPositionFromChunkID(chunkID)
    dx = RADIUS_FOR_LOCATION_AD * math.cos(PI / 10.0 * (gridX + gridZ))
    dz = RADIUS_FOR_LOCATION_AD * math.sin(PI / 10.0 * (gridX + gridZ))
    return Math.Vector3(pos.x + dx, 0, pos.z + dz)


def encodeUint16(value):
    return (value >> 8 & 255, value & 255)


def decodeUint16(data):
    return data[0] << 8 | data[1]


def encodeDestructibleModule(destrID, matKind, isShotDamage):
    return encodeUint16(destrID) + ((matKind & 127) << 1 | int(isShotDamage),)


def decodeDestructibleModule(data):
    return (decodeUint16(data[:2]), data[2] >> 1, bool(data[2] & 1))


def encodeFragile(destrID, isShotDamage):
    return encodeUint16(destrID) + (int(isShotDamage),)


def decodeFragile(data):
    return (decodeUint16(data[:2]), bool(data[2]))


def encodeFallenColumn(destrID, fallYaw, fallSpeed):
    params = packAngleToUint(fallYaw, 6) << 2 | max(0, min(int(fallSpeed), 3))
    return encodeUint16(destrID) + (params,)


def decodeFallenColumn(data):
    destrID = decodeUint16(data[:2])
    params = data[2]
    fallYaw = unpackAngleFromUint(params >> 2, 6)
    fallSpeed = float(params & 3)
    return (destrID, fallYaw, fallSpeed)


def encodeFallenTree(destrID, fallYaw, fallPitchConstr, fallSpeed):
    params = packAngleToUint(fallYaw, 6) << 2 | max(0, min(int(fallSpeed), 3))
    return encodeUint16(destrID) + encodeUint16(packAngleToUint(fallPitchConstr, 16)) + (params,)


def decodeFallenTree(data):
    destrID = decodeUint16(data[:2])
    fallPitchConstr = unpackAngleFromUint(decodeUint16(data[2:4]), 16)
    params = data[4]
    fallYaw = unpackAngleFromUint(params >> 2, 6)
    fallSpeed = float(params & 3)
    return (destrID,
     fallYaw,
     fallPitchConstr,
     fallSpeed)
