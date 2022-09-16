# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/bootcamp/lobby/functional.py
from functools import partial
import BigWorld
import VSE
from visual_script import ASPECT
from wg_async import wg_await, wg_async
from gui.platform.base.statuses.constants import StatusTypes
from gui.shared.event_dispatcher import showDemoAccRenamingOverlay
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.platform.wgnp_controllers import IWGNPDemoAccRequestController
from skeletons.gui.shared.utils import IHangarSpace
from tutorial.control.functional import FunctionalCondition, FunctionalEffect, FunctionalChapterContext
from tutorial.gui import GUI_EFFECT_NAME
from tutorial.logger import LOG_DEBUG, LOG_ERROR, LOG_WARNING
from helpers import dependency
from skeletons.gui.game_control import IBootcampController, IDemoAccCompletionController
from PlayerEvents import g_playerEvents
from tutorial.control.context import SOUND_EVENT

class FunctionalCheckpointReachedCondition(FunctionalCondition):

    def isConditionOk(self, condition):
        isReached = self._funcChapterCtx.isCheckpointReached(condition.getID())
        return isReached if condition.isPositiveState() else not isReached


class FunctionalRequestExclusiveHintEffect(FunctionalEffect):

    def triggerEffect(self):
        itemID = self._effect.getTargetID()
        soundID = self._effect.getSoundID()
        effectID = id(self._effect)
        self._funcChapterCtx.requestExclusiveHint(itemID, soundID, effectID)
        return True


class FunctionalUpdateExclusiveHintsEffect(FunctionalEffect):

    def triggerEffect(self):
        self._funcChapterCtx.updateExclusiveHints()
        return True


class FunctionalStartVSEPlan(FunctionalEffect):

    def triggerEffect(self):
        plan = self._effect.getPlan()
        self._funcChapterCtx.startVSEPlan(plan)


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
    demoAccController = dependency.descriptor(IDemoAccCompletionController)

    def triggerEffect(self):
        if self.demoAccController.isDemoAccount:
            self.demoAccController.runDemoAccRegistration()
        else:
            self.bootcampCtrl.finishBootcamp()
        return True


class FunctionalBootcampLobbyChapterContext(FunctionalChapterContext):
    _HINT_SOUND_DELAY = 0.1

    def __init__(self):
        super(FunctionalBootcampLobbyChapterContext, self).__init__()
        self.__restoreCheckpointID = None
        self.__reachedCheckpoints = []
        self.__forceRefreshActiveHint = False
        self.__activeExclusiveHint = None
        self.__requestedExclusiveHint = None
        self.__requestedExclusiveHintSoundID = None
        self.__exclusiveHintSoundCallback = None
        self.__requestedID = None
        self.__activeID = None
        self.__plans = set()
        return

    def clear(self):
        super(FunctionalBootcampLobbyChapterContext, self).clear()
        self.stopVSEPlans()

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

    def requestExclusiveHint(self, hint, soundID, effectID):
        LOG_DEBUG('requestExclusiveHint', hint, soundID, effectID)
        self.__requestedExclusiveHint = hint
        self.__requestedExclusiveHintSoundID = soundID
        self.__requestedID = effectID

    def updateExclusiveHints(self):
        if self.__requestedExclusiveHint != self.__activeExclusiveHint:
            LOG_DEBUG('updateExclusiveHints: changed', self.__activeExclusiveHint, self.__requestedExclusiveHint)
            if self.__activeExclusiveHint is not None:
                self._gui.stopEffect(GUI_EFFECT_NAME.SHOW_HINT, self.__activeExclusiveHint)
                self.__cancelHintSoundCallback()
            self.__activeExclusiveHint = self.__requestedExclusiveHint
            self.__activeID = self.__requestedID
            if self.__activeExclusiveHint is not None:
                self._gui.playEffect(GUI_EFFECT_NAME.SHOW_HINT, self.__activeExclusiveHint)
                self.__delayedPlayHintSound()
        elif self.__activeExclusiveHint is not None and self.__forceRefreshActiveHint:
            LOG_DEBUG('updateExclusiveHints: forced refresh of active hint', self.__activeExclusiveHint)
            self._gui.playEffect(GUI_EFFECT_NAME.SHOW_HINT, self.__activeExclusiveHint)
        elif self.__activeID != self.__requestedID:
            LOG_DEBUG('updateExclusiveHints: effect id changed, play sound', self.__activeExclusiveHint)
            self.__activeID = self.__requestedID
            self.__delayedPlayHintSound()
        else:
            LOG_DEBUG('updateExclusiveHints: no changes', self.__activeExclusiveHint)
        self.__requestedExclusiveHint = None
        self.__requestedExclusiveHintSoundID = None
        self.__forceRefreshActiveHint = False
        self.__requestedID = None
        return

    def forceHideExclusiveHint(self):
        if self.__activeExclusiveHint is not None:
            LOG_DEBUG('forceHideExclusiveHint: removing', self.__activeExclusiveHint)
            self._gui.stopEffect(GUI_EFFECT_NAME.SHOW_HINT, self.__activeExclusiveHint)
            self.__cancelHintSoundCallback()
            self.__activeExclusiveHint = None
            self.__activeID = None
        else:
            LOG_DEBUG('forceHideExclusiveHint: nothing to remove')
        return

    def startVSEPlan(self, planName):
        for name, _ in self.__plans:
            if name == planName:
                LOG_WARNING('Trying to start the VSE plan that is already running', planName)
                return

        plan = VSE.Plan()
        if plan.load(planName, ASPECT.HANGAR):
            plan.start()
            self.__plans.add((planName, plan))

    def stopVSEPlan(self, planName):
        for name, p in self.__plans:
            if name == planName and p.isActive():
                p.stop()
                self.__plans.remove((name, p))
                break

    def stopVSEPlans(self):
        for _, p in self.__plans:
            if p.isActive():
                p.stop()

        self.__plans.clear()

    def __delayedPlayHintSound(self):
        if self.__requestedExclusiveHintSoundID:
            self.__exclusiveHintSoundCallback = BigWorld.callback(self._HINT_SOUND_DELAY, partial(self.__playHintSound, SOUND_EVENT.HINT_SHOWN, self.__requestedExclusiveHintSoundID))

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


class FunctionalShowDemoAccRenameOverlay(FunctionalEffect):
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _wgnpDemoAccCtrl = dependency.descriptor(IWGNPDemoAccRequestController)
    _connectionMgr = dependency.descriptor(IConnectionManager)
    _demoAccController = dependency.descriptor(IDemoAccCompletionController)
    _WAITING_ID = 'loadContent'

    def __init__(self, effect):
        super(FunctionalShowDemoAccRenameOverlay, self).__init__(effect)
        self.__running = False

    def isInstantaneous(self):
        return False

    def isStillRunning(self):
        return self.__running

    @wg_async
    def triggerEffect(self):
        self._gui.release()
        if not self._demoAccController.isDemoAccount:
            return
        self.__running = True
        status = yield wg_await(self._wgnpDemoAccCtrl.getNicknameStatus(self._WAITING_ID))
        if status.typeIs(StatusTypes.ADD_NEEDED):
            if self._hangarSpace.spaceInited:
                self._showRenameOverlay()
            else:
                self._hangarSpace.onSpaceCreate += self._showRenameOverlay
        else:
            self.__running = False

    def stop(self):
        self._hangarSpace.onSpaceCreate -= self._showRenameOverlay
        self.__running = False

    def _showRenameOverlay(self):
        showDemoAccRenamingOverlay(onClose=self.stop)
