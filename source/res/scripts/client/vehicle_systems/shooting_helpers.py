# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/shooting_helpers.py
import typing
from cgf_events import gun_events
from constants import IS_CLIENT, DEFAULT_GUN_INDEX
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicle_systems.instant_status_helpers import invokeShotsDoneStatus
if typing.TYPE_CHECKING:
    from items.components.gun_installation_components import GunInstallationSlot
    from Vehicle import Vehicle

def processVehicleSingleShot(vehicle, gunInstallationSlot, gunIndex=DEFAULT_GUN_INDEX):
    gun_events.postVehicularSingleShotEvent(vehicle.spaceID, vehicle.id, gunInstallationSlot.partSlotName, gunIndex)
    processVehicleDiscreteShots(vehicle, gunInstallationSlot)


def processVehicleMultiShot(vehicle, gunInstallationSlot, gunIndexes):
    gun_events.postVehicularMultiShotEvent(vehicle.spaceID, vehicle.id, gunInstallationSlot.partSlotName, gunIndexes)
    processVehicleDiscreteShots(vehicle, gunInstallationSlot)


def processVehicleDiscreteShots(vehicle, gunInstallationSlot):
    if gunInstallationSlot.isMainInstallation():
        invokeShotsDoneStatus(vehicle)
    if IS_CLIENT:
        vehicle.events.onDiscreteShotDone(gunInstallationSlot)
        notifyVehicleDiscreteShots(vehicle, gunInstallationSlot)


@dependency.replace_none_kwargs(sessionProvider=IBattleSessionProvider)
def notifyVehicleDiscreteShots(vehicle, gunInstallationSlot, sessionProvider=None):
    feedback = sessionProvider.shared.feedback
    if feedback is not None:
        feedback.onDiscreteShotsDone(vehicle.id, gunInstallationSlot)
    return
