# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/DestructiblesCache.py
# Compiled at: 2011-03-17 17:45:45
import ResMgr
import BigWorld
import Math
import math
import constants
import string
from material_kinds import EFFECT_MATERIAL_INDEXES_BY_NAMES
from constants import IS_CLIENT, DESTRUCTIBLE_MATKIND
from debug_utils import *
if IS_CLIENT:
    from helpers import EffectsList
DESTRUCTIBLES_CONFIG_FILE = 'scripts/destructibles.xml'
DESTRUCTIBLES_EFFECTS_FILE = 'scripts/destructibles_effects.xml'
SPT_MATKIND_SOLID = 71
DESTR_TYPE_TREE = 0
DESTR_TYPE_FALLING_ATOM = 1
DESTR_TYPE_FRAGILE = 2
DESTR_TYPE_STRUCTURE = 3
DESTR_STATE_NAME_DESTROYED = 'destroyed'
DESTR_STATE_NAME_UNDAMAGED = 'undamaged'
STATIC_OBSTACLE_ID = 10000
_INV_CHUNK_RANGE = 0.01
PI = math.pi
PI_2 = 2.0 * PI
FALLING_DESTRUCTIBLES_IGNORE_ANGLE = PI / 4.0
FALLING_DESTRUCTIBLES_IGNORE_SIN = math.sin(FALLING_DESTRUCTIBLES_IGNORE_ANGLE)

class DestructiblesCache:

    def __init__(self):
        if IS_CLIENT:
            sec = ResMgr.openSection(DESTRUCTIBLES_EFFECTS_FILE)
            if not sec:
                raise Exception, "Fail to read '%s'" % DESTRUCTIBLES_EFFECTS_FILE
            self.__effects = _readDestructiblesEffects(sec)
        sec = ResMgr.openSection(DESTRUCTIBLES_CONFIG_FILE)
        if not sec:
            raise Exception, "Fail to read '%s'" % DESTRUCTIBLES_CONFIG_FILE
        self.__defaultLifetimeEffectChance = sec.readFloat('defaultLifetimeEffectChance')
        self.__unitVehicleMass = sec.readFloat('unitVehicleMass')
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

    @property
    def unitVehicleMass(self):
        return self.__unitVehicleMass

    def getDescByID(self, descID):
        if descID < len(self.__descs):
            return self.__descs[descID]
        else:
            return None

    def getDescIDByFilename(self, filename):
        return self.__descIDs.get(filename)

    def getDescByFilename(self, filename):
        id = self.getDescIDByFilename(filename)
        if id is not None:
            return self.__descs[id]
        else:
            return

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
                module['effectHP'] = moduleSec.readString('effectHP')
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
            while 1:
                cur = len(stack) > 0 and stack.pop()
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
         'statePresets': statePresets}
        return desc

    def __readFragile(self, fragileSec):
        filename = fragileSec.readString('filename')
        kineticDamageCorrection = fragileSec.readFloat('kineticDamageCorrection', 0.0)
        desc = {'filename': filename,
         'health': fragileSec.readInt('health'),
         'kineticDamageCorrection': kineticDamageCorrection,
         'type': DESTR_TYPE_FRAGILE}
        if IS_CLIENT:
            _readAndMapEffect(desc, fragileSec, 'effect', self.__effects['fragiles'], filename)
            _readAndMapEffect(desc, fragileSec, 'decayEffect', self.__effects['fragiles'], filename)
            desc['effectHP'] = fragileSec.readString('effectHP')
            desc['effectScale'] = fragileSec.readFloat('effectScale')
        return desc

    def __readTree(self, treeSec):
        filename = treeSec.readString('filename')
        kineticDamageCorrection = treeSec.readFloat('kineticDamageCorrection', 0.0)
        desc = {'filename': filename,
         'health': treeSec.readInt('health'),
         'density': treeSec.readFloat('density'),
         'kineticDamageCorrection': kineticDamageCorrection,
         'type': DESTR_TYPE_TREE}
        if IS_CLIENT:
            _readAndMapEffect(desc, treeSec, 'fractureEffect', self.__effects['trees'], filename)
            _readAndMapEffect(desc, treeSec, 'touchdownEffect', self.__effects['trees'], filename)
            _readAndMapEffect(desc, treeSec, 'lifetimeEffect', self.__effects['trees'], filename)
            if treeSec.has_key('lifetimeEffectChance'):
                desc['lifetimeEffectChance'] = treeSec.readFloat('lifetimeEffectChance')
            else:
                desc['lifetimeEffectChance'] = self.__defaultLifetimeEffectChance
            physParams = _readDestructiblePhysicParams(treeSec)
            desc.update(physParams)
        return desc

    def __readFallingAtom(self, fallingSec):
        filename = fallingSec.readString('filename')
        kineticDamageCorrection = fallingSec.readFloat('kineticDamageCorrection', 0.0)
        desc = {'filename': filename,
         'health': fallingSec.readInt('health'),
         'kineticDamageCorrection': kineticDamageCorrection,
         'type': DESTR_TYPE_FALLING_ATOM}
        if IS_CLIENT:
            _readAndMapEffect(desc, fallingSec, 'fractureEffect', self.__effects['fallingAtoms'], filename)
            _readAndMapEffect(desc, fallingSec, 'touchdownEffect', self.__effects['fallingAtoms'], filename)
            _readAndMapEffect(desc, fallingSec, 'lifetimeEffect', self.__effects['fallingAtoms'], filename)
            if fallingSec.has_key('lifetimeEffectChance'):
                desc['lifetimeEffectChance'] = treeSec.readFloat('lifetimeEffectChance')
            else:
                desc['lifetimeEffectChance'] = self.__defaultLifetimeEffectChance
            physParams = _readDestructiblePhysicParams(fallingSec)
            desc.update(physParams)
            desc['effectScale'] = fallingSec.readFloat('effectScale')
        return desc


def _parseMaterialName(matName, filename):
    try:
        arr = matName.split('_')
        type = arr[0]
        surface = arr[1]
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
            for varSec in effSec.values():
                variants.append(_readStagesAndEffects(varSec))

            groupEffects[effName] = tuple(variants)

        effects[groupName] = groupEffects

    return effects


def _readStagesAndEffects(section):
    stagesNames = set()
    stages = []
    stagesSec = section['stages']
    for sname in stagesSec.keys():
        if sname in stagesNames:
            raise Exception, 'Duplicated stage %s in %s destructible effect' % (sname, section.name)
        duration = stagesSec.readFloat(sname)
        stagesNames.add(sname)
        stages.append((sname, duration))

    effectsSec = section['effects']
    try:
        effects = EffectsList.EffectsList(effectsSec)
    except:
        LOG_CURRENT_EXCEPTION()

    return (stages, effects)


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


def _readFloatArray(sec, count):
    arrayStr = sec.readString('')
    strArr = arrayStr.split()
    if len(strArr) != count:
        raise Exception, 'Error reading float array from section %s' % sec.name
    return tuple(map(float, strArr))


def _readIntArray(sec, count):
    arrayStr = sec.readString('')
    strArr = arrayStr.split()
    if len(strArr) != count:
        raise Exception, 'Error reading int array from section %s' % sec.name
    return tuple(map(int, strArr))


def _readStringArray(sec, count):
    arrayStr = sec.readString('')
    strArr = arrayStr.split()
    if len(strArr) != count:
        raise Exception, 'Error reading int array from section %s' % sec.name
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


def encodeFallenParams(fallDirYaw, fallSpeed):
    fallSpeed = int(fallSpeed)
    if fallSpeed < 0:
        fallSpeed = 0
    elif fallSpeed > 3:
        fallSpeed = 3
    discreteYaw = int(64.0 * (fallDirYaw + PI) / PI_2) % 64
    return discreteYaw << 2 | fallSpeed & 3


def decodeFallenParams(params):
    fallDirYaw = (params >> 2) / 64.0 * PI_2 - PI
    return (fallDirYaw, params & 3)


def encodeFallenDestructible(destrID, params):
    return destrID << 8 | params


def decodeFallenDestructible(data):
    id = data >> 8
    return (id,) + decodeFallenParams(data & 255)


def encodeDestructibleModule(destrID, matKind, isShotDamage):
    return destrID << 8 | matKind << 1 | int(isShotDamage) & 1


def decodeDestructibleModule(data):
    return (data >> 8, data >> 1 & 127, data & 1)
