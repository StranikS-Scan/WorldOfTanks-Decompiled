# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/buffs/components.py
import logging
import AnimationSequence
import BigWorld
import Math
from helpers.buffs import ClientBuffComponent
from helpers.EffectsList import EffectsListPlayer
import SoundGroups
from gui.battle_control import avatar_getter
from vehicle_systems.components.terrain_circle_component import TerrainCircleComponent
from vehicle_systems.stricted_loading import makeCallbackWeak
from helpers import newFakeModel
from AvatarInputHandler import aih_global_binding
from aih_constants import CTRL_MODE_NAME
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
_logger = logging.getLogger(__name__)

class EffectBuffComponent(ClientBuffComponent):

    def __init__(self, name, config, owner):
        super(EffectBuffComponent, self).__init__(name, config, owner)
        self._playerEffect = None
        return

    def _initEffect(self):
        effect = self._config.effectData
        return EffectsListPlayer(effect.effectsList, effect.keyPoints, debugParent=self)

    def _apply(self):
        if not self._playerEffect:
            self._playerEffect = self._initEffect()
            self._playerEffect.play(self._owner.appearance.compoundModel)

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
                avatar_getter.getSoundNotifications().play(self._config.notificationOnStart)
        return

    def _unapply(self):
        if self._config.wwsoundOnStop:
            SoundGroups.g_instance.playSound2D(self._config.wwsoundOnStop)
        if self._config.notificationOnStop:
            soundNotifications = avatar_getter.getSoundNotifications()
            if soundNotifications is not None:
                avatar_getter.getSoundNotifications().play(self._config.notificationOnStop)
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

    def _unapply(self):
        self._owner.canBeDamaged = True


class ExhaustBuffComponent(ClientBuffComponent):

    class NitroTypes(object):
        NONE = 0
        DIESEL = 1
        GAS = 2

    def _apply(self):
        self._setType(self._config.nitro)

    def _unapply(self):
        self._setType(self.NitroTypes.NONE)

    def _setType(self, nitro):
        appearance = self._owner.appearance
        if appearance is not None:
            effectMgr = appearance.customEffectManager
            if effectMgr is not None:
                effectMgr.variables['hw19Nitro'] = nitro
        return
