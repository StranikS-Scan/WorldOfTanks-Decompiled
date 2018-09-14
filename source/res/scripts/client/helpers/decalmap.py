# Embedded file name: scripts/client/helpers/DecalMap.py
import BigWorld
import ResMgr
from debug_utils import *
g_instance = None

class DecalMap:

    def __init__(self, dataSec):
        self.__cfg = dict()
        self.__texMap = dict()
        self.__textureSets = dict()
        self._readCfg(dataSec)

    def initGroups(self, scaleFactor):
        try:
            for group in self.__cfg['groups'].items():
                BigWorld.wg_addDecalGroup(group[0], group[1]['lifeTime'] * scaleFactor, group[1]['trianglesCount'] * scaleFactor)

            for tex in self.__cfg['textures'].items():
                index = BigWorld.wg_decalTextureIndex(tex[1])
                if index == -1:
                    LOG_ERROR("texture '%s' is not exist or to more textures added to the texture atlas.Max textures count is 16." % tex[1])
                else:
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

            for dsTexSet in dataSec['textureSets'].values():
                ts = {}
                _DIF_TEXT = 0
                _BUMP_TEXT = 1
                _HMAP_TEXT = 2
                for dsMaterial in dsTexSet.values():
                    tsMaterial = [None, None, None]
                    ts[dsMaterial.name] = tsMaterial
                    for dsTexture in dsMaterial.values():
                        texName = dsMaterial.readString(dsTexture.name)
                        texIndex = BigWorld.wg_traceTextureIndex(texName)
                        self.__texMap[texName] = texIndex
                        textListIndex = _DIF_TEXT
                        if dsTexture.name == 'ANM':
                            textListIndex = _BUMP_TEXT
                        elif dsTexture.name == 'GMM':
                            textListIndex = _HMAP_TEXT
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
