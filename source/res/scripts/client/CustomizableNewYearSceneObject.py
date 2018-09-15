# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/CustomizableNewYearSceneObject.py
import BigWorld
import MapActivities
from DormantSelectableObject import DormantSelectableObject
from helpers import dependency
from skeletons.new_year import ICustomizableObjectsManager
from debug_utils import LOG_ERROR
from collections import namedtuple
from helpers.EffectsList import EffectsListPlayer
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.Scaleform.genConsts.NY_CONSTANTS import NY_CONSTANTS
from vehicle_systems.stricted_loading import makeCallbackWeak
_NodeData = namedtuple('NodeData', ['model', 'regularEffect', 'hangingEffect'])

class CustomizableNewYearSceneObject(DormantSelectableObject):
    customizableObjectsMgr = dependency.descriptor(ICustomizableObjectsManager)

    def __init__(self):
        self.__placedToys = {}
        self.__effectsCache = {}
        super(CustomizableNewYearSceneObject, self).__init__(0)

    def onEnterWorld(self, prereqs):
        super(CustomizableNewYearSceneObject, self).onEnterWorld(prereqs)
        self.customizableObjectsMgr.addCustomizableEntity(self)

    def onLeaveWorld(self):
        self.customizableObjectsMgr.removeCustomizableEntity(self)
        for node, nodeData in self.__placedToys.iteritems():
            self.__removeToy(node, nodeData=nodeData)

        self.__placedToys = None
        self.__effectsCache = None
        super(CustomizableNewYearSceneObject, self).onLeaveWorld()
        return

    def _doClick(self):
        if self.anchorName:
            self.customizableObjectsMgr.switchTo(self.anchorName)

    def setEffectsCache(self, effectsCache):
        self.__effectsCache = effectsCache

    def updateNode(self, node, slotInfo):
        nodeDesc = slotInfo.nodeDesc
        slotType = slotInfo.slotType
        if nodeDesc or self.blankModel:
            self.__placeToy(node, nodeDesc, slotType)
        else:
            self.__removeToy(node, slotType=slotType)

    def __removeToy(self, node, slotType=None, nodeData=None):
        if slotType == NY_CONSTANTS.SLOT_TYPE_LAMP:
            g_eventBus.handleEvent(events.NewYearEvent(events.NewYearEvent.ON_REMOVE_GROUND_LIGHTS), scope=EVENT_BUS_SCOPE.LOBBY)
            return
        else:
            nodeData = nodeData or self.__placedToys.pop(node, None)
            if nodeData:
                if nodeData.model:
                    try:
                        self.model.node(node).detach(nodeData.model)
                    except:
                        LOG_ERROR('Could not detach model {} from hardpoint {}'.format(nodeData.model.sources, node))

                if nodeData.regularEffect:
                    nodeData.regularEffect.stop()
                if nodeData.hangingEffect:
                    nodeData.hangingEffect.stop()
            return

    def __placeToy(self, node, nodeDesc, slotType):
        if nodeDesc is None:
            modelName = self.blankModel
        else:
            modelName = nodeDesc.modelName
            if slotType == NY_CONSTANTS.SLOT_TYPE_LAMP:
                g_eventBus.handleEvent(events.NewYearEvent(events.NewYearEvent.ON_PLACE_GROUND_LIGHTS, ctx={'modelName': modelName,
                 'regularEffectName': nodeDesc.regularEffectName,
                 'hangingEffectName': nodeDesc.hangingEffectName}), scope=EVENT_BUS_SCOPE.LOBBY)
                return
        BigWorld.loadResourceListBG([modelName], makeCallbackWeak(self.__onModelLoaded, node=node, nodeDesc=nodeDesc))
        return

    def __onModelLoaded(self, resourceRefs, node, nodeDesc):
        self.__removeToy(node)
        modelName = nodeDesc.modelName if nodeDesc else self.blankModel
        if modelName not in resourceRefs.failedIDs:
            model = resourceRefs[modelName]
            try:
                self.model.node(node).attach(model)
                regular = hanging = None
                if nodeDesc:
                    regular, hanging = self.__playEffects(model, nodeDesc.regularEffectName, nodeDesc.hangingEffectName)
                self.__placedToys[node] = _NodeData(model, regular, hanging)
                if self.blankModel:
                    self._tryToOverrideBSP(model)
            except:
                LOG_ERROR('Could not find hardpoint {}'.format(node))

        else:
            LOG_ERROR('Failed to load toy model {}'.format(modelName))
        return

    def __playEffects(self, model, regularEffectName, hangingEffectName):
        hangingEffectPlayer = None
        if regularEffectName in self.__effectsCache:
            regularEffect = self.__effectsCache[regularEffectName]
            regularEffectPlayer = EffectsListPlayer(regularEffect.effectsList, regularEffect.keyPoints)
            regularEffectPlayer.play(model)
        else:
            regularEffectPlayer = MapActivities.startActivity(regularEffectName)
        if self.customizableObjectsMgr.state:
            if hangingEffectName in self.__effectsCache:
                hangingEffect = self.__effectsCache[hangingEffectName]
                hangingEffectPlayer = EffectsListPlayer(hangingEffect.effectsList, hangingEffect.keyPoints)
                hangingEffectPlayer.play(model)
            else:
                hangingEffectPlayer = MapActivities.startActivity(hangingEffectName)
        return (regularEffectPlayer, hangingEffectPlayer)
