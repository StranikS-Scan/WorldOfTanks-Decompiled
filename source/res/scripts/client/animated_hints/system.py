# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/animated_hints/system.py
import time
from collections import deque, namedtuple
import SoundGroups
from animated_hints.controllers import createPrimaryHintController, createReplayPlayHintSystem
from animated_hints.base import HINT_COMMAND
_Voiceover = namedtuple('_Voiceover', ('name', 'sound'))

class HintSystem(object):
    highPriorityVoiceovers = ('vo_bc_weakness_in_armor',)

    def __init__(self):
        super(HintSystem, self).__init__()
        self.__secondaryHintQueue = deque()
        self.__currentSecondaryHint = None
        self.__currentHint = None
        self.__hintsCompleted = deque()
        self.__hintsNotCompleted = deque()
        self.__inCooldown = False
        self.__timeCooldownStart = 0
        self.__timeCooldown = 3.0
        self._hints = []
        self.__currentVoiceover = None
        self.__voiceoverSchedule = []
        self.__replayPlayer = createReplayPlayHintSystem(self)
        return

    def addHint(self, hint):
        hint.id = len(self._hints)
        self._hints.append(hint)

    def __processPrimaryHintCommands(self, commandsQueue):
        for hintId, typeId, commandId, timeCompleted, cooldownTimeout, message, voiceover in commandsQueue:
            if commandId == HINT_COMMAND.SHOW:
                hintController = createPrimaryHintController(self, hintId, typeId, False, timeCompleted, cooldownTimeout, message, voiceover)
                self.__hintsNotCompleted.append(hintController)
            if commandId == HINT_COMMAND.SHOW_COMPLETED:
                if self.__currentHint is not None and self.__currentHint.id == hintId:
                    self.__currentHint.complete()
                else:
                    for curHint in self.__hintsNotCompleted:
                        if curHint.id == hintId:
                            self.__hintsNotCompleted.remove(curHint)
                            break

                    hintController = createPrimaryHintController(self, hintId, typeId, True, timeCompleted, cooldownTimeout, message, voiceover)
                    self.__hintsCompleted.append(hintController)
            if commandId == HINT_COMMAND.HIDE:
                if self.__currentHint is not None and self.__currentHint.id == hintId:
                    self.__currentHint.hide()
                    self.__currentHint = None
                else:
                    hintToRemove = None
                    for curHint in self.__hintsCompleted:
                        if curHint.id == hintId:
                            hintToRemove = curHint
                            break

                    if hintToRemove is not None:
                        self.__hintsCompleted.remove(hintToRemove)
                    else:
                        for curHint in self.__hintsNotCompleted:
                            if curHint.id == hintId:
                                hintToRemove = curHint
                                break

                        if hintToRemove is not None:
                            self.__hintsNotCompleted.remove(hintToRemove)

        if self.__currentHint is None:
            if self.__inCooldown:
                if time.time() - self.__timeCooldownStart < self.__timeCooldown:
                    return
                self.__inCooldown = False
            if self.__hintsCompleted:
                self.__currentHint = self.__hintsCompleted.popleft()
                self.__currentHint.show()
            elif self.__hintsNotCompleted:
                self.__currentHint = self.__hintsNotCompleted.popleft()
                self.__currentHint.show()
        elif self.__hintsCompleted and not self.__currentHint.isComplete():
            self.__currentHint.close()
            self.__hintsNotCompleted.appendleft(self.__currentHint)
            self.__currentHint = self.__hintsCompleted.popleft()
            self.__currentHint.show()
        if self.__currentHint is not None and self.__currentHint.isReadyToClose():
            self.__timeCooldown = self.__currentHint.timeCooldown
            self.__inCooldown = True
            self.__timeCooldownStart = time.time()
            self.__currentHint.close()
            self.__currentHint = None
        return

    def update(self):
        primaryCommandsQueue = []
        for hint in self._hints:
            curCommandId = hint.update()
            if curCommandId is not None:
                primaryCommandsQueue.append((hint.id,
                 hint.typeId,
                 curCommandId,
                 hint.timeCompleted,
                 hint.cooldownAfter,
                 hint.message,
                 hint.voiceover))

        self.__processPrimaryHintCommands(primaryCommandsQueue)
        if self.__replayPlayer:
            self.__replayPlayer.update()
        if self.__currentVoiceover and not self.__currentVoiceover.sound.isPlaying:
            self.__currentVoiceover = None
        if self.__currentVoiceover is None and self.__voiceoverSchedule:
            self.playVoiceover(self.__voiceoverSchedule.pop(0))
        return

    def start(self):
        for hint in self._hints:
            hint.start()

    def stop(self):
        if self.__currentHint is not None:
            self.__currentHint.close()
            self.__currentHint = None
        for hint in self._hints:
            hint.stop()
            hint.destroy()

        del self._hints[:]
        if self.__replayPlayer:
            self.__replayPlayer.destroy()
            self.__replayPlayer = None
        self.__hintsCompleted.clear()
        self.__hintsNotCompleted.clear()
        return

    def playVoiceover(self, soundEvent):
        if self.__currentVoiceover:
            if self.__currentVoiceover.name == soundEvent:
                return
            if self.__currentVoiceover.name in HintSystem.highPriorityVoiceovers:
                if soundEvent not in self.__voiceoverSchedule:
                    self.__voiceoverSchedule.append(soundEvent)
                return
            self.__currentVoiceover.sound.stop()
        self.__currentVoiceover = _Voiceover(soundEvent, SoundGroups.g_instance.getSound2D(soundEvent))
        self.__currentVoiceover.sound.play()

    def unscheduleVoiceover(self, soundEvent):
        if soundEvent in self.__voiceoverSchedule:
            self.__voiceoverSchedule.remove(soundEvent)
