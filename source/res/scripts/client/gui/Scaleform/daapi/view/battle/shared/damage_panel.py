# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/damage_panel.py
import logging
import math
import weakref
import BattleReplay
import BigWorld
import GUI
import Math
from ReplayEvents import g_replayEvents
from constants import VEHICLE_SIEGE_STATE as _SIEGE_STATE
from gui.Scaleform.daapi.view.battle.shared.formatters import formatHealthProgress, normalizeHealthPercent
from gui.Scaleform.daapi.view.battle.shared.timers_common import PythonTimer
from gui.Scaleform.daapi.view.meta.DamagePanelMeta import DamagePanelMeta
from gui.Scaleform.flash_wrapper import InputKeyMode
from gui.Scaleform.genConsts.APP_CONTAINERS_NAMES import APP_CONTAINERS_NAMES
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control import vehicle_getter
from gui.battle_control.battle_constants import ALL_VEHICLE_GUI_ITEMS, AUTO_ROTATION_FLAG
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from helpers import dependency
from helpers import i18n
from shared_utils import CONST_CONTAINER
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)
_STATE_HANDLERS = {VEHICLE_VIEW_STATE.HEALTH: '_updateHealth',
 VEHICLE_VIEW_STATE.SPEED: 'as_updateSpeedS',
 VEHICLE_VIEW_STATE.CRUISE_MODE: 'as_setCruiseModeS',
 VEHICLE_VIEW_STATE.FIRE: 'as_setFireInVehicleS',
 VEHICLE_VIEW_STATE.AUTO_ROTATION: '_setAutoRotation',
 VEHICLE_VIEW_STATE.DESTROYED: '_updateDestroyed',
 VEHICLE_VIEW_STATE.CREW_DEACTIVATED: '_updateCrewDeactivated',
 VEHICLE_VIEW_STATE.PLAYER_INFO: '_updatePlayerInfo',
 VEHICLE_VIEW_STATE.DEVICES: '_updateDeviceState',
 VEHICLE_VIEW_STATE.REPAIRING: '_updateRepairingDevice',
 VEHICLE_VIEW_STATE.SWITCHING: '_switching',
 VEHICLE_VIEW_STATE.STUN: '_updateStun',
 VEHICLE_VIEW_STATE.INSPIRE: '_updateInspire',
 VEHICLE_VIEW_STATE.SIEGE_MODE: '_changeSpeedoType'}

class STATUS_ID(CONST_CONTAINER):
    STUN = 0
    INSPIRE = 1


class _IStatusAnimPlayer(object):

    def __init__(self, statusId, **kwargs):
        self._statusId = statusId
        self._hasStatus = False

    def showStatus(self, time, animated):
        self._hasStatus = True

    def hideStatus(self, animated):
        self._hasStatus = False


class _ActionScriptTimer(_IStatusAnimPlayer):

    def __init__(self, view, statusId):
        super(_ActionScriptTimer, self).__init__(statusId=statusId)
        self._view = view

    def showStatus(self, time, animated):
        super(_ActionScriptTimer, self).showStatus(time, animated)
        self._view.as_showStatusS(self._statusId, time, animated)

    def hideStatus(self, animated):
        if self._hasStatus:
            self._view.as_hideStatusS(self._statusId, animated)
        super(_ActionScriptTimer, self).hideStatus(animated)


class _PythonTimer(PythonTimer, _IStatusAnimPlayer):

    def __init__(self, viewObject, statusId):
        super(_PythonTimer, self).__init__(viewObject, 0, 0, 0, 0, statusId=statusId)
        self._animated = False
        self.__hideAnimated = False

    def showStatus(self, totalTime, animated):
        super(_PythonTimer, self).showStatus(totalTime, animated)
        self._animated = animated
        self._totalTime = totalTime
        self._startTime = BigWorld.serverTime()
        self._finishTime = self._startTime + totalTime if totalTime else 0
        self.show()

    def hideStatus(self, animated):
        self.__hideAnimated = animated
        self.hide()
        super(_PythonTimer, self).hideStatus(animated)

    def _showView(self, isBubble):
        self._viewObject.as_showStatusS(self._statusId, self._totalTime, self._animated)

    def _hideView(self):
        if self._hasStatus:
            self._viewObject.as_hideStatusS(self._statusId, self.__hideAnimated)

    def _setViewSnapshot(self, timeLeft):
        self._viewObject.as_setStatusTimerSnapshotS(self._statusId, math.ceil(timeLeft))


class _TankIndicatorCtrl(object):

    def __init__(self, app):
        self.__component = GUI.WGTankIndicatorFlash(app.movie, '_level0.root.{}.main.damagePanel.tankIndicator'.format(APP_CONTAINERS_NAMES.VIEWS))
        self.__component.wg_inputKeyMode = InputKeyMode.NO_HANDLE
        self.__app = app
        self.__app.component.addChild(self.__component, 'tankIndicator')

    def __del__(self):
        _logger.debug('_TankIndicatorCtrl is deleted')

    def clear(self):
        if self.__app is not None:
            self.__app.component.delChild(self.__component)
            self.__app = None
        self.__component = None
        return

    def setup(self, vehicle, yawLimits):
        if vehicle.isPlayerVehicle:
            hullMat = BigWorld.player().getOwnVehicleMatrix()
        else:
            hullMat = vehicle.matrix
        turretMat = vehicle.appearance.turretMatrix
        if yawLimits:
            self.__component.wg_turretYawConstraints = yawLimits
        else:
            self.__component.wg_turretYawConstraints = Math.Vector2(0.0, 0.0)
        self.__component.wg_hullMatProv = hullMat
        self.__component.wg_turretMatProv = turretMat


class DamagePanel(DamagePanelMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(DamagePanel, self).__init__()
        self.__tankIndicator = None
        self.__isShow = True
        self.__maxHealth = 0
        self.__isAutoRotationOn = True
        self.__isAutoRotationShown = False
        self.__statusAnimPlayers = {}
        self.__initialized = False
        self.__isWheeledTech = False
        return

    def __del__(self):
        _logger.debug('DamagePanel is deleted')

    def showAll(self, isShow):
        if self.__isShow != isShow:
            self.__isShow = isShow
            self.as_showS(isShow)

    def getTooltipData(self, entityName, state):
        if entityName in ALL_VEHICLE_GUI_ITEMS:
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

    def clickToStunTimer(self):
        self.__changeVehicleSetting('medkit', None)
        return

    def hideStatusImmediate(self):
        for player in self.__statusAnimPlayers.itervalues():
            player.hideStatus(False)

    def _populate(self):
        super(DamagePanel, self)._populate()
        if self.app is not None:
            self.__tankIndicator = _TankIndicatorCtrl(self.app)
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleControlling += self.__onVehicleControlling
            vehicle = ctrl.getControllingVehicle()
            if vehicle is not None:
                self._updatePlayerInfo(vehicle.id)
                self.__onVehicleControlling(vehicle)
        self.as_setStaticDataS(i18n.makeString(INGAME_GUI.PLAYER_MESSAGES_TANK_IN_FIRE))
        g_replayEvents.onPause += self.__onReplayPaused
        timerCls = _PythonTimer if self.sessionProvider.isReplayPlaying else _ActionScriptTimer
        for statusId in STATUS_ID.ALL():
            self.__statusAnimPlayers[statusId] = timerCls(weakref.proxy(self), statusId)

        return

    def _dispose(self):
        self.as_resetS()
        self.hideStatusImmediate()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleControlling -= self.__onVehicleControlling
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        if self.__tankIndicator is not None:
            self.__tankIndicator.clear()
            self.__tankIndicator = None
        self.__isShow = False
        g_replayEvents.onPause -= self.__onReplayPaused
        super(DamagePanel, self)._dispose()
        return

    def _updatePlayerInfo(self, value):
        result = self.sessionProvider.getCtx().getPlayerFullNameParts(vID=value, showVehShortName=True)
        self.as_setPlayerInfoS(result.playerName, result.clanAbbrev, result.regionCode, result.vehicleName)

    def _updateDeviceState(self, value):
        controllingVehicle = self.sessionProvider.shared.vehicleState.getControllingVehicle()
        if controllingVehicle is None:
            return
        else:
            self.as_updateDeviceStateS(*value[:2])
            return

    def _updateRepairingDevice(self, value):
        self.as_updateRepairingDeviceS(*value)

    def _updateCrewDeactivated(self, _):
        self.as_setCrewDeactivatedS()
        self.hideStatusImmediate()

    def _updateDestroyed(self, _=None):
        self.as_setVehicleDestroyedS()
        self.hideStatusImmediate()

    def _updateHealth(self, health):
        if health <= self.__maxHealth and self.__maxHealth > 0:
            healthStr = formatHealthProgress(health, self.__maxHealth)
            healthProgress = normalizeHealthPercent(health, self.__maxHealth)
            self.as_updateHealthS(healthStr, healthProgress)

    def _setAutoRotation(self, isOn):
        if self.__isAutoRotationShown and self.__isAutoRotationOn != isOn:
            self.__isAutoRotationOn = isOn
            self.as_setAutoRotationS(isOn)

    def _switching(self, _):
        self.as_resetS()
        if self.__isWheeledTech:
            self.__isWheeledTech = False
        self.hideStatusImmediate()

    def _updateStun(self, stunInfo):
        if STATUS_ID.STUN in self.__statusAnimPlayers:
            stunDuration = stunInfo.duration
            if stunDuration > 0:
                self.__statusAnimPlayers[STATUS_ID.STUN].showStatus(stunDuration, True)
            else:
                self.__statusAnimPlayers[STATUS_ID.STUN].hideStatus(True)
        else:
            _logger.warning('Animations times are not initialized, stun status can be lost: %r', stunInfo)

    def _updateInspire(self, values):
        if STATUS_ID.INSPIRE in self.__statusAnimPlayers:
            if values['isInactivation'] is not None:
                time = values['endTime'] - BigWorld.serverTime()
                if time > 0:
                    self.__statusAnimPlayers[STATUS_ID.INSPIRE].showStatus(time, True)
            else:
                self.__statusAnimPlayers[STATUS_ID.INSPIRE].hideStatus(True)
        else:
            _logger.warning('Animations times are not initialized, inspire status can be lost: %r', values)
        return

    def __changeVehicleSetting(self, tag, entityName):
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is None:
            return
        else:
            result, error = ctrl.changeSettingByTag(tag, entityName=entityName, avatar=BigWorld.player())
            if not result and error:
                ctrl = self.sessionProvider.shared.messages
                if ctrl is not None:
                    ctrl.onShowVehicleErrorByKey(error.key, error.ctx)
            return

    def __setupDevicesStates(self):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is None:
            return
        else:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            for stateID in _STATE_HANDLERS.iterkeys():
                value = ctrl.getStateValue(stateID)
                if value is not None:
                    if stateID == VEHICLE_VIEW_STATE.DEVICES:
                        for v in value:
                            self.__onVehicleStateUpdated(stateID, v)

                    else:
                        self.__onVehicleStateUpdated(stateID, value)

            return

    def __onVehicleControlling(self, vehicle):
        vTypeDesc = vehicle.typeDescriptor
        vType = vTypeDesc.type
        yawLimits = vehicle_getter.getYawLimits(vTypeDesc)
        if yawLimits:
            inDegrees = (math.degrees(-yawLimits[0]), math.degrees(yawLimits[1]))
        else:
            inDegrees = None
        self.__isAutoRotationOn = True
        self.__isAutoRotationShown = False
        if vehicle.isPlayerVehicle or BigWorld.player().isObserver():
            flag = vehicle_getter.getAutoRotationFlag(vTypeDesc)
            if flag != AUTO_ROTATION_FLAG.IGNORE_IN_UI:
                self.__isAutoRotationOn = flag == AUTO_ROTATION_FLAG.TURN_ON
                self.__isAutoRotationShown = True
        self.__isWheeledTech = vehicle.isWheeledTech
        self.__maxHealth = vTypeDesc.maxHealth
        health = vehicle.health
        healthStr = formatHealthProgress(health, self.__maxHealth)
        healthProgress = normalizeHealthPercent(health, self.__maxHealth)
        self.as_setupS(healthStr, healthProgress, vehicle_getter.getVehicleIndicatorType(vTypeDesc), vehicle_getter.getCrewMainRolesWithIndexes(vType.crewRoles), inDegrees, vehicle_getter.hasTurretRotator(vTypeDesc), self.__isWheeledTech, self.__isAutoRotationOn)
        if self.__isWheeledTech:
            self.as_setupWheeledS(vTypeDesc.chassis.generalWheelsAnimatorConfig.getNonTrackWheelsCount())
        self._updatePlayerInfo(vehicle.id)
        if self.__tankIndicator is not None:
            self.__tankIndicator.setup(vehicle, yawLimits)
        self.__setupDevicesStates()
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

    def _changeSpeedoType(self, value):
        siegeState = value[0]
        if self.__isWheeledTech:
            if siegeState == _SIEGE_STATE.ENABLED:
                self.as_setSpeedModeS(True)
            elif siegeState == _SIEGE_STATE.DISABLED:
                self.as_setSpeedModeS(False)

    def __onReplayPaused(self, _):
        self.as_setPlaybackSpeedS(BattleReplay.g_replayCtrl.playbackSpeed)
