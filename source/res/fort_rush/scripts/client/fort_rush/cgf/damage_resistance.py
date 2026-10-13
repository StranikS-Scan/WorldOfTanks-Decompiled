# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/cgf/damage_resistance.py
from __future__ import absolute_import
import BigWorld
import CGF
from VehicleExpirableComponent import VehicleExpirableComponent
from constants import IS_EDITOR
from debug_utils import LOG_WARNING
from fort_rush_common.cgf import getTopMostGO
from FortRushDamageResistanceComponent import FortRushDamageResistanceComponent
from helpers import dependency
if IS_EDITOR:

    class Vehicle(object):

        def __init__(self):
            self.id = None
            return


    class battle_constants(object):

        class DestroyTimerViewState(object):

            def __init__(self, *args, **kwargs):
                pass

        class TIMER_VIEW_STATE(object):
            CRITICAL = 'critical'
            WARNING = 'warning'


    class fort_rush_battle_constants(object):

        class FR_VEHICLE_VIEW_STATE(object):
            INVULNERABLE = 19807040628566084398385987584L


    class IBattleSessionProvider(object):

        def invalidateVehicleState(self, *args):
            pass


    class BATTLE_CTRL_ID(object):
        FORT_RUSH_GUI_CTRL = None


else:
    from Vehicle import Vehicle
    from gui.battle_control import battle_constants
    from skeletons.gui.battle_session import IBattleSessionProvider
    from fort_rush.gui.battle_control import fort_rush_battle_constants
    from fort_rush.gui.fort_rush_gui_constants import BATTLE_CTRL_ID

def _getPlayerVehicleID(playerAvatar=None):
    playerAvatar = playerAvatar or BigWorld.player()
    return 0 if not playerAvatar else getattr(playerAvatar, 'playerVehicleID', 0)


@dependency.replace_none_kwargs(guiSessionProvider=IBattleSessionProvider)
def _notifyMarkerInvulnerability(vehicleID, isActive, guiSessionProvider=None):
    ctrl = guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.FORT_RUSH_GUI_CTRL)
    if ctrl is not None:
        ctrl.setVehicleInvulnerable(vehicleID, isActive)
    return


@dependency.replace_none_kwargs(guiSessionProvider=IBattleSessionProvider)
def _hideStatusEffect(vehicle, status, guiSessionProvider=None):
    if vehicle.id == _getPlayerVehicleID():
        guiSessionProvider.invalidateVehicleState(status, battle_constants.DestroyTimerViewState(status, 0.0, None))
    if status == fort_rush_battle_constants.FR_VEHICLE_VIEW_STATE.INVULNERABLE:
        _notifyMarkerInvulnerability(vehicle.id, False, guiSessionProvider=guiSessionProvider)
    return


@dependency.replace_none_kwargs(guiSessionProvider=IBattleSessionProvider)
def _showStatusEffect(vehicle, duration, status, level, guiSessionProvider=None):
    playerAvatar = BigWorld.player()
    if not playerAvatar:
        return
    if vehicle.id == _getPlayerVehicleID(playerAvatar):
        startTime = BigWorld.serverTime()
        guiSessionProvider.invalidateVehicleState(status, battle_constants.DestroyTimerViewState(status, level=level, startTime=startTime, totalTime=duration))
    if status == fort_rush_battle_constants.FR_VEHICLE_VIEW_STATE.INVULNERABLE:
        _notifyMarkerInvulnerability(vehicle.id, True, guiSessionProvider=guiSessionProvider)


class FortRushDamageResistanceSystem(CGF.System):
    DmgResistanceActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRo(VehicleExpirableComponent), CGF.ReactRo(FortRushDamageResistanceComponent))
    DmgResistanceRemoved = CGF.RemoveReaction(CGF.GameObject, CGF.ReactRo(VehicleExpirableComponent), CGF.ReactRo(FortRushDamageResistanceComponent))
    VehicleAccess = CGF.AccessReaction(CGF.Rw(Vehicle))
    Reactions = CGF.Reactions(DmgResistanceRemoved, DmgResistanceActivated, VehicleAccess)

    def __init__(self):
        super(FortRushDamageResistanceSystem, self).__init__()
        self.__vehicleIDsByGameObject = {}

    def onMappingUnloaded(self):
        self.__vehicleIDsByGameObject.clear()

    def update(self):
        removed, activated, vehicleAccess = self.reactions
        for go, _, __ in removed:
            self.onRemoved(go, vehicleAccess)

        for go, vehExpirebleCmp, _ in activated:
            self.onActivated(go, vehExpirebleCmp, vehicleAccess)

    def onActivated(self, go, vehExpirebleCmp, vehicleAccess):
        topMostGo = getTopMostGO(go)
        vehicle = vehicleAccess.find(topMostGo)
        if vehicle is None:
            LOG_WARNING('[FortRushDamageResistanceManager] Vehicle not found on the resistance GO during odAdded(spaceId=%s)' % go.spaceID)
            return
        else:
            self.__vehicleIDsByGameObject[go.id] = vehicle.id
            _showStatusEffect(vehicle, vehExpirebleCmp.duration, fort_rush_battle_constants.FR_VEHICLE_VIEW_STATE.INVULNERABLE, battle_constants.TIMER_VIEW_STATE.WARNING)
            return

    def onRemoved(self, go, vehicleAccess):
        topMostGo = getTopMostGO(go)
        vehicle = vehicleAccess.find(topMostGo)
        vehicleID = self.__vehicleIDsByGameObject.pop(go.id, None)
        if vehicle is None:
            LOG_WARNING('[FortRushDamageResistanceManager] Vehicle not found on the resistance GO during onRemoved(spaceId=%s)' % go.spaceID)
            if vehicleID is not None:
                _notifyMarkerInvulnerability(vehicleID, False)
            return
        else:
            _hideStatusEffect(vehicle, fort_rush_battle_constants.FR_VEHICLE_VIEW_STATE.INVULNERABLE)
            return
