# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ActivationController.py
import BigWorld
import logging
import CGF
import GenericComponents
from Event import Event
from cgf_components_common.scenario.timed_activation import ActivationController as Controller, TimedActivation
from cgf_network import NetworkComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, autoregister
from cgf_components.zone_components import ZoneMarker, ZoneUINotification
_logger = logging.getLogger(__name__)

class ActivationController(BigWorld.DynamicScriptComponent, Controller):

    def __init__(self):
        super(ActivationController, self).__init__()
        self.objects = {}
        self.__onActivated = Event()
        self.__onDeactivated = Event()
        self.__activatedIndex = 0
        self.__deactivatedIndex = 0

    def set_activated(self, _):
        self.__onActivated(self)

    def set_deactivated(self, _):
        self.__onDeactivated(self)

    def getLastAddedActivated(self):
        current = len(self.activated)
        old = self.__activatedIndex
        self.__activatedIndex = current
        return self.getSubset(self.activated, old, current)

    def getLastAddedDeactivated(self):
        current = len(self.deactivated)
        old = self.__deactivatedIndex
        self.__deactivatedIndex = current
        return self.getSubset(self.deactivated, old, current)

    def subscribe(self, onActivated, onDeactivated):
        if onActivated:
            self.__onActivated += onActivated
        if onDeactivated:
            self.__onDeactivated += onDeactivated

    def unsubscribe(self, onActivated, onDeactivated):
        if onActivated:
            self.__onActivated -= onActivated
        if onDeactivated:
            self.__onDeactivated -= onDeactivated

    @staticmethod
    def getSubset(items, old, current):
        if current > old:
            diff = current - old
            return items[-diff:]
        return []


@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient)
class ActivationControllerManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, ActivationController)
    def onControllerAdded(self, go, controller):
        objects = Controller.getTimedActivators(go)
        for obj, component in objects:
            network = obj.findComponentByType(NetworkComponent)
            if network is None:
                _logger.error('Failed to find NetworkComponent for [%s]', obj.name)
                continue
            controller.objects[network.id] = (obj, component)

        self.__onActivated(controller)
        self.__onDeactivated(controller)
        controller.subscribe(self.__onActivated, self.__onDeactivated)
        return

    @onRemovedQuery(ActivationController)
    def onControllerRemoved(self, controller):
        controller.unsubscribe(self.__onActivated, self.__onDeactivated)

    @onAddedQuery(TimedActivation, ZoneUINotification)
    def onActivationAndZone(self, activator, zone):
        if not activator.ready:
            return
        zone.finishTime = activator.endTime
        zone.startTime = activator.startTime

    @onAddedQuery(TimedActivation, ZoneMarker)
    def onActivationMarker(self, activator, marker):
        if not activator.ready:
            return
        marker.startTime = activator.startTime
        marker.finishTime = activator.endTime

    @onAddedQuery(TimedActivation, GenericComponents.AnimatorComponent)
    def onActivationAndAnimation(self, activator, animation):
        if not activator.ready:
            return
        if activator.activateAnimations:
            rewind = max(0.0, BigWorld.serverTime() - activator.startTime)
            animation.start(rewind)

    @onAddedQuery(TimedActivation, GenericComponents.TrajectoryMoverComponent)
    def onActivationAndTrajectory(self, activator, trajectory):
        if not activator.ready:
            return
        if activator.activateMovers:
            rewind = max(0.0, BigWorld.serverTime() - activator.startTime)
            trajectory.currentCurveTime = rewind
            trajectory.resume()

    def __onActivated(self, controller):
        deactivated = controller.deactivated
        objects = controller.objects
        time = BigWorld.serverTime()
        subset = controller.getLastAddedActivated()
        for item in subset:
            networkID = item.id
            obj = objects.get(networkID, None)
            isExpired = item.end < time and item.end > item.start
            if obj and networkID not in deactivated and not isExpired:
                self.__activate(item, *obj)

        return

    def __onDeactivated(self, controller):
        objects = controller.objects
        subset = controller.getLastAddedDeactivated()
        for item in subset:
            obj = objects.pop(item, None)
            if obj:
                self.__deactivate(*obj)

        return

    @staticmethod
    def __activate(data, go, activator):
        if not go.isValid():
            _logger.error('Activation failed GO is invalid')
            return
        start = data.start
        end = data.end
        activator.setupTime(start, end)
        if activator.detach:
            goTransform = go.findComponentByType(GenericComponents.TransformComponent)
            if goTransform:
                goTransform.transform = goTransform.worldTransform
            go.removeComponentByType(GenericComponents.HierarchyComponent)
        if go.isActive():
            go.removeComponentByType(TimedActivation)
            go.addComponent(activator)
        else:
            go.activate()
        _logger.debug('Activation of [%s]', go.name)

    @staticmethod
    def __deactivate(go, activator):
        if not go.isValid():
            _logger.error('Deactivation failed GO is invalid')
            return
        _logger.debug('Deactivation of [%s]', go.name)
        if activator.autoRemove:
            CGF.removeGameObject(go)
        else:
            go.deactivate()
