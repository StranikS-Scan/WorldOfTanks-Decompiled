# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/radar.py
import BattleReplay
import CommandMapping
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import TOOLTIP_FORMAT
from gui.Scaleform.daapi.view.meta.RadarButtonMeta import RadarButtonMeta
from gui.Scaleform.genConsts.ANIMATION_TYPES import ANIMATION_TYPES
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from battle_royale.gui.battle_control.controllers.radar_ctrl import RadarResponseCode, IReplayRadarListener
from gui.impl import backport
from gui.impl.backport import image
from gui.impl.gen import R
from gui.shared.utils.key_mapping import getScaleformKey
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_RADAR_FAILED_MSG = 'radarInCooldown'
_RADAR_IS_READY_TO_USE_MGS = 'RADAR_IS_READY_TO_USE'

class RadarButton(RadarButtonMeta, IReplayRadarListener, IAbstractPeriodView):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(RadarButton, self).__init__()
        self.__arenaPeriod = None
        self.__isAvailable = True
        self.__isVehicleAlive = True
        self.__radarIsReady = True
        return

    def onClick(self):
        self.__sessionProvider.dynamic.radar.activateRadar()

    def setCoolDownTimeSnapshot(self, time):
        self.as_setCoolDownTimeSnapshotS(time)

    def startTimeOut(self, timeLeft, duration):
        self.as_setCoolDownTimeS(timeLeft, duration, duration - timeLeft, ANIMATION_TYPES.MOVE_ORANGE_BAR_UP)

    def radarIsReady(self, isReady):
        self.__radarIsReady = isReady
        self.__updateAvailability()

    def timeOutDone(self):
        ctrl = self.__sessionProvider.shared.messages
        if ctrl is not None:
            ctrl.onShowPlayerMessageByKey(_RADAR_IS_READY_TO_USE_MGS)
        return

    def radarActivationFailed(self, code):
        if code == RadarResponseCode.COOLDOWN:
            ctrl = self.__sessionProvider.shared.messages
            if ctrl is not None:
                ctrl.showVehicleError(_RADAR_FAILED_MSG)
        return

    def setPeriod(self, period):
        self.__arenaPeriod = period
        self.__updateAvailability()

    def _populate(self):
        super(RadarButton, self)._populate()
        bwKey, sfKey = self.__getCommandStr()
        tooltipTitle = backport.text(R.strings.artefacts.radar.name())
        tooltipDescr = backport.text(R.strings.artefacts.radar.descr())
        tooltip = TOOLTIP_FORMAT.format(tooltipTitle, tooltipDescr)
        self.as_initS(bwKey, sfKey, image(R.images.gui.maps.icons.artefact.radar()), tooltip, self.__sessionProvider.isReplayPlaying)
        vehicleStateCtrl = self.__getVehicleStateCtrl()
        if vehicleStateCtrl is not None:
            vehicleStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        return

    def _dispose(self):
        vehicleStateCtrl = self.__getVehicleStateCtrl()
        if vehicleStateCtrl is not None:
            vehicleStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        if BattleReplay.isPlaying():
            self.as_updateEnableS(False)
            self.as_setCoolDownPosAsPercentS(0)
            self.as_setCoolDownTimeSnapshotS(0)
        super(RadarButton, self)._dispose()
        return

    def __getCommandStr(self):
        command = CommandMapping.CMD_CM_VEHICLE_ACTIVATE_RADAR
        bwKey, _ = CommandMapping.g_instance.getCommandKeys(command)
        sfKey = getScaleformKey(bwKey)
        return (bwKey, sfKey)

    def __getVehicleStateCtrl(self):
        return self.__sessionProvider.shared.vehicleState

    def __onVehicleStateUpdated(self, stateID, _):
        if stateID == VEHICLE_VIEW_STATE.DEATH_INFO:
            self.__isVehicleAlive = False
            self.__updateAvailability()

    def __updateAvailability(self):
        newAvailableVal = self.__arenaPeriod == ARENA_PERIOD.BATTLE and self.__isVehicleAlive and self.__radarIsReady
        if newAvailableVal != self.__isAvailable:
            self.__isAvailable = newAvailableVal
            self.as_updateEnableS(self.__isAvailable)
