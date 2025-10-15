# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal_client_cgf/guided_missile/managers.py
import BigWorld
import CGF
import Keys
import GenericComponents
from portal.gui.portal_event_helpers import useFadingBinocular, PortalBinocularsMode
from portal.sounds.sound_constants import PortalAbilitySound
from portal.sounds.sound_helpers import play2DSound
from portal_client_cgf.guided_missile.components import ActiveGuidedMissileComponent
from portal_common_cgf.guided_missile import components
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, onProcessQuery
from constants import IS_EDITOR, SERVER_TICK_LENGTH
from gui import InputHandler
from aih_constants import CTRL_MODE_NAME
from portal_common_cgf.portal_helpers import registerPortalManager
if IS_EDITOR:
    from portal_common_cgf.guided_missile.components import GuidedMissileReplicableComponent
else:
    from GuidedMissileReplicableComponent import GuidedMissileReplicableComponent

@registerPortalManager(CGF.DomainOption.DomainClient)
class DisplayPortalReplicableValuesManager(CGF.ComponentManager):

    def __init__(self):
        super(DisplayPortalReplicableValuesManager, self).__init__()
        self.activeReplicableComponents = None
        return

    def destroy(self):
        binoculars = BigWorld.binoculars()
        if binoculars:
            binoculars.setIsPTUR(False)

    @onProcessQuery(GuidedMissileReplicableComponent, tickGroup='Simulation', period=SERVER_TICK_LENGTH)
    def onTick(self, r):
        player = BigWorld.player()
        if player is not None and player.id == r.replicableAvatarId:
            r.cell.setDirection(player.id, player.inputHandler.ctrl.camera.camera.direction)
        return

    @onProcessQuery(GenericComponents.TransformComponent, GuidedMissileReplicableComponent, tickGroup='Simulation')
    def onProcessCameraPosition(self, transform, r):
        player = BigWorld.player()
        if player is not None and player.id == r.replicableAvatarId and player.inputHandler.ctrl is not None:
            player.inputHandler.ctrl.camera.position = transform.position
        return

    @onProcessQuery(GenericComponents.TransformComponent, GuidedMissileReplicableComponent, ActiveGuidedMissileComponent, tickGroup='Simulation')
    def onClientCollision(self, transform, r, _):
        player = BigWorld.player()
        if player is None or player.id != r.replicableAvatarId or player.inputHandler.ctrl is None:
            return
        elif r.isDetonateProjectile:
            return
        else:
            startPos = transform.position
            endPos = transform.position + player.inputHandler.ctrl.camera.camera.direction * 1.5
            resultStatic = BigWorld.collideSphere(self.spaceID, startPos, endPos, 2.0)
            if resultStatic is not None:
                self.__doAction('detonateProjectile', r)
            return

    @onAddedQuery(GuidedMissileReplicableComponent, CGF.GameObject)
    def onAdded(self, r, go):
        r.onReplicated += self.__onReplicationDone
        r.onDetonate += self.__onDetonate
        self.__updateActiveReplicableComponentsQuery()

    @onRemovedQuery(CGF.GameObject, GuidedMissileReplicableComponent, GenericComponents.TransformComponent, components.PortalGuidedMissileComponent)
    def onRemoved(self, go, r, transform, gm):
        r.onDetonate -= self.__onDetonate
        r.onReplicated -= self.__onReplicationDone
        player = BigWorld.player()
        if player is not None and player.id == r.replicableAvatarId and not r.isDeploying:
            if player.vehicle and player.vehicle.health > 0:
                self.__updateControlMode(CTRL_MODE_NAME.ARCADE, r.replicableAvatarId)
            else:
                self.__updateControlMode(CTRL_MODE_NAME.POSTMORTEM, r.replicableAvatarId)
        self.__updateActiveReplicableComponentsQuery()
        CGF.loadGameObject(gm.explosionPrefabPath, self.spaceID, transform.worldPosition)
        return

    def __onReplicationDone(self, r, new):
        go = self.__getActiveGOByComponent(r)
        player = BigWorld.player()
        if player is not None and player.id == r.replicableAvatarId:
            go.createComponent(ActiveGuidedMissileComponent)
            self.__updateControlMode(CTRL_MODE_NAME.ATGM, r.replicableAvatarId)
            InputHandler.g_instance.onKeyDown += self.__handleStartBoostKeyEvent
            InputHandler.g_instance.onKeyUp += self.__handleEndBoostKeyEvent
            InputHandler.g_instance.onKeyDown += self.__handleDetonateKeyEvent
            play2DSound(PortalAbilitySound.GUIDED_MISSILE_FLY)
            player.autoAim(None, False)
        if not r.isDeploying:
            gm = go.findComponentByType(components.PortalGuidedMissileComponent)
            go.createComponent(GenericComponents.ParticleComponent, gm.trailEffectPath, True, 1.0)
        return

    def __onDetonate(self, r):
        player = BigWorld.player()
        if player is not None and player.id == r.replicableAvatarId and r.isDetonateProjectile:
            self.__detonateProjectile(r)
            InputHandler.g_instance.onKeyDown -= self.__handleStartBoostKeyEvent
            InputHandler.g_instance.onKeyUp -= self.__handleEndBoostKeyEvent
            InputHandler.g_instance.onKeyDown -= self.__handleDetonateKeyEvent
        return

    def __handleStartBoostKeyEvent(self, event):
        self.__processInputEvent(event=event, triggerCondition=event.isKeyDown(), key=Keys.KEY_LEFTMOUSE, actionName='startBoostEffect')

    def __handleEndBoostKeyEvent(self, event):
        self.__processInputEvent(event=event, triggerCondition=event.isKeyUp(), key=Keys.KEY_LEFTMOUSE, actionName='endBoostEffect')

    def __handleDetonateKeyEvent(self, event):
        self.__processInputEvent(event=event, triggerCondition=event.isKeyDown(), key=Keys.KEY_SPACE, actionName='detonateProjectile')

    def __processInputEvent(self, event, triggerCondition, key, actionName):
        if not (triggerCondition and event.key == key):
            return
        else:
            player = BigWorld.player()
            if player is None:
                return
            if not self.activeReplicableComponents:
                return
            for _, replicable in self.activeReplicableComponents:
                if replicable.replicableAvatarId == player.id:
                    self.__doAction(actionName, replicable)

            return

    def __doAction(self, actionName, replicable):
        getattr(replicable.cell, actionName)(replicable.replicableAvatarId)
        selfCallbackName = '_{}__{}'.format(self.__class__.__name__, actionName)
        callback = getattr(self, selfCallbackName, None)
        if callback:
            callback(replicable)
        return

    def __startBoostEffect(self, replicable):
        binoculars = BigWorld.binoculars()
        if binoculars:
            binoculars.setIsNeuronsBoost(True)

    def __endBoostEffect(self, replicable):
        binoculars = BigWorld.binoculars()
        if binoculars:
            binoculars.setIsNeuronsBoost(False)

    def __detonateProjectile(self, replicable):
        go = self.__getActiveGOByComponent(replicable)
        activeGM = go.findComponentByType(ActiveGuidedMissileComponent)
        if activeGM:
            go.removeComponent(activeGM)

    def __updateActiveReplicableComponentsQuery(self):
        p = BigWorld.player()
        if p is not None:
            self.activeReplicableComponents = CGF.Query(p.spaceID, (CGF.GameObject, GuidedMissileReplicableComponent))
        return

    @useFadingBinocular(PortalBinocularsMode.GUIDED_MISSILE)
    def __updateControlMode(self, modeName, avatarId):
        player = BigWorld.player()
        if player is not None and player.id == avatarId:
            player.inputHandler.onControlModeChanged(modeName)
            self.__hideVisualsForOwner()
        return

    def __hideVisualsForOwner(self):
        player = BigWorld.player()
        for go, replicable in self.activeReplicableComponents:
            if replicable.replicableAvatarId == player.id:
                particle = go.findComponentByType(GenericComponents.ParticleComponent)
                if particle is not None:
                    go.removeComponent(particle)
                model = go.findComponentByType(GenericComponents.DynamicModelComponent)
                if model is not None:
                    go.removeComponent(model)
                animator = go.findComponentByType(GenericComponents.AnimatorComponent)
                if animator is not None:
                    go.removeComponent(animator)

        return

    def __getActiveGOByComponent(self, component):
        return component.entity.entityGameObject
