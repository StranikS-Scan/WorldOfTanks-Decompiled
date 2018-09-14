# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/christmas/ChristmasTank.py
import ChristmassTreeManager
import ResMgr
import BigWorld
import weakref
import Math
from collections import namedtuple
from functools import partial
from christmas_shared import CHRISTMAS_TOOLTIPS_IDS
from debug_utils import LOG_ERROR
from helpers.EffectsList import effectsFromSection, EffectsListPlayer
_CHRISTMASS_CONFIG_FILE = 'scripts/christmasstree.xml'
_TankModelInfo = namedtuple('_TankModelInfo', ['file', 'fileExt', 'hangEffect'])
_TankTextureInfo = namedtuple('_TankTextureInfo', ['file'])
_TankHangInfo = namedtuple('_TankHangInfo', ['model',
 'modelExt',
 'hangEffect',
 'texture'])
_TankUIDInfo = namedtuple('_TankUIDInfo', ['model', 'texture'])

class ChristmasTank(object):
    parent = property(lambda self: self.__parent())

    def __init__(self, parent):
        self.__onClickcallback = None
        self.__modelsDB = None
        self.__textureDB = None
        self.__uids = None
        self.__effectsTimeLine = None
        self.__parent = weakref.ref(parent)
        self.__tankDesc = dict()
        self.__fillModelsDict()
        self.__fashion = BigWorld.WGNYFashion()
        ChristmassTreeManager.g_christMassManager.setPart(self, ChristmassTreeManager.TANK)
        return

    def tooltipID(self):
        return CHRISTMAS_TOOLTIPS_IDS.TANK

    def onEnterWorld(self):
        self.parent.model.nyFashion = self.__fashion

    def onLeaveWorld(self):
        self.__onClickcallback = None
        for hpName, nodeDesc in self.__tankDesc.iteritems():
            self.__destroyToy(hpName, nodeDesc)

        self.__tankDesc = None
        return

    def setOnClickCallback(self, callback):
        self.__onClickcallback = callback

    def onClicked(self):
        if self.__onClickcallback is not None:
            self.__onClickcallback()
        return

    def hangToyByID(self, toyID, HPname=None):
        uidInfo = self.__uids.get(toyID, _TankUIDInfo(None, None))
        if uidInfo.model is not None:
            if uidInfo.model is not None:
                self.__hangToy(uidInfo.model, HPname, uidInfo.texture)
            else:
                LOG_ERROR("Model ID not found '%s'." % toyID)
        else:
            self.removeToy(HPname)
            if uidInfo.texture is not None:
                self.__applyTexture(uidInfo.texture)
                self.__tankDesc[HPname] = _TankHangInfo(None, None, None, uidInfo.texture is not None)
        return

    def applyTexture(self, textureID):
        uidInfo = self.__uids.get(textureID, _TankUIDInfo(None, None))
        if uidInfo.texture is not None:
            self.__applyTexture(uidInfo.texture)
        else:
            LOG_ERROR("Texture ID not found '%s'." % textureID)
        return

    def removeTexture(self):
        self.__applyTexture('')

    def removeToy(self, HPname):
        nodeDesc = self.__tankDesc.get(HPname, None)
        if nodeDesc is not None:
            self.__destroyToy(HPname, nodeDesc)
            del self.__tankDesc[HPname]
        return

    def __destroyToy(self, HPname, nodeDesc):
        if nodeDesc.texture:
            self.removeTexture()
        if nodeDesc.model is not None:
            self.parent.model.node(HPname).detach(nodeDesc.model)
        elif nodeDesc.modelExt is not None:
            BigWorld.delModel(nodeDesc.modelExt)
        if nodeDesc.hangEffect is not None:
            nodeDesc.hangEffect.stop()
        return

    def __hangToy(self, modelName, HPname, texture):
        modelDesc = self.__modelsDB.get(modelName, None)
        if modelDesc is not None:
            prereqs = []
            if modelDesc.file != '':
                prereqs = [modelDesc.file]
            elif modelDesc.fileExt != '':
                prereqs = [modelDesc.fileExt]
            loadFunc = partial(self.__modelLoaded, modelName=modelName, modelPath=modelDesc.file, modelExtPath=modelDesc.fileExt, hardPoint=HPname, texture=texture)
            BigWorld.loadResourceListBG(list(prereqs), loadFunc)
        else:
            LOG_ERROR("Can't create model '%s'." % modelName)
        return

    def __applyTexture(self, textureName):
        if self.__fashion is not None:
            if textureName != '':
                textureDesc = self.__textureDB.get(textureName, None)
                texturePath = textureDesc.file
                self.__fashion.setTexture(texturePath, 'diffuseMap')
            else:
                self.__fashion.setTexture('', 'diffuseMap')
        return

    def __playEffect(self, modelName, model):
        modelDesc = self.__modelsDB.get(modelName, None)
        effectsPlayer = None
        if modelDesc is not None:
            effect = modelDesc.hangEffect
            if effect is not None:
                effectsPlayer = EffectsListPlayer(effect.effectsList, effect.keyPoints)
                effectsPlayer.play(model)
        return effectsPlayer

    def __modelLoaded(self, resourceRefs, modelPath, modelExtPath, hardPoint, modelName, texture):
        if resourceRefs.failedIDs:
            LOG_ERROR('Failed to load resources %s' % (resourceRefs.failedIDs,))
        else:
            nodeDesc = self.__tankDesc.get(hardPoint, None)
            if texture is not None:
                self.__applyTexture(texture)
            if nodeDesc is not None:
                if nodeDesc.model is not None:
                    self.parent.model.node(hardPoint).detach(nodeDesc.model)
                elif nodeDesc.modelExt is not None:
                    BigWorld.delModel(nodeDesc.modelExt)
                if nodeDesc.hangEffect is not None:
                    nodeDesc.hangEffect.stop()
            if modelPath != '':
                model = resourceRefs[modelPath]
                self.parent.model.node(hardPoint).attach(model)
                self.__tankDesc[hardPoint] = _TankHangInfo(model, None, self.__playEffect(modelName, model), texture is not None)
            elif modelExtPath != '':
                extModel = resourceRefs[modelExtPath]
                hardPointMatrix = Math.Matrix(self.parent.model.node(hardPoint))
                extModel.position = hardPointMatrix.translation
                extModel.yaw = hardPointMatrix.yaw
                extModel.visible = True
                BigWorld.addModel(extModel, BigWorld.player().spaceID)
                self.__tankDesc[hardPoint] = _TankHangInfo(None, extModel, self.__playEffect(modelName, extModel), texture is not None)
        return

    def __textureLoaded(self, resourceRefs, texturePath, textureName):
        if resourceRefs.failedIDs:
            LOG_ERROR('Failed to load resources %s' % (resourceRefs.failedIDs,))
        else:
            BigWorld.wg_setPyModelTexture(self.__parent.model, 'diffuseMap', textureName)

    def __fillModelsDict(self):
        configSection = ResMgr.openSection(_CHRISTMASS_CONFIG_FILE)
        self.__modelsDB = dict()
        self.__textureDB = dict()
        self.__uids = dict()
        self.__effectsTimeLine = dict()
        if configSection is not None:
            tank = configSection['tank']
            if tank is None:
                return
            effects = tank['effects']
            if effects is not None:
                for effect in effects.values():
                    self.__effectsTimeLine[effect.name] = effectsFromSection(effect)

            models = tank['models']
            if models is not None:
                for model in models.values():
                    modelName = model.readString('name', '').split()[0]
                    modelFile = model.readString('file', '')
                    if modelFile != '':
                        modelFile = modelFile.split()[0]
                    modelExtFile = model.readString('fileExt', '')
                    hangEffectName = model.readString('hangEffect', '').split()
                    hangEffectName = hangEffectName[0] if len(hangEffectName) > 0 else None
                    if modelName == '' or modelFile == '' and modelExtFile == '':
                        continue
                    uid = model.readInt('uid', 0)
                    uidInfo = self.__uids.get(uid, None)
                    if uidInfo is None:
                        self.__uids[uid] = _TankUIDInfo(modelName, None)
                    else:
                        self.__uids[uid] = _TankUIDInfo(modelName, uidInfo.texture)
                    if hangEffectName is not None:
                        hangEffectList = self.__effectsTimeLine.get(hangEffectName, None)
                    else:
                        hangEffectList = None
                    self.__modelsDB[modelName] = _TankModelInfo(modelFile, modelExtFile, hangEffectList)

            textures = tank['textures']
            if textures is not None:
                for texture in textures.values():
                    textureName = texture.readString('name', '').split()[0]
                    textureFile = texture.readString('file', '').split()[0]
                    if textureName == '' or textureFile == '':
                        continue
                    uid = texture.readInt('uid', 0)
                    uidInfo = self.__uids.get(uid, None)
                    if uidInfo is None:
                        self.__uids[uid] = _TankUIDInfo(None, textureName)
                    else:
                        self.__uids[uid] = _TankUIDInfo(uidInfo.model, textureName)
                    self.__textureDB[textureName] = _TankTextureInfo(textureFile)

        return
