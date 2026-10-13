# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWBuffSequencesComponent.py
from __future__ import absolute_import
import typing
import CGF
import GenericComponents
import Math
from dyn_components_groups import groupComponent
from halloween.hw_buff_effect_component_common import HWBuffEffectComponentCommon
from xml_config_specs import StrParam, Vector3Param, ListParam, ObjParam, IntParam, BoolParam
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import dependency
from halloween.gui.halloween_gui_constants import BATTLE_CTRL_ID

@groupComponent(sequences=ListParam(valueParam=ObjParam(sequence=StrParam(), bindNode=StrParam(), offset=Vector3Param(), scale=Vector3Param(default=(1.0, 1.0, 1.0)), rotationYPR=Vector3Param(), loopCount=IntParam(default=-1), autoStart=BoolParam(default=True), visibleTo=StrParam(default='all'), sniperModeVisibleTo=StrParam(default='all'), checkNodeExists=BoolParam(default=False))))
class HWBuffSequencesComponent(HWBuffEffectComponentCommon):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(HWBuffSequencesComponent, self).__init__()
        count = len(self.groupComponentConfig.sequences)
        self._gameObjects = [None] * count
        self._gameObjectsHideInSniperMode = []
        return

    def onDestroy(self):
        super(HWBuffSequencesComponent, self).onDestroy()
        if self._hasAppearance:
            self.entity.events.onAppearanceReady -= self._onAppearanceReady
        self._hwBattleGuiCtrl.onVehicleModelHidden -= self._onVehicleModelHidden
        self._gameObjects = []
        self._gameObjectsHideInSniperMode = []

    def _onAvatarReady(self):
        super(HWBuffSequencesComponent, self)._onAvatarReady()
        if self._hasAppearance:
            self.entity.events.onAppearanceReady += self._onAppearanceReady
        self._hwBattleGuiCtrl.onVehicleModelHidden += self._onVehicleModelHidden

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

    @property
    def _hwBattleGuiCtrl(self):
        return self.guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)

    def _activateEffects(self):
        self._gameObjectsHideInSniperMode = []
        queue = CGF.CommandQueue(self.spaceID)
        for i, gameObject in enumerate(self._gameObjects):
            config = self.groupComponentConfig.sequences[i]
            if not config.sequence or not self._isVisible(config.visibleTo) or not self._checkNode(config):
                if gameObject is not None:
                    queue.removeGameObject(gameObject)
                    self._gameObjects[i] = None
                continue
            if gameObject is None:
                transform = Math.createSRTMatrix(config.scale, config.rotationYPR, config.offset)
                gameObject = self._createGameObject(queue, config.bindNode, transform)
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
                queue.removeGameObject(gameObject)
                self._gameObjects[i] = None

        return

    def _createGameObject(self, queue, bindNode='', transform=Math.Matrix()):
        if self._hasAppearance:
            parentGO = self.entity.appearance.gameObject
        else:
            parentGO = self.entity.entityGameObject
        gameObject = queue.createGameObject()
        queue.createComponent(gameObject, CGF.HierarchyComponent, parentGO)
        queue.createComponent(gameObject, CGF.TransformComponent, transform)
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

    def _onVehicleModelHidden(self, vehicleID, isHidden):
        if self.entity.id == vehicleID and isHidden:
            self._stopEffects()
