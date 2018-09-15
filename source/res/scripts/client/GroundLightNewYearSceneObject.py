# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/GroundLightNewYearSceneObject.py
import BigWorld
import MapActivities
from collections import namedtuple
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from debug_utils import LOG_ERROR
from helpers import dependency
from skeletons.new_year import ICustomizableObjectsManager
from helpers.EffectsList import EffectsListPlayer
from vehicle_systems.stricted_loading import makeCallbackWeak
_ModelEffects = namedtuple('_ModelEffects', ('regularEffect', 'hangingEffect'))
_ModelData = namedtuple('_ModelData', ('model', 'effects'))

class GroundLightNewYearSceneObject(BigWorld.Entity):
    customizableObjectsMgr = dependency.descriptor(ICustomizableObjectsManager)

    def __init__(self):
        super(GroundLightNewYearSceneObject, self).__init__()
        self.__nodeModels = {}

    def prerequisites(self):
        return [self.baseModelName]

    def onEnterWorld(self, prereqs):
        if self.baseModelName not in prereqs.failedIDs:
            model = prereqs[self.baseModelName]
            self.model = model
            self.filter = BigWorld.DumbFilter()
            self.model.addMotor(BigWorld.Servo(self.matrix))
        g_eventBus.addListener(events.NewYearEvent.ON_PLACE_GROUND_LIGHTS, self.__handlePlaceToyEvent, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.NewYearEvent.ON_REMOVE_GROUND_LIGHTS, self.__handleRemoveToyEvent, EVENT_BUS_SCOPE.LOBBY)

    def onLeaveWorld(self):
        self.__clearNodes()
        g_eventBus.removeListener(events.NewYearEvent.ON_PLACE_GROUND_LIGHTS, self.__handlePlaceToyEvent, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.NewYearEvent.ON_REMOVE_GROUND_LIGHTS, self.__handleRemoveToyEvent, EVENT_BUS_SCOPE.LOBBY)

    def collideSegment(self, startPoint, endPoint, skipGun=False):
        return None

    def __handlePlaceToyEvent(self, event):
        self.__clearNodes()
        modelName = event.ctx['modelName']
        effects = _ModelEffects(event.ctx['regularEffectName'], event.ctx['hangingEffectName'])
        for i in range(self.hardPointCount):
            BigWorld.loadResourceListBG([modelName], makeCallbackWeak(self.__onModelLoaded, nodeIndex=i + 1, modelName=modelName, effects=effects))

    def __handleRemoveToyEvent(self, _):
        self.__clearNodes()

    def __onModelLoaded(self, resourceRefs, nodeIndex, modelName, effects):
        if modelName not in resourceRefs.failedIDs:
            model = resourceRefs[modelName]
            nodeName = '{}{:02d}'.format(self.hardPointPrefix, nodeIndex)
            try:
                node = self.model.node(nodeName)
                node.attach(model)
            except ValueError:
                LOG_ERROR('No node named "{}" in this model: {}'.format(nodeName, modelName))
                return

            effectPlayers = []
            regularEffectPlayer = self.__playEffect(model, effects.regularEffect)
            if regularEffectPlayer is not None:
                effectPlayers.append(regularEffectPlayer)
            hangingEffectPlayer = self.__playHangingEffect(model, effects.hangingEffect)
            if hangingEffectPlayer is not None:
                effectPlayers.append(hangingEffectPlayer)
            self.__nodeModels[nodeName] = _ModelData(model, effectPlayers)
        else:
            LOG_ERROR('Failed to load model: ', modelName)
        return

    def __clearNodes(self):
        for nodeName, modelData in self.__nodeModels.iteritems():
            for effect in modelData.effects:
                effect.stop()

            model = modelData.model
            try:
                node = self.model.node(nodeName)
                node.detach(model)
            except ValueError:
                continue

        self.__nodeModels.clear()

    def __playHangingEffect(self, model, effectName):
        return None if not self.customizableObjectsMgr.state else self.__playEffect(model, effectName)

    def __playEffect(self, model, effectName):
        effectsCache = self.customizableObjectsMgr.effectsCache
        if effectName in effectsCache:
            effect = effectsCache[effectName]
            effectPlayer = EffectsListPlayer(effect.effectsList, effect.keyPoints)
            effectPlayer.play(model)
        else:
            effectPlayer = MapActivities.startActivity(effectName)
        return effectPlayer
