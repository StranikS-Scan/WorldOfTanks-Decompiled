# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTMapCaseMode.py
import logging
from aih_constants import CTRL_MODE_NAME
from AvatarInputHandler.DynamicCameras.camera_switcher import SwitchToPlaces
import BigWorld
import SoundGroups
from AvatarInputHandler.MapCaseMode import MapCaseControlMode
_logger = logging.getLogger(__name__)

class HyperionMapCaseControlMode(MapCaseControlMode):
    MODE_NAME = CTRL_MODE_NAME.MAP_CASE
    _WT_HYPERION_OVERLAY_SOUND_ID = {True: 'ev_white_tiger_waiting_overlay_ambient',
     False: 'ev_white_tiger_waiting_overlay_ambient_stop'}
    _WT_HYPERION_OVERLAY_STATE_GROUP = 'STATE_white_tiger_gameplay_waiting'
    _WT_HYPERION_OVERLAY_STATE = {True: 'STATE_white_tiger_gameplay_waiting_on',
     False: 'STATE_white_tiger_gameplay_waiting_off'}

    def _enableCamera(self, arcadeState):
        self.camera.enable(BigWorld.player().position, False, switchToPos=1.0, switchToPlace=SwitchToPlaces.TO_RELATIVE_POS)

    def enable(self, **args):
        super(HyperionMapCaseControlMode, self).enable(**args)
        self.__playSound(True)

    def disable(self):
        wasEnabled = self.isEnabled
        super(HyperionMapCaseControlMode, self).disable()
        if wasEnabled:
            self.__playSound(False)

    def __playSound(self, start):
        soundEventName = self._WT_HYPERION_OVERLAY_SOUND_ID.get(start)
        SoundGroups.g_instance.playSound2D(soundEventName)
        self.__setSoundState(start)

    def __setSoundState(self, setState):
        stateName = self._WT_HYPERION_OVERLAY_STATE.get(setState)
        SoundGroups.g_instance.setState(self._WT_HYPERION_OVERLAY_STATE_GROUP, stateName)
