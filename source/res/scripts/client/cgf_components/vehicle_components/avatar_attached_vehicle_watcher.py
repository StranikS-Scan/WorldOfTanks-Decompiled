# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/vehicle_components/avatar_attached_vehicle_watcher.py
from __future__ import absolute_import
import enum
import typing
import logging
from functools import partial
import BigWorld
import CGF
from constants import IS_EDITOR, IS_CGF_DUMP
from cgf_script.registration import ComponentProperty, registerComponent
from Event import EventsSubscriber
if typing.TYPE_CHECKING:
    from Avatar import Avatar
    from Event import SafeEvent
    from Vehicle import Vehicle
    VehAccessorType = typing.Union[Vehicle, CGF.ComponentAccessor[Vehicle]]
elif IS_EDITOR or IS_CGF_DUMP:

    class Vehicle(object):
        pass


else:
    from Vehicle import Vehicle
_logger = logging.getLogger(__name__)

@enum.unique
class ActiveForTypes(enum.IntEnum):
    SELF = 0
    OTHERS = 1
    TEAMMATES = 2
    ENEMIES = 3


@registerComponent
class AvatarAttachedVehicleWatcherComponent(object):
    category = 'Vehicle'
    editorTitle = 'Avatar Attached Vehicle Watcher'
    domain = CGF.Domain.ClientEditor
    activeFor = ComponentProperty(type=CGF.PropertyType.Int, editorName='Active for', annotations={'comboBox': {n.name:str(n.value) for n in list(ActiveForTypes)}}, value=ActiveForTypes.SELF.value)

    def __init__(self):
        self._subscriber = None
        _logger.debug('Created %s', self)
        return

    def subscribe(self, event, callback):
        if self._subscriber is None:
            self._subscriber = EventsSubscriber()
        self._subscriber.subscribeToEvent(event, callback)
        _logger.debug('%s subscribed to event', self)
        return

    def clear(self):
        if self._subscriber is not None:
            self._subscriber.unsubscribeFromAllEvents()
            self._subscriber = None
        _logger.debug('Cleared %s', self)
        return

    def destroy(self):
        self.clear()
        _logger.debug('Destroyed %s', self)

    def __repr__(self):
        return '<AvatarAttachedVehicleWatcherComp: {}>'.format(self.activeFor)


class AvatarAttachedVehicleWatcherSystem(CGF.System):
    WatcherActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(AvatarAttachedVehicleWatcherComponent))
    WatcherDeactivated = CGF.DeactivateReaction(CGF.ReactRw(AvatarAttachedVehicleWatcherComponent))
    WatcherRemoved = CGF.RemoveReaction(CGF.ReactRw(AvatarAttachedVehicleWatcherComponent))
    VehicleAccess = CGF.AccessReaction(CGF.GameObject, CGF.Rw(Vehicle))
    Reactions = CGF.Reactions(WatcherRemoved, WatcherDeactivated, WatcherActivated, VehicleAccess)

    def update(self):
        removed, deactivated, activated, vehAccess = self.reactions
        for comp in deactivated:
            comp.clear()

        for comp in removed:
            comp.clear()

        for go, comp in activated:
            self._onActivated(go, comp, vehAccess)

    def _onActivated(self, go, component, vehAccess):
        avatar = BigWorld.player()
        if avatar is None or avatar.isDestroyed:
            _logger.error('<AvatarAttachedVehicleWatcherSys|%s> Initialize. No avatar.', go.id)
            return
        else:
            result = CGF.findParentWithReaction(go, vehAccess)
            if result is None:
                _logger.debug('<AvatarAttachedVehicleWatcherSys|%s> Initialize. No vehicle access.', go.id)
                return
            vehGO, vehicle = result
            if not vehicle or vehicle.isDestroyed:
                _logger.debug('<AvatarAttachedVehicleWatcherSys|%s> Initialize. No vehicle.', go.id)
                return
            component.subscribe(avatar.onAvatarVehicleChanged, partial(self._updateHierarchy, go, vehGO, component.activeFor))
            self._updateHierarchy(go, vehGO, component.activeFor)
            _logger.debug('<AvatarAttachedVehicleWatcherSys|%s> Watcher initialized for (%s).', go.id, (avatar.id, vehicle.id, component))
            return

    def _updateHierarchy(self, go, vehGO, activeFor):
        if not go.valid:
            _logger.debug('<AvatarAttachedVehicleWatcherSys> Update. GO is not valid.')
            return
        else:
            attachedVehicle = None
            avatar = BigWorld.player()
            if avatar is not None and not avatar.isDestroyed:
                attachedVehicle = avatar.getVehicleAttached()
            if attachedVehicle is None:
                _logger.debug('<AvatarAttachedVehicleWatcherSys|%s> Update. Unattached avatar vehicle.', go.id)
                self._deactivate(go)
                return
            vehAccess = self.reaction(self.VehicleAccess)
            _, currentVehicle = vehAccess.find(vehGO)
            if not currentVehicle or currentVehicle.isDestroyed:
                _logger.error('<AvatarAttachedVehicleWatcherSys|%s> Update. No current vehicle.', go.id)
                self._deactivate(go)
                return
            if self._shouldBeActive(attachedVehicle, currentVehicle, activeFor):
                _logger.debug('<AvatarAttachedVehicleWatcherSys|%s> Update. Activating.', go.id)
                self._activate(go)
            else:
                _logger.debug('<AvatarAttachedVehicleWatcherSys|%s> Update. Deactivating.', go.id)
                self._deactivate(go)
            return

    def _deactivate(self, go):
        for child in self.hierarchy.getDirectChildren(go):
            if child.valid:
                child.deactivate()
                _logger.debug('<AvatarAttachedVehicleWatcherSys|%s> Deactivating.', child.id)

    def _activate(self, go):
        for child in self.hierarchy.getDirectChildrenIncludingInactive(go):
            if child.valid and not child.isActive:
                child.activate()
                _logger.debug('<AvatarAttachedVehicleWatcherSys|%s> Activating.', child.id)

    @staticmethod
    def _shouldBeActive(attachedVehicle, currentVehicle, activeFor):
        attachedToSelf = attachedVehicle.id == currentVehicle.id
        attachedToTeammate = attachedVehicle.publicInfo.team == currentVehicle.publicInfo.team
        if activeFor == ActiveForTypes.SELF:
            if attachedToSelf:
                _logger.debug('<AvatarAttachedVehicleWatcherSys> Attached to self.')
                return True
        elif activeFor == ActiveForTypes.OTHERS:
            if not attachedToSelf:
                _logger.debug('<AvatarAttachedVehicleWatcherSys> Attached to others.')
                return True
        elif activeFor == ActiveForTypes.TEAMMATES:
            if attachedToTeammate and not attachedToSelf:
                _logger.debug('<AvatarAttachedVehicleWatcherSys> Attached to teammate.')
                return True
        elif activeFor == ActiveForTypes.ENEMIES:
            if not attachedToTeammate:
                _logger.debug('<AvatarAttachedVehicleWatcherSys> Attached to enemy.')
                return True
        return False
