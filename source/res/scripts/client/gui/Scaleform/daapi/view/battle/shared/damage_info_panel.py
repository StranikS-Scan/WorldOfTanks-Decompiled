# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/damage_info_panel.py
import operator
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION, LOG_DEBUG
from gui.Scaleform.daapi.view.meta.DamageInfoPanelMeta import DamageInfoPanelMeta
from gui.Scaleform.genConsts.DAMAGE_INFO_PANEL_CONSTS import DAMAGE_INFO_PANEL_CONSTS
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _EVENT_ID
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_DEVICE_NAME_TO_ID = {'gunHealth': DAMAGE_INFO_PANEL_CONSTS.GUN,
 'turretRotatorHealth': DAMAGE_INFO_PANEL_CONSTS.TURRET_ROTATOR,
 'surveyingDeviceHealth': DAMAGE_INFO_PANEL_CONSTS.SURVEYING_DEVICE,
 'engineHealth': DAMAGE_INFO_PANEL_CONSTS.ENGINE,
 'fuelTankHealth': DAMAGE_INFO_PANEL_CONSTS.FUEL_TANK,
 'radioHealth': DAMAGE_INFO_PANEL_CONSTS.RADIO,
 'ammoBayHealth': DAMAGE_INFO_PANEL_CONSTS.AMMO_BAY,
 'leftTrackHealth': DAMAGE_INFO_PANEL_CONSTS.LEFT_TRACK,
 'rightTrackHealth': DAMAGE_INFO_PANEL_CONSTS.RIGHT_TRACK,
 'commanderHealth': DAMAGE_INFO_PANEL_CONSTS.COMMANDER,
 'gunner1Health': DAMAGE_INFO_PANEL_CONSTS.FIRST_GUNNER,
 'gunner2Health': DAMAGE_INFO_PANEL_CONSTS.SECOND_GUNNER,
 'driverHealth': DAMAGE_INFO_PANEL_CONSTS.DRIVER,
 'radioman1Health': DAMAGE_INFO_PANEL_CONSTS.FIRST_RADIOMAN,
 'radioman2Health': DAMAGE_INFO_PANEL_CONSTS.SECOND_RADIOMAN,
 'loader1Health': DAMAGE_INFO_PANEL_CONSTS.FIRST_LOADER,
 'loader2Health': DAMAGE_INFO_PANEL_CONSTS.SECOND_LOADER}
_DEVICE_HIDE_METHODS = {DAMAGE_INFO_PANEL_CONSTS.GUN: 'as_hideGunS',
 DAMAGE_INFO_PANEL_CONSTS.TURRET_ROTATOR: 'as_hideTurretRotatorS',
 DAMAGE_INFO_PANEL_CONSTS.SURVEYING_DEVICE: 'as_hideSurveyingDeviceS',
 DAMAGE_INFO_PANEL_CONSTS.ENGINE: 'as_hideEngineS',
 DAMAGE_INFO_PANEL_CONSTS.FUEL_TANK: 'as_hideFuelTankS',
 DAMAGE_INFO_PANEL_CONSTS.RADIO: 'as_hideRadioS',
 DAMAGE_INFO_PANEL_CONSTS.AMMO_BAY: 'as_hideAmmoBayS',
 DAMAGE_INFO_PANEL_CONSTS.LEFT_TRACK: 'as_hideLeftTrackS',
 DAMAGE_INFO_PANEL_CONSTS.RIGHT_TRACK: 'as_hideRightTrackS',
 DAMAGE_INFO_PANEL_CONSTS.COMMANDER: 'as_hideCommanderS',
 DAMAGE_INFO_PANEL_CONSTS.FIRST_GUNNER: 'as_hideFirstGunnerS',
 DAMAGE_INFO_PANEL_CONSTS.SECOND_GUNNER: 'as_hideSecondGunnerS',
 DAMAGE_INFO_PANEL_CONSTS.DRIVER: 'as_hideDriverS',
 DAMAGE_INFO_PANEL_CONSTS.FIRST_RADIOMAN: 'as_hideFirstRadiomanS',
 DAMAGE_INFO_PANEL_CONSTS.SECOND_RADIOMAN: 'as_hideSecondRadiomanS',
 DAMAGE_INFO_PANEL_CONSTS.FIRST_LOADER: 'as_hideFirstLoaderS',
 DAMAGE_INFO_PANEL_CONSTS.SECOND_LOADER: 'as_hideSecondLoaderS'}
_DEVICE_UPDATE_METHODS = {DAMAGE_INFO_PANEL_CONSTS.GUN: 'as_updateGunS',
 DAMAGE_INFO_PANEL_CONSTS.TURRET_ROTATOR: 'as_updateTurretRotatorS',
 DAMAGE_INFO_PANEL_CONSTS.SURVEYING_DEVICE: 'as_updateSurveyingDeviceS',
 DAMAGE_INFO_PANEL_CONSTS.ENGINE: 'as_updateEngineS',
 DAMAGE_INFO_PANEL_CONSTS.FUEL_TANK: 'as_updateFuelTankS',
 DAMAGE_INFO_PANEL_CONSTS.RADIO: 'as_updateRadioS',
 DAMAGE_INFO_PANEL_CONSTS.AMMO_BAY: 'as_updateAmmoBayS',
 DAMAGE_INFO_PANEL_CONSTS.LEFT_TRACK: 'as_updateLeftTrackS',
 DAMAGE_INFO_PANEL_CONSTS.RIGHT_TRACK: 'as_updateRightTrackS',
 DAMAGE_INFO_PANEL_CONSTS.COMMANDER: 'as_updateCommanderS',
 DAMAGE_INFO_PANEL_CONSTS.FIRST_GUNNER: 'as_updateFirstGunnerS',
 DAMAGE_INFO_PANEL_CONSTS.SECOND_GUNNER: 'as_updateSecondGunnerS',
 DAMAGE_INFO_PANEL_CONSTS.DRIVER: 'as_updateDriverS',
 DAMAGE_INFO_PANEL_CONSTS.FIRST_RADIOMAN: 'as_updateFirstRadiomanS',
 DAMAGE_INFO_PANEL_CONSTS.SECOND_RADIOMAN: 'as_updateSecondRadiomanS',
 DAMAGE_INFO_PANEL_CONSTS.FIRST_LOADER: 'as_updateFirstLoaderS',
 DAMAGE_INFO_PANEL_CONSTS.SECOND_LOADER: 'as_updateSecondLoaderS'}

def _getDevicesIterator(fetcher):
    for deviceName, state in fetcher.getDamagedDevices():
        if deviceName not in _DEVICE_NAME_TO_ID:
            LOG_ERROR('Device ID is not found', deviceName)
            continue
        if state == 'destroyed':
            stateID = DAMAGE_INFO_PANEL_CONSTS.DESTROYED
        else:
            stateID = DAMAGE_INFO_PANEL_CONSTS.DAMAGED
        yield (_DEVICE_NAME_TO_ID[deviceName], stateID)


def _getDevicesSnapshot(fetcher):
    snap = set()
    for deviceID, stateID in _getDevicesIterator(fetcher):
        snap.add((deviceID, stateID))

    return snap


class DamageInfoPanel(DamageInfoPanelMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(DamageInfoPanel, self).__init__()
        self.__isShown = False
        self.__vehicleID = 0
        self.__devicesSnap = set()
        self.__isInFire = False

    def _populate(self):
        super(DamageInfoPanel, self)._populate()
        feedback = self.sessionProvider.shared.feedback
        if feedback is not None:
            feedback.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        vehicleState = self.sessionProvider.shared.vehicleState
        if vehicleState is not None:
            vehicleState.onPostMortemSwitched += self.__onPostMortemSwitched
            vehicleState.onVehicleControlling += self.__onVehicleControlling
        return

    def _dispose(self):
        vehicleState = self.sessionProvider.shared.vehicleState
        if vehicleState is not None:
            vehicleState.onPostMortemSwitched -= self.__onPostMortemSwitched
            vehicleState.onVehicleControlling -= self.__onVehicleControlling
        feedback = self.sessionProvider.shared.feedback
        if feedback is not None:
            feedback.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        self.__devicesSnap.clear()
        self.__isInFire = False
        super(DamageInfoPanel, self)._dispose()
        return

    def __show(self, vehicleID, fetcher):
        if not self.__isShown:
            self.__setDevicesStates(fetcher)
        else:
            self.__updateDevicesStates(vehicleID, fetcher)
        self.__vehicleID = vehicleID

    def __hide(self):
        if not self.__isShown:
            return
        LOG_DEBUG('Hides all states of device')
        self.as_hideS()
        self.__vehicleID = 0
        self.__devicesSnap.clear()
        self.__isShown = False

    def __setDevicesStates(self, fetcher):
        self.__isShown = True
        items = []
        for deviceID, stateID in _getDevicesIterator(fetcher):
            items.append((deviceID, stateID))
            self.__devicesSnap.add((deviceID, stateID))

        self.__isInFire = fetcher.isInFire()
        if self.__isInFire:
            fireID = DAMAGE_INFO_PANEL_CONSTS.SHOW_FIRE
        else:
            fireID = DAMAGE_INFO_PANEL_CONSTS.HIDE_FIRE
        LOG_DEBUG('Shows states of devices', items, self.__isInFire)
        self.as_showS(items, fireID)

    def __updateDevicesStates(self, vehicleID, fetcher):
        newDevicesSnap = _getDevicesSnapshot(fetcher)
        toHide = self.__devicesSnap.difference(newDevicesSnap)
        toUpdate = dict(newDevicesSnap.difference(self.__devicesSnap))
        for deviceID, _ in toHide:
            if deviceID in toUpdate:
                continue
            if deviceID in _DEVICE_HIDE_METHODS:
                method = _DEVICE_HIDE_METHODS[deviceID]
                LOG_DEBUG('Hides state of device', method)
                try:
                    operator.methodcaller(method)(self)
                except (AttributeError, TypeError):
                    LOG_CURRENT_EXCEPTION()

            LOG_ERROR('Method to hide device is not found', deviceID)

        isHit = self.__vehicleID != vehicleID
        for deviceID, stateID in toUpdate.iteritems():
            if deviceID in _DEVICE_UPDATE_METHODS:
                method = _DEVICE_UPDATE_METHODS[deviceID]
                LOG_DEBUG('Updates state of device', method, stateID, isHit)
                try:
                    operator.methodcaller(method, stateID, isHit)(self)
                except (AttributeError, TypeError):
                    LOG_CURRENT_EXCEPTION()

            LOG_ERROR('Method to update device is not found', deviceID)

        self.__devicesSnap = newDevicesSnap
        isInFire = fetcher.isInFire()
        if isInFire != self.__isInFire:
            self.__isInFire = isInFire
            if self.__isInFire:
                self.as_showFireS(True)
            else:
                self.as_hideFireS()

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if eventID == _EVENT_ID.SHOW_VEHICLE_DAMAGES_DEVICES:
            self.__show(vehicleID, value)
        elif eventID == _EVENT_ID.HIDE_VEHICLE_DAMAGES_DEVICES:
            self.__hide()

    def __onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self.__hide()

    def __onVehicleControlling(self, vehicle):
        self.__hide()
