# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/EventPointsBase.py
from functools import partial
import logging
import BigWorld
import ArenaType
from helpers import newFakeModel
from helpers.EffectsList import EffectsListPlayer, effectsFromSection
from vehicle_systems.stricted_loading import _MAX_PRIORITY
_logger = logging.getLogger(__name__)

class EventPointsBase(BigWorld.Entity):
    _EFFECT_OFFSET = (0.0, 23.16, 0.0)
    _STATIC_MODEL_BASE_NAME = 'particles/content_deferred/GFX_models/environment/Halloween2018_Ghost_Base.model'
    _STATIC_MODEL_BASE_OFFSET = (0.0, -0.34, 0.0)
    _STATIC_MODEL_BASE_SCALE = (30.0, 60.0, 30.0)
    _STATIC_MODEL_CONE_NAME = 'particles/content_deferred/GFX_models/environment/Halloween2018_Ghost_Cone.model'
    _STATIC_MODEL_CONE_OFFSET = (0.0, -6.3, 0.0)
    _STATIC_MODEL_CONE_SCALE = (30.0, 10.0, 30.0)

    def __init__(self):
        super(EventPointsBase, self).__init__(self)
        self._effectsPlayer = None
        self._fakeModel = None
        self._staticModelBase = None
        self._staticModelCone = None
        return

    def prerequisites(self):
        effectsSection = ArenaType.g_cache[BigWorld.player().arenaTypeID].eventPointsPickupSettings.epEffects
        effect = effectsFromSection(effectsSection['CollectorLargeEffect'])
        prereqs = effect.effectsList.prerequisites()
        self._effectsPlayer = EffectsListPlayer(effect.effectsList, effect.keyPoints)
        return prereqs

    def onEnterWorld(self, prereqs):
        eventPointsBaseComponent = BigWorld.player().arena.componentSystem.eventPointsBaseComponent
        if eventPointsBaseComponent is not None:
            eventPointsBaseComponent.init(self)
        self._fakeModel = newFakeModel()
        self._fakeModel.position = self.position + self._EFFECT_OFFSET
        BigWorld.player().addModel(self._fakeModel)
        eventPointsComponent = BigWorld.player().arena.componentSystem.eventPointsComponent
        if eventPointsComponent is not None:
            eventPointsComponent.onTotalEventPointsUpdated += self.__onTotalEventPointsUpdated
        BigWorld.loadResourceListBG((EventPointsBase._STATIC_MODEL_BASE_NAME, EventPointsBase._STATIC_MODEL_CONE_NAME), partial(self.__onModelLoaded, totalEventPoints=eventPointsComponent.totalEventPoints), _MAX_PRIORITY)
        return

    def onLeaveWorld(self):
        eventPointsComponent = BigWorld.player().arena.componentSystem.eventPointsComponent
        if eventPointsComponent is not None:
            eventPointsComponent.onTotalEventPointsUpdated -= self.__onTotalEventPointsUpdated
        if self._effectsPlayer is not None:
            self._effectsPlayer.stop()
            self._effectsPlayer = None
        if self._fakeModel is not None:
            BigWorld.player().delModel(self._fakeModel)
            self._fakeModel = None
        self.__destroyModels()
        eventPointsBaseComponent = BigWorld.player().arena.componentSystem.eventPointsBaseComponent
        if eventPointsBaseComponent is not None:
            eventPointsBaseComponent.clear()
        return

    def __onTotalEventPointsUpdated(self, eventPoints):
        totalEventPoints = eventPoints.get(self.team, 0)
        if totalEventPoints:
            self.__addModels()
            if not self._effectsPlayer.isPlaying:
                self._effectsPlayer.play(self._fakeModel)
        else:
            self.__delModels()
            self._effectsPlayer.stop()

    def __addModels(self):
        self.__addModel(self._staticModelBase, EventPointsBase._STATIC_MODEL_BASE_NAME)
        self.__addModel(self._staticModelCone, EventPointsBase._STATIC_MODEL_CONE_NAME)

    def __addModel(self, model, modelName):
        if model is not None:
            if not model.inWorld:
                BigWorld.player().addModel(model)
        else:
            _logger.error('Unable to add model: %s', modelName)
        return

    def __destroyModels(self):
        self.__delModels()
        self._staticModelBase = None
        self._staticModelCone = None
        return

    def __delModels(self):
        if self._staticModelBase is not None and self._staticModelBase.inWorld:
            BigWorld.player().delModel(self._staticModelBase)
        if self._staticModelCone is not None and self._staticModelCone.inWorld:
            BigWorld.player().delModel(self._staticModelCone)
        return

    def __onModelLoaded(self, resourceRefs, totalEventPoints):
        self._staticModelBase = self.__createModel(resourceRefs, EventPointsBase._STATIC_MODEL_BASE_NAME, EventPointsBase._STATIC_MODEL_BASE_OFFSET, EventPointsBase._STATIC_MODEL_BASE_SCALE)
        self._staticModelCone = self.__createModel(resourceRefs, EventPointsBase._STATIC_MODEL_CONE_NAME, EventPointsBase._STATIC_MODEL_CONE_OFFSET, EventPointsBase._STATIC_MODEL_CONE_SCALE)
        self.__onTotalEventPointsUpdated(totalEventPoints)

    def __createModel(self, resourceRefs, modelName, modelOffset, modelScale):
        model = None
        if modelName not in resourceRefs.failedIDs:
            model = resourceRefs[modelName]
            model.position = self.position + modelOffset
            model.scale = modelScale
        else:
            _logger.error('Model not found: %s', modelName)
        return model
