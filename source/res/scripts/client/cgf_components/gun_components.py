# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/gun_components.py
import typing
import CGF
from constants import IS_CLIENT
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery
from Vehicular import GunEffectsController
from cgf_common.cgf_helpers import getParentComponentByGameObject
if IS_CLIENT:
    from SecondaryGunComponent import SecondaryGunComponent
else:

    class SecondaryGunComponent(object):
        pass


if typing.TYPE_CHECKING:
    from vehicles.parts.guns import IGunShootingEvents

@autoregister(presentInAllWorlds=True)
class GunComponentsManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, GunEffectsController, tickGroup='PreSimulation')
    def onGunEffectsControllerAdded(self, gameObject, gunEffectsController):
        ctrl = getParentComponentByGameObject(gameObject, SecondaryGunComponent)
        if ctrl is not None and ctrl.shootingEvents is not None and ctrl.isPrefabRoot(gameObject):
            events = ctrl.shootingEvents
            events.onDiscreteShot += gunEffectsController.singleShot
            events.onMultiShot += gunEffectsController.multiShot
        return

    @onRemovedQuery(CGF.GameObject, GunEffectsController)
    def onGunEffectsControllerRemoved(self, gameObject, gunEffectsController):
        ctrl = getParentComponentByGameObject(gameObject, SecondaryGunComponent)
        if ctrl is not None and ctrl.shootingEvents is not None:
            events = ctrl.shootingEvents
            events.onDiscreteShot -= gunEffectsController.singleShot
            events.onMultiShot -= gunEffectsController.multiShot
        return
