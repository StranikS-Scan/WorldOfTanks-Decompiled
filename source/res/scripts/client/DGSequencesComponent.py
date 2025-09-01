# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DGSequencesComponent.py
import enum
import typing
import CGF
import BigWorld
import GenericComponents
from aih_constants import CTRL_MODE_NAME
from dyn_components_groups import groupComponent
from script_component.DynamicScriptComponent import DynamicScriptComponent
from xml_config_specs import StrParam, Vector3Param, ListParam, ObjParam, IntParam, BoolParam

@enum.unique
class SequenceVisibilityMode(enum.IntEnum):
    NONE = 0
    SELF = 1
    OTHERS = 2
    ALL = 3


class DGEffectComponentCommon(DynamicScriptComponent):
    _SNIPER_MODES = (CTRL_MODE_NAME.SNIPER, CTRL_MODE_NAME.DUAL_GUN)

    def __init__(self):
        super(DGEffectComponentCommon, self).__init__()
        self._isReady = False
        self._isSniperModeAvailable = self.__checkSniperModeAvailable()

    def onDestroy(self):
        if self._isSniperModeAvailable:
            BigWorld.player().inputHandler.onCameraChanged -= self.__onCameraChanged
        if self._isReady:
            self._isReady = False
            BigWorld.player().onAvatarVehicleChanged -= self._onAvatarVehicleChanged
            self._deactivateEffects()
        super(DGEffectComponentCommon, self).onDestroy()

    @property
    def _isActive(self):
        return True

    @property
    def _isInSniperMode(self):
        return BigWorld.player().inputHandler.ctrlModeName in self._SNIPER_MODES

    @property
    def _componentConfigs(self):
        raise NotImplementedError()

    def _onAvatarReady(self):
        super(DGEffectComponentCommon, self)._onAvatarReady()
        self._isReady = True
        if self._isSniperModeAvailable:
            BigWorld.player().inputHandler.onCameraChanged += self.__onCameraChanged
        BigWorld.player().onAvatarVehicleChanged += self._onAvatarVehicleChanged
        self._updateEffectsStatus()

    def _activateEffects(self):
        raise NotImplementedError()

    def _deactivateEffects(self):
        pass

    def _updateEffectsStatus(self):
        if not self._isReady:
            return
        if self._isActive:
            self._activateEffects()
        else:
            self._deactivateEffects()

    def _isVehicleObservedByAvatar(self):
        avatar = BigWorld.player()
        if not avatar:
            return False
        vehicle = avatar.getVehicleAttached()
        return vehicle == self.entity

    def _isVisible(self, param):
        visibleTo = getattr(SequenceVisibilityMode, param.upper())
        if visibleTo == SequenceVisibilityMode.ALL:
            return True
        if visibleTo == SequenceVisibilityMode.SELF and self._isVehicleObservedByAvatar():
            return True
        return True if visibleTo == SequenceVisibilityMode.OTHERS and not self._isVehicleObservedByAvatar() else False

    def _needsListenToSniperMode(self, visibleTo):
        return self._isSniperModeAvailable and not self._isVisible(visibleTo)

    def _onAvatarVehicleChanged(self):
        self._updateEffectsStatus()

    def _onSniperModeChanged(self, isEnabled):
        raise NotImplementedError()

    def __checkSniperModeAvailable(self):
        for config in self._componentConfigs:
            visibleTo = getattr(SequenceVisibilityMode, config.sniperModeVisibleTo.upper())
            if visibleTo != SequenceVisibilityMode.ALL:
                return True

        return False

    def __onCameraChanged(self, mode, currentVehicleId=None):
        self._onSniperModeChanged(mode in self._SNIPER_MODES)


@groupComponent(sequences=ListParam(valueParam=ObjParam(sequence=StrParam(), bindNode=StrParam(), offset=Vector3Param(), loopCount=IntParam(default=-1), autoStart=BoolParam(default=True), visibleTo=StrParam(default='all'), sniperModeVisibleTo=StrParam(default='all'), checkNodeExists=BoolParam(default=False))))
class DGSequencesComponent(DGEffectComponentCommon):

    def __init__(self):
        super(DGSequencesComponent, self).__init__()
        count = len(self.groupComponentConfig.sequences)
        self._gameObjects = [None] * count
        self._gameObjectsHideInSniperMode = []
        return

    def onDestroy(self):
        super(DGSequencesComponent, self).onDestroy()
        if self._hasAppearance:
            self.entity.onAppearanceReady -= self._onAppearanceReady
        self._gameObjects = []
        self._gameObjectsHideInSniperMode = []

    def _onAvatarReady(self):
        super(DGSequencesComponent, self)._onAvatarReady()
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
