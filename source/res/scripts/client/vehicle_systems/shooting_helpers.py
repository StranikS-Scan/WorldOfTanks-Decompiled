# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/shooting_helpers.py
import typing
from constants import IS_CLIENT
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicle_systems.instant_status_helpers import invokeShotsDoneStatus
if typing.TYPE_CHECKING:
    import CGF
    from items.components.gun_installation_components import GunInstallationSlot
    from Vehicle import Vehicle

def processVehicleDiscreteShots(vehicle, gunInstallationSlot, _=None):
    if gunInstallationSlot.isMainInstallation():
        invokeShotsDoneStatus(vehicle)
    if IS_CLIENT:
        vehicle.onDiscreteShotDone(gunInstallationSlot)
        notifyVehicleDiscreteShots(vehicle, gunInstallationSlot)


@dependency.replace_none_kwargs(sessionProvider=IBattleSessionProvider)
def notifyVehicleDiscreteShots(vehicle, gunInstallationSlot, sessionProvider=None):
    feedback = sessionProvider.shared.feedback
    if feedback is not None:
        feedback.onDiscreteShotsDone(vehicle.id, gunInstallationSlot)
    return
