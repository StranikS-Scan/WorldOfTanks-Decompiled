# Embedded file name: scripts/client/helpers/bound_effects.py
import helpers
from debug_utils import *
from functools import partial
from helpers.EffectsList import EffectsListPlayer

class StaticSceneBoundEffects(object):

    def __init__(self):
        self._models = {}
        self.__incrementalEffectID = -1

    def destroy(self):
        self._matProv = None
        for id, elem in self._models.items():
            elem['effectsPlayer'].stop()
            model = elem['model']
            if model is not None:
                BigWorld.delModel(model)
            del self._models[id]

        return

    def addNew(self, position, effectsList, keyPoints, callbackOnStop, **args):
        model = helpers.newFakeModel()
        model.position = position
        BigWorld.addModel(model)
        dir = args.get('dir', None)
        if dir is not None:
            model.rotate(dir.yaw, (0.0, 1.0, 0.0))
        self.__incrementalEffectID += 1
        effectID = self.__incrementalEffectID
        desc = dict()
        desc['model'] = model
        desc['effectsPlayer'] = EffectsListPlayer(effectsList, keyPoints, **args)
        desc['effectsPlayer'].play(model, None, partial(self.__callbackBeforeDestroy, effectID, callbackOnStop))
        self._models[effectID] = desc
        return effectID

    def stop(self, effectID):
        if self._models.has_key(effectID):
            desc = self._models[effectID]
            desc['effectsPlayer'].stop()
            BigWorld.delModel(desc['model'])
            del self._models[effectID]

    def __callbackBeforeDestroy(self, effectID, callbackOnStop):
        if callbackOnStop is not None:
            callbackOnStop()
        self.stop(effectID)
        return


class ModelBoundEffects(object):

    def __init__(self, model, nodeName = ''):
        self.__model = model
        self.__nodeName = nodeName
        self._effects = list()

    def destroy(self):
        for elem in self._effects[:]:
            elem.stop()
            self._effects.remove(elem)

        self.__model = None
        return

    def addNew(self, matProv, effectsList, keyPoints, **args):
        desc = EffectsListPlayer(effectsList, keyPoints, position=(self.__nodeName, matProv), **args)
        desc.play(self.__model, None, partial(self._effects.remove, desc))
        self._effects.append(desc)
        return

    def reattachTo(self, model):
        self.__model = model
        for elem in self._effects:
            elem.reattachTo(model)
