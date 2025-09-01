# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/helpers/prefab_helpers.py
from abc import ABCMeta, abstractmethod
import CGF
import GenericComponents

class PrefabHandlerComponent(object):
    __meta__ = ABCMeta

    def __init__(self):
        super(PrefabHandlerComponent, self).__init__()
        self._gameObject = None
        self._parentEntity = None
        self.__isAppearanceReady = False
        return

    @abstractmethod
    def createGameObject(self):
        pass

    def loadGameObject(self, entity, prefabPath, gameObject, matrix):
        self._parentEntity = entity
        CGF.loadGameObjectIntoHierarchy(prefabPath, gameObject, matrix, self._onGameObjectLoaded)

    def _onGameObjectLoaded(self, gameObject):
        self._gameObject = gameObject
        if hasattr(self._parentEntity, 'appearance') and self._parentEntity.appearance is not None:
            appearance = self._parentEntity.appearance
            gameObject.createComponent(GenericComponents.RedirectorComponent, appearance.gameObject)
            self.attachDynamicModelComponent()
        else:
            gameObject.createComponent(GenericComponents.RedirectorComponent, self._parentEntity.entityGameObject)
        return

    def setAppearanceReady(self):
        self.__isAppearanceReady = True
        self.attachDynamicModelComponent()

    def attachDynamicModelComponent(self):
        if self._gameObject is not None and self.__isAppearanceReady:
            appearance = self._parentEntity.appearance
            self._gameObject.removeComponentByType(GenericComponents.DynamicModelComponent)
            self._gameObject.createComponent(GenericComponents.DynamicModelComponent, appearance.compoundModel)
        return

    def destroyGameObject(self):
        if not self._gameObject:
            return
        else:
            CGF.removeGameObject(self._gameObject)
            self._gameObject = None
            return
