# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ChristmassTree.py
import BigWorld
import ResMgr
import ChristmassTreeManager
import SoundGroups
import Math
import WWISE
from ClientSelectableCameraObject import ClientSelectableCameraObject, CameraMovementStates
from functools import partial
from christmas_shared import CHRISTMAS_TOOLTIPS_IDS
from helpers.EffectsList import effectsFromSection, EffectsListPlayer
from debug_utils import LOG_ERROR
_CHRISTMASS_CONFIG_FILE = 'scripts/christmasstree.xml'

class ChristmassTree(ClientSelectableCameraObject):

    def __init__(self):
        super(ChristmassTree, self).__init__()
        self.__toysDB = None
        self.__treeDesc = dict()
        self.__uids = dict()
        self.__effectsTimeLine = None
        self.__clickSound = None
        self.__hoverSound = None
        self.__fillToysDict()
        self.enable(True)
        return

    def __del__(self):
        self.__clickSound = None
        self.__hoverSound = None
        return

    def tooltipID(self):
        return CHRISTMAS_TOOLTIPS_IDS.TREE

    def onEnterWorld(self, prereqs):
        super(ChristmassTree, self).onEnterWorld(prereqs)
        ChristmassTreeManager.g_christMassManager.setPart(self, ChristmassTreeManager.TREE)
        self.__treeDesc = dict()

    def onLeaveWorld(self):
        super(ChristmassTree, self).onLeaveWorld()
        ChristmassTreeManager.g_christMassManager.removePart(ChristmassTreeManager.TREE)
        self.__clearTree()

    def defaultSetup(self):
        self.hangToyByID(50, 'HP_mount_01')
        self.hangToyByID(23, 'HP_mount_08')
        self.hangToyByID(102, 'HP_mount_02')
        self.hangToyByID(109, 'HP_mount_03')
        self.hangToyByID(112, 'HP_mount_04')
        self.hangToyByID(104, 'HP_mount_06')
        self.hangToyByID(106, 'HP_mount_07')
        self.hangToyByID(108, 'HP_mount_09')
        self.hangToyByID(53, 'HP_mount_11')
        self.hangToyByID(56, 'HP_mount_12')

    def __clearTree(self):
        for hardPoint, nodeDesc in self.__treeDesc.iteritems():
            if nodeDesc[2] is not None:
                BigWorld.delModel(nodeDesc[2])
            self.model.node(hardPoint).detach(nodeDesc[0])
            if nodeDesc[1][0] is not None:
                nodeDesc[1][0].stop()
            if nodeDesc[1][1] is not None:
                nodeDesc[1][1].stop()

        self.__treeDesc = dict()
        return

    def enable(self, enabled, clear=False):
        if self.state == CameraMovementStates.ON_OBJECT and enabled:
            return
        super(ChristmassTree, self).enable(enabled)
        if not enabled and clear:
            self.__clearTree()

    def hangToy(self, toyName, HPname=None):
        toyDesc = self.__toysDB.get(toyName, None)
        if toyDesc is not None:
            modelWPath, hardPoint, _, _, extModel = toyDesc
            if HPname is None:
                HPname = hardPoint
            if extModel != '':
                prereqs = [modelWPath, extModel]
            else:
                prereqs = [modelWPath]
            loadFunc = partial(self.__modelLoaded, toyName=toyName, modelName=modelWPath, hardPoint=HPname, extModelName=extModel)
            BigWorld.loadResourceListBG(list(prereqs), loadFunc)
        else:
            LOG_ERROR("Can't create toy '%s'." % toyName)
        return

    def hangToyByID(self, toyID, HPname=None, isLeft=False):
        toyNames = self.__uids.get(toyID, None)
        if toyNames is not None:
            if isinstance(toyNames, tuple):
                self.hangToy(toyNames[0 if isLeft else 1], HPname)
            else:
                self.hangToy(toyNames, HPname)
        else:
            LOG_ERROR("Toy ID not found '%s'." % toyID)
        return

    def removeToy(self, HPname):
        nodeDesc = self.__treeDesc.get(HPname, None)
        if nodeDesc is not None:
            if nodeDesc[1][0] is not None:
                nodeDesc[1][0].stop()
            if nodeDesc[1][1] is not None:
                nodeDesc[1][1].stop()
            if nodeDesc[2] is not None:
                BigWorld.delModel(nodeDesc[2])
            self.model.node(HPname).detach(nodeDesc[0])
            del self.__treeDesc[HPname]
        return

    def onClicked(self):
        if self.enabled:
            super(ChristmassTree, self).onClicked()

    def stopHangEffects(self):
        for _, effectPlayers, _ in self.__treeDesc.itervalues():
            hangEffectsPlayer = effectPlayers[1]
            if hangEffectsPlayer is not None:
                hangEffectsPlayer.stop()

        return

    def highlight(self, show):
        super(ChristmassTree, self).highlight(show)
        if self.__hoverSound is not None:
            if show:
                self.__hoverSound.play()
        return

    def __modelLoaded(self, resourceRefs, modelName, hardPoint, toyName, extModelName):
        if resourceRefs.failedIDs:
            LOG_ERROR('Failed to load resources %s' % (resourceRefs.failedIDs,))
        else:
            nodeDesc = self.__treeDesc.get(hardPoint, None)
            if nodeDesc is not None:
                if nodeDesc[1][0] is not None:
                    nodeDesc[1][0].stop()
                if nodeDesc[1][1] is not None:
                    nodeDesc[1][1].stop()
                if nodeDesc[2] is not None:
                    BigWorld.delModel(nodeDesc[2])
                self.model.node(hardPoint).detach(nodeDesc[0])
            extModel = None
            if extModelName != '':
                extModel = resourceRefs[modelName]
                model = resourceRefs[extModelName]
                hardPointPosition = Math.Matrix(self.model.node(hardPoint)).translation
                extModel.position = hardPointPosition
                extModel.visible = True
                BigWorld.addModel(extModel, BigWorld.player().spaceID)
                self.model.node(hardPoint).attach(model)
            else:
                model = resourceRefs[modelName]
                self.model.node(hardPoint).attach(model)
            self.__treeDesc[hardPoint] = (model, self.__playEffect(toyName, model), extModel)
        return

    def __playEffect(self, toyName, model):
        effectsPlayer = None
        hangEffectsPlayer = None
        toyDesc = self.__toysDB.get(toyName, None)
        if toyDesc is not None:
            effect = toyDesc[2]
            if effect is not None:
                effectsPlayer = EffectsListPlayer(effect.effectsList, effect.keyPoints)
                effectsPlayer.play(model)
            if ChristmassTreeManager.isChristmasView():
                effect = toyDesc[3]
                if effect is not None:
                    hangEffectsPlayer = EffectsListPlayer(effect.effectsList, effect.keyPoints)
                    hangEffectsPlayer.play(model)
        return (effectsPlayer, hangEffectsPlayer)

    def __fillToysDict(self):
        configSection = ResMgr.openSection(_CHRISTMASS_CONFIG_FILE)
        self.__toysDB = dict()
        self.__effectsTimeLine = dict()
        self.__uids = dict()
        if configSection is not None:
            effects = configSection['effects']
            if effects is not None:
                for effect in effects.values():
                    name = effect.name
                    self.__effectsTimeLine[name] = effectsFromSection(effect)

            toys = configSection['toys']
            if toys is not None:
                for toy in toys.values():
                    toyName = toy.readString('name', '')
                    toyFile = toy.readString('file', '')
                    extModel = toy.readString('extModel', '')
                    if toyName == '' or toyFile == '':
                        continue
                    defaultHP = toy.readString('defaultHP', '')
                    effectName = toy.readString('effect', '')
                    hangEffectName = toy.readString('hangEffect', '')
                    uid = toy.readInt('uid', 0)
                    prevToyName = self.__uids.get(uid, None)
                    if prevToyName is not None:
                        isLeft = toy.readBool('left', False)
                        if isLeft:
                            self.__uids[uid] = (toyName, prevToyName)
                        else:
                            self.__uids[uid] = (prevToyName, toyName)
                    elif uid > 0:
                        self.__uids[uid] = toyName
                    effectList = self.__effectsTimeLine.get(effectName, None)
                    hangEffectList = self.__effectsTimeLine.get(hangEffectName, None)
                    self.__toysDB[toyName] = (toyFile,
                     defaultHP,
                     effectList,
                     hangEffectList,
                     extModel)

            soundsSec = configSection['sounds']
            if soundsSec is not None:
                clickSoundName = soundsSec.readString('treeclick', '')
                hoverSoundName = soundsSec.readString('treeover', '')
                try:
                    self.__clickSound = SoundGroups.g_instance.getSound2D(clickSoundName)
                except:
                    LOG_ERROR('Could not load sound %s' % clickSoundName)

                try:
                    self.__hoverSound = SoundGroups.g_instance.getSound2D(hoverSoundName)
                except:
                    LOG_ERROR('Could not load sound %s' % hoverSoundName)

        return
