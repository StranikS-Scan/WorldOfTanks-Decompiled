# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/DecalMap.py
import BigWorld
import ResMgr
import material_kinds
from constants import IS_EDITOR
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
g_instance = None

class DecalMap(object):

    def __init__(self, dataSec):
        self.__cfg = dict()
        self.__texMap = dict()
        self.__textureSets = dict()
        if IS_EDITOR:
            self.__chassisEffectGroups = dict()
        self._readCfg(dataSec)

    def initGroups(self, scaleFactor):
        if not BigWorld.isDynamicDecalEnabled():
            return
        try:
            for group in self.__cfg['groups'].items():
                BigWorld.wg_addDecalGroup(group[0], group[1]['lifeTime'] * scaleFactor, group[1]['trianglesCount'] * scaleFactor)

            for tex in self.__cfg['textures'].items():
                index = BigWorld.wg_decalTextureIndex(tex[1])
                if index == -1:
                    LOG_ERROR("texture '%s' is not exist or to more textures added to the texture atlas.Max textures count is 16." % tex[1])
                self.__texMap[tex[0]] = index

        except Exception:
            LOG_CURRENT_EXCEPTION()

    def getIndex(self, name):
        if not self.__texMap.has_key(name):
            if name != '':
                LOG_ERROR("Invalid texture name '%s'" % name)
            return -1
        return self.__texMap[name]

    def getTextureSet(self, name):
        if not self.__textureSets.has_key(name):
            LOG_ERROR("Invalid texture set name '%s'" % name)
            return dict()
        return self.__textureSets[name]

    if IS_EDITOR:

        @property
        def textureSets(self):
            return self.__textureSets

        @property
        def chassisEffectGroups(self):
            return self.__chassisEffectGroups

    def _readCfg(self, dataSec):
        if dataSec is None:
            LOG_ERROR('Invalid dataSection.')
            return
        else:
            criticalHitDecalAngle = dataSec.readFloat('criticalAngle', 30.0)
            BigWorld.setDamageStickerCriticalAngle(criticalHitDecalAngle)
            self.__cfg['groups'] = dict()
            groups = self.__cfg['groups']
            for group in dataSec['groups'].values():
                desc = dict()
                desc['lifeTime'] = _readFloat(group, 'lifeTime', 0, 1000, 1)
                desc['trianglesCount'] = _readFloat(group, 'trianglesCount', 1000, 100000, 1000)
                groups[group.name] = desc

            self.__cfg['textures'] = dict()
            textures = self.__cfg['textures']
            for texture in dataSec['textures'].values():
                textures[texture.name] = texture.readString('texture')

            chassisEffectsSection = ResMgr.openSection('scripts/item_defs/vehicles/common/chassis_effects.xml')
            if not chassisEffectsSection or chassisEffectsSection['decals'] is None:
                LOG_ERROR('Failed to read chassis_effects.xml file')
                return
            dataSec = chassisEffectsSection['decals']
            for group in dataSec['bufferPrefs'].values():
                desc = dict()
                desc['lifeTime'] = _readFloat(group, 'lifeTime', 0, 1000, 1)
                desc['trianglesCount'] = _readFloat(group, 'trianglesCount', 1000, 100000, 1000)
                groups[group.name] = desc
                if IS_EDITOR:
                    self.__chassisEffectGroups[group.name] = desc

            for sMatId in dataSec['scales'].values():
                scaleU = _readFloat(sMatId, 'scaleU', 1, 2, 1)
                for matKind in material_kinds.EFFECT_MATERIAL_IDS_BY_NAMES[sMatId.name]:
                    BigWorld.wg_addMatkindScaleU(sMatId.name, matKind, scaleU)

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
                        texIndex = BigWorld.wg_traceTextureIndex(texName)
                        self.__texMap[texName] = texIndex
                        textListIndex = _DIF_TEXT
                        if dsTexture.name == 'ANM':
                            textListIndex = _BUMP_TEXT
                        elif dsTexture.name == 'STRAFE_AM':
                            textListIndex = _STRAFE_DIF_TEXT
                        elif dsTexture.name == 'STRAFE_ANM':
                            textListIndex = _STRAFE_BUMP_TEXT
                        tsMaterial[textListIndex] = texIndex

                self.__textureSets[dsTexSet.name] = ts

            return

    def writeCfg(self):
        pass


def _readFloat(dataSec, name, minVal, maxVal, defaultVal):
    if dataSec is None:
        return defaultVal
    else:
        value = dataSec.readFloat(name, defaultVal)
        value = min(maxVal, value)
        value = max(minVal, value)
        return value
