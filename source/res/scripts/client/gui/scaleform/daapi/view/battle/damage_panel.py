# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/damage_panel.py
import math
import BigWorld
import GUI, Math
from debug_utils import LOG_DEBUG
from gui import TANKMEN_ROLES_ORDER_DICT
from gui.Scaleform.daapi.view.battle import DAMAGE_PANEL_PATH, TANK_INDICATOR_PANEL_PATH
from gui.Scaleform.daapi.view.battle.meta.DamagePanelMeta import DamagePanelMeta
from gui.battle_control import g_sessionProvider, vehicle_getter
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE

class _TankIndicatorCtrl(object):

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
        if vehicle.isPlayer:
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


def _getCrewLayout(crewRoles):
    crewLayout = [ elem[0] for elem in crewRoles ]
    order = TANKMEN_ROLES_ORDER_DICT['plain']
    lastIdx = len(order)

    def comparator(item, other):
        itemIdx = order.index(item) if item in order else lastIdx
        otherIdx = order.index(other) if other in order else lastIdx
        return cmp(itemIdx, otherIdx)

    return sorted(crewLayout, cmp=comparator)


class DamagePanel(DamagePanelMeta):
    __stateHandlers = {VEHICLE_VIEW_STATE.HEALTH: 'as_updateHealthS',
     VEHICLE_VIEW_STATE.SPEED: 'as_updateSpeedS',
     VEHICLE_VIEW_STATE.CRUISE_MODE: 'as_setCruiseModeS',
     VEHICLE_VIEW_STATE.FIRE: 'as_setFireInVehicleS',
     VEHICLE_VIEW_STATE.AUTO_ROTATION: 'as_setAutoRotationS',
     VEHICLE_VIEW_STATE.DESTROYED: 'as_setVehicleDestroyedS',
     VEHICLE_VIEW_STATE.CREW_DEACTIVATED: 'as_setCrewDeactivatedS',
     VEHICLE_VIEW_STATE.PLAYER_INFO: '_updatePlayerInfo',
     VEHICLE_VIEW_STATE.DEVICES: '_updateDeviceState',
     VEHICLE_VIEW_STATE.REPAIRING: '_updateRepairingDevice'}

    def __init__(self, parentUI):
        super(DamagePanel, self).__init__()
        self.__ui = parentUI
        self.__tankIndicator = None
        self.__isShow = True
        return

    def __del__(self):
        LOG_DEBUG('DamagePanel deleted')

    def start(self):
        if self._populate(self.__ui.getMember(DAMAGE_PANEL_PATH)):
            self.__tankIndicator = _TankIndicatorCtrl(self.__ui)
            ctrl = g_sessionProvider.getVehicleStateCtrl()
            ctrl.onVehicleControlling += self.__onVehicleControlling
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            vehicle = ctrl.getControllingVehicle()
            if vehicle:
                self._updatePlayerInfo(vehicle.id)
                self.__onVehicleControlling(vehicle)

    def destroy(self):
        ctrl = g_sessionProvider.getVehicleStateCtrl()
        ctrl.onVehicleControlling -= self.__onVehicleControlling
        ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        if self._flashObject:
            self.as_destroyS()
        self._dispose()
        if self.__tankIndicator:
            self.__tankIndicator.clear(self.__ui)
            self.__tankIndicator = None
        self.__ui = None
        self.__isShow = False
        return

    def showAll(self, isShow):
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

    def _updatePlayerInfo(self, value):
        parts = g_sessionProvider.getCtx().getFullPlayerNameWithParts(vID=value, showVehShortName=False)
        self.as_setPlayerInfoS(*parts)

    def _updateDeviceState(self, value):
        LOG_DEBUG('updateDeviceState', value)
        self.as_updateDeviceStateS(*value[:2])

    def _updateRepairingDevice(self, value):
        self.as_updateRepairingDeviceS(*value)

    def __changeVehicleSetting(self, tag, entityName):
        result, error = g_sessionProvider.getEquipmentsCtrl().changeSettingByTag(tag, entityName=entityName, avatar=BigWorld.player())
        if not result and error:
            self.__ui.vErrorsPanel.showMessage(error.key, error.ctx)

    def __onVehicleControlling(self, vehicle):
        vTypeDesc = vehicle.typeDescriptor
        vType = vTypeDesc.type
        yawLimits = vehicle_getter.getYawLimits(vTypeDesc)
        if yawLimits:
            inDegrees = (math.degrees(-yawLimits[0]), math.degrees(yawLimits[1]))
        else:
            inDegrees = None
        if vehicle.isPlayer:
            isAutoRotationOn = vehicle_getter.isAutoRotationOn(vTypeDesc)
        else:
            isAutoRotationOn = None
        self.as_setupS((vTypeDesc.maxHealth, vehicle.health), vehicle_getter.getVehicleIndicatorType(vTypeDesc), _getCrewLayout(vType.crewRoles), inDegrees, vehicle_getter.hasTurretRotator(vTypeDesc), isAutoRotationOn)
        if self.__tankIndicator:
            self.__tankIndicator.setup(self.__ui, vehicle, yawLimits)
        return

    def __onVehicleStateUpdated(self, state, value):
        if state not in self.__stateHandlers:
            return
        else:
            handler = getattr(self, self.__stateHandlers[state], None)
            if handler and callable(handler):
                if value is not None:
                    handler(value)
                else:
                    handler()
            return
