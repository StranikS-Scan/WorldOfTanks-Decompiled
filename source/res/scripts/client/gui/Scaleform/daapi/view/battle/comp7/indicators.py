# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/comp7/indicators.py
from constants import DIRECT_DETECTION_TYPE
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.view.meta.Comp7ReconFlightMeta import Comp7ReconFlightMeta
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from helpers.time_utils import MS_IN_SECOND
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.daapi.view.battle.shared.indicators import SixthSenseSound

class ReconFlightIndicator(Comp7ReconFlightMeta):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(ReconFlightIndicator, self).__init__()
        self.__callbackDelayer = CallbackDelayer()
        self.__enabled = True
        self.__sound = SixthSenseSound()

    @property
    def enabled(self):
        return self.__enabled

    @enabled.setter
    def enabled(self, enabled):
        self.__enabled = enabled
        if not enabled:
            self.__hide()

    def _populate(self):
        super(ReconFlightIndicator, self)._populate()
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        self.__sound.init()
        return

    def _dispose(self):
        self.__callbackDelayer.destroy()
        self.__callbackDelayer = None
        self.__sound.fini()
        self.__sound = None
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        super(ReconFlightIndicator, self)._dispose()
        return

    def __show(self):
        if not self.__enabled:
            return
        self.as_showS()
        self.__sound.play()
        self.__callbackDelayer.delayCallback(GUI_SETTINGS.reconFlightDuration / float(MS_IN_SECOND), self.__hide)

    def __hide(self):
        self.as_hideS()
        self.__callbackDelayer.clearCallbacks()

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.OBSERVED_BY_ENEMY:
            if value.get('detectionType') == DIRECT_DETECTION_TYPE.SPECIAL_RECON:
                if value.get('isObserved', False):
                    self.__show()
                else:
                    self.__hide()
