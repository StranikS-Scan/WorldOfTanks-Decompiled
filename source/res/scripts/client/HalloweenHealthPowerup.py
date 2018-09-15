# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HalloweenHealthPowerup.py
import BigWorld
from debug_utils import LOG_ERROR
from helpers.EffectsList import effectsFromSection, EffectsListPlayer
from BossModeSettings import BossModeEvents
from gui.Scaleform.daapi.view.battle.bossmode_leviathan.minimap import LEVIATHAN_HEALTH_POWERUP_STATIC_MARKER
import ArenaType
import ResMgr
import copy
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class HalloweenHealthPowerup(BigWorld.Entity):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        self.__destroyed = False
        self.__effectsTimeLine = {}
        self.__settings = ArenaType.g_cache[BigWorld.player().arenaTypeID].bossModes
        self.__preparePowerupEffects()
        self.__effectsPlayerList = []
        self.__consumed = False
        self.__activeModels = []
        self.__modelActiveTimerId = None
        if self.__settings is not None:
            self.__modelDataList = copy.deepcopy(self.__settings.healthPowerupModels)
            self.__loadModels()
        return

    def destroy(self):
        self.onLeaveWorld()

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

        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onStaticMarkerRemoved(self.id)
        return

    def __clearActiveModels(self):
        for model in self.__activeModels:
            BigWorld.delModel(model)

        del self.__activeModels[:]

    def onConsume(self):
        if not self.__consumed:
            self.__startPowerupEffect('powerupConsumeEffect')
            self.__consumed = True

    def __loadModels(self):
        allModels = []
        for key, modelList in self.__modelDataList.iteritems():
            for modelData in modelList:
                allModels.append(modelData['modelName'])

        BigWorld.loadResourceListBG(allModels, self.__onModelLoaded)

    def __onModelLoaded(self, resourceRefs):
        if getattr(self, '_HalloweenHealthPowerup__destroyed', None) is None:
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

            self.__startPowerupVisuals()
            return

    def __startPowerupVisuals(self):
        self.__turnOnModels('powerupEnterAndActive')
        self.__startPowerupEffect('powerupEnterEffect')
        self.__startPowerupEffect('powerupActiveEffect')
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onStaticMarkerAdded(self.id, self.position, LEVIATHAN_HEALTH_POWERUP_STATIC_MARKER)
        return

    def __turnOnModels(self, modelKey):
        self.__clearActiveModels()
        modelDataList = self.__modelDataList
        modelList = modelDataList.get(modelKey, None)
        if modelList is not None:
            for modelData in modelList:
                model = modelData.get('model', None)
                if model is not None:
                    self.__activeModels.append(model)
                    model.position = self.position
                    BigWorld.addModel(model, BigWorld.player().spaceID)
                    modelAnim = modelData.get('actionName', None)
                    if modelAnim:
                        modelAction = model.action(modelAnim)
                        if modelAction is not None:
                            modelAction(0)

        return

    def __startPowerupEffect(self, effectName):
        if self.__activeModels:
            activeEffect = self.__effectsTimeLine[effectName]
            effectPlayer = EffectsListPlayer(activeEffect.effectsList, activeEffect.keyPoints)
            self.__effectsPlayerList.append(effectPlayer)
            effectPlayer.play(self.__activeModels[0])

    def __preparePowerupEffects(self):
        effects = self.__settings.healthPowerupEffects
        if effects is not None:
            for effect in effects.values():
                name = effect.name
                self.__effectsTimeLine[name] = effectsFromSection(effect)

        return
