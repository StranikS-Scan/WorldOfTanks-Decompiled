# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/BossLandmine.py
import BigWorld
import Math
from debug_utils import LOG_ERROR
from helpers.EffectsList import effectsFromSection, EffectsListPlayer
from BossModeSettings import BossModeEvents
import ArenaType
import ResMgr
import copy
import SoundGroups
_HALLOWEEN_STUN_SOUND = 'ev_halloween_imp_stun'

class BossLandmine(BigWorld.Entity):
    _BASE_LANDMINE_ACTIVATE_DURATION = 5.5

    def __init__(self):
        self.__destroyed = False
        self.__effectsTimeLine = {}
        self.__settings = ArenaType.g_cache[BigWorld.player().arenaTypeID].bossModes
        self.__prepareMineEffects()
        self.__effectsPlayerList = []
        self.__exploded = False
        self.__activeModels = []
        self.__modelActiveTimerId = None
        if self.__settings is not None:
            self.__modelDataList = copy.deepcopy(self.__settings.mineModels)
            self.__loadModels()
        return

    def destroy(self):
        self.onLeaveWorld()

    def onEnterWorld(self, prereqs):
        pass

    def onDestroy(self):
        self.onLeaveWorld()

    def onLeaveWorld(self):
        self.__destroyed = True
        self.__clearActiveModels()
        if self.__modelActiveTimerId is not None:
            BigWorld.cancelCallback(self.__modelActiveTimerId)
            self.__modelActiveTimerId = None
        for effectPlayer in self.__effectsPlayerList:
            effectPlayer.stop()

        return

    def __clearActiveModels(self):
        for model in self.__activeModels:
            BigWorld.delModel(model)

        del self.__activeModels[:]

    def onExplode(self, vehicleID):
        if not self.__exploded:
            self.__startMineEffect('mineExitEffect')
            self.__exploded = True
            vehicle = BigWorld.player().vehicle
            if vehicle is not None and vehicle.id == vehicleID:
                SoundGroups.g_instance.playSound2D(_HALLOWEEN_STUN_SOUND)
        return

    def onActivate(self):
        self.__startMineEffect('mineActivationEffect')
        self.__modelActiveTimerId = BigWorld.callback(self.__settings.mineModelActivationDelay, self.__activateMineActiveModel)

    def __activateMineActiveModel(self):
        self.__modelActiveTimerId = None
        self.__turnOnModels('mineActive')
        self.__startMineEffect('mineActiveEffect')
        return

    def __loadModels(self):
        allModels = []
        for key, modelList in self.__modelDataList.iteritems():
            for modelData in modelList:
                allModels.append(modelData['modelName'])

        BigWorld.loadResourceListBG(allModels, self.__onModelLoaded)

    def __onModelLoaded(self, resourceRefs):
        if getattr(self, '_BossLandmine__destroyed', None) is None:
            return
        elif self.__destroyed:
            return
        else:
            modelDataList = self.__modelDataList
            for key, modelList in modelDataList.iteritems():
                for modelData in modelList:
                    modelName = modelData['modelName']
                    if modelName not in resourceRefs.failedIDs:
                        modelData['model'] = resourceRefs[modelName]
                    LOG_ERROR('Could not load model %s' % modelName)

            self.__startMineVisuals()
            return

    def __startMineVisuals(self):
        self.__turnOnModels('mineEnter')
        for model in self.__activeModels:
            model.actionScale = self._BASE_LANDMINE_ACTIVATE_DURATION / self.__settings.mineActivationDelay

        self.__startMineEffect('mineEnterEffect')

    def __turnOnModels(self, modelKey):
        self.__clearActiveModels()
        modelDataList = self.__modelDataList
        modelList = modelDataList.get(modelKey, None)
        if modelList is not None:
            for modelData in modelList:
                model = modelData.get('model', None)
                if model is not None:
                    self.__activeModels.append(model)
                    BigWorld.addModel(model)
                    model.position = self.position
                    modelAnim = modelData.get('actionName', None)
                    if modelAnim:
                        modelAction = model.action(modelAnim)
                        if modelAction is not None:
                            modelAction(0)

        return

    def __startMineEffect(self, effectName):
        if self.__activeModels:
            activeEffect = self.__effectsTimeLine[effectName]
            effectPlayer = EffectsListPlayer(activeEffect.effectsList, activeEffect.keyPoints)
            self.__effectsPlayerList.append(effectPlayer)
            effectPlayer.play(self.__activeModels[0])

    def __prepareMineEffects(self):
        effects = self.__settings.mineEffects
        if effects is not None:
            for effect in effects.values():
                name = effect.name
                self.__effectsTimeLine[name] = effectsFromSection(effect)

        return
