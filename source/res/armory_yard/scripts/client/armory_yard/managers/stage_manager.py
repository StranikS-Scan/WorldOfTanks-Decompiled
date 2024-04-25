# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/managers/stage_manager.py
import CGF
from functools import partial
from Queue import Queue
from Event import Event, EventManager
from gui.impl.gen import R
from helpers.CallbackDelayer import CallbackDelayer, TimeDeltaMeter
from helpers import dependency
from cgf_components.armory_yard_components import AssemblyStageIndexManager
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.game_control import IArmoryYardController
from cache import cached_property
from gui.impl.lobby.video.video_view import VideoViewWindow
from gui.shared import g_eventBus
from gui.shared.events import ArmoryYardEvent
from armory_yard.gui.Scaleform.daapi.view.lobby.hangar.sounds import ArmoryYardVideoSoundControl
from armory_yard.managers.fade_manager import ArmoryYardFadeManager, ArmoryYardFadeState
from adisp import adisp_process

def showVideo(videoName, onVideoClose, isAutoClose=True):
    videoSource = R.videos.armory_yard.dyn(videoName)
    if not videoSource or not videoSource.exists():
        onVideoClose()
        return

    def onVideoCloseWrapper(*args, **kwargs):
        if onVideoClose:
            onVideoClose(*args, **kwargs)
        g_eventBus.handleEvent(ArmoryYardEvent(ArmoryYardEvent.STAGE_UNMUTE_SOUND))

    g_eventBus.handleEvent(ArmoryYardEvent(ArmoryYardEvent.STAGE_MUTE_SOUND))
    window = VideoViewWindow(videoSource(), onVideoClosed=onVideoCloseWrapper, isAutoClose=isAutoClose, soundControl=ArmoryYardVideoSoundControl(videoSource()))
    window.load()


class HullXrayManager(TimeDeltaMeter):
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        TimeDeltaMeter.__init__(self)
        self.__isInTransition = False
        self.__transitionTime = 0.0
        self.__currentDuration = 0.0
        self.__isOpening = False
        self.__isOpen = False

    def reset(self):
        self.__isInTransition = False
        self.__transitionTime = 0.0
        self.__currentDuration = 0.0
        self.__isOpening = False
        self.__isOpen = False

    def isInTransition(self):
        return self.__isInTransition

    def isOpen(self):
        return self.__isOpen

    def openXray(self):
        self.measureDeltaTime()
        self.__currentDuration = self.cgfStageManager.openXray()
        if self.__currentDuration > 0.0:
            self.__transitionTime = 0.0
            self.__isInTransition = True
            self.__isOpening = True

    def closeXray(self):
        self.measureDeltaTime()
        self.__currentDuration = self.cgfStageManager.closeXray()
        if self.__currentDuration > 0.0:
            self.__transitionTime = 0.0
            self.__isInTransition = True
            self.__isOpening = False

    def update(self):
        dt = self.measureDeltaTime()
        self.__transitionTime += dt
        if self.__transitionTime >= self.__currentDuration:
            self.__isOpen = self.__isOpening
            self.__currentDuration = 0.0
            self.__transitionTime = 0.0
            self.__isInTransition = False

    @cached_property
    def cgfStageManager(self):
        return CGF.getManager(self.__hangarSpace.space.getSpaceID(), AssemblyStageIndexManager)


class StageManager(CallbackDelayer, TimeDeltaMeter):
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)

    def __init__(self):
        CallbackDelayer.__init__(self)
        TimeDeltaMeter.__init__(self)
        self.__currentStage = None
        self.__previousStage = None
        self.__currentGroup = None
        self.__previousGroup = None
        self.__xrayDuration = 0.0
        self.__stageQueue = Queue()
        self.__playTime = None
        self.__isPlaying = False
        self.__lastAnimStageID = -1
        self.__paused = False
        self.__viewedVideo = False
        self.__hidedDetailsOnStage = False
        self.__fadeManager = ArmoryYardFadeManager()
        self.__fadeManager.setup()
        self.__hullXrayManager = HullXrayManager()
        self.__eventManager = EventManager()
        self.onStartStage = Event(self.__eventManager)
        self.onFinishStage = Event(self.__eventManager)
        return

    def __clear(self):
        self.clearCallbacks()
        self.__currentStage = None
        self.__previousStage = None
        self.__currentGroup = None
        self.__previousGroup = None
        self.__playTime = None
        self.__isPlaying = False
        self.__paused = False
        self.__hidedDetailsOnStage = False
        self.__viewedVideo = False
        self.__xrayDuration = 0.0
        while not self.__stageQueue.empty():
            self.__stageQueue.get()

        return

    def destroy(self):
        self.__clear()
        self.__eventManager.clear()
        self.__fadeManager.destroy()
        self.__hullXrayManager = None
        super(StageManager, self).destroy()
        return

    def startStages(self, fromStage, toStage, reset=False, forceUpdate=False):
        if reset:
            self.cgfStageManager.tryUnhideUnnecessaryPartsAfterStage(toStage)
            self.cgfStageManager.tryUnhideUnnecessaryPartsOnStage(toStage)
            self.cgfStageManager.hideNonSequenceObjectAfterStage()
            self.reset()
        for stage in range(fromStage, toStage):
            if self.cgfStageManager.stageExists(stage):
                if self.cgfStageManager.getStageSortedGroups(stage):
                    for group in self.cgfStageManager.getStageSortedGroups(stage):
                        self.__stageQueue.put((stage, group))

                else:
                    self.__stageQueue.put((stage, None))
            if self.cgfStageManager.isSchemeStage(stage):
                self.__stageQueue.put((stage, 0))

        if not self.__stageQueue.empty() and not self.__isPlaying and self.__currentStage is None:
            self.cgfStageManager.turnOffHighlight()
            self.__armoryYardCtrl.cameraManager.isStagePlaying = True
            currentState = self.__stageQueue.get()
            self.__currentStage = currentState[0]
            self.__currentGroup = currentState[1]
            if not self.hasDelayedCallback(self.__update):
                self.delayCallback(0.0, self.__update)
            if forceUpdate:
                self.__update()
        return

    def reset(self):
        self.cgfStageManager.deactivateAllStage()
        self.__clear()

    def pause(self):
        self.__paused = True

    def resume(self):
        self.__paused = False

    def getLastStageIndexToPlay(self):
        result = -1
        if self.__currentStage is not None:
            result = max(result, self.__currentStage)
        if not self.__stageQueue.empty():
            result = max(result, self.__stageQueue.queue[-1][0])
        return result

    def setStage(self, stage):
        self.__hullXrayManager.reset()
        self.cgfStageManager.activateToStage(0, stage + 1)
        self.cgfStageManager.tryHideUnnecessaryPartsAfterStage(stage)
        self.cgfStageManager.hideNonSequenceObjectAfterStage()
        self.cgfStageManager.showNonSequenceObjectAfterStage(stage)
        self.cgfStageManager.tryHideUnnecessaryPartsOnStage(stage)

    def skip(self, toStage):
        self.reset()
        self.setStage(toStage)
        self.cgfStageManager.turnOnHighlight(self.cgfStageManager.getCameraDataByStageIndex(toStage))
        self.__armoryYardCtrl.cameraManager.isStagePlaying = False

    def playProgress(self, start, stageCount):
        self.startStages(start, start + stageCount, forceUpdate=start == 0)

    def gotToPositionByStage(self, stage, instantly=True):
        self.__armoryYardCtrl.cameraManager.goToPosition(self.cgfStageManager.getCameraDataByStageIndex(stage), instantly=instantly)

    def __setStartStage(self, stage, extraDuration=0.0):
        if self.cgfStageManager.stageHasDurationPart(stage):
            stageDuration = self.cgfStageManager.stageDuration(stage) + extraDuration
            self.onStartStage(stage, stageDuration or 1.0, skipCameraTransition=False)
        else:
            self.onStartStage(stage, 1.0 + extraDuration, skipCameraTransition=True)

    def __update(self):
        if self.__paused:
            return 0.0
        elif self.__hullXrayManager.isInTransition():
            self.__hullXrayManager.update()
            return 0.0
        elif self.__currentStage is None or self.cgfStageManager.getRoot() is None:
            self.__clear()
            return
        else:
            videoName = self.cgfStageManager.stageVideoName(self.__currentStage)
            if videoName is not None and not self.__viewedVideo:
                if self.__previousStage != self.__currentStage:
                    self.__setStartStage(self.__currentStage)
                self.cgfStageManager.turnOffRecorderHighlight()
                self.__fadeIn(partial(showVideo, videoName, self.__fadeOut))
                return 0.0
            if self.cgfStageManager.stageHasXray(self.__currentStage) and not self.__hullXrayManager.isOpen():
                self.__hullXrayManager.openXray()
                self.__xrayDuration = self.__hullXrayManager.cgfStageManager.openXrayDuration
            if not self.__isPlaying:
                self.__playTime = 0.0
                self.__isPlaying = True
                self.measureDeltaTime()
                self.cgfStageManager.activateStageGroup(self.__currentStage, self.__currentGroup)
                self.__hidedDetailsOnStage = False
                if self.__previousStage != self.__currentStage:
                    self.__setStartStage(self.__currentStage, self.__xrayDuration)
            else:
                self.__playTime += self.measureDeltaTime()
                stageGroupDuration = 0.0
                if self.cgfStageManager.stageHasDurationPart(self.__currentStage):
                    stageGroupDuration = self.cgfStageManager.stageGroupDuration(self.__currentStage, self.__currentGroup) + self.__xrayDuration
                if not self.__hidedDetailsOnStage and self.cgfStageManager.stageIsPlaying(self.__currentStage):
                    self.cgfStageManager.tryHideUnnecessaryPartsOnStage(self.__currentStage)
                    self.__hidedDetailsOnStage = True
                if self.__playTime >= stageGroupDuration:
                    self.__playTime = None
                    self.__isPlaying = False
                    self.__previousStage = self.__currentStage
                    self.__previousGroup = self.__currentGroup
                    self.__viewedVideo = False
                    self.__xrayDuration = 0.0
                    if self.__stageQueue.empty():
                        self.__currentStage = self.__currentGroup = None
                        self.cgfStageManager.turnOnHighlight(self.cgfStageManager.getCameraDataByStageIndex(self.__previousStage))
                        self.__armoryYardCtrl.cameraManager.isStagePlaying = False
                        if self.__hullXrayManager.isOpen():
                            self.__hullXrayManager.closeXray()
                    else:
                        self.__currentStage, self.__currentGroup = self.__stageQueue.get()
                        if not self.cgfStageManager.stageHasXray(self.__currentStage) and self.__hullXrayManager.isOpen():
                            self.__hullXrayManager.closeXray()
                    if self.__previousStage != self.__currentStage:
                        self.cgfStageManager.tryHideUnnecessaryPartsAfterStage(self.__previousStage)
                        self.cgfStageManager.showNonSequenceObjectAfterStage(self.__previousStage)
                        self.onFinishStage(self.__previousStage)
            return 0.0

    @adisp_process
    def __fadeIn(self, fadeCallback=None):
        self.pause()
        result = yield self.__fadeManager.startFade()
        if fadeCallback is not None and result in (ArmoryYardFadeState.released, ArmoryYardFadeState.destroying):
            fadeCallback()
        return

    @adisp_process
    def __fadeOut(self, fadeCallback=None):
        self.cgfStageManager.deactivateAllStage()
        self.setStage(self.__currentStage)
        self.cgfStageManager.turnOnRecorderHighlight()
        self.__viewedVideo = True
        self.resume()
        if not self.__fadeManager.isActive():
            return
        else:
            result = yield self.__fadeManager.startFade(fadeIn=False)
            if fadeCallback is not None and result in (ArmoryYardFadeState.released, ArmoryYardFadeState.destroying):
                fadeCallback()
            return

    @cached_property
    def cgfStageManager(self):
        return CGF.getManager(self.__hangarSpace.space.getSpaceID(), AssemblyStageIndexManager)
