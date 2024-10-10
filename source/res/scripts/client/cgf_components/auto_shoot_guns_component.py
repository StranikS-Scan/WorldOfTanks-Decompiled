# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/auto_shoot_guns_component.py
import logging
import CGF
import GenericComponents
import Vehicular
from constants import IS_CLIENT
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery, onProcessQuery
if IS_CLIENT:
    from AutoShootGunController import AutoShootGunController
else:

    class AutoShootGunController(object):
        pass


_logger = logging.getLogger(__name__)

@registerComponent
class AutoShootingGunEffect(object):
    editorTitle = 'Auto Shooting Gun Effect'
    category = 'Auto Shoot Guns'
    shot = ComponentProperty(type=CGFMetaTypes.LINK, editorName='One Shot', value=CGF.GameObject)


@registerComponent
class AutoShootingGunBurstPixie(object):
    editorTitle = 'Auto Shooting Gun Burst Pixie'
    category = 'Auto Shoot Guns'
    rateFactor = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Rate factor', value=1.0)


@autoregister(presentInAllWorlds=True)
class AutoShootingGunManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, AutoShootingGunBurstPixie, GenericComponents.ParticleComponent)
    def onBurstParticleAdded(self, go, particleConfig, particleComponent):
        hierarchy = CGF.HierarchyManager(go.spaceID)
        root = hierarchy.getTopMostParent(go)
        controller = root.findComponentByType(AutoShootGunController)
        if controller is not None:
            controller.shootingAnimator.addBurstParticleComponent(particleConfig, particleComponent)
        return

    @onAddedQuery(CGF.GameObject, AutoShootingGunEffect)
    def onGunEffectAdded(self, go, gunEffect):
        hierarchy = CGF.HierarchyManager(go.spaceID)
        root = hierarchy.getTopMostParent(go)
        controller = root.findComponentByType(AutoShootGunController)
        if controller is not None:
            controller.shootingAnimator.addShotGameObject(gunEffect.shot)
        return

    @onAddedQuery(CGF.GameObject, Vehicular.GunRecoilAnimator)
    def onGunRecoilAnimatorAdded(self, go, gunRecoilAnimator):
        hierarchy = CGF.HierarchyManager(go.spaceID)
        root = hierarchy.getTopMostParent(go)
        controller = root.findComponentByType(AutoShootGunController)
        if controller is not None:
            controller.shootingAnimator.addRecoilAnimator(gunRecoilAnimator)
        return

    @onRemovedQuery(CGF.GameObject, AutoShootingGunBurstPixie, GenericComponents.ParticleComponent)
    def onBurstParticleRemoved(self, go, particleConfig, particleComponent):
        hierarchy = CGF.HierarchyManager(go.spaceID)
        root = hierarchy.getTopMostParent(go)
        controller = root.findComponentByType(AutoShootGunController)
        if controller is not None:
            controller.shootingAnimator.removeBurstParticleComponent(particleConfig, particleComponent)
        return

    @onRemovedQuery(CGF.GameObject, AutoShootingGunEffect)
    def onGunEffectRemoved(self, go, gunEffect):
        hierarchy = CGF.HierarchyManager(go.spaceID)
        root = hierarchy.getTopMostParent(go)
        controller = root.findComponentByType(AutoShootGunController)
        if controller is not None:
            controller.shootingAnimator.removeShotGameObject(gunEffect.shot)
        return

    @onRemovedQuery(CGF.GameObject, Vehicular.GunRecoilAnimator)
    def onGunRecoilAnimatorRemoved(self, go, gunRecoilAnimator):
        hierarchy = CGF.HierarchyManager(go.spaceID)
        root = hierarchy.getTopMostParent(go)
        controller = root.findComponentByType(AutoShootGunController)
        if controller is not None:
            controller.shootingAnimator.removeRecoilAnimator(gunRecoilAnimator)
        return

    @onProcessQuery(AutoShootGunController)
    def onTick(self, controller):
        if controller is not None and controller.shootingAnimator is not None:
            controller.shootingAnimator.receiveShotsImpulse(self.clock.gameDelta)
        return
