# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/bootcamp/lobby/triggers.py
from tutorial.control.triggers import TriggerWithSubscription
from tutorial.control.functional import FunctionalConditions
from tutorial.data.effects import EFFECT_TYPE
from tutorial.logger import LOG_ERROR, LOG_DEBUG
__all__ = ('LinearCheckpointControllerTrigger',)
_EFFECT_TYPES_TO_SKIP_DURING_RESTORE = (EFFECT_TYPE.SHOW_DIALOG,
 EFFECT_TYPE.PLAY_ANIMATION,
 EFFECT_TYPE.SAVE_ACCOUNT_SETTING,
 EFFECT_TYPE.PLAY_VIDEO,
 EFFECT_TYPE.PLAY_SOUND,
 EFFECT_TYPE.SHOW_DEMO_ACCOUNT_RENAMING)

def _allConditionsOk(item):
    conditions = item.getConditions()
    return True if conditions is None or FunctionalConditions(conditions).allConditionsOk() else False


class LinearCheckpointControllerTrigger(TriggerWithSubscription):
    _RESTORE_NOT_NEEDED = -1

    def __init__(self, triggerID, validateVarID, setVarID, checkpointsSequence):
        super(LinearCheckpointControllerTrigger, self).__init__(triggerID, validateVarID, setVarID)
        self.__checkpointsSequence = checkpointsSequence
        self.__nextCheckpointIndex = 0
        self.__restoredCheckpointIndex = None
        return

    def getCheckpointsSequence(self):
        return self.__checkpointsSequence[:]

    def run(self):
        if self.isRunning:
            return False
        self.__initRestore()
        super(LinearCheckpointControllerTrigger, self).run()

    def isOn(self):
        if self.__isRestoring():
            return True
        else:
            nextCheckpoint = self.__getNextCheckpoint()
            return True if nextCheckpoint is not None and _allConditionsOk(nextCheckpoint) else False

    def toggle(self, isOn=True, **kwargs):
        if not isOn:
            self.isRunning = False
            return
        nextCheckpoint = self.__getNextCheckpoint()
        isRestoring = self.__isRestoring()
        if isRestoring:
            LOG_DEBUG('[BOOTCAMP] restoring checkpoint', nextCheckpoint.getID())
        else:
            LOG_DEBUG('[BOOTCAMP] reached checkpoint', nextCheckpoint.getID())
        self._funcChapterCtx.onCheckpointReached(nextCheckpoint.getID())
        effects = [ e for e in nextCheckpoint.getEffects() if not self.__needSkipCheckpointEffect(e) and _allConditionsOk(e) ]
        if effects:
            self._tutorial.storeEffectsInQueue(effects, isGlobal=True)
        if not isRestoring:
            super(LinearCheckpointControllerTrigger, self).toggle(isOn=isOn, benefit=False, **kwargs)
        self.__nextCheckpointIndex += 1
        self.isRunning = False
        self.run()

    def _subscribe(self):
        self._funcChapterCtx.onBeforeUpdate += self.run

    def _unsubscribe(self):
        self._funcChapterCtx.onBeforeUpdate -= self.run

    def __initRestore(self):
        if self.__restoredCheckpointIndex is None:
            restoreCheckpointID = self._funcChapterCtx.getRestoreCheckpointID()
            if restoreCheckpointID is not None:
                if restoreCheckpointID in self.__checkpointsSequence:
                    self.__restoredCheckpointIndex = self.__checkpointsSequence.index(restoreCheckpointID)
                else:
                    LOG_ERROR('unknown checkpoint:', restoreCheckpointID)
                    self.__restoredCheckpointIndex = LinearCheckpointControllerTrigger._RESTORE_NOT_NEEDED
                self._funcChapterCtx.setRestoreCheckpointID(None)
            else:
                self.__restoredCheckpointIndex = LinearCheckpointControllerTrigger._RESTORE_NOT_NEEDED
        return

    def __isRestoring(self):
        return self.__nextCheckpointIndex <= self.__restoredCheckpointIndex

    def __getNextCheckpoint(self):
        if self.__nextCheckpointIndex < len(self.__checkpointsSequence):
            nextCheckpointID = self.__checkpointsSequence[self.__nextCheckpointIndex]
            checkpoint = self._data.getHasIDEntity(nextCheckpointID)
            if checkpoint is None:
                LOG_ERROR('checkpoint not found:', nextCheckpointID)
            else:
                return checkpoint
        return

    def __needSkipCheckpointEffect(self, checkpointEffect):
        return self.__isRestoring() and checkpointEffect.getType() in _EFFECT_TYPES_TO_SKIP_DURING_RESTORE
