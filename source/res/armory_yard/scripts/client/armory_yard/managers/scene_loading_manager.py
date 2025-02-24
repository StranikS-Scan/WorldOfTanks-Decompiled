# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/managers/scene_loading_manager.py
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.game_control import IHangarSpaceSwitchController
ARMORY_YARD_SCENE_NAME = 'ARMORY_YARD'

class SceneLoadingManager(object):
    __hangarSwitchController = dependency.descriptor(IHangarSpaceSwitchController)

    def __init__(self):
        self.__isLoading = False
        self.__sceneIsLoaded = False
        self.__loadedCallback = None
        self.__defaultSpacePath = None
        return

    def destroy(self):
        self.__loadedCallback = None
        self.__sceneIsLoaded = False
        self.__isLoading = False
        self.__defaultSpacePath = None
        return

    def __updateHangarScene(self):
        self.__hangarSwitchController.hangarSpaceUpdate(ARMORY_YARD_SCENE_NAME)

    @dependency.replace_none_kwargs(hangarSpace=IHangarSpace)
    def loadScene(self, loadedCallback=None, hangarSpace=None):
        self.__loadedCallback = loadedCallback
        if hangarSpace is not None and hangarSpace.space is not None:
            self.__defaultSpacePath = hangarSpace.spacePath
            hangarSpace.setSelectionEnabled(True)
            hangarSpace.onSpaceCreate += self.sceneLoaded
            self.__hangarSwitchController.customEventModeEnabled = True
            self.__hangarSwitchController.onCheckSceneChange += self.__updateHangarScene
            self.__hangarSwitchController.processPossibleSceneChange()
            self.__isLoading = True
        return

    def unloadScene(self, isReload=True):
        if self.__sceneIsLoaded or self.__isLoading:
            self.__sceneIsLoaded = False
            self.__hangarSwitchController.customEventModeEnabled = False
            self.__hangarSwitchController.onCheckSceneChange -= self.__updateHangarScene
            if isReload:
                self.__hangarSwitchController.processPossibleSceneChange()

    @dependency.replace_none_kwargs(hangarSpace=IHangarSpace)
    def sceneLoaded(self, hangarSpace=None):
        hangarSpace.onSpaceCreate -= self.sceneLoaded
        self.__isLoading = False
        self.__sceneIsLoaded = True
        if self.__loadedCallback:
            self.__loadedCallback()
        self.__loadedCallback = None
        return

    def isLoading(self):
        return self.__isLoading

    def sceneIsLoaded(self):
        return self.__sceneIsLoaded
