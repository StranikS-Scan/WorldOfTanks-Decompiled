# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/commander/indicators.py
import SoundGroups
from account_helpers.settings_core.settings_constants import SOUND
from gui.Scaleform.daapi.view.meta.SixthSenseMeta import SixthSenseMeta
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.team_sixth_sense import ITeamSixthSenseView
from gui.battle_control.view_components import IViewComponentsCtrlListener
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider

class RTSSixthSenseIndicator(SixthSenseMeta, ITeamSixthSenseView):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(RTSSixthSenseIndicator, self).__init__()
        self.__targetVehicleID = None
        return

    def refresh(self):
        currentVehicleID = avatar_getter.getPlayerVehicleID()
        observed = self.__sessionProvider.dynamic.teamSixthSense.isVehicleObserved(currentVehicleID)
        if observed:
            self.__show(currentVehicleID)

    def sixthSenseActive(self, vehicleID):
        if vehicleID == avatar_getter.getPlayerVehicleID():
            self.__show(vehicleID)

    def sixthSenseNotActive(self, vehicleID):
        if self.__targetVehicleID == vehicleID:
            self.__targetVehicleID = None
            self.as_hideS()
        return

    def __show(self, vehicleID):
        self.__targetVehicleID = vehicleID
        self.as_showS()


class SixthSenseSound(ITeamSixthSenseView, IViewComponentsCtrlListener):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(SixthSenseSound, self).__init__()
        self.__detectionSoundEventName = None
        self.__detectionSoundEvent = None
        self.__initialized = False
        return

    def sixthSenseActive(self, vehicleID):
        if vehicleID == avatar_getter.getPlayerVehicleID():
            if not self.__initialized:
                detectionAlertSetting = self.__settingsCore.options.getSetting(SOUND.DETECTION_ALERT_SOUND)
                self.__setDetectionSoundEvent(detectionAlertSetting.getEventName())
                self.__settingsCore.onSettingsChanged += self.__onSettingsChanged
                self.__initialized = True
            if self.__detectionSoundEvent is not None:
                if self.__detectionSoundEvent.isPlaying:
                    self.__detectionSoundEvent.restart()
                else:
                    self.__detectionSoundEvent.play()
                self.__sessionProvider.shared.optionalDevices.soundManager.playLightbulbEffect()
        return

    def detachedFromCtrl(self, ctrlID):
        self.__settingsCore.onSettingsChanged -= self.__onSettingsChanged

    def __onSettingsChanged(self, diff):
        key = SOUND.DETECTION_ALERT_SOUND
        if key in diff:
            detectionAlertSetting = self.__settingsCore.options.getSetting(key)
            self.__setDetectionSoundEvent(detectionAlertSetting.getEventName())

    def __setDetectionSoundEvent(self, soundEventName):
        if self.__detectionSoundEventName != soundEventName:
            self.__detectionSoundEventName = soundEventName
            self.__detectionSoundEvent = SoundGroups.g_instance.getSound2D(self.__detectionSoundEventName)
