# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/managers/scene_loading_manager.py
from armory_yard.managers.sound_manager import ArmorySoundManager
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.game_control import IHangarSpaceSwitchController
ARMORY_YARD_SCENE_NAME = 'ARMORY_YARD'

class SceneLoadingManager(object):
    __hangarSwitchController = dependency.descriptor(IHangarSpaceSwitchController)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        self.__isLoading = False
        self.__sceneIsLoaded = False
        self.__loadedCallback = None
        self.__defaultSpacePath = None
        self.__soundManager = ArmorySoundManager()
        return

    def destroy(self):
        self.__clearAllPossibleHandlers()
        self.__loadedCallback = None
        self.__sceneIsLoaded = False
        self.__isLoading = False
        self.__defaultSpacePath = None
        self.__soundManager.onSoundModeChanged(False)
        self.__soundManager.clear()
        return

    def __clearAllPossibleHandlers(self):
        if self.__sceneIsLoaded:
            self.__hangarSpace.onSpaceDestroy -= self.__onSpaceDestroy
        if self.__isLoading:
            self.__hangarSpace.onSpaceCreate -= self.sceneLoaded
        if self.__sceneIsLoaded or self.__isLoading:
            self.__hangarSwitchController.onCheckSceneChange -= self.__updateHangarScene

    def __updateHangarScene(self):
        self.__hangarSwitchController.hangarSpaceUpdate(ARMORY_YARD_SCENE_NAME)

    def loadScene(self, loadedCallback=None):
        self.__loadedCallback = loadedCallback
        if self.__hangarSpace.space is not None:
            self.__defaultSpacePath = self.__hangarSpace.spacePath
            self.__hangarSpace.setSelectionEnabled(True)
            self.__hangarSpace.onSpaceCreate += self.sceneLoaded
            self.__hangarSwitchController.customEventModeEnabled = True
            self.__hangarSwitchController.onCheckSceneChange += self.__updateHangarScene
            self.__hangarSwitchController.processPossibleSceneChange()
            self.__isLoading = True
        return

    def unloadScene(self, isReload=True):
        if self.__sceneIsLoaded:
            self.__hangarSpace.onSpaceDestroy -= self.__onSpaceDestroy
            self.__soundManager.onSoundModeChanged(False)
        if self.__sceneIsLoaded or self.__isLoading:
            self.__sceneIsLoaded = False
            self.__hangarSwitchController.customEventModeEnabled = False
            self.__hangarSwitchController.onCheckSceneChange -= self.__updateHangarScene
            self.__hangarSpace.setSelectionEnabled(False)
            if isReload:
                self.__hangarSwitchController.processPossibleSceneChange()

    def sceneLoaded(self):
        self.__hangarSpace.onSpaceCreate -= self.sceneLoaded
        self.__isLoading = False
        self.__sceneIsLoaded = True
        if self.__loadedCallback:
            self.__loadedCallback()
        self.__loadedCallback = None
        self.__soundManager.onSoundModeChanged(True)
        self.__hangarSpace.onSpaceDestroy += self.__onSpaceDestroy
        return

    def isLoading(self):
        return self.__isLoading

    def sceneIsLoaded(self):
        return self.__sceneIsLoaded

    def __onSpaceDestroy(self, _):
        self.__soundManager.onSoundModeChanged(False)
