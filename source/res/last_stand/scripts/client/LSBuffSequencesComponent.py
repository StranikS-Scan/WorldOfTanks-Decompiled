# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/LSBuffSequencesComponent.py
from __future__ import absolute_import
import typing
import CGF
import GenericComponents
from dyn_components_groups import groupComponent
from last_stand.ls_buff_effect_component_common import LSBuffEffectComponentCommon
from xml_config_specs import StrParam, Vector3Param, ListParam, ObjParam, IntParam, BoolParam

@groupComponent(sequences=ListParam(valueParam=ObjParam(sequence=StrParam(), bindNode=StrParam(), offset=Vector3Param(), loopCount=IntParam(default=-1), autoStart=BoolParam(default=True), visibleTo=StrParam(default='all'), sniperModeVisibleTo=StrParam(default='all'), checkNodeExists=BoolParam(default=False))))
class LSBuffSequencesComponent(LSBuffEffectComponentCommon):

    def __init__(self):
        super(LSBuffSequencesComponent, self).__init__()
        self._gameObjects = []
        self._gameObjectsHideInSniperMode = []

    def onDestroy(self):
        super(LSBuffSequencesComponent, self).onDestroy()
        if self._hasAppearance:
            self.entity.events.onAppearanceReady -= self._onAppearanceReady
        self._gameObjects = []
        self._gameObjectsHideInSniperMode = []

    def _onAvatarReady(self):
        self._gameObjects = [None] * len(self._componentConfigs)
        if self._hasAppearance:
            self.entity.events.onAppearanceReady += self._onAppearanceReady
        super(LSBuffSequencesComponent, self)._onAvatarReady()
        return

    @property
    def _componentConfigs(self):
        return self.groupComponentConfig.sequences

    @property
    def _animators(self):
        for go in self._gameObjects:
            animator = go.findWrite(GenericComponents.AnimatorComponent) if go else None
            if animator:
                yield animator

        return

    @property
    def _hasAppearance(self):
        return hasattr(self.entity, 'appearance')

    def _activateEffects(self):
        self._gameObjectsHideInSniperMode = []
        queue = CGF.CommandQueue(self.spaceID)
        for i, gameObject in enumerate(self._gameObjects):
            config = self._componentConfigs[i]
            if not config.sequence or not self._isVisible(config.visibleTo) or not self._checkNode(config):
                if gameObject is not None:
                    if gameObject.valid:
                        queue.removeGameObject(gameObject)
                    self._gameObjects[i] = None
                continue
            if gameObject is None:
                gameObject = self._createGameObject(queue, config.bindNode, config.offset)
                queue.createComponent(gameObject, GenericComponents.AnimatorComponent, config.sequence, 0, 1, config.loopCount, config.autoStart, '')
                self._gameObjects[i] = gameObject
            if self._needsListenToSniperMode(config.sniperModeVisibleTo):
                self._gameObjectsHideInSniperMode.append(gameObject)
                if self._isInSniperMode:
                    queue.deactivateGameObject(gameObject)

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
        queue = CGF.CommandQueue(self.spaceID)
        for i, gameObject in enumerate(self._gameObjects):
            if gameObject is not None:
                if gameObject.valid:
                    queue.removeGameObject(gameObject)
                self._gameObjects[i] = None

        return

    def _createGameObject(self, queue, bindNode='', offset=(0, 0, 0)):
        if self._hasAppearance:
            parentGO = self.entity.appearance.gameObject
        else:
            parentGO = self.entity.entityGameObject
        gameObject = queue.createGameObject()
        queue.createComponent(gameObject, CGF.HierarchyComponent, parentGO)
        queue.createComponent(gameObject, CGF.TransformComponent, offset)
        queue.createComponent(gameObject, GenericComponents.NodeFollowerComponent, bindNode, parentGO.uuid)
        return gameObject

    def _onSniperModeChanged(self, isEnabled):
        for go in self._gameObjectsHideInSniperMode:
            if not go.valid:
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
