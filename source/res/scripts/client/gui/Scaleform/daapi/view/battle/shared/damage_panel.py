# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/damage_panel.py
import math
import BattleReplay
import BigWorld
import GUI
import Math
from ReplayEvents import g_replayEvents
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.meta.DamagePanelMeta import DamagePanelMeta
from gui.Scaleform.genConsts.APP_CONTAINERS_NAMES import APP_CONTAINERS_NAMES
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.app_loader.loader import g_appLoader
from gui.battle_control import g_sessionProvider, vehicle_getter
from gui.battle_control.battle_constants import VEHICLE_GUI_ITEMS
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from helpers import i18n
_STATE_HANDLERS = {VEHICLE_VIEW_STATE.HEALTH: '_updateHealth',
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
 VEHICLE_VIEW_STATE.MAX_SPEED: 'as_setMaxSpeedS',
 VEHICLE_VIEW_STATE.VEHICLE_MOVEMENT_STATE: '_updateVehicleMovementState',
 VEHICLE_VIEW_STATE.VEHICLE_ENGINE_STATE: '_updateVehicleEngineState'}

def _getHealthParams(health, maxHealth):
    assert maxHealth > 0
    healthStr = '%d/%d' % (health, maxHealth)
    progress = round(100 * health / maxHealth, 0)
    return (healthStr, progress)


class _TankIndicatorCtrl(object):

    def __init__(self, damagePanel):
        app = g_appLoader.getDefBattleApp()
        if app is not None:
            mc = GUI.WGTankIndicatorFlash(app.movie, '_level0.root.{}.main.damagePanel.tankIndicator'.format(APP_CONTAINERS_NAMES.VIEWS))
            mc.wg_inputKeyMode = 2
            app.component.addChild(mc, 'tankIndicator')
        return

    def __del__(self):
        LOG_DEBUG('_TankIndicatorCtrl deleted')

    def clear(self, ui):
        setattr(ui.component, 'tankIndicator', None)
        return

    def setup(self, ui, vehicle, yawLimits):
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


class DamagePanel(DamagePanelMeta):

    def __init__(self):
        super(DamagePanel, self).__init__()
        self.__tankIndicator = None
        self.__isShow = True
        self._maxHealth = 0
        return

    def __del__(self):
        LOG_DEBUG('DamagePanel deleted')

    def showAll(self, isShow):
        if self.__isShow != isShow:
            self.__isShow = isShow
            self.as_showS(isShow)

    def getTooltipData(self, entityName, state):
        if entityName in VEHICLE_GUI_ITEMS:
            formatter = '#ingame_gui:damage_panel/devices/{}/{}'
        else:
            formatter = '#ingame_gui:damage_panel/crew/{}/{}'
        return i18n.makeString(formatter.format(entityName, state))

    def clickToTankmanIcon(self, entityName):
        self.__changeVehicleSetting('medkit', entityName)

    def clickToDeviceIcon(self, entityName):
        self.__changeVehicleSetting('repairkit', entityName)

    def clickToFireIcon(self):
        self.__changeVehicleSetting('extinguisher', None)
        return

    def _populate(self):
        super(DamagePanel, self)._populate()
        self.__tankIndicator = _TankIndicatorCtrl(self.flashObject)
        ctrl = g_sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleControlling += self.__onVehicleControlling
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            vehicle = ctrl.getControllingVehicle()
            if vehicle:
                self._updatePlayerInfo(vehicle.id)
                self.__onVehicleControlling(vehicle)
            for stateID in _STATE_HANDLERS.iterkeys():
                value = ctrl.getStateValue(stateID)
                if value:
                    self.__onVehicleStateUpdated(stateID, value)

        self.as_setStaticDataS(i18n.makeString(INGAME_GUI.PLAYER_MESSAGES_TANK_IN_FIRE))
        g_replayEvents.onPause += self.__onReplayPaused
        return

    def _dispose(self):
        ctrl = g_sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleControlling -= self.__onVehicleControlling
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        if self.__tankIndicator:
            self.__tankIndicator = None
        self.__isShow = False
        g_replayEvents.onPause -= self.__onReplayPaused
        super(DamagePanel, self)._dispose()
        return

    def _updatePlayerInfo(self, value):
        result = g_sessionProvider.getCtx().getPlayerFullNameParts(vID=value, showVehShortName=False)
        self.as_setPlayerInfoS(result.playerName, result.clanAbbrev, result.regionCode, result.vehicleName)

    def _updateDeviceState(self, value):
        self.as_updateDeviceStateS(*value[:2])

    def _updateRepairingDevice(self, value):
        self.as_updateRepairingDeviceS(*value)

    def _updateCrewDeactivated(self, deathZoneID):
        self.as_setCrewDeactivatedS()

    def _updateDestroyed(self, _=None):
        self.as_setVehicleDestroyedS()

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

    def _updateHealth(self, health):
        self.as_updateHealthS(*_getHealthParams(health, self._maxHealth))

    def _switching(self, _):
        self.as_resetS()

    @staticmethod
    def __changeVehicleSetting(tag, entityName):
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
        self._maxHealth = vTypeDesc.maxHealth
        helthStr, helthProgress = _getHealthParams(vehicle.health, self._maxHealth)
        self.as_setupS(helthStr, helthProgress, vehicle_getter.getVehicleIndicatorType(vTypeDesc), vehicle_getter.getCrewMainRolesWithIndexes(vType.crewRoles), inDegrees, vehicle_getter.hasTurretRotator(vTypeDesc), isAutoRotationOn)
        if self.__tankIndicator:
            app = g_appLoader.getDefBattleApp()
            self.__tankIndicator.setup(app, vehicle, yawLimits)
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

    def __onReplayPaused(self, _):
        self.as_setPlaybackSpeedS(BattleReplay.g_replayCtrl.playbackSpeed)
