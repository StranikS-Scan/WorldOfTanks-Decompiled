# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/managers/scene_loading_manager.py
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from gui.ClientHangarSpace import g_clientHangarSpaceOverride
ARMORY_YARD_SPACE_PATH = 'h00_armory_yard'

class SceneLoadingManager(object):

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

    @dependency.replace_none_kwargs(hangarSpace=IHangarSpace)
    def loadScene(self, loadedCallback=None, hangarSpace=None):
        self.__loadedCallback = loadedCallback
        if hangarSpace is not None and hangarSpace.space is not None:
            self.__defaultSpacePath = hangarSpace.spacePath
            hangarSpace.setSelectionEnabled(True)
            hangarSpace.onSpaceCreate += self.sceneLoaded
            g_clientHangarSpaceOverride.setPath(ARMORY_YARD_SPACE_PATH, visibilityMask=None, isPremium=None, isReload=True)
            self.__isLoading = True
        return

    @dependency.replace_none_kwargs(hangarSpace=IHangarSpace)
    def unloadScene(self, hangarSpace=None, isReload=True):
        if self.__sceneIsLoaded or self.__isLoading:
            self.__sceneIsLoaded = False
            isPremium = hangarSpace.isPremium
            g_clientHangarSpaceOverride.setPath(self.__defaultSpacePath, visibilityMask=None, isPremium=isPremium, isReload=isReload)
        return

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
