# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/LootBoxManager.py
import BigWorld
import LootBoxReader as lbr
from debug_utils import LOG_ERROR
from functools import partial
from LootBoxObject import LootBoxObject, BoxStates
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from helpers import dependency
from skeletons.new_year import ICustomizableObjectsManager, INewYearUIManager, INewYearController, ILootBoxManager
from gui.shared.utils.HangarSpace import g_hangarSpace
from gui.shared.events import FightButtonEvent
from helpers.CallbackDelayer import CallbackDelayer
from new_year.new_year_sounds import NYSoundEvents
from items.new_year_types import NY_STATE

class LootBoxManager(CallbackDelayer, ILootBoxManager):

    class _EntityManager(object):
        __LOOTBOX_CONFIG_FILE = 'scripts/item_defs/new_year/lootbox.xml'

        def __init__(self, config=__LOOTBOX_CONFIG_FILE):
            super(LootBoxManager._EntityManager, self).__init__()
            self.__vBoxId = None
            self.__callbackId = None
            self.__cfg = config
            self.__anchorName = None
            self.clickedCallback = None
            self.stateChangedCallback = None
            self.doneCallback = None
            return

        def destroy(self):
            self.clickedCallback = None
            self.stateChangedCallback = None
            self.doneCallback = None
            self.__finiBox()
            return

        @property
        def anchorName(self):
            return self.__anchorName

        @property
        def isOnScene(self):
            return self.__vBoxId is not None

        @property
        def isDone(self):
            if not self.__vBoxId:
                return True
            entity = self.__getVisualBox()
            return entity.state == BoxStates.DONE or entity.state == BoxStates.FINISH_OPENING

        @property
        def isReadyToFinishBoxAnimation(self):
            if not self.__vBoxId:
                return False
            entity = self.__getVisualBox()
            return entity.state == BoxStates.START_OPENING

        def enableEntity(self):
            entity = self.__getVisualBox()
            if entity:
                entity.enable(True)

        def __initBox(self, callback):
            root = lbr.getRoot(self.__cfg)
            if root:
                position, direction, modelName, self.__anchorName, selectionId = lbr.readEntity(root)
                vBoxId = LootBoxObject.create(position, direction, modelName, self.__anchorName, selectionId, self.__cfg, BigWorld.camera().spaceID)
                self.__waitForEntity(vBoxId, callback)
            else:
                LOG_ERROR("Can't create LootBox entity - no arguments provided")

        def __finiBox(self):
            if self.__callbackId:
                BigWorld.cancelCallback(self.__callbackId)
                self.__callbackId = None
            if self.__vBoxId:
                LootBoxObject.destroy(self.__vBoxId)
            return

        def __onLootBoxLeaveWorld(self):
            self.__vBoxId = None
            if self.doneCallback is not None:
                self.doneCallback()
            return

        def createEntity(self, callback):
            if not self.__existing():
                self.__initBox(partial(self.createEntity, callback))
                return
            if not self.__vBoxId:
                return
            entity = self.__getVisualBox()
            entity.setOnStateChangedCallback(self.stateChangedCallback)
            entity.setOnClickCallback(self.clickedCallback)
            entity.setOnLeaveWorldCallback(self.__onLootBoxLeaveWorld)
            if callback:
                callback()

        def receiveBox(self, isNew):
            if not self.__vBoxId:
                return False
            entity = self.__getVisualBox()
            return entity.startTransition(BoxStates.APPEAR if isNew else BoxStates.ON_SCENE)

        def startOpenBox(self):
            if not self.__vBoxId:
                return False
            entity = self.__getVisualBox()
            return entity.startTransition(BoxStates.START_OPENING)

        def finishOpenBox(self):
            if not self.__vBoxId:
                return False
            entity = self.__getVisualBox()
            return entity.startTransition(BoxStates.FINISH_OPENING)

        def hideBox(self):
            if not self.__vBoxId:
                return
            self.__finiBox()

        def __existing(self):
            if not self.__vBoxId:
                for k, v in BigWorld.entities.items():
                    if isinstance(v, LootBoxObject):
                        self.__vBoxId = k
                        break

            return self.__vBoxId

        def __getVisualBox(self):
            try:
                entity = BigWorld.entities[self.__vBoxId]
            except:
                entity = None
                LOG_ERROR("Can't find enity with id = {}".format(self.__vBoxId))

            return entity

        def __waitForEntity(self, entityID, callback):
            try:
                entity = BigWorld.entities[entityID]
                self.__vBoxId = entityID
                if callback:
                    callback()
                self.__callbackId = None
            except:
                self.__callbackId = BigWorld.callback(0.0, partial(self.__waitForEntity, entityID, callback))

            return

    class BoxActions:
        SHOW_BOX_ON_SCENE = 0
        PLAY_RECEIVE_BOX_ANIMATION = 1
        PLAY_START_OPEN_BOX_ANIMATION = 2
        PLAY_FINISH_OPEN_BOX_ANIMATION = 3
        CREATE_ENTITY = 4
        DESTROY_ENTITY = 5
        SWITCH_CAMERA_TO_BOX = 6
        SWITCH_CAMERA_TO_HANGAR = 7
        SHOW_UI = 8
        SHOW_UI_CONTENT = 9
        HIDE_UI = 13
        HIDE_UI_CONTENT = 14
        ENABLE_BOX_ONLY = 10
        ENABLE_ALL = 11
        OPEN_BOX_VIA_CHEST_STORAGE = 12

    customizableObjectsMgr = dependency.descriptor(ICustomizableObjectsManager)
    newYearController = dependency.descriptor(INewYearController)
    newYearUIManager = dependency.descriptor(INewYearUIManager)

    @property
    def __isAnyBoxAvailable(self):
        if self.newYearController.state != NY_STATE.IN_PROGRESS:
            return False
        chestCount = self.newYearController.chestStorage.count
        return chestCount > 0

    @property
    def __isAnyActionQueued(self):
        return self.__currentAction or self.__actionsQueue

    @property
    def isQuestBoosterAwardWindowBlocked(self):
        if self.__isInUI:
            return True
        if self.__currentAction == self.BoxActions.SHOW_UI or self.__currentAction == self.BoxActions.SHOW_UI_CONTENT:
            return True
        if self.__actionsQueue:
            for action in self.__actionsQueue:
                if action == self.BoxActions.SHOW_UI or action == self.BoxActions.SHOW_UI_CONTENT:
                    return True

        return False

    def __init__(self):
        CallbackDelayer.__init__(self)
        self.__entityManager = None
        self.__isInUI = False
        self.__currentAction = None
        self.__actionsQueue = None
        self.__actionMapping = {self.BoxActions.SHOW_BOX_ON_SCENE: {'action': self.__showBoxOnScene},
         self.BoxActions.PLAY_RECEIVE_BOX_ANIMATION: {'action': self.__playReceiveBoxAnimation,
                                                      'delay': 0.5},
         self.BoxActions.PLAY_START_OPEN_BOX_ANIMATION: {'action': self.__playStartOpenBoxAnimation,
                                                         'delay': 0.1},
         self.BoxActions.PLAY_FINISH_OPEN_BOX_ANIMATION: {'action': self.__playFinishOpenBoxAnimation,
                                                          'delay': 0.5},
         self.BoxActions.CREATE_ENTITY: {'action': self.__createEntity},
         self.BoxActions.DESTROY_ENTITY: {'action': self.__destroyEntity},
         self.BoxActions.SWITCH_CAMERA_TO_BOX: {'action': self.__switchCameraToBox},
         self.BoxActions.SWITCH_CAMERA_TO_HANGAR: {'action': self.__switchCameraToHangar},
         self.BoxActions.SHOW_UI: {'action': self.__showUI},
         self.BoxActions.SHOW_UI_CONTENT: {'action': self.__showUIContent,
                                           'delay': 1.0},
         self.BoxActions.ENABLE_BOX_ONLY: {'action': self.__enableBoxOnly},
         self.BoxActions.ENABLE_ALL: {'action': self.__enableAll},
         self.BoxActions.OPEN_BOX_VIA_CHEST_STORAGE: {'action': self.__openBoxViaStorage},
         self.BoxActions.HIDE_UI: {'action': self.__hideUI},
         self.BoxActions.HIDE_UI_CONTENT: {'action': self.__hideUIContent}}
        self.__boxStateToActionMapping = {BoxStates.DEFAULT: (self.BoxActions.CREATE_ENTITY,),
         BoxStates.ON_SCENE: (self.BoxActions.SHOW_BOX_ON_SCENE, self.BoxActions.PLAY_RECEIVE_BOX_ANIMATION),
         BoxStates.START_OPENING: (self.BoxActions.PLAY_START_OPEN_BOX_ANIMATION,),
         BoxStates.FINISH_OPENING: (self.BoxActions.PLAY_FINISH_OPEN_BOX_ANIMATION,)}
        return

    def init(self):
        g_hangarSpace.onSpaceCreate += self.__onSpaceCreated
        g_hangarSpace.onSpaceDestroy += self.__onSpaceDestroyed

    def fini(self):
        CallbackDelayer.destroy(self)
        if self.__entityManager:
            self.__entityManager.destroy()
        self.__entityManager = None
        self.__actionsQueue = None
        self.__actionMapping = None
        self.__boxStateToActionMapping = None
        g_hangarSpace.onSpaceCreate -= self.__onSpaceCreated
        g_hangarSpace.onSpaceDestroy -= self.__onSpaceDestroyed
        return

    def __addEventListeners(self):
        self.newYearController.chestStorage.onItemOpened += self.__onChestOpenSuccess
        self.newYearController.chestStorage.onItemOpenError += self.__onChestOpenFail
        self.newYearController.chestStorage.onCountChanged += self.__onChestCountChanged
        self.newYearUIManager.buttonClickOpenChest += self.__openChestButtonClicked
        self.newYearUIManager.buttonClickOpenNextChest += self.__openNextChestButtonClicked
        self.newYearUIManager.buttonClickCloseChest += self.__closeChestButtonClicked
        self.newYearUIManager.chestViewDone += self.__chestViewDone
        self.customizableObjectsMgr.onNYSceneObjectsLoadedEvent += self.__onCustomizableObjectsLoaded

    def __removeEventListeners(self):
        self.newYearController.chestStorage.onItemOpened -= self.__onChestOpenSuccess
        self.newYearController.chestStorage.onItemOpenError -= self.__onChestOpenFail
        self.newYearController.chestStorage.onCountChanged -= self.__onChestCountChanged
        self.newYearUIManager.buttonClickOpenChest -= self.__openChestButtonClicked
        self.newYearUIManager.buttonClickOpenNextChest -= self.__openNextChestButtonClicked
        self.newYearUIManager.buttonClickCloseChest -= self.__closeChestButtonClicked
        self.newYearUIManager.chestViewDone -= self.__chestViewDone
        self.customizableObjectsMgr.onNYSceneObjectsLoadedEvent -= self.__onCustomizableObjectsLoaded

    def receiveBox(self, isNew=True):
        if not self.__isAnyBoxAvailable:
            return
        self.__addAction(self.BoxActions.HIDE_UI_CONTENT)
        self.__addAction(self.BoxActions.CREATE_ENTITY)
        self.__addAction(self.BoxActions.PLAY_RECEIVE_BOX_ANIMATION if isNew else self.BoxActions.SHOW_BOX_ON_SCENE)
        self.__addAction(self.BoxActions.ENABLE_BOX_ONLY)

    def openBox(self):
        self.__addAction(self.BoxActions.SWITCH_CAMERA_TO_BOX)
        self.__addAction(self.BoxActions.SHOW_UI)
        self.__addAction(self.BoxActions.OPEN_BOX_VIA_CHEST_STORAGE)
        self.__addAction(self.BoxActions.PLAY_START_OPEN_BOX_ANIMATION)

    def boxDone(self):
        self.__addAction(self.BoxActions.SWITCH_CAMERA_TO_HANGAR)
        self.__addAction(self.BoxActions.HIDE_UI)
        self.__addAction(self.BoxActions.DESTROY_ENTITY)
        if not self.__isAnyBoxAvailable:
            self.__addAction(self.BoxActions.ENABLE_ALL)

    def __onSpaceCreated(self):
        self.__addEventListeners()
        self.__actionsQueue = list()
        self.__currentAction = None
        self.__isInUI = False
        self.__entityManager = self._EntityManager()
        self.__entityManager.clickedCallback = self.__onEntityClicked
        self.__entityManager.stateChangedCallback = self.__onEntityStateChanged
        self.__entityManager.doneCallback = self.__onEntityDone
        if self.__isAnyBoxAvailable:
            self.receiveBox(False)
        return

    def __onSpaceDestroyed(self):
        self.__removeEventListeners()
        self.__actionsQueue = None
        self.__currentAction = None
        if self.__entityManager:
            self.__entityManager.destroy()
        self.__entityManager = None
        self.clearCallbacks()
        return

    def __openChestButtonClicked(self):
        self.openBox()

    def __openNextChestButtonClicked(self):
        if not self.__entityManager.isDone:
            return
        if self.__isAnyBoxAvailable:
            self.__addAction(self.BoxActions.DESTROY_ENTITY)
            self.receiveBox(True)
            self.openBox()
        else:
            self.__closeChestButtonClicked()

    def __closeChestButtonClicked(self):
        self.__actionsQueue = list()
        self.__currentAction = None
        self.boxDone()
        if self.__isAnyBoxAvailable:
            self.receiveBox(False)
        return

    def __chestViewDone(self):
        if self.__isInUI:
            self.__closeChestButtonClicked()

    def __onCustomizableObjectsLoaded(self):
        if self.__isAnyBoxAvailable:
            self.__addAction(self.BoxActions.ENABLE_BOX_ONLY)

    def __onChestOpenSuccess(self, id, bonuses):
        isInOpenAnimation = self.__currentAction == self.BoxActions.PLAY_START_OPEN_BOX_ANIMATION
        if self.__entityManager.isReadyToFinishBoxAnimation or isInOpenAnimation:
            self.__addAction(self.BoxActions.PLAY_FINISH_OPEN_BOX_ANIMATION)
            self.__addAction(self.BoxActions.SHOW_UI_CONTENT, bonuses)

    def __onChestOpenFail(self, id):
        self.boxDone()

    def __onChestCountChanged(self, addedAmout, _, __):
        if addedAmout > 0 and not self.__entityManager.isOnScene and not self.__isAnyActionQueued:
            self.receiveBox(True)

    def __onEntityStateChanged(self, prevState, state):
        if prevState != state and self.__stateFitAction(state):
            self.__actionDone()

    def __stateFitAction(self, state):
        actions = self.__boxStateToActionMapping.get(state, None)
        return actions and self.__currentAction in actions

    def __onEntityClicked(self):
        self.openBox()

    def __onEntityDone(self):
        if self.__currentAction == self.BoxActions.DESTROY_ENTITY:
            self.__actionDone()

    def __addAction(self, action, *args):
        if self.__actionsQueue is None:
            return
        else:
            self.__actionsQueue.append((action, args))
            self.__doAction()
            return

    def __doAction(self):
        if self.__currentAction or not self.__actionsQueue:
            return
        self.__currentAction, args = self.__actionsQueue.pop(0)
        actionInfo = self.__actionMapping[self.__currentAction]
        delay = actionInfo.get('delay', 0.0)
        self.delayCallback(delay, partial(actionInfo['action'], self.__actionDone, *args))

    def __actionDone(self):
        self.__currentAction = None
        self.__doAction()
        return

    def __showBoxOnScene(self, _=None, *args):
        if not self.__entityManager.receiveBox(False):
            self.delayCallback(0.0, self.__showBoxOnScene)

    def __playReceiveBoxAnimation(self, _=None, *args):
        if not self.__entityManager.receiveBox(True):
            self.delayCallback(0.0, self.__playReceiveBoxAnimation)

    def __playStartOpenBoxAnimation(self, _=None, *args):
        if not self.__entityManager.startOpenBox():
            self.delayCallback(0.0, self.__playStartOpenBoxAnimation)

    def __playFinishOpenBoxAnimation(self, _=None, *args):
        if self.__entityManager.finishOpenBox():
            NYSoundEvents.playSound(NYSoundEvents.LOOTBOX_START_FINISH_OPEN)
        else:
            self.delayCallback(0.0, self.__playFinishOpenBoxAnimation)

    def __createEntity(self, callback, *args):
        self.__entityManager.createEntity(callback)

    def __destroyEntity(self, callback, *args):
        if self.__entityManager.isOnScene:
            self.__entityManager.hideBox()
        else:
            callback()

    def __switchCameraToBox(self, callback, *args):

        def callbackWrapper():
            g_eventBus.handleEvent(events.NewYearEvent(events.NewYearEvent.CLOSE_LEVEL_UP_VIEW), scope=EVENT_BUS_SCOPE.LOBBY)
            callback()

        isSwitchCameraAction = self.__currentAction == self.BoxActions.SWITCH_CAMERA_TO_HANGAR
        if self.customizableObjectsMgr.state != self.__entityManager.anchorName or isSwitchCameraAction:
            self.customizableObjectsMgr.switchTo(self.__entityManager.anchorName, callbackWrapper)
        else:
            callbackWrapper()

    def __switchCameraToHangar(self, callback, *args):
        self.customizableObjectsMgr.switchTo(None, callback)
        return

    def __showUI(self, callback, *args):
        NYSoundEvents.playSound(NYSoundEvents.LOOTBOX_CAMERA_SWITCH)
        if not self.__isInUI:
            g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_NY_CHESTS, ctx={'callback': callback}), EVENT_BUS_SCOPE.LOBBY)
            self.__isInUI = True
        else:
            callback()

    def __showUIContent(self, callback, *args):
        NYSoundEvents.playSound(NYSoundEvents.LOOTBOX_SHOW_UI_CONTENT)
        self.newYearUIManager.onChestGiftsLoaded(*args)
        callback()

    def __enableBoxOnly(self, callback, *args):
        self.customizableObjectsMgr.enableAllSelectableEntities(False)
        self.__entityManager.enableEntity()
        callback()

    def __enableAll(self, callback, *args):
        self.customizableObjectsMgr.enableAllSelectableEntities(True)
        callback()

    def __openBoxViaStorage(self, callback, *args):
        self.newYearController.chestStorage.open()
        callback()

    def __hideUI(self, callback, *args):
        self.__isInUI = False
        self.newYearUIManager.onChestDone()
        callback()

    def __hideUIContent(self, callback, *args):
        self.newYearUIManager.onChestGiftsDone()
        callback()
