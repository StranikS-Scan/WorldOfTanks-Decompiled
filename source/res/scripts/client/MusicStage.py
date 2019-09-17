# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/MusicStage.py
import logging
import BigWorld
import AnimationSequence
from helpers import dependency
from vehicle_systems.stricted_loading import makeCallbackWeak
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.hangar_music_stage import IOffspringConcertManager, IConcertEntity
from hangar_music_stage.sounds import TheOffspringSound, setSoundState
_logger = logging.getLogger(__name__)

class _AnimatorParams(object):
    STATE_IDLE = 'Camera_Idle'
    STATE_SWITCH = 'Switch'
    STATE_SONG_PREFIX = 'song_0'
    STATE_SONG_TEMPLATE = STATE_SONG_PREFIX + '{}'
    TRIGGER_TO_IDLE = 'SwitchToIdle'
    TRIGGER_FROM_IDLE = 'IdleToSwitch'
    TRIGGER_TO_SONG_PREFIX = 'SwitchToSong_0'
    TRIGGER_TO_SONG_TEMPLATE = TRIGGER_TO_SONG_PREFIX + '{}'
    TRIGGER_FROM_SONG_PREFIX = 'SongToSwitch_0'
    TRIGGER_FROM_SONG_TEMPLATE = TRIGGER_FROM_SONG_PREFIX + '{}'


class MusicStage(BigWorld.Entity, IConcertEntity, CallbackDelayer):
    __concertMgr = dependency.descriptor(IOffspringConcertManager)

    def __init__(self):
        super(MusicStage, self).__init__()
        self.__animator = None
        self.__stateToSwitch = None
        self.__lastFinishedSong = None
        return

    def onEnterWorld(self, _):
        self.__concertMgr.setConcertEntity(self)
        if not self.animation:
            _logger.warning('Music stage animation is not set!')
        else:
            loader = AnimationSequence.Loader(self.animation, self.spaceID)
            BigWorld.loadResourceListBG((loader,), makeCallbackWeak(self.__onAnimatorLoaded))
        setSoundState(TheOffspringSound.THE_OFFSPRING_CONCERT_STATE, TheOffspringSound.THE_OFFSPRING_CONCERT_STATE_EXIT)

    def onLeaveWorld(self):
        self.__concertMgr.removeConcertEntity()
        if self.__animator is not None:
            self.__animator.stop()
            self.__animator = None
        self.clearCallbacks()
        return

    def switchToIdle(self):
        self.__lastFinishedSong = None
        if self.__animator is not None:
            self.__switchAnimator(_AnimatorParams.STATE_IDLE)
        return

    def switchToSong(self, songIdx):
        if self.__animator is not None:
            self.__switchAnimator(_AnimatorParams.STATE_SONG_TEMPLATE.format(songIdx + 1))
        if not self.hasDelayedCallback(self.__tick):
            self.delayCallback(0.0, self.__tick)
        return

    def __onAnimatorLoaded(self, resourceList):
        if self.animation in resourceList.failedIDs:
            _logger.warning('Could not load %s', self.animation)
            return
        self.__animator = resourceList[self.animation]
        self.__animator.bindToWorld(self.matrix)
        self.__animator.start()

    def __switchAnimator(self, newState):
        if self.__animator is None:
            return
        else:
            oldState = self.__animator.getCurrNodeName()
            if oldState == _AnimatorParams.STATE_SWITCH:
                self.__transitTo(newState)
            else:
                self.__transitFrom(oldState)
                self.__stateToSwitch = newState
            return

    def __transitTo(self, newState):
        trigger = self.__getTriggerTo(newState)
        if trigger is not None:
            self.__animator.setTrigger(trigger)
        return

    def __getTriggerTo(self, newState):
        if newState == _AnimatorParams.STATE_IDLE:
            return _AnimatorParams.TRIGGER_TO_IDLE
        else:
            _, _, newSongIdx = newState.partition(_AnimatorParams.STATE_SONG_PREFIX)
            if newSongIdx:
                return _AnimatorParams.TRIGGER_TO_SONG_TEMPLATE.format(newSongIdx)
            _logger.warning('Could not find transition to %s', newState)
            return None

    def __transitFrom(self, oldState):
        trigger = self.__getTriggerFrom(oldState)
        if trigger is not None:
            self.__animator.setTrigger(trigger)
        return

    def __getTriggerFrom(self, currentStateName):
        if currentStateName == _AnimatorParams.STATE_IDLE:
            return _AnimatorParams.TRIGGER_FROM_IDLE
        else:
            _, _, currentSongIdx = currentStateName.partition(_AnimatorParams.STATE_SONG_PREFIX)
            if currentSongIdx:
                return _AnimatorParams.TRIGGER_FROM_SONG_TEMPLATE.format(currentSongIdx)
            _logger.warning('Could not find transition from %s', currentStateName)
            return None

    def __tick(self):
        currentStateName = self.__animator.getCurrNodeName()
        if currentStateName == _AnimatorParams.STATE_SWITCH:
            self.__lastFinishedSong = None
            if self.__stateToSwitch is not None:
                self.__transitTo(self.__stateToSwitch)
                self.__stateToSwitch = None
        elif not self.__animator.isCurrNodePlaying():
            _, _, currentSongIdx = currentStateName.partition(_AnimatorParams.STATE_SONG_PREFIX)
            if currentSongIdx and currentStateName != self.__lastFinishedSong:
                self.__lastFinishedSong = currentStateName
                self.__concertMgr.onSongFinished(int(currentSongIdx) - 1)
        if currentStateName == _AnimatorParams.STATE_IDLE:
            self.__lastFinishedSong = None
        else:
            self.delayCallback(0.0, self.__tick)
        return
