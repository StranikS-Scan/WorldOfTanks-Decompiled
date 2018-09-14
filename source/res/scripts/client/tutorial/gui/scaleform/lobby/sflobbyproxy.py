# Embedded file name: scripts/client/tutorial/gui/Scaleform/lobby/SfLobbyProxy.py
from debug_utils import LOG_CURRENT_EXCEPTION
from gui import SystemMessages
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.framework import AppRef, g_entitiesFactories, ViewTypes
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from messenger.m_constants import PROTO_TYPE, SCH_CLIENT_MSG_TYPE
from messenger.proto import proto_getter
from tutorial import LOG_DEBUG, LOG_ERROR, LOG_WARNING
from tutorial.gui import GUIProxy, GUI_EFFECT_NAME
from tutorial.gui.Scaleform.items_manager import ItemsManager
from tutorial.gui.Scaleform.TutorialConfig import TutorialConfig

class SfLobbyProxy(GUIProxy, AppRef):
    __dispatcher = None

    def __init__(self, effectPlayer):
        super(SfLobbyProxy, self).__init__()
        self.config = TutorialConfig()
        self.items = ItemsManager()
        self.effects = effectPlayer

    @proto_getter(PROTO_TYPE.BW)
    def proto(self):
        return None

    def getViewSettings(self):
        raise Exception, 'Routine getViewSettings must be implemented'

    def init(self):
        result = False
        if self.app is not None:
            loader = self.app.loaderManager
            loader.onViewLoadInit += self.__onViewLoadInit
            loader.onViewLoadError += self.__onViewLoadError
            addSettings = g_entitiesFactories.addSettings
            try:
                for settings in self.getViewSettings():
                    addSettings(settings)

                self.app.varsManager.setTutorialRunning(True)
                result = True
            except Exception:
                LOG_CURRENT_EXCEPTION()

        dispatcher = self.getDispatcher()
        if dispatcher is not None:
            dispatcher.findGUI()
            self.onGUILoaded()
        return result

    def fini(self, isItemsRevert = True):
        self.eManager.clear()
        self.effects.stopAll()
        if self.app is not None:
            loader = self.app.loaderManager
            loader.onViewLoadInit -= self.__onViewLoadInit
            loader.onViewLoadError -= self.__onViewLoadError
            removeSettings = g_entitiesFactories.removeSettings
            for settings in self.getViewSettings():
                removeSettings(settings.alias)

            self.app.varsManager.setTutorialRunning(False)
        return

    def clear(self):
        self.clearChapterInfo()
        self.effects.stopAll()

    def lock(self):
        self.showWaiting('update-scene', isSingle=True)

    def release(self):
        self.hideWaiting('update-scene')

    def loadConfig(self, filePath):
        self.config.loadConfig(filePath)

    def reloadConfig(self, filePath):
        self.config.reloadConfig(filePath)

    def getSceneID(self):
        sceneID = None
        container = self.app.containerManager.getContainer(ViewTypes.LOBBY_SUB)
        if container is not None:
            pyView = container.getView()
            if pyView is not None:
                sceneID = self.config.getSceneID(pyView.settings.alias)
        LOG_DEBUG('GUI.getSceneID', sceneID)
        return sceneID

    def goToScene(self, sceneID):
        method = self.config.getGoToSceneMethod(sceneID)
        if method:
            g_eventBus.handleEvent(events.LoadViewEvent(method), scope=EVENT_BUS_SCOPE.LOBBY)

    def playEffect(self, effectName, args, itemRef = None, containerRef = None):
        return self.effects.play(effectName, args)

    def stopEffect(self, effectName, effectID):
        self.effects.stop(effectName, effectID)

    def showWaiting(self, messageID, isSingle = False):
        Waiting.show('tutorial-{0:>s}'.format(messageID), isSingle=isSingle)

    def hideWaiting(self, messageID = None):
        if messageID is not None:
            Waiting.hide('tutorial-{0:>s}'.format(messageID))
        else:
            Waiting.close()
        return

    def showMessage(self, text, lookupType = None):
        guiType = None
        if type is not None:
            guiType = SystemMessages.SM_TYPE.lookup(lookupType)
        if guiType is None:
            guiType = SystemMessages.SM_TYPE.Information
        SystemMessages.pushMessage(text, type=guiType)
        return

    def showI18nMessage(self, key, *args, **kwargs):
        guiType = None
        if 'type' in kwargs:
            guiType = SystemMessages.SM_TYPE.lookup(kwargs['type'])
        if guiType is None:
            guiType = SystemMessages.SM_TYPE.Information
        kwargs['type'] = guiType
        SystemMessages.pushI18nMessage(key, *args, **kwargs)
        return

    def showServiceMessage(self, data, msgTypeName):
        msgType, messageID = (None, 0)
        if msgTypeName is not None:
            msgType = getattr(SCH_CLIENT_MSG_TYPE, msgTypeName, None)
        if msgType is None:
            LOG_ERROR('Message type not found', msgType)
        if self.proto:
            messageID = self.proto.serviceChannel.pushClientMessage(data, msgType)
        return messageID

    def isGuiDialogDisplayed(self):
        container = self.app.containerManager.getContainer(ViewTypes.TOP_WINDOW)
        result = False
        if container is not None:
            dialogCount = container.getViewCount(isModal=True)
            if dialogCount > 0:
                if self.effects.isStillRunning(GUI_EFFECT_NAME.SHOW_DIALOG):
                    dialogCount -= 1
                result = dialogCount > 0
        return result

    def isTutorialDialogDisplayed(self, dialogID):
        return self.effects.isStillRunning(GUI_EFFECT_NAME.SHOW_DIALOG, effectID=dialogID)

    def isTutorialWindowDisplayed(self, windowID):
        return self.effects.isStillRunning(GUI_EFFECT_NAME.SHOW_WINDOW, effectID=windowID)

    def findItem(self, itemID, criteria):
        if criteria is None:
            item = self.config.getItem(itemID)
            valuePath = None
            value = None
        else:
            parentID, valuePath, value = criteria
            item = self.config.getItem(parentID)
        return self.items.findTargetByCriteria(item['path'], valuePath, value)

    @classmethod
    def setDispatcher(cls, dispatcher):
        cls.__dispatcher = dispatcher

    @classmethod
    def getDispatcher(cls):
        return cls.__dispatcher

    def setChapterInfo(self, title, description):
        dispatcher = self.getDispatcher()
        if dispatcher is not None:
            dispatcher.setChapterInfo(title, description)
        else:
            LOG_ERROR('Tutorial dispatcher is not defined.')
        return

    def clearChapterInfo(self):
        dispatcher = self.getDispatcher()
        if dispatcher is not None:
            dispatcher.clearChapterInfo()
        else:
            LOG_ERROR('Tutorial dispatcher is not defined.')
        return

    def setTrainingRestartMode(self):
        dispatcher = self.getDispatcher()
        if dispatcher is not None:
            dispatcher.setTrainingRestartMode()
        else:
            LOG_ERROR('Tutorial dispatcher is not defined.')
        return

    def setTrainingRunMode(self):
        dispatcher = self.getDispatcher()
        if dispatcher is not None:
            dispatcher.setTrainingRunMode()
        else:
            LOG_ERROR('Tutorial dispatcher is not defined.')
        return

    def setPlayerXPLevel(self, level):
        dispatcher = self.getDispatcher()
        if dispatcher is not None:
            dispatcher.setPlayerXPLevel(level)
        else:
            LOG_ERROR('Tutorial dispatcher is not defined.')
        return

    def __onViewLoadInit(self, pyEntity):
        if pyEntity.settings.type is ViewTypes.LOBBY_SUB:
            pageName = pyEntity.settings.alias
            sceneID = self.config.getSceneID(pageName)
            LOG_DEBUG('GUI.onPageChanging', sceneID)
            if sceneID is None:
                self.clear()
                LOG_WARNING('Scene alias not found, page:', pageName)
            else:
                self.effects.stopAll()
                self.onPageChanging(sceneID)
        return

    def __onViewLoadError(self, name, msg, item):
        if item is not None:
            effectID = item.name
            for effectName in [GUI_EFFECT_NAME.SHOW_DIALOG, GUI_EFFECT_NAME.SHOW_WINDOW]:
                if self.effects.isStillRunning(effectName, effectID=effectID):
                    self.effects.stop(effectName, effectID=effectID)
                    break

        return
