# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/buffs/components.py
import logging
from functools import partial
import AnimationSequence
import BigWorld
import Math
from helpers.buffs import ClientBuffComponent
from helpers.EffectsList import EffectsListPlayer
from effect_controller import EffectController
from gui.battle_control import avatar_getter
import SoundGroups
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicle_systems.components.terrain_circle_component import TerrainCircleComponent
from gui.Scaleform.daapi.view.battle.event.game_event_getter import GameEventGetterMixin
from vehicle_systems.stricted_loading import makeCallbackWeak
from helpers.CallbackDelayer import CallbackDelayer
from helpers import newFakeModel, dependency
from AvatarInputHandler import aih_global_binding
from aih_constants import CTRL_MODE_NAME
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.utils.graphics import isRendererPipelineDeferred
from BattleFeedbackCommon import BATTLE_EVENT_TYPE as _BET
from gui.battle_control.controllers import feedback_events
_logger = logging.getLogger(__name__)

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


class SoundBuffComponent(ClientBuffComponent):

    def _apply(self):
        if self._config.wwsoundOnStart:
            SoundGroups.g_instance.playSound2D(self._config.wwsoundOnStart)
        if self._config.notificationOnStart:
            soundNotifications = avatar_getter.getSoundNotifications()
            if soundNotifications is not None:
                soundNotifications.play(self._config.notificationOnStart)
        return

    def _unapply(self):
        if self._config.wwsoundOnStop:
            SoundGroups.g_instance.playSound2D(self._config.wwsoundOnStop)
        if self._config.notificationOnStop:
            soundNotifications = avatar_getter.getSoundNotifications()
            if soundNotifications is not None:
                soundNotifications.play(self._config.notificationOnStop)
        return


class ModelBuffComponent(ClientBuffComponent):

    def __init__(self, name, config, owner):
        super(ModelBuffComponent, self).__init__(name, config, owner)
        self._active = False
        self._model = None
        self._servo = None
        return

    def _apply(self):
        self._active = True
        self._loadModel()
        if self._model:
            self._attachModel()

    def _unapply(self):
        self._active = False
        self._detachModel()
        self._model = None
        return

    def _onModelLoaded(self, resourceRefs):
        if self._config.model not in resourceRefs.failedIDs:
            self._model = resourceRefs[self._config.model]
            if self._active:
                self._attachModel()

    def _loadModel(self):
        BigWorld.loadResourceListBG((self._config.model,), self._onModelLoaded)

    def _attachModel(self):
        model = self._model
        BigWorld.player().addModel(model)
        attachNode = self._owner.model.node(self._config.node)
        scaleMatrix = Math.Matrix()
        scaleMatrix.setScale(self._config.scale)
        translationMatrix = Math.Matrix()
        translationMatrix.setTranslate(self._config.offset)
        yawOnly = Math.WGYawOnlyTransform()
        yawOnly.source = attachNode
        posOnly = Math.WGTranslationOnlyMP()
        posOnly.source = attachNode
        noPithRollMatrix = Math.WGCombinedMP()
        noPithRollMatrix.rotationSrc = yawOnly
        noPithRollMatrix.translationSrc = posOnly
        localTransform = Math.MatrixProduct()
        localTransform.a = scaleMatrix
        localTransform.b = translationMatrix
        refinedMatrixProvider = Math.MatrixProduct()
        refinedMatrixProvider.a = localTransform
        refinedMatrixProvider.b = noPithRollMatrix
        self._servo = BigWorld.Servo(refinedMatrixProvider)
        model.addMotor(self._servo)

    def _detachModel(self):
        if self._servo is not None and self._model is not None:
            self._model.delMotor(self._servo)
            self._servo = None
            if self._model.attached:
                BigWorld.player().delModel(self._model)
            self._model = None
        return


class IconBuffComponent(ClientBuffComponent):

    def _apply(self):
        g_eventBus.handleEvent(events.BuffUiEvent(events.BuffUiEvent.ON_APPLY, ctx={'id': self._config.iconName,
         'iconName': self._config.iconName,
         'tooltipTextTag': self._config.tooltipTextTag}), scope=EVENT_BUS_SCOPE.BATTLE)

    def _unapply(self):
        g_eventBus.handleEvent(events.BuffUiEvent(events.BuffUiEvent.ON_UNAPPLY, ctx={'id': self._config.iconName}), scope=EVENT_BUS_SCOPE.BATTLE)


class DecalBuffComponent(ClientBuffComponent):
    pass


class TerrainCircleBuffComponent(ClientBuffComponent):

    def __init__(self, name, config, owner):
        super(TerrainCircleBuffComponent, self).__init__(name, config, owner)
        self._terrainCircle = None
        return

    def _apply(self):
        self._createCircles()

    def _unapply(self):
        self._destroyCircles()

    def _createCircles(self):
        if self._terrainCircle is not None:
            return
        else:
            self._terrainCircle = TerrainCircleComponent()
            self._terrainCircle.configure(self._config.radius, self._config.settings)
            if not self._terrainCircle.isAttached():
                self._terrainCircle.attach(self._owner.id)
            self._terrainCircle.setVisible()
            return

    def _destroyCircles(self):
        if self._terrainCircle and self._terrainCircle.isAttached():
            self._terrainCircle.detach()
            self._terrainCircle.destroy()
            self._terrainCircle = None
        return


class AuraVictimVisualComponent(ClientBuffComponent, GameEventGetterMixin, CallbackDelayer):

    def __init__(self, name, config, owner):
        super(AuraVictimVisualComponent, self).__init__(name, config, owner)
        GameEventGetterMixin.__init__(self)
        CallbackDelayer.__init__(self)
        self._shieldIdle = EffectController('shieldIdle')
        self._shieldStart = EffectController('shieldStart')
        self._shieldEnd = EffectController('shieldEnd')

    def _apply(self):
        self._owner.onCanBeDamagedChanged += self._onCanBeDamagedChanged
        self._onCanBeDamagedChanged(self._owner.canBeDamaged)

    def _unapply(self):
        self.souls.onSoulsChanged -= self._onSoulsChanged
        self._owner.onCanBeDamagedChanged -= self._onCanBeDamagedChanged
        self._displayFireOnVehicle(False)
        self._displayShieldOnVehicle(False)

    def _displayFireOnVehicle(self, isStarted):
        vehicle = self._owner
        vehicleTypeDescriptor = vehicle.typeDescriptor
        fireExtra = vehicleTypeDescriptor.extrasDict['fire']
        if isStarted and fireExtra and not fireExtra.isRunningFor(vehicle):
            fireExtra.startFor(vehicle)
        elif not isStarted and fireExtra and fireExtra.isRunningFor(vehicle):
            fireExtra.stopFor(vehicle)

    def _displayShieldOnVehicle(self, isStarted):
        if not self._owner.isAlive() or self._owner.compoundInvalidated:
            self._shieldIdle.reset()
            self._shieldStart.reset()
            self._shieldEnd.reset()
            self.clearCallbacks()
        elif isStarted and not self._shieldIdle.isSequencePlaying:
            self._shieldStart.playSequence(self._owner)
            self.delayCallback(0.475, partial(self._shieldIdle.playSequence, self._owner))
        elif not isStarted and self._shieldIdle.isSequencePlaying:
            self._shieldEnd.playSequence(self._owner)
            self._shieldIdle.stopSequnce()

    def _onSoulsChanged(self, _=None):
        currentSoulsOnVehicle = self.souls.getSouls(self._owner.id)
        if currentSoulsOnVehicle > 0:
            self._displayShieldOnVehicle(True)
            self._displayFireOnVehicle(False)
        else:
            self._displayFireOnVehicle(True)
            self._displayShieldOnVehicle(False)

    def _onCanBeDamagedChanged(self, canBeDamaged):
        vehicle = self._owner
        extra = vehicle.typeDescriptor.extrasDict['fire']
        if extra.isRunningFor(vehicle):
            extra.canBeDamagedChanged(vehicle, canBeDamaged)
        if canBeDamaged:
            self.souls.onSoulsChanged += self._onSoulsChanged
            self._onSoulsChanged()
        else:
            self.souls.onSoulsChanged -= self._onSoulsChanged
            self._displayShieldOnVehicle(False)
            self._displayFireOnVehicle(False)


class LaserBeamBuffComponent(ClientBuffComponent):
    _MAX_DISTANCE = 500.0

    def __init__(self, name, config, owner):
        super(LaserBeamBuffComponent, self).__init__(name, config, owner)
        self._active = False
        self._beamModelPath = self._config.beamModel if isRendererPipelineDeferred() else self._config.beamModelFwd
        self._beamModel = None
        self._beamMP = None
        self._bindNode = None
        self._cbId = None
        return

    def _apply(self):
        self._active = True
        resources = (self._beamModelPath,)
        BigWorld.loadResourceListBG(resources, makeCallbackWeak(self._onLoaded))

    def _unapply(self):
        self._detachModel()
        self._active = False

    def _onLoaded(self, resourceRefs):
        if self._beamModelPath not in resourceRefs.failedIDs:
            self._beamModel = resourceRefs[self._beamModelPath]
            if self._active and self._beamModel is not None:
                self._attachModel()
        return

    def _attachModel(self):
        self._bindNode = self._owner.model.node(self._config.bindNode)
        if self._bindNode is not None:
            scaleMatrix = Math.Matrix()
            scaleMatrix.setIdentity()
            self._beamMP = Math.MatrixProduct()
            self._beamMP.a = scaleMatrix
            self._beamMP.b = self._bindNode
            self._beamModel.addMotor(BigWorld.Servo(self._beamMP))
            BigWorld.player().addModel(self._beamModel)
            self._cbId = BigWorld.callback(0.1, self._updateLaserPoint)
        return

    def _detachModel(self):
        if self._cbId is not None:
            BigWorld.cancelCallback(self._cbId)
            self._cbId = None
        if self._beamModel is not None and self._beamModel.attached:
            BigWorld.player().delModel(self._beamModel)
            self._beamModel = None
        self._bindNode = None
        return

    def _updateLaserPoint(self):
        gunMatr = Math.Matrix(self._bindNode)
        gunPos = gunMatr.translation
        gunDir = gunMatr.applyVector((0, 0, 1))
        endPos = gunPos + gunDir * self._MAX_DISTANCE
        collidePos = BigWorld.wg_collideDynamicStatic(self._owner.spaceID, gunPos, endPos, 128, self._owner.id, -1)
        if collidePos:
            endPos = collidePos[0]
        self._beamMP.a.setScale((1, 1, gunPos.distTo(endPos) / self._config.beamLength))
        self._cbId = BigWorld.callback(0.1, self._updateLaserPoint)


class SequenceBuffComponent(ClientBuffComponent):

    def __init__(self, name, config, owner):
        super(SequenceBuffComponent, self).__init__(name, config, owner)
        self._active = False
        self._animator = None
        self._bindNode = None
        self._spaceID = None
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

    def _applyVisualEffects(self, checkForSniperMode=False):
        if checkForSniperMode and self._getAvatarCtrlMode() == CTRL_MODE_NAME.SNIPER:
            return
        self._spaceID = BigWorld.player().spaceID
        loader = AnimationSequence.Loader(self._config.sequence, self._spaceID)
        BigWorld.loadResourceListBG((loader,), makeCallbackWeak(self._onLoaded))

    def _unapplyVisualEffects(self):
        self._detachModel()

    def _onAvatarCtrlModeChanged(self, modeName):
        if modeName == CTRL_MODE_NAME.SNIPER:
            self._unapplyVisualEffects()
        else:
            self._applyVisualEffects()

    def _onLoaded(self, resourceRefs):
        if self._config.sequence not in resourceRefs.failedIDs:
            self._animator = resourceRefs[self._config.sequence]
        if self._active:
            self._attachModel()

    def _attachModel(self):
        self._bindNode = self._owner.model.node(self._config.bindNode)
        if self._bindNode is not None:
            model = newFakeModel()
            self._bindNode.attach(model)
            if self._animator is not None:
                self._animator.bindTo(AnimationSequence.ModelWrapperContainer(model, self._spaceID))
                self._animator.start()
        return

    def _detachModel(self):
        if self._animator is not None and self._active:
            self._animator.stop()
            self._animator = None
        self._bindNode = None
        self._spaceID = None
        return

    def _getAvatarCtrlMode(self):
        avatar = BigWorld.player()
        return CTRL_MODE_NAME.DEFAULT if not avatar else avatar.inputHandler.ctrlModeName

    def _isVisibleInSniperMode(self):
        if self._hideInSniperModeFor == self.VisibilityModes.ALL:
            return False
        if self._hideInSniperModeFor == self.VisibilityModes.SELF and self._shouldShowForSelf():
            return False
        return False if self._hideInSniperModeFor == self.VisibilityModes.OTHERS and not self._shouldShowForSelf() else True


class InvulnerabilityBuffComponent(ClientBuffComponent):

    def _apply(self):
        self._owner.canBeDamaged = False
        self._onCanBeDamagedChanged(self._owner.canBeDamaged)

    def _unapply(self):
        self._owner.canBeDamaged = True
        self._onCanBeDamagedChanged(self._owner.canBeDamaged)

    def _onCanBeDamagedChanged(self, canBeDamaged):
        vehicle = self._owner
        extra = vehicle.typeDescriptor.extrasDict['fire']
        if extra.isRunningFor(vehicle):
            extra.canBeDamagedChanged(vehicle, canBeDamaged)


class ExhaustBuffComponent(ClientBuffComponent):

    class NitroTypes(object):
        NONE = 0
        BATTLE_ROYALE = 1
        GAS = 2
        DIESEL = 3

    def _apply(self):
        self._setType(self._config.nitro)

    def _unapply(self):
        self._setType(self.NitroTypes.NONE)

    def _setType(self, nitro):
        appearance = self._owner.appearance
        if appearance is not None:
            effectMgr = appearance.customEffectManager
            if effectMgr is not None:
                effectMgr.variables['Nitro'] = nitro
        return


class RibbonBuffComponent(ClientBuffComponent):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, name, config, owner):
        super(RibbonBuffComponent, self).__init__(name, config, owner)
        self.__feedbackProvider = self.sessionProvider.shared.feedback

    def _apply(self):
        data = {'eventType': _BET.BUFF_APPLIED,
         'targetID': 0,
         'details': self._config.buffName,
         'count': 1}
        data = (feedback_events.PlayerFeedbackEvent.fromDict(data),)
        self.__feedbackProvider.onBuffApplied(data)
