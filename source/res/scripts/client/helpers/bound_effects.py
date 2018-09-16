# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/bound_effects.py
from functools import partial
import BigWorld
import helpers
from helpers.EffectsList import EffectsListPlayer

class StaticSceneBoundEffects(object):

    def __init__(self):
        self._models = {}
        self.__incrementalEffectID = -1

    def destroy(self):
        self._matProv = None
        for mID, elem in self._models.items():
            elem['effectsPlayer'].stop()
            model = elem['model']
            if model is not None:
                BigWorld.player().delModel(model)
            del self._models[mID]

        return

    def addNew(self, position, effectsList, keyPoints, callbackOnStop, **args):
        model = helpers.newFakeModel()
        model.position = position
        BigWorld.player().addModel(model)
        direction = args.get('dir', None)
        if direction is not None:
            model.rotate(direction.yaw, (0.0, 1.0, 0.0))
        self.__incrementalEffectID += 1
        effectID = self.__incrementalEffectID
        desc = dict()
        desc['model'] = model
        desc['effectsPlayer'] = EffectsListPlayer(effectsList, keyPoints, **args)
        desc['effectsPlayer'].play(model, None, partial(self.__callbackBeforeDestroy, effectID, callbackOnStop), args.get('waitForKeyOff', False))
        self._models[effectID] = desc
        return effectID

    def stop(self, effectID):
        if self._models.has_key(effectID):
            desc = self._models[effectID]
            desc['effectsPlayer'].stop()
            BigWorld.player().delModel(desc['model'])
            del self._models[effectID]

    def __callbackBeforeDestroy(self, effectID, callbackOnStop):
        if callbackOnStop is not None:
            callbackOnStop()
        self.stop(effectID)
        return


class ModelBoundEffects(object):

    def __init__(self, model):
        self.__model = model
        self._effects = list()

    def destroy(self):
        self.stop()
        self.__model = None
        return

    def stop(self):
        for elem in self._effects[:]:
            elem.stop()
            self._effects.remove(elem)

    def addNew(self, matProv, effectsList, keyPoints, waitForKeyOff=False, **args):
        return self.addNewToNode('', matProv, effectsList, keyPoints, waitForKeyOff, **args)

    def addNewToNode(self, node, matProv, effectsList, keyPoints, waitForKeyOff=False, **args):
        if not node and matProv is None:
            position = None
        else:
            position = (node, matProv)
        desc = EffectsListPlayer(effectsList, keyPoints, position=position, **args)
        desc.play(self.__model, None, partial(self._effects.remove, desc), waitForKeyOff)
        self._effects.append(desc)
        return desc

    def reattachTo(self, model):
        self.__model = model
        for elem in self._effects:
            elem.reattachTo(model)
