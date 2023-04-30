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
from armory_yard.gui.Scaleform.daapi.view.lobby.hangar.sounds import ArmoryYardVideoSoundControl
from armory_yard.managers.fade_manager import ArmoryYardFadeManager, ArmoryYardFadeState
from adisp import adisp_process

def showVideo(videoName, onVideoClose, isAutoClose=True):
    videoSource = R.videos.armory_yard.dyn(videoName)
    if not videoSource or not videoSource.exists():
        onVideoClose()
        return
    window = VideoViewWindow(videoSource(), onVideoClosed=onVideoClose, isAutoClose=isAutoClose, soundControl=ArmoryYardVideoSoundControl(videoSource()))
    window.load()


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
        self.__stageQueue = Queue()
        self.__playTime = None
        self.__isPlaying = False
        self.__lastAnimStageID = -1
        self.__paused = False
        self.__hidedDetailsOnStage = False
        self.__fadeManager = ArmoryYardFadeManager()
        self.__fadeManager.setup()
        self.__eventManager = EventManager()
        self.onStartStage = Event(self.__eventManager)
        self.onFinishStage = Event(self.__eventManager)
        return

    def __clear(self):
        self.__currentStage = None
        self.__previousStage = None
        self.__currentGroup = None
        self.__previousGroup = None
        self.__playTime = None
        self.__isPlaying = False
        self.__paused = False
        self.__hidedDetailsOnStage = False
        while not self.__stageQueue.empty():
            self.__stageQueue.get()

        return

    def destroy(self):
        self.__clear()
        self.__eventManager.clear()
        self.__fadeManager.destroy()
        super(StageManager, self).destroy()

    def startStages(self, fromStage, toStage, reset=False, forceUpdate=False):
        if reset:
            self.cgfStageManager.tryUnhideUnnecessaryPartsAfterStage(toStage)
            self.cgfStageManager.tryUnhideUnnecessaryPartsOnStage(toStage)
            self.reset()
        for stage in range(fromStage, toStage):
            if self.cgfStageManager.stageExists(stage):
                if self.cgfStageManager.getStageSortedGroups(stage):
                    for group in self.cgfStageManager.getStageSortedGroups(stage):
                        self.__stageQueue.put((stage, group))

                else:
                    self.__stageQueue.put((stage, None))

        if not self.__stageQueue.empty() and not self.__isPlaying:
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

    def setStage(self, stage):
        self.cgfStageManager.activateToStage(0, stage + 1)
        self.cgfStageManager.tryHideUnnecessaryPartsAfterStage(stage)
        self.cgfStageManager.tryHideUnnecessaryPartsOnStage(stage)

    def skip(self, toStage):
        self.reset()
        self.setStage(toStage)

    def playProgress(self, start, stageCount):
        end = start + stageCount
        self.startStages(start, end, forceUpdate=start == 0)

    def getPositionByStage(self, stage):
        return self.cgfStageManager.getCameraDataByStageIndex(stage)

    def __update(self):
        if self.__paused:
            return 0.0
        elif self.__currentStage is None:
            self.__isPlaying = False
            self.__playTime = None
            return
        else:
            if not self.__isPlaying:
                self.__playTime = 0.0
                self.__isPlaying = True
                self.measureDeltaTime()
                self.cgfStageManager.activateStageGroup(self.__currentStage, self.__currentGroup)
                self.__hidedDetailsOnStage = False
                if self.__previousStage != self.__currentStage:
                    stageDuration = 1.0
                    skipCameraTransition = False
                    if self.cgfStageManager.stageHasDurationPart(self.__currentStage):
                        stageDuration = self.cgfStageManager.stageDuration(self.__currentStage)
                    else:
                        skipCameraTransition = True
                    self.onStartStage(self.__currentStage, stageDuration, skipCameraTransition=skipCameraTransition)
            else:
                self.__playTime += self.measureDeltaTime()
                stageGroupDuration = 0.0
                if self.cgfStageManager.stageHasDurationPart(self.__currentStage):
                    stageGroupDuration = self.cgfStageManager.stageGroupDuration(self.__currentStage, self.__currentGroup)
                if not self.__hidedDetailsOnStage and self.cgfStageManager.stageIsPlaying(self.__currentStage):
                    self.cgfStageManager.tryHideUnnecessaryPartsOnStage(self.__currentStage)
                    self.__hidedDetailsOnStage = True
                if self.__playTime >= stageGroupDuration:
                    self.__playTime = None
                    self.__isPlaying = False
                    self.__previousStage = self.__currentStage
                    self.__previousGroup = self.__currentGroup
                    if self.__stageQueue.empty():
                        self.__currentStage = None
                        self.__currentGroup = None
                    else:
                        currentState = self.__stageQueue.get()
                        self.__currentStage = currentState[0]
                        self.__currentGroup = currentState[1]
                    if self.__previousStage != self.__currentStage:
                        self.cgfStageManager.tryHideUnnecessaryPartsAfterStage(self.__previousStage)
                        videoName = self.cgfStageManager.stageVideoName(self.__previousStage)
                        if videoName is not None:
                            self.pause()
                            self.__fadeIn(partial(showVideo, videoName, partial(self.__onFinishStageVideo, self.__fadeOut)))
                        else:
                            self.cgfStageManager.endStageGroup(self.__previousStage, self.__previousGroup)
                            self.onFinishStage(self.__previousStage)
            return 0.0

    def __onFinishStageVideo(self, callback=None):
        self.cgfStageManager.endStageGroup(self.__previousStage, self.__previousGroup)
        self.onFinishStage(self.__previousStage)
        self.resume()
        if callback:
            callback()

    @adisp_process
    def __fadeIn(self, fadeCallback=None):
        result = yield self.__fadeManager.startFade()
        if (result == ArmoryYardFadeState.released or result == ArmoryYardFadeState.destroying) and fadeCallback is not None:
            fadeCallback()
        return

    @adisp_process
    def __fadeOut(self, fadeCallback=None):
        if not self.__fadeManager.isActive():
            return
        else:
            result = yield self.__fadeManager.startFade(fadeIn=False)
            if (result == ArmoryYardFadeState.released or result == ArmoryYardFadeState.destroying) and fadeCallback is not None:
                fadeCallback()
            return

    @cached_property
    def cgfStageManager(self):
        return CGF.getManager(self.__hangarSpace.space.getSpaceID(), AssemblyStageIndexManager)
