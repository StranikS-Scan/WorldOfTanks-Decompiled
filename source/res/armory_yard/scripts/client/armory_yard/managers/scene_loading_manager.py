# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/managers/scene_loading_manager.py
import Math
import BigWorld
import CGF
from cgf_components.armory_yard_components import AssemblyStageIndexManager
from gui.shared.utils.graphics import isRendererPipelineDeferred
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.game_control import IArmoryYardController
from debug_utils import LOG_DEBUG_DEV
ARMORY_YARD_PREFAB_PATH = 'content/Hangars/h21_Armory_Yard_customisation/Armory_Yard_Environment_01.prefab'
ARMORY_YARD_PREFAB_FORWARD_PATH = 'content/Hangars/h21_Armory_Yard_customisation/Armory_Yard_Environment_01_fwd.prefab'
ARMORY_YARD_PREFAB_TARGET_POS = Math.Vector3(1.138, 206.268, 0.286)

class SceneLoadingManager(object):
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)

    def __init__(self):
        self.__isLoading = False
        self.__sceneIsLoaded = False
        self.__loadedCallback = None
        return

    def destroy(self):
        self.__loadedCallback = None
        self.__sceneIsLoaded = False
        self.__isLoading = False
        return

    @dependency.replace_none_kwargs(hangarSpace=IHangarSpace)
    def loadScene(self, loadedCallback=None, hangarSpace=None):
        self.__loadedCallback = loadedCallback
        if hangarSpace is not None and hangarSpace.space is not None:
            hangarSpace.setSelectionEnabled(True)
            cgfStageManager = CGF.getManager(hangarSpace.space.getSpaceID(), AssemblyStageIndexManager)
            cgfStageManager.onReady += self.sceneLoaded
            self.__isLoading = True
            if cgfStageManager.getHangarDetailsGameObject():
                LOG_DEBUG_DEV('Unloading hangar details prefab: path =', cgfStageManager.getHangarDetailsPath())
                CGF.removeGameObject(cgfStageManager.getHangarDetailsGameObject())
                CGF.clearGameObjectsCache([cgfStageManager.getHangarDetailsPath()])
            CGF.loadGameObject(self.__getPrefabPath(), hangarSpace.space.getSpaceID(), ARMORY_YARD_PREFAB_TARGET_POS)
        return

    @dependency.replace_none_kwargs(hangarSpace=IHangarSpace)
    def unloadScene(self, hangarSpace=None):
        if hangarSpace is not None and hangarSpace.space is not None:
            hangarSpace.setSelectionEnabled(False)
            cgfStageManager = CGF.getManager(hangarSpace.space.getSpaceID(), AssemblyStageIndexManager)
            root = cgfStageManager.getRoot()
            if root is not None:
                CGF.removeGameObject(root)
                if cgfStageManager.getHangarDetailsPath() != '' and cgfStageManager.getHangarDetailsPosition() is not None:
                    LOG_DEBUG_DEV('Loading hangar details prefab: path =', cgfStageManager.getHangarDetailsPath())
                    CGF.loadGameObject(cgfStageManager.getHangarDetailsPath(), hangarSpace.space.getSpaceID(), cgfStageManager.getHangarDetailsPosition())
                CGF.clearGameObjectsCache([self.__getPrefabPath()])
                self.__sceneIsLoaded = False
        self.__switchSceneEnvironment(False)
        return

    @dependency.replace_none_kwargs(hangarSpace=IHangarSpace)
    def sceneLoaded(self, hangarSpace=None):
        if hangarSpace is not None and hangarSpace.space is not None:
            cgfStageManager = CGF.getManager(hangarSpace.space.getSpaceID(), AssemblyStageIndexManager)
            cgfStageManager.onReady -= self.sceneLoaded
        self.__switchSceneEnvironment(True)
        self.__isLoading = False
        self.__sceneIsLoaded = True
        if self.__loadedCallback:
            self.__loadedCallback()
        self.__loadedCallback = None
        return

    def __switchSceneEnvironment(self, isInArmoryYard=False):
        environment = BigWorld.CustomizationEnvironment()
        environment.enable(isInArmoryYard)

    def isLoading(self):
        return self.__isLoading

    def sceneIsLoaded(self):
        return self.__sceneIsLoaded

    def __getPrefabPath(self):
        return ARMORY_YARD_PREFAB_PATH if isRendererPipelineDeferred() else ARMORY_YARD_PREFAB_FORWARD_PATH
