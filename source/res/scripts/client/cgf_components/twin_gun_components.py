# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/twin_gun_components.py
import typing
import CGF
from constants import IS_CLIENT
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery
from Vehicular import GunEffectsController
from cgf_common.cgf_helpers import getParentComponentByGameObject
if IS_CLIENT:
    from TwinGunController import TwinGunController
else:

    class TwinGunController(object):
        pass


if typing.TYPE_CHECKING:
    from vehicles.mechanics.twin_guns.mechanic_interfaces import ITwinGunShootingEvents

@autoregister(presentInAllWorlds=True)
class TwinGunManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, GunEffectsController, tickGroup='PreSimulation')
    def onGunEffectsControllerAdded(self, gameObject, gunEffectsController):
        ctrl = getParentComponentByGameObject(gameObject, TwinGunController)
        if ctrl is not None and ctrl.shootingEvents is not None and ctrl.isPrefabRoot(gameObject):
            events = ctrl.shootingEvents
            events.onDiscreteShot += gunEffectsController.singleShot
            events.onDoubleShot += gunEffectsController.multiShot
        return

    @onRemovedQuery(CGF.GameObject, GunEffectsController)
    def onGunEffectsControllerRemoved(self, gameObject, gunEffectsController):
        ctrl = getParentComponentByGameObject(gameObject, TwinGunController)
        if ctrl is not None and ctrl.shootingEvents is not None:
            events = ctrl.shootingEvents
            events.onDoubleShot -= gunEffectsController.multiShot
            events.onDiscreteShot -= gunEffectsController.singleShot
        return
