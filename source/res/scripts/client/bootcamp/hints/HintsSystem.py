# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/hints/HintsSystem.py
import time
from collections import deque, namedtuple
import BattleReplay
import SoundGroups
from bootcamp.BootcampConstants import HINT_TYPE, HINT_NAMES
from debug_utils_bootcamp import LOG_CURRENT_EXCEPTION_BOOTCAMP
from HintControllers import createPrimaryHintController, createSecondaryHintController, createReplayPlayHintSystem
from HintsBase import HINT_COMMAND
from HintsMove import HintMove, HintMoveTurret, HintNoMove, HintNoMoveTurret, HintMoveToMarker
from HintsScenario import HintAllyShoot, HintUselessConsumable, HintExitGameArea, HintAvoidAndDestroy, HintStartNarrative, HintSectorClear, HintSniperOnDistance, HintLowHP
from HintsDamage import HintCompositeDetrack, HintCompositeHealCommander, HintCompositeBurn
from HintsLobby import HintLobbyRotate
from HintsShoot import HintSniper, HintSniperLevel0, HintShoot, HintAdvancedSniper, HintAim, HintTargetLock, HintWaitReload, HintShootWhileMoving, HintSecondarySniper, HintTargetUnLock
_Voiceover = namedtuple('_Voiceover', ('name', 'sound'))

class HintSystem(object):
    hintsBattleClasses = {HINT_TYPE.HINT_MOVE: HintMove,
     HINT_TYPE.HINT_NO_MOVE: HintNoMove,
     HINT_TYPE.HINT_MOVE_TURRET: HintMoveTurret,
     HINT_TYPE.HINT_NO_MOVE_TURRET: HintNoMoveTurret,
     HINT_TYPE.HINT_MESSAGE_AVOID: HintAvoidAndDestroy,
     HINT_TYPE.HINT_SNIPER: HintSniper,
     HINT_TYPE.HINT_SHOOT: HintShoot,
     HINT_TYPE.HINT_ADVANCED_SNIPER: HintAdvancedSniper,
     HINT_TYPE.HINT_SHOT_WHILE_MOVING: HintShootWhileMoving,
     HINT_TYPE.HINT_REPAIR_TRACK: HintCompositeDetrack,
     HINT_TYPE.HINT_USE_EXTINGUISHER: HintCompositeBurn,
     HINT_TYPE.HINT_HEAL_CREW: HintCompositeHealCommander,
     HINT_TYPE.HINT_EXIT_GAME_AREA: HintExitGameArea,
     HINT_TYPE.HINT_SNIPER_ON_DISTANCE: HintSniperOnDistance,
     HINT_TYPE.HINT_SHOOT_ALLY: HintAllyShoot,
     HINT_TYPE.HINT_AIM: HintAim,
     HINT_TYPE.HINT_TARGET_LOCK: HintTargetLock,
     HINT_TYPE.HINT_WAIT_RELOAD: HintWaitReload,
     HINT_TYPE.HINT_START_NARRATIVE: HintStartNarrative,
     HINT_TYPE.HINT_USELESS_CONSUMABLE: HintUselessConsumable,
     HINT_TYPE.HINT_MOVE_TO_MARKER: HintMoveToMarker,
     HINT_TYPE.HINT_SECTOR_CLEAR: HintSectorClear,
     HINT_TYPE.HINT_SECONDARY_SNIPER: HintSecondarySniper,
     HINT_TYPE.HINT_LOW_HP: HintLowHP,
     HINT_TYPE.HINT_UNLOCK_TARGET: HintTargetUnLock,
     HINT_TYPE.HINT_SNIPER_LEVEL0: HintSniperLevel0}
    hintsLobbyClasses = {HINT_TYPE.HINT_ROTATE_LOBBY: HintLobbyRotate}
    highPriorityVoiceovers = ('vo_bc_weakness_in_armor',)

    def __init__(self, avatar=None, hintsInfo={}):
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
        replayPlaying = BattleReplay.g_replayCtrl.isPlaying
        replaySafeHints = (HINT_TYPE.HINT_MESSAGE_AVOID,)
        self.__replayPlayer = createReplayPlayHintSystem(self)
        for hintName, hintParams in hintsInfo.iteritems():
            try:
                hintTypeId = HINT_NAMES.index(hintName)
                if hintTypeId in HINT_TYPE.BATTLE_HINTS:
                    if replayPlaying and hintTypeId not in replaySafeHints:
                        continue
                    cls = HintSystem.hintsBattleClasses.get(hintTypeId, None)
                    if cls is None:
                        raise Exception('Hint not implemented (%s)' % HINT_NAMES[hintTypeId])
                    hint = cls(avatar, hintParams)
                else:
                    cls = HintSystem.hintsLobbyClasses.get(hintTypeId, None)
                    if cls is None:
                        raise Exception('Hint not implemented (%s)' % HINT_NAMES[hintTypeId])
                    hint = cls(hintParams)
                timeCompleted = hintParams.get('time_completed', 2.0)
                cooldownAfter = hintParams.get('cooldown_after', 2.0)
                voiceover = hintParams.get('voiceover', None)
                message = hintParams.get('message', 'Default Message')
                hint.timeCompleted = timeCompleted
                hint.cooldownAfter = cooldownAfter
                hint.message = message
                if voiceover is not None:
                    hint.voiceover = voiceover
                self.addHint(hint)
            except Exception:
                LOG_CURRENT_EXCEPTION_BOOTCAMP()

        return

    def onAction(self, actionId, actionParams):
        for hint in self._hints:
            hint.onAction(actionId, actionParams)

    def addHint(self, hint):
        hint.id = len(self._hints)
        self._hints.append(hint)

    def __processPrimaryHintCommands(self, commandsQueue):
        for hintId, typeId, commandId, timeCompleted, cooldownTimeout, message, voiceover in commandsQueue:
            if commandId == HINT_COMMAND.SHOW:
                hintController = createPrimaryHintController(self, hintId, typeId, False, timeCompleted, cooldownTimeout, message, voiceover)
                self.__hintsNotCompleted.append(hintController)
            if commandId == HINT_COMMAND.SHOW_COMPLETED:
                hintController = createPrimaryHintController(self, hintId, typeId, True, timeCompleted, cooldownTimeout, message, voiceover)
                self.__hintsCompleted.append(hintController)
            if commandId == HINT_COMMAND.SHOW_COMPLETED_WITH_HINT:
                if self.__currentHint is not None and self.__currentHint.id == hintId:
                    self.__currentHint.complete()
                else:
                    correspondedHint = None
                    for curHint in self.__hintsNotCompleted:
                        if curHint.id == hintId:
                            correspondedHint = curHint
                            break

                    if correspondedHint is None:
                        raise UserWarning('Not found corresponded hint')
                    self.__hintsNotCompleted.remove(correspondedHint)
                    self.__hintsCompleted.append(createPrimaryHintController(self, hintId, typeId, True, timeCompleted, cooldownTimeout, message, voiceover))
            if commandId == HINT_COMMAND.HIDE:
                if self.__currentHint is not None and self.__currentHint.id == hintId:
                    self.__currentHint.close()
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

    def __processSecondaryHintCommands(self, commandsQueue):
        for commandId, hintId, typeId, message in commandsQueue:
            if commandId == HINT_COMMAND.SHOW:
                hintController = createSecondaryHintController(self, hintId, typeId, message)
                self.__secondaryHintQueue.append(hintController)
            if commandId == HINT_COMMAND.HIDE:
                if self.__currentSecondaryHint and self.__currentSecondaryHint.id == hintId:
                    self.__currentSecondaryHint.hide()
                    self.__currentSecondaryHint = None
                else:
                    for curHint in self.__secondaryHintQueue:
                        if curHint.id == hintId:
                            self.__secondaryHintQueue.remove(curHint)
                            break

        if not self.__currentSecondaryHint and self.__secondaryHintQueue:
            self.__currentSecondaryHint = self.__secondaryHintQueue.popleft()
            self.__currentSecondaryHint.show()
        return

    def update(self):
        primaryCommandsQueue = []
        secondaryCommandsQueue = []
        for hint in self._hints:
            curCommandId = hint.update()
            if curCommandId is not None:
                if hint.typeId in HINT_TYPE.SECONDARY_HINTS:
                    secondaryCommandsQueue.append((curCommandId,
                     hint.id,
                     hint.typeId,
                     hint.message))
                else:
                    primaryCommandsQueue.append((hint.id,
                     hint.typeId,
                     curCommandId,
                     hint.timeCompleted,
                     hint.cooldownAfter,
                     hint.message,
                     hint.voiceover))

        self.__processPrimaryHintCommands(primaryCommandsQueue)
        self.__processSecondaryHintCommands(secondaryCommandsQueue)
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
