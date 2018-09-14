# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/PixieNode.py
import BigWorld
import Math
import weakref
from helpers.PixieBG import PixieBG
from helpers.EffectsList import EffectsListPlayer

class BaseNodeEffect(object):

    @property
    def enabled(self):
        return self._enabled

    def __init__(self):
        self._enabled = False

    def attach(self):
        pass

    def detach(self):
        pass


class PixieEffect(BaseNodeEffect):
    __slots__ = ('__effectName', '__pixieRef', '__ttl', '__node', '__ttlCallback')

    def __init__(self, name, node, ttl):
        super(PixieEffect, self).__init__()
        self.__pixieRef = None
        self.__effectName = name
        self.__ttl = ttl
        self.__node = node
        self.__ttlCallback = None
        return

    def __del__(self):
        if self.__ttlCallback is not None:
            BigWorld.cancelCallback(self.__ttlCallback)
        self.__detach()
        self.__node = None
        return

    def attach(self):
        self._enabled = True
        if self.__ttl > 0.0:
            if self.__ttlCallback is not None:
                BigWorld.cancelCallback(self.__ttlCallback)
                self.__ttlCallback = BigWorld.callback(self.__ttl, self.__detachTTL)
            else:
                PixieCache.getPixie(self.__effectName, weakref.ref(self))
        elif self.__pixieRef is None:
            PixieCache.getPixie(self.__effectName, weakref.ref(self))
        else:
            self.__attach(self.__pixieRef)
        return

    def detach(self):
        self._enabled = False
        if self.__ttl == 0.0:
            self.__detach()

    def deactivate(self):
        self._enabled = False
        self.__detach()
        if self.__ttlCallback is not None:
            BigWorld.cancelCallback(self.__ttlCallback)
            self.__ttlCallback = None
        return

    def onLoadedCallback(self, pixie, clone):
        if not self._enabled:
            return False
        else:
            self.__detach()
            if self.__ttl > 0.0:
                if self.__ttlCallback is not None:
                    BigWorld.cancelCallback(self.__ttlCallback)
                    self.__ttlCallback = None
                if clone:
                    pixie = pixie.clone()
                self.__attachTTL(pixie)
                return True
            if clone:
                pixie = pixie.clone()
            self.__attach(pixie)
            return True

    def __attach(self, pixie):
        self.__node.node.attach(pixie)
        self.__pixieRef = pixie
        PixieBG.enablePixie(pixie, True)
        PixieCache.pixiesCount += 1

    def __attachTTL(self, pixie):
        self.__attach(pixie)
        self.__ttlCallback = BigWorld.callback(self.__ttl, self.__detachTTL)

    def __detach(self):
        if self.__pixieRef is not None:
            node = self.__node.node
            if not node.isDangling:
                node.detach(self.__pixieRef)
            self.__pixieRef = None
            PixieCache.pixiesCount -= 1
        return

    def __detachTTL(self):
        self.__detach()
        self.__ttlCallback = None
        return


class NodeEffectList(BaseNodeEffect):
    __slots__ = ('__node', '__player', '__model', '__timeLine')

    def __init__(self, name, model, node):
        super(NodeEffectList, self).__init__()
        self.__node = node
        self.__model = model
        from CustomEffect import getEffectList
        self.__timeLine = getEffectList(name)
        self.__player = None
        return

    def __del__(self):
        if self.__player is not None:
            self.__player.stop()
        self.__node = None
        self.__model = None
        self.__timeLine = None
        self.__player = None
        return

    def attach(self):
        if self.__player is None:
            self.__player = EffectsListPlayer(self.__timeLine.effectsList, self.__timeLine.keyPoints, node=self.__node.node)
        self.__player.play(self.__model)
        return

    def detach(self):
        if self.__player is not None:
            self.__player.stop()
        return

    def deactivate(self):
        if self.__player is not None:
            self.__player.stop()
        return


class EffectNode(object):
    __slots__ = ('__node', '__nodeDefaultLocalTranslation', '__drawOrder', '__waterY', '__effects')
    _PIXIE_NAME = 0
    _PIXIE_ENABLED = 1
    _PIXIE_REF = 2
    _PIXIE_TTL = 3
    EFFECT_ID = 0
    EFFECT_TTL = 1
    EFFECT_LIST = 2

    @property
    def node(self):
        return self.__node

    def __init__(self, model, node, waterY, drawOrder, effects):
        self.__node = node
        self.__nodeDefaultLocalTranslation = Math.Matrix(self.__node.local).translation
        self.__drawOrder = drawOrder
        self.__waterY = waterY
        self.__effects = dict()
        for effectName, effectDesc in effects.iteritems():
            if effectDesc[self.EFFECT_LIST]:
                self.__effects[effectDesc[self.EFFECT_ID]] = NodeEffectList(effectName, model, self)
            self.__effects[effectDesc[self.EFFECT_ID]] = PixieEffect(effectName, self, effectDesc[self.EFFECT_TTL])

    def deactivate(self):
        for effect in self.__effects.values():
            effect.deactivate()

    def destroy(self):
        self.deactivate()
        self.__effects = None
        self.__node = None
        return

    def correctWater(self, waterShiftRel):
        if self.__waterY:
            self.__node.local.translation = waterShiftRel + self.__nodeDefaultLocalTranslation

    def enable(self, effectID, enable):
        effect = self.__effects.get(effectID, None)
        if effect is None:
            return False
        else:
            if effect.enabled != enable:
                if enable:
                    effect.attach()
                else:
                    effect.detach()
            return


class PixieCache(object):
    pixieCache = dict()
    refCount = 0
    pixiesCount = 0

    @staticmethod
    def getPixie(name, callbackData):
        pixieInfo = PixieCache.pixieCache.get(name, [None, set()])
        cbksSize = len(pixieInfo[1])
        pixieInfo[1].add(callbackData)
        if cbksSize == 0:
            pixieInfo[0] = PixieBG(name, PixieCache.onPixieLoaded)
            PixieCache.pixieCache[name] = pixieInfo
        return

    @staticmethod
    def incref():
        PixieCache.refCount += 1

    @staticmethod
    def decref():
        PixieCache.refCount -= 1
        if PixieCache.refCount == 0:
            PixieCache.pixieCache.clear()

    @staticmethod
    def onPixieLoaded(pixieBG):
        pixieInfo = PixieCache.pixieCache.get(pixieBG.name, None)
        if pixieInfo is not None:
            callbacks = pixieInfo[1]
            origPixieAccepted = False
            for callback in callbacks:
                effect = callback()
                if effect is not None:
                    if effect.onLoadedCallback(pixieBG.pixie, origPixieAccepted):
                        origPixieAccepted = True

            if not origPixieAccepted:
                pixieBG.pixie.removeAllSystems()
            PixieCache.pixieCache[pixieBG.name] = [None, set()]
        else:
            pixieBG.pixie.removeAllSystems()
        return
