# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/delayed_sixth_sense_indicator.py
import BigWorld
import SoundGroups
import WWISE
from constants import SERVER_TICK_LENGTH
from SMDetectionDelayObservableComponent import SMDetectionDelayObservableComponent
from story_mode.gui.scaleform.daapi.view.meta.DelayedSixthSenseMeta import DelayedSixthSenseMeta
from story_mode.gui.sound_constants import VDAY_SIXTH_SENSE_SOUND_START, VDAY_SIXTH_SENSE_SOUND_STOP, VDAY_SIXTH_SENSE_RTPC_VALUE

class SixthSenseSound(object):

    def __init__(self):
        self.__startSound = None
        return

    def playStart(self):
        self.update(0)
        self.__startSound = SoundGroups.g_instance.getSound2D(VDAY_SIXTH_SENSE_SOUND_START)
        self.__startSound.play()

    def playStop(self):
        self.update(0)
        SoundGroups.g_instance.playSound2D(VDAY_SIXTH_SENSE_SOUND_STOP)

    def fini(self):
        if self.__startSound is not None:
            if self.__startSound.isPlaying:
                self.__startSound.stop()
            self.__startSound = None
        return

    def update(self, rtpcValue):
        WWISE.WW_setRTCPGlobal(VDAY_SIXTH_SENSE_RTPC_VALUE, rtpcValue)


class DelayedSixthSenseIndicator(DelayedSixthSenseMeta):
    FULL_PROGRESS = 100

    def __init__(self):
        super(DelayedSixthSenseIndicator, self).__init__()
        self._timers = {}
        self._timerId = None
        self._isShown = False
        self._sound = SixthSenseSound()
        return

    def _populate(self):
        super(DelayedSixthSenseIndicator, self)._populate()
        SMDetectionDelayObservableComponent.onTimersChange += self.__onTimersChange
        self._timerId = BigWorld.callback(SERVER_TICK_LENGTH, self._update)

    def _update(self):
        isVehicleAlive = BigWorld.player().isVehicleAlive
        items = []
        if self._timers and isVehicleAlive:
            if not self._isShown:
                self.as_showS()
                self._isShown = True
                self._sound.playStart()
        else:
            if self._isShown:
                self._sound.playStop()
            self.as_hideS(False)
            self._isShown = False
        if isVehicleAlive:
            for value in self._timers.itervalues():
                duration = value['endTime'] - value['startTime']
                progress = (BigWorld.serverTime() - value['startTime']) / duration if duration > 0 else 1.0
                items.append(max(0, min(self.FULL_PROGRESS, int(self.FULL_PROGRESS * progress))))

            if items:
                progress = max(items)
                self._sound.update(progress)
                self.as_updateS(progress)
        self._timerId = BigWorld.callback(SERVER_TICK_LENGTH, self._update)

    def _dispose(self):
        SMDetectionDelayObservableComponent.onTimersChange -= self.__onTimersChange
        if self._timerId is not None:
            BigWorld.cancelCallback(self._timerId)
            self._timerId = None
        self._timers = None
        self._isShown = False
        self._sound.fini()
        self._sound = None
        super(DelayedSixthSenseIndicator, self)._dispose()
        return

    def __onTimersChange(self, _, timers):
        self._timers = timers
