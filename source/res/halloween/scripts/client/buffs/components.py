# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/buffs/components.py
import logging
import AnimationSequence
import BigWorld
import Math
import configs
from vehicle_systems.stricted_loading import makeCallbackWeak
from helpers import newFakeModel
from helpers.EffectsList import EffectsListPlayer
from AvatarInputHandler import aih_global_binding
from aih_constants import CTRL_MODE_NAME
from buffs import ClientBuffComponent, clientBuffComponent
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from halloween.gui.shared import events as hw_events
_logger = logging.getLogger(__name__)

@clientBuffComponent('exhaust')
class ExhaustBuffComponent(ClientBuffComponent):

    def _apply(self):
        self._setType(self._config.nitro)

    def _unapply(self):
        self._setType(configs.ExhaustBuffComponentConfig.NitroTypes.NONE)

    def _setType(self, nitro):
        appearance = self._owner.appearance
        if appearance is not None:
            effectMgr = appearance.customEffectManager
            if effectMgr is not None:
                effectMgr.variables['Nitro'] = nitro
        return


@clientBuffComponent('sequence')
class SequenceBuffComponent(ClientBuffComponent):

    def __init__(self, name, config, owner):
        super(SequenceBuffComponent, self).__init__(name, config, owner)
        self._active = False
        self._animator = None
        self._bindNode = None
        self._spaceID = None
        self._model = None
        self._loadingTaskID = None
        self._hideInSniperModeFor = config.hideInSniperModeFor
        return

    def _apply(self):
        self._active = True
        hideInSniperMode = not self._isVisibleInSniperMode()
        if hideInSniperMode:
            aih_global_binding.subscribe(aih_global_binding.BINDING_ID.CTRL_MODE_NAME, self._onAvatarCtrlModeChanged)
        self._applyVisualEffects(hideInSniperMode)

    def _unapply(self):
        self._unapplyVisualEffects()
        if not self._isVisibleInSniperMode():
            aih_global_binding.unsubscribe(aih_global_binding.BINDING_ID.CTRL_MODE_NAME, self._onAvatarCtrlModeChanged)
        self._active = False

    def _cancelLoadingTask(self):
        if self._loadingTaskID is None:
            return
        else:
            BigWorld.stopLoadResourceListBGTask(self._loadingTaskID)
            self._loadingTaskID = None
            return

    def _applyVisualEffects(self, checkForSniperMode=False):
        self._cancelLoadingTask()
        if checkForSniperMode and self._getAvatarCtrlMode() in (CTRL_MODE_NAME.SNIPER, CTRL_MODE_NAME.DUAL_GUN):
            return
        self._spaceID = BigWorld.player().spaceID
        loader = AnimationSequence.Loader(self._config.sequence, self._spaceID)
        self._loadingTaskID = BigWorld.loadResourceListBG((loader,), makeCallbackWeak(self._onLoaded))

    def _unapplyVisualEffects(self):
        self._cancelLoadingTask()
        self._detachModel()

    def _onAvatarCtrlModeChanged(self, modeName):
        if modeName in (CTRL_MODE_NAME.SNIPER, CTRL_MODE_NAME.DUAL_GUN):
            self._unapplyVisualEffects()
        else:
            self._applyVisualEffects()

    def _onLoaded(self, resourceRefs):
        self._loadingTaskID = None
        if self._config.sequence not in resourceRefs.failedIDs:
            self._animator = resourceRefs[self._config.sequence]
            self._animator.loopCount = self._config.loopCount
        if self._active and self._owner.model:
            self._attachModel()
        return

    def _attachModel(self):
        self._model = newFakeModel()
        if self._config.bindNode == 'ground':
            self._model.position = Math.Vector3(self._owner.position)
            BigWorld.player().addModel(self._model)
            if self._animator is not None:
                self._animator.bindTo(AnimationSequence.ModelWrapperContainer(self._model, self._spaceID))
                self._animator.start()
        elif self._config.bindNode == 'detached':
            BigWorld.player().addModel(self._model)
            rotationMatrix = Math.WGTranslationOnlyMP()
            rotationMatrix.source = self._owner.matrix
            self._model.addMotor(BigWorld.Servo(rotationMatrix))
            if self._animator is not None:
                self._animator.bindTo(AnimationSequence.ModelWrapperContainer(self._model, self._spaceID))
                self._animator.start()
        else:
            self._bindNode = self._owner.model.node(self._config.bindNode)
            if self._bindNode is not None:
                self._bindNode.attach(self._model)
                if self._animator is not None:
                    self._animator.bindTo(AnimationSequence.ModelWrapperContainer(self._model, self._spaceID))
                    self._animator.start()
        return

    def _detachModel(self):
        if self._animator is not None and self._active:
            self._animator.stop()
            self._animator = None
        self._model = None
        self._bindNode = None
        self._spaceID = None
        return

    def _getAvatarCtrlMode(self):
        avatar = BigWorld.player()
        return CTRL_MODE_NAME.DEFAULT if not avatar else avatar.inputHandler.ctrlModeName

    def _isVisibleInSniperMode(self):
        if self._hideInSniperModeFor == self.VisibilityModes.ALL:
            return False
        if self._hideInSniperModeFor == self.VisibilityModes.SELF and self._isVisibleToPlayer():
            return False
        return False if self._hideInSniperModeFor == self.VisibilityModes.OTHERS and not self._isVisibleToPlayer() else True


@clientBuffComponent('effect')
class EffectBuffComponent(ClientBuffComponent):
    MAX_APPLY_ATTEMPTS = 10
    APPLY_ATTEMPT_DELAY = 0.1

    def __init__(self, name, config, owner):
        super(EffectBuffComponent, self).__init__(name, config, owner)
        self._playerEffect = None
        self._applyAttempts = 0
        return

    def _initEffect(self):
        effect = self._config.effectData
        return EffectsListPlayer(effect.effectsList, effect.keyPoints, debugParent=self)

    def _apply(self):
        if self._playerEffect:
            return
        self._playerEffect = self._initEffect()
        if self._owner.appearance:
            self._playerEffect.play(self._owner.appearance.compoundModel)
        elif self._applyAttempts >= EffectBuffComponent.MAX_APPLY_ATTEMPTS:
            self._applyAttempts = 0
            _logger.error('Could not apply buff %s to vehicle: %s. Missing Appearance object', self._playerEffect, self._owner)
        else:
            BigWorld.callback(EffectBuffComponent.APPLY_ATTEMPT_DELAY, self._apply)
            self._applyAttempts += 1
            _logger.debug('Setting up callback for applying buff %s to vehicle: %s. Missing Appearance object', self._playerEffect, self._owner)

    def _unapply(self):
        if self._playerEffect:
            self._playerEffect.stop()
            self._playerEffect = None
        return


@clientBuffComponent('ttcModifier')
class TTCModifierBuffComponent(ClientBuffComponent):
    pass


@clientBuffComponent('icon')
class IconBuffComponent(ClientBuffComponent):

    def _apply(self):
        g_eventBus.handleEvent(hw_events.BuffGUIEvent(hw_events.BuffGUIEvent.ON_APPLY, ctx={'id': self._config.iconName,
         'iconName': self._config.iconName,
         'tooltip': self._config.tooltip,
         'vehicleID': self._owner.id}), scope=EVENT_BUS_SCOPE.BATTLE)

    def _unapply(self):
        g_eventBus.handleEvent(hw_events.BuffGUIEvent(hw_events.BuffGUIEvent.ON_UNAPPLY, ctx={'id': self._config.iconName,
         'vehicleID': self._owner.id}), scope=EVENT_BUS_SCOPE.BATTLE)
