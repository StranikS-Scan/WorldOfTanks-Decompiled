# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/DecalMap.py
from functools import partial
import typing
import BigWorld
import ResMgr
import material_kinds
import persistent_data_cache as pdc
from constants import IS_EDITOR
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION

class DecalMap(object):

    def __init__(self, config):
        self.__texMap = {}
        self.__textureSets = {}
        if IS_EDITOR:
            self.__chassisEffectGroups = config.get('chassisEffectsGroups', {})
        self._init(config)

    def _init(self, config):
        BigWorld.setDamageStickerCriticalAngle(config['criticalHitDecalAngle'])
        for sMatName, scale in config['scales']:
            for matKind in material_kinds.EFFECT_MATERIAL_IDS_BY_NAMES[sMatName]:
                BigWorld.wg_addMatkindScaleU(sMatName, matKind, scale)

        for texName in config['traceTextures']:
            self.__texMap[texName] = BigWorld.wg_traceTextureIndex(texName)

        for tsName, tset in config['textureSets'].iteritems():
            self.__textureSets[tsName] = {}
            for mName, material in tset.iteritems():
                self.__textureSets[tsName][mName] = [ (self.__texMap[texName] if texName is not None else None) for texName in material ]

        self._initGroups(config)
        return

    def _initGroups(self, config, scaleFactor=1.0):
        if not BigWorld.isDynamicDecalEnabled():
            return
        try:
            for group in config['groups'].items():
                BigWorld.wg_addDecalGroup(group[0], group[1]['lifeTime'] * scaleFactor, group[1]['trianglesCount'] * scaleFactor)

            for tex in config['textures'].items():
                index = BigWorld.wg_decalTextureIndex(tex[1])
                if index == -1:
                    LOG_ERROR("texture '%s' is not exist or to more textures added to the texture atlas.Max textures count is 16." % tex[1])
                self.__texMap[tex[0]] = index

        except Exception:
            LOG_CURRENT_EXCEPTION()

    def getIndex(self, name):
        if not self.__texMap.has_key(name):
            if name != '':
                LOG_ERROR("Invalid texture name '%s'" % name, stack=True)
            return -1
        return self.__texMap[name]

    def getTextureSet(self, name):
        if not self.__textureSets.has_key(name):
            LOG_ERROR("Invalid texture set name '%s'" % name, stack=True)
            return dict()
        return self.__textureSets[name]

    if IS_EDITOR:

        @property
        def textureSets(self):
            return self.__textureSets

        @property
        def chassisEffectGroups(self):
            return self.__chassisEffectGroups


def _readFloat(dataSec, name, minVal, maxVal, defaultVal):
    if dataSec is None:
        return defaultVal
    else:
        value = dataSec.readFloat(name, defaultVal)
        value = min(maxVal, value)
        value = max(minVal, value)
        return value


def _readCfg(dataSec):
    if dataSec is None:
        LOG_ERROR('Invalid dataSection.')
        return {}
    else:
        config = {'criticalHitDecalAngle': dataSec.readFloat('criticalAngle', 30.0),
         'groups': {group.name:{'lifeTime': _readFloat(group, 'lifeTime', 0, 1000, 1),
                    'trianglesCount': _readFloat(group, 'trianglesCount', 1000, 100000, 1000)} for group in dataSec['groups'].values()},
         'chassisEffectsGroups': {},
         'textures': {texture.name:texture.readString('texture') for texture in dataSec['textures'].values()},
         'scales': [],
         'traceTextures': set(),
         'textureSets': {}}
        chassisEffectsSection = ResMgr.openSection('scripts/item_defs/vehicles/common/chassis_effects.xml')
        if not chassisEffectsSection or chassisEffectsSection['decals'] is None:
            LOG_ERROR('Failed to read chassis_effects.xml file')
            return config
        dataSec = chassisEffectsSection['decals']
        for group in dataSec['bufferPrefs'].values():
            desc = {'lifeTime': _readFloat(group, 'lifeTime', 0, 1000, 1),
             'trianglesCount': _readFloat(group, 'trianglesCount', 1000, 100000, 1000)}
            config['groups'][group.name] = desc
            config['chassisEffectsGroups'][group.name] = desc

        for sMatId in dataSec['scales'].values():
            config['scales'].append((sMatId.name, _readFloat(sMatId, 'scaleU', 1, 2, 1)))

        for dsTexSet in dataSec['textureSets'].values():
            ts = {}
            _DIF_TEXT = 0
            _BUMP_TEXT = 1
            _STRAFE_DIF_TEXT = 2
            _STRAFE_BUMP_TEXT = 3
            for dsMaterial in dsTexSet.values():
                tsMaterial = [None,
                 None,
                 None,
                 None]
                ts[dsMaterial.name] = tsMaterial
                for dsTexture in dsMaterial.values():
                    texName = dsMaterial.readString(dsTexture.name)
                    config['traceTextures'].add(texName)
                    textListIndex = _DIF_TEXT
                    if dsTexture.name == 'ANM':
                        textListIndex = _BUMP_TEXT
                    elif dsTexture.name == 'STRAFE_AM':
                        textListIndex = _STRAFE_DIF_TEXT
                    elif dsTexture.name == 'STRAFE_ANM':
                        textListIndex = _STRAFE_BUMP_TEXT
                    tsMaterial[textListIndex] = texName

            config['textureSets'][dsTexSet.name] = ts

        return config


g_instance = None

def init(section):
    global g_instance
    config = pdc.load('decal_map_config', partial(_readCfg, section))
    g_instance = DecalMap(config)
