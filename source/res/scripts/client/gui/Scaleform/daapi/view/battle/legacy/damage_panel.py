# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/legacy/damage_panel.py
import math
import BigWorld
import GUI
import Math
from constants import ATTACK_REASON_INDICES
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.battle.legacy import DAMAGE_PANEL_PATH, TANK_INDICATOR_PANEL_PATH
from gui.Scaleform.daapi.view.battle.legacy.meta.DamagePanelMeta import DamagePanelMeta
from gui.Scaleform.locale.FALLOUT import FALLOUT
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.battle_control import g_sessionProvider, vehicle_getter
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
_STATE_HANDLERS = {VEHICLE_VIEW_STATE.HEALTH: 'as_updateHealthS',
 VEHICLE_VIEW_STATE.SPEED: 'as_updateSpeedS',
 VEHICLE_VIEW_STATE.CRUISE_MODE: 'as_setCruiseModeS',
 VEHICLE_VIEW_STATE.FIRE: 'as_setFireInVehicleS',
 VEHICLE_VIEW_STATE.AUTO_ROTATION: 'as_setAutoRotationS',
 VEHICLE_VIEW_STATE.DESTROYED: '_updateDestroyed',
 VEHICLE_VIEW_STATE.CREW_DEACTIVATED: '_updateCrewDeactivated',
 VEHICLE_VIEW_STATE.PLAYER_INFO: '_updatePlayerInfo',
 VEHICLE_VIEW_STATE.DEVICES: '_updateDeviceState',
 VEHICLE_VIEW_STATE.REPAIRING: '_updateRepairingDevice',
 VEHICLE_VIEW_STATE.SWITCHING: '_switching',
 VEHICLE_VIEW_STATE.RPM: 'as_setNormalizedEngineRpmS',
 VEHICLE_VIEW_STATE.MAX_SPEED: 'as_updateMaxSpeedS',
 VEHICLE_VIEW_STATE.VEHICLE_MOVEMENT_STATE: '_updateVehicleMovementState',
 VEHICLE_VIEW_STATE.VEHICLE_ENGINE_STATE: '_updateVehicleEngineState'}

class _TankIndicatorCtrl(object):
    """
    Tank Indicator flash GUI component.
    """

    def __init__(self, ui):
        mc = GUI.WGTankIndicatorFlash(ui.movie, TANK_INDICATOR_PANEL_PATH)
        mc.wg_inputKeyMode = 2
        ui.component.addChild(mc, 'tankIndicator')

    def __del__(self):
        LOG_DEBUG('_TankIndicatorCtrl deleted')

    def clear(self, ui):
        setattr(ui.component, 'tankIndicator', None)
        return

    def setup(self, ui, vehicle, yawLimits):
        """
        Setups current properties of vehicle.
        
        :param ui: instance of parent UI.
        :param vehicle: entity of vehicle.
        :param yawLimits: tuple(left angle, right angle) containing yaw limit in degrees.
        """
        if vehicle.isPlayerVehicle:
            hullMat = BigWorld.player().getOwnVehicleMatrix()
        else:
            hullMat = vehicle.matrix
        turretMat = vehicle.appearance.turretMatrix
        tankIndicator = ui.component.tankIndicator
        if yawLimits:
            tankIndicator.wg_turretYawConstraints = yawLimits
        else:
            tankIndicator.wg_turretYawConstraints = Math.Vector2(0.0, 0.0)
        tankIndicator.wg_hullMatProv = hullMat
        tankIndicator.wg_turretMatProv = turretMat


class DamagePanel(DamagePanelMeta, IArenaVehiclesController):
    """
    The panel that displays current properties of vehicle:
    - name of player and type of tank;
    - crew, devices;
    - tank indicator by type: SPG, AT-SPG, Tank. For vehicles that have yaw limit (for SPG, AT-SPG)
    - angle constraints for turret.
    - speed of vehicle;
    - tachometer;
    - current and maximum health of vehicle;
    - current mode for cruise control. Only for player's vehicle;
    - indicators of damage to crew. Only for player's vehicle;
    - indicators of damage to device. Only for player's vehicle;
    - auto rotation. Only for player's vehicle;
    - fire. Only for player's vehicle.
    """

    def __init__(self, parentUI):
        super(DamagePanel, self).__init__()
        self.__ui = parentUI
        self.__tankIndicator = None
        self.__isShow = True
        self.__isHasGasAttack = False
        self.__vehicleID = None
        return

    def __del__(self):
        LOG_DEBUG('DamagePanel deleted')

    def start(self):
        """
        Routine invokes when battle interface is created - player joined to arena.
        """
        self.__isHasGasAttack = g_sessionProvider.arenaVisitor.hasGasAttack()
        if self._populate(self.__ui.getMember(DAMAGE_PANEL_PATH)):
            self.__tankIndicator = _TankIndicatorCtrl(self.__ui)
            ctrl = g_sessionProvider.shared.vehicleState
            if ctrl is not None:
                ctrl.onVehicleControlling += self.__onVehicleControlling
                ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            g_sessionProvider.addArenaCtrl(self)
            vehicle = ctrl.getControllingVehicle()
            if vehicle:
                self.__vehicleID = vehicle.id
                self._updatePlayerInfo(vehicle.id)
                self.__onVehicleControlling(vehicle)
        return

    def destroy(self):
        """
        Routine invokes when player leave arena.
        """
        ctrl = g_sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleControlling -= self.__onVehicleControlling
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        g_sessionProvider.removeArenaCtrl(self)
        if self._flashObject:
            self.as_destroyS()
        self._dispose()
        if self.__tankIndicator:
            self.__tankIndicator.clear(self.__ui)
            self.__tankIndicator = None
        self.__ui = None
        self.__isShow = False
        self.__isHasGasAttack = False
        return

    def showAll(self, isShow):
        """
        Hides damage panel component if camera mode equals video.
        
        :param isShow: True if damage panel component should be visible, otherwise false.
        """
        if self.__isShow != isShow:
            self.__isShow = isShow
            self.as_showS(isShow)

    def clickToTankmanIcon(self, entityName):
        self.__changeVehicleSetting('medkit', entityName)

    def clickToDeviceIcon(self, entityName):
        self.__changeVehicleSetting('repairkit', entityName)

    def clickToFireIcon(self):
        self.__changeVehicleSetting('extinguisher', None)
        return

    def updateVehiclesInfo(self, updated, arenaDP):
        for flags, vo in updated:
            if vo.vehicleID == self.__vehicleID:
                self._updatePlayerInfo(self.__vehicleID)
                break

    def _updatePlayerInfo(self, value):
        """
        Updates player information on panel.
        
        :param value: ID of vehicle.
        """
        result = g_sessionProvider.getCtx().getPlayerFullNameParts(vID=value, showVehShortName=False)
        self.as_setPlayerInfoS(result.playerFullName, result.playerName, result.clanAbbrev, result.regionCode, result.vehicleName)

    def _updateDeviceState(self, value):
        """
        Updates indicators of damage to crew/devices .
        
        :param value: name of entity.
        :return: (deviceName, deviceState, realState).
        """
        LOG_DEBUG('updateDeviceState', value)
        self.as_updateDeviceStateS(*value[:2])

    def _updateRepairingDevice(self, value):
        """
        Updates current module repair status bar. It's called from Avatar.updateVehicleMiscStatus.
        
        :param value: (deviceName, progress, seconds) where are
            - deviceName, string value of device name;
            - progress, integer containing current progress of repair (percent);
            - seconds, integer containing time left to repair module.
        """
        self.as_updateRepairingDeviceS(*value)

    def _updateCrewDeactivated(self, deathReasonID):
        self.as_setCrewDeactivatedS()

    def _updateDestroyed(self, deathReasonID=None):
        if self.__isHasGasAttack and deathReasonID is not None:
            if deathReasonID == ATTACK_REASON_INDICES['gas_attack']:
                self.__ui.movie.falloutItems.as_setPostmortemGasAtackInfo({'imgPath': RES_ICONS.MAPS_ICONS_BATTLE_ICON_BATTLE_DEAD,
                 'infoStr': FALLOUT.GASATTACK_POSTMORTEM_VEHICLEDESTROYED,
                 'respawnInfo': FALLOUT.GASATTACK_POSTMORTEM_RESPAWNINFO})
            else:
                self.__ui.movie.falloutItems.as_setPostmortemGasAtackInfo({'infoStr': FALLOUT.GASATTACK_POSTMORTEM_VEHICLEDESTROYED,
                 'respawnInfo': FALLOUT.GASATTACK_POSTMORTEM_RESPAWNINFO})
        self.as_setVehicleDestroyedS()
        return

    def _updateVehicleMovementState(self, runAnimation):
        if runAnimation:
            self.as_startVehicleStartAnimS()
        else:
            self.as_finishVehicleStartAnimS()

    def _updateVehicleEngineState(self, runAnimation):
        if runAnimation:
            self.as_playEngineStartAnimS()
        else:
            self.as_finishVehicleStartAnimS()

    def _switching(self, _):
        self.as_resetS()
        if self.__isHasGasAttack:
            self.__ui.movie.falloutItems.as_hidePostmortemGasAtackInfo()

    def __changeVehicleSetting(self, tag, entityName):
        ctrl = g_sessionProvider.shared.equipments
        if ctrl is None:
            return
        else:
            result, error = ctrl.changeSettingByTag(tag, entityName=entityName, avatar=BigWorld.player())
            if not result and error:
                ctrl = g_sessionProvider.shared.messages
                if ctrl is not None:
                    ctrl.onShowVehicleErrorByKey(error.key, error.ctx)
            return

    def __onVehicleControlling(self, vehicle):
        self.__vehicleID = vehicle.id
        vTypeDesc = vehicle.typeDescriptor
        vType = vTypeDesc.type
        yawLimits = vehicle_getter.getYawLimits(vTypeDesc)
        if yawLimits:
            inDegrees = (math.degrees(-yawLimits[0]), math.degrees(yawLimits[1]))
        else:
            inDegrees = None
        if vehicle.isPlayerVehicle:
            isAutoRotationOn = vehicle_getter.isAutoRotationOn(vTypeDesc)
        else:
            isAutoRotationOn = None
        self.as_setupS((vTypeDesc.maxHealth, vehicle.health), vehicle_getter.getVehicleIndicatorType(vTypeDesc), vehicle_getter.getCrewMainRolesWoIndexes(vType.crewRoles), inDegrees, vehicle_getter.hasTurretRotator(vTypeDesc), isAutoRotationOn)
        if self.__tankIndicator:
            self.__tankIndicator.setup(self.__ui, vehicle, yawLimits)
        return

    def __onVehicleStateUpdated(self, state, value):
        if state not in _STATE_HANDLERS:
            return
        else:
            handler = getattr(self, _STATE_HANDLERS[state], None)
            if handler and callable(handler):
                if value is not None:
                    handler(value)
                else:
                    handler()
            return
