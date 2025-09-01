# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/LSBuffSequencesComponent.py
import CGF
import GenericComponents
from dyn_components_groups import groupComponent
from last_stand.ls_buff_effect_component_common import LSBuffEffectComponentCommon
from xml_config_specs import StrParam, Vector3Param, ListParam, ObjParam, IntParam, BoolParam

@groupComponent(sequences=ListParam(valueParam=ObjParam(sequence=StrParam(), bindNode=StrParam(), offset=Vector3Param(), loopCount=IntParam(default=-1), autoStart=BoolParam(default=True), visibleTo=StrParam(default='all'), sniperModeVisibleTo=StrParam(default='all'), checkNodeExists=BoolParam(default=False))))
class LSBuffSequencesComponent(LSBuffEffectComponentCommon):

    def __init__(self):
        super(LSBuffSequencesComponent, self).__init__()
        count = len(self.groupComponentConfig.sequences)
        self._gameObjects = [None] * count
        self._gameObjectsHideInSniperMode = []
        return

    def onDestroy(self):
        super(LSBuffSequencesComponent, self).onDestroy()
        if self._hasAppearance:
            self.entity.onAppearanceReady -= self._onAppearanceReady
        self._gameObjects = []
        self._gameObjectsHideInSniperMode = []

    def _onAvatarReady(self):
        super(LSBuffSequencesComponent, self)._onAvatarReady()
        if self._hasAppearance:
            self.entity.onAppearanceReady += self._onAppearanceReady

    @property
    def _componentConfigs(self):
        return self.groupComponentConfig.sequences

    @property
    def _animators(self):
        for go in self._gameObjects:
            animator = go.findComponentByType(GenericComponents.AnimatorComponent) if go and go.isValid() else None
            if animator:
                yield animator

        return

    @property
    def _hasAppearance(self):
        return hasattr(self.entity, 'appearance')

    def _activateEffects(self):
        self._gameObjectsHideInSniperMode = []
        for i, gameObject in enumerate(self._gameObjects):
            config = self.groupComponentConfig.sequences[i]
            if not config.sequence or not self._isVisible(config.visibleTo) or not self._checkNode(config):
                if gameObject is not None:
                    self.__destroyObject(gameObject)
                    self._gameObjects[i] = None
                continue
            if gameObject is None:
                gameObject = self._createGameObject(config.bindNode, config.offset)
                gameObject.createComponent(GenericComponents.AnimatorComponent, config.sequence, 0, 1, config.loopCount, config.autoStart, '')
                self._gameObjects[i] = gameObject
            if self._needsListenToSniperMode(config.sniperModeVisibleTo):
                self._gameObjectsHideInSniperMode.append(gameObject)
                if self._isInSniperMode:
                    gameObject.deactivate()

        return

    def _startEffects(self, startTime=0.0):
        for animator in self._animators:
            animator.start(startTime)

    def _stopEffects(self):
        for animator in self._animators:
            animator.stop()

    def _triggerEffects(self, triggerName):
        for animator in self._animators:
            animator.setTrigger(triggerName)

    def _deactivateEffects(self):
        for i, gameObject in enumerate(self._gameObjects):
            if gameObject is not None:
                self.__destroyObject(gameObject)
                self._gameObjects[i] = None

        return

    def _createGameObject(self, bindNode='', offset=(0, 0, 0)):
        if self._hasAppearance:
            parentGO = self.entity.appearance.gameObject
        else:
            parentGO = self.entity.entityGameObject
        gameObject = CGF.GameObject(self.spaceID)
        gameObject.createComponent(GenericComponents.HierarchyComponent, parentGO)
        gameObject.createComponent(GenericComponents.TransformComponent, offset)
        gameObject.createComponent(GenericComponents.NodeFollower, bindNode, parentGO)
        return gameObject

    def _onSniperModeChanged(self, isEnabled):
        for go in self._gameObjectsHideInSniperMode:
            if not go.isValid():
                continue
            if isEnabled:
                go.deactivate()
            go.activate()

    def _onAppearanceReady(self):
        if self._isActive:
            self._deactivateEffects()
        self._updateEffectsStatus()

    def _checkNode(self, config):
        if not config.checkNodeExists:
            return True
        else:
            return False if not self._hasAppearance or not getattr(self.entity, 'model', None) else self.entity.model.node(config.bindNode)

    def __destroyObject(self, gameObject):
        if gameObject.isValid():
            gameObject.destroy()
