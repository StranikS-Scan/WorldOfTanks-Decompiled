# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/hint_panel/crosshair_hint_plugin.py
from account_helpers import AccountSettings
from gui.battle_control.battle_constants import ITimerViewState
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from hint_panel_plugin import HintPanelPlugin, HINT_TIMEOUT
from skeletons.gui.battle_session import IBattleSessionProvider
_VIEW_HINT_CHECK_STATES = (VEHICLE_VIEW_STATE.DESTROY_TIMER,
 VEHICLE_VIEW_STATE.DEATHZONE_TIMER,
 VEHICLE_VIEW_STATE.FIRE,
 VEHICLE_VIEW_STATE.STUN)

class AbstractCrosshairHintPlugin(HintPanelPlugin):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _SETTINGS_NAME = None
    _CMD_NAME = None
    __slots__ = ('_isHintShown', '_isSuitableVehicle', '_settings', '__callbackDelayer', '__isTimerDisplaying')

    def __init__(self, parentObj):
        super(AbstractCrosshairHintPlugin, self).__init__(parentObj)
        self._isHintShown = False
        self._isSuitableVehicle = False
        self._settings = {}
        self.__isTimerDisplaying = False
        self.__callbackDelayer = CallbackDelayer()
        self._settings = AccountSettings.getSettings(self._SETTINGS_NAME)

    def start(self):
        self._addListeners()
        if self._haveHintsLeft(self._settings):
            sharedController = self.sessionProvider.shared
            crosshairCtrl = sharedController.crosshair
            vehicleCtrl = sharedController.vehicleState
            if crosshairCtrl is not None and vehicleCtrl is not None:
                self._setup(crosshairCtrl, vehicleCtrl)
        return

    def stop(self):
        self._removeListeners()
        self.__callbackDelayer.destroy()
        self._saveSettings()

    def updateMapping(self):
        if self._isHintShown:
            self._addHint()

    @classmethod
    def isSuitable(cls):
        return not cls.sessionProvider.isReplayPlaying and not cls._getIsObserver()

    @classmethod
    def _getIsObserver(cls):
        arenaDP = cls.sessionProvider.getArenaDP()
        return arenaDP is not None and arenaDP.getVehicleInfo().isObserver()

    def _canShowHint(self, viewID):
        return self._isSuitableVehicle and not self.__isTimerDisplaying

    def _addListeners(self):
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onCrosshairViewChanged += self.__onCrosshairViewChanged
        vehicleState = self.sessionProvider.shared.vehicleState
        if vehicleState is not None:
            vehicleState.onVehicleControlling += self.__onVehicleControlling
            vehicleState.onVehicleStateUpdated += self.__onVehicleStateUpdated
        return

    def _removeListeners(self):
        ctrl = self.sessionProvider.shared.crosshair
        if ctrl is not None:
            ctrl.onCrosshairViewChanged -= self.__onCrosshairViewChanged
        vehicleState = self.sessionProvider.shared.vehicleState
        if vehicleState is not None:
            vehicleState.onVehicleControlling -= self.__onVehicleControlling
            vehicleState.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        return

    def _checkIsSuitableVehicle(self):
        arenaDP = self.sessionProvider.getArenaDP()
        if arenaDP is not None:
            vInfo = arenaDP.getVehicleInfo()
            return vInfo.isPlayerVehicle() and vInfo.isSPG()
        else:
            return False

    def _setup(self, crosshairCtrl, vehicleCtrl):
        self.__onCrosshairViewChanged(crosshairCtrl.getViewID())
        for stateID in _VIEW_HINT_CHECK_STATES:
            stateValue = vehicleCtrl.getStateValue(stateID)
            if stateValue:
                self.__onVehicleStateUpdated(stateID, stateValue)

    def _saveSettings(self):
        AccountSettings.setSettings(self._SETTINGS_NAME, self._settings)

    def __onVehicleControlling(self, vehicle):
        self._isSuitableVehicle = self._checkIsSuitableVehicle()
        if self._isSuitableVehicle:
            self._updateCounterOnBattle(self._settings)

    def __onCrosshairViewChanged(self, viewID):
        haveHintsLeft = self._haveHintsLeft(self._settings)
        if haveHintsLeft and self._canShowHint(viewID):
            self._addHint()
        elif self._isHintShown:
            self._removeHint()

    def __onVehicleStateUpdated(self, stateID, stateValue):
        if stateID in _VIEW_HINT_CHECK_STATES:
            self.__updateTimerStatus(stateID, stateValue)
            if self._isHintShown and self.__isTimerDisplaying:
                self._removeHint()
            else:
                ctrl = self.sessionProvider.shared.crosshair
                if ctrl is not None:
                    self.__onCrosshairViewChanged(ctrl.getViewID())
        return

    def __updateTimerStatus(self, stateID, stateValue):
        if stateID == VEHICLE_VIEW_STATE.STUN:
            self.__isTimerDisplaying = stateValue.endTime > 0.0 if stateValue is not None else False
        elif isinstance(stateValue, ITimerViewState):
            self.__isTimerDisplaying = stateValue.needToShow()
        else:
            self.__isTimerDisplaying = stateValue
        return

    def _addHint(self):
        if not self.__isTimerDisplaying:
            self._parentObj.setBtnHint(self._CMD_NAME, self._getHint())
            self._isHintShown = True
            self.__callbackDelayer.delayCallback(HINT_TIMEOUT, self.__onHintTimeOut)

    def _removeHint(self):
        self._parentObj.removeBtnHint(self._CMD_NAME)
        self._isHintShown = False
        self.__callbackDelayer.stopCallback(self.__onHintTimeOut)
        if self._haveHintsLeft(self._settings) <= 0:
            self.stop()

    def __onHintTimeOut(self):
        self._removeHint()
