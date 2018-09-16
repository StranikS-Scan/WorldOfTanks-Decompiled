# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/__init__.py
from abc import ABCMeta, abstractmethod
import BigWorld
from helpers.aop import Weaver
from tutorial.logger import LOG_ERROR
from tutorial.data.effects import EFFECT_TYPE_NAMES
from tutorial.data.conditions import CONDITION_TYPE

class TutorialProxyHolder(object):
    _tutorial = None

    @property
    def _gui(self):
        return self._tutorial.getGUIProxy()

    @property
    def _data(self):
        return self._tutorial.getChapterData()

    @property
    def _funcChapterCtx(self):
        return self._tutorial.getChapterFunctionalContext()

    @property
    def _cache(self):
        return self._tutorial.getCache()

    @property
    def _bonuses(self):
        return self._tutorial.getBonuses()

    @property
    def _sound(self):
        return self._tutorial.getSoundPlayer()

    @property
    def _descriptor(self):
        return self._tutorial.getDescriptor()

    @property
    def _funcScene(self):
        return self._tutorial.getFunctionalScene()

    @property
    def _ctrlFactory(self):
        return self._tutorial.getControlsFactory()


def setTutorialProxy(tutorial):
    TutorialProxyHolder._tutorial = tutorial


def clearTutorialProxy():
    TutorialProxyHolder._tutorial = None
    return


class ContentQuery(TutorialProxyHolder):

    def invoke(self, content, varID):
        pass

    def getVar(self, varID, default=None):
        return self._tutorial.getVars().get(varID, default=default)


class ControlsFactory(object):
    __meta__ = ABCMeta

    def __init__(self, funcEffects, contentQueries, customFuncConditions=None):
        self._funcEffects = funcEffects
        self._contentQueries = contentQueries
        self._customFuncConditions = customFuncConditions or {}

    @abstractmethod
    def createBonuses(self, completed):
        pass

    @abstractmethod
    def createSoundPlayer(self):
        pass

    @abstractmethod
    def createFuncScene(self, sceneModel):
        pass

    @abstractmethod
    def createFuncChapterCtx(self):
        pass

    def createContentQuery(self, name):
        result = ContentQuery()
        if name in self._contentQueries:
            result = self._contentQueries[name]()
        else:
            LOG_ERROR('Not found ContentQuery class by name:', name)
        return result

    def createFuncEffect(self, effect):
        if effect is None:
            return
        else:
            effectType = effect.getType()
            funcEffect = None
            if effectType in self._funcEffects:
                funcEffect = self._funcEffects[effectType](effect)
            else:
                LOG_ERROR('Not found FunctionalEffect class by effect type:', EFFECT_TYPE_NAMES.get(effectType, effectType))
            return funcEffect

    def createFuncEffects(self, effects):
        effectItems = [ self.createFuncEffect(e) for e in effects ]
        return [ item for item in effectItems if item is not None ]

    def createCustomFuncCondition(self, condition):
        if condition is None:
            return
        else:
            conditionType = condition.getType()
            funcConditionClass = self._customFuncConditions.get(conditionType)
            if funcConditionClass is not None:
                if callable(funcConditionClass):
                    return funcConditionClass()
                LOG_ERROR('FunctionalCondition class is not callable', conditionType, funcConditionClass)
            elif conditionType >= CONDITION_TYPE.FIRST_CUSTOM:
                LOG_ERROR('Not found FunctionalCondition by custom condition type', conditionType)
            return


def getServerSettings():
    try:
        serverSettings = BigWorld.player().serverSettings
    except AttributeError:
        serverSettings = {}

    return serverSettings


g_tutorialWeaver = Weaver()
