# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/bootcamp/lobby/functional.py
from functools import partial
import BigWorld
from tutorial.control.functional import FunctionalCondition, FunctionalEffect, FunctionalChapterContext
from tutorial.gui import GUI_EFFECT_NAME
from tutorial.logger import LOG_DEBUG, LOG_ERROR
from helpers import dependency
from skeletons.gui.game_control import IBootcampController
from PlayerEvents import g_playerEvents
from bootcamp.Assistant import LobbyAssistant
from tutorial.control.context import SOUND_EVENT

class FunctionalCheckpointReachedCondition(FunctionalCondition):

    def isConditionOk(self, condition):
        isReached = self._funcChapterCtx.isCheckpointReached(condition.getID())
        return isReached if condition.isPositiveState() else not isReached


class FunctionalRequestExclusiveHintEffect(FunctionalEffect):

    def triggerEffect(self):
        itemID = self._effect.getTargetID()
        soundID = self._effect.getSoundID()
        self._funcChapterCtx.requestExclusiveHint(itemID, soundID)
        return True


class FunctionalUpdateExclusiveHintsEffect(FunctionalEffect):

    def triggerEffect(self):
        self._funcChapterCtx.updateExclusiveHints()
        return True


class FunctionalStartAssistant(FunctionalEffect):

    def triggerEffect(self):
        hints = self._effect.getHints()
        self._funcChapterCtx.startAssistant(hints)


class FunctionalRestoreCheckpointEffect(FunctionalEffect):
    bootcampCtrl = dependency.descriptor(IBootcampController)

    def triggerEffect(self):
        checkpointID = self.bootcampCtrl.getCheckpoint()
        if checkpointID:
            LOG_DEBUG('[BOOTCAMP] checkpoint to restore:', checkpointID)
            self._funcChapterCtx.setRestoreCheckpointID(checkpointID)
            return True
        LOG_DEBUG('[BOOTCAMP] no checkpoint to restore')
        return False


class FunctionalSaveCheckpointEffect(FunctionalEffect):

    def __init__(self, effect):
        super(FunctionalSaveCheckpointEffect, self).__init__(effect)
        self.__checkpointID = self._funcChapterCtx.getLastReachedCheckpoint()

    bootcampCtrl = dependency.descriptor(IBootcampController)

    def triggerEffect(self):
        LOG_DEBUG('[BOOTCAMP] saving checkpoint:', self.__checkpointID)
        self.bootcampCtrl.saveCheckpoint(self.__checkpointID)
        return True


class FunctionalSetNationEffect(FunctionalEffect):
    bootcampCtrl = dependency.descriptor(IBootcampController)

    def __init__(self, effect):
        super(FunctionalSetNationEffect, self).__init__(effect)
        self.__running = False

    def triggerEffect(self):
        varID = self._effect.getTargetID()
        nationIndex = self._tutorial.getVars().get(varID)
        if nationIndex is None:
            LOG_ERROR('selected nation index is empty!')
            return False
        else:
            self.__running = True
            g_playerEvents.onClientUpdated += self.__onNationChanged
            self.bootcampCtrl.changeNation(nationIndex)
            return True

    def isInstantaneous(self):
        return False

    def isStillRunning(self):
        return self.__running

    def __onNationChanged(self, _, __):
        g_playerEvents.onClientUpdated -= self.__onNationChanged
        self.__running = False


class FunctionalPlayFinalVideoEffect(FunctionalEffect):
    bootcampCtrl = dependency.descriptor(IBootcampController)

    def __init__(self, effect):
        super(FunctionalPlayFinalVideoEffect, self).__init__(effect)
        self.__running = False

    def triggerEffect(self):
        self.__running = True
        self.bootcampCtrl.showFinalVideo(self.__onFinish)
        return True

    def isInstantaneous(self):
        return False

    def isStillRunning(self):
        return self.__running

    def __onFinish(self):
        self.__running = False


class FunctionalFinishBootcampEffect(FunctionalEffect):
    bootcampCtrl = dependency.descriptor(IBootcampController)

    def triggerEffect(self):
        self.bootcampCtrl.finishBootcamp()
        return True


class FunctionalBootcampLobbyChapterContext(FunctionalChapterContext):
    _HINT_SOUND_DELAY = 5

    def __init__(self):
        super(FunctionalBootcampLobbyChapterContext, self).__init__()
        self.__restoreCheckpointID = None
        self.__reachedCheckpoints = []
        self.__forceRefreshActiveHint = False
        self.__activeExclusiveHint = None
        self.__requestedExclusiveHint = None
        self.__requestedExclusiveHintSoundID = None
        self.__exclusiveHintSoundCallback = None
        self.__assistant = None
        return

    def clear(self):
        super(FunctionalBootcampLobbyChapterContext, self).clear()
        self.stopAssistant()

    def onItemLost(self, itemID):
        if itemID == self.__activeExclusiveHint:
            self.__forceRefreshActiveHint = True
            self.__cancelHintSoundCallback()
            self.invalidate()

    def onStartLongEffect(self):
        super(FunctionalBootcampLobbyChapterContext, self).onStartLongEffect()
        self.forceHideExclusiveHint()

    def getRestoreCheckpointID(self):
        return self.__restoreCheckpointID

    def setRestoreCheckpointID(self, checkpointID):
        self.__restoreCheckpointID = checkpointID

    def onCheckpointReached(self, checkpointID):
        self.__reachedCheckpoints.append(checkpointID)

    def isCheckpointReached(self, checkpointID):
        return checkpointID in self.__reachedCheckpoints

    def getLastReachedCheckpoint(self):
        return self.__reachedCheckpoints[-1] if self.__reachedCheckpoints else None

    def requestExclusiveHint(self, hint, soundID):
        LOG_DEBUG('requestExclusiveHint', hint, soundID)
        self.__requestedExclusiveHint = hint
        self.__requestedExclusiveHintSoundID = soundID

    def updateExclusiveHints(self):
        if self.__requestedExclusiveHint != self.__activeExclusiveHint:
            LOG_DEBUG('updateExclusiveHints: changed', self.__activeExclusiveHint, self.__requestedExclusiveHint)
            if self.__activeExclusiveHint is not None:
                self._gui.stopEffect(GUI_EFFECT_NAME.SHOW_HINT, self.__activeExclusiveHint)
                self.__cancelHintSoundCallback()
            self.__activeExclusiveHint = self.__requestedExclusiveHint
            if self.__activeExclusiveHint is not None:
                self._gui.playEffect(GUI_EFFECT_NAME.SHOW_HINT, self.__activeExclusiveHint)
                if self.__requestedExclusiveHintSoundID:
                    self.__exclusiveHintSoundCallback = BigWorld.callback(self._HINT_SOUND_DELAY, partial(self.__playHintSound, SOUND_EVENT.HINT_SHOWN, self.__requestedExclusiveHintSoundID))
        elif self.__activeExclusiveHint is not None and self.__forceRefreshActiveHint:
            LOG_DEBUG('updateExclusiveHints: forced refresh of active hint', self.__activeExclusiveHint)
            self._gui.playEffect(GUI_EFFECT_NAME.SHOW_HINT, self.__activeExclusiveHint)
        else:
            LOG_DEBUG('updateExclusiveHints: no changes', self.__activeExclusiveHint)
        self.__requestedExclusiveHint = None
        self.__requestedExclusiveHintSoundID = None
        self.__forceRefreshActiveHint = False
        return

    def forceHideExclusiveHint(self):
        if self.__activeExclusiveHint is not None:
            LOG_DEBUG('forceHideExclusiveHint: removing', self.__activeExclusiveHint)
            self._gui.stopEffect(GUI_EFFECT_NAME.SHOW_HINT, self.__activeExclusiveHint)
            self.__cancelHintSoundCallback()
            self.__activeExclusiveHint = None
        else:
            LOG_DEBUG('forceHideExclusiveHint: nothing to remove')
        return

    def startAssistant(self, hints):
        self.__assistant = LobbyAssistant(hints)
        self.__assistant.start()

    def stopAssistant(self):
        if self.__assistant is not None:
            self.__assistant.stop()
            self.__assistant = None
        return

    def __playHintSound(self, soundEvent, soundId):
        self.__cancelHintSoundCallback()
        if self._tutorial is not None:
            self._sound.play(soundEvent, soundId)
        return

    def __cancelHintSoundCallback(self):
        if self.__exclusiveHintSoundCallback is not None:
            BigWorld.cancelCallback(self.__exclusiveHintSoundCallback)
            self.__exclusiveHintSoundCallback = None
        return
