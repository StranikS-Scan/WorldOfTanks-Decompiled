# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/auto_shoot_gun_components.py
import typing
import CGF
from constants import IS_CLIENT
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery
from Vehicular import GunEffectsController
from vehicle_systems.cgf_helpers import getVehicleEntityComponentByGameObject
if IS_CLIENT:
    from AutoShootGunController import AutoShootGunController
else:

    class AutoShootGunController(object):
        pass


if typing.TYPE_CHECKING:
    from vehicle_systems.auto_shoot_guns.system_interfaces import IAutoShootingEvents

@autoregister(presentInAllWorlds=True)
class AutoShootingGunManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, GunEffectsController, tickGroup='PreSimulation')
    def onGunEffectsControllerAdded(self, gameObject, gunEffectsController):
        ctrl = getVehicleEntityComponentByGameObject(gameObject, AutoShootGunController)
        if ctrl is not None and ctrl.shootingEvents is not None:
            events = ctrl.shootingEvents
            events.onShotRateUpdate.lateAdd(gunEffectsController.setShotsPerSec)
            events.onContinuousBurstActivation.lateAdd(gunEffectsController.startContinuousBurst)
            events.onContinuousBurstDeactivation += gunEffectsController.stopContinuousBurst
            events.onDiscreteShot += gunEffectsController.singleShot
        return

    @onRemovedQuery(CGF.GameObject, GunEffectsController)
    def onGunEffectsControllerRemoved(self, gameObject, gunEffectsController):
        ctrl = getVehicleEntityComponentByGameObject(gameObject, AutoShootGunController)
        if ctrl is not None and ctrl.shootingEvents is not None:
            events = ctrl.shootingEvents
            events.onDiscreteShot -= gunEffectsController.singleShot
            events.onContinuousBurstDeactivation -= gunEffectsController.stopContinuousBurst
            events.onContinuousBurstActivation -= gunEffectsController.startContinuousBurst
            events.onShotRateUpdate -= gunEffectsController.setShotsPerSec
        return
