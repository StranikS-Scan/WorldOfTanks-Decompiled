# Embedded file name: scripts/client/tutorial/gui/Scaleform/lobby/proxy.py
from debug_utils import LOG_CURRENT_EXCEPTION
from gui import SystemMessages
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.framework import g_entitiesFactories, ViewTypes
from gui.Scaleform.genConsts.TUTORIAL_TRIGGER_TYPES import TUTORIAL_TRIGGER_TYPES
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from messenger.m_constants import PROTO_TYPE, SCH_CLIENT_MSG_TYPE
from messenger.proto import proto_getter
from tutorial import LOG_DEBUG, LOG_ERROR, LOG_WARNING
from tutorial.data.events import ClickEvent, ClickOutsideEvent, EscEvent
from tutorial.doc_loader import gui_config
from tutorial.gui import GUIProxy, GUI_EFFECT_NAME
from tutorial.gui.Scaleform.items_manager import ItemsManager
from gui.app_loader.decorators import sf_lobby
_TEvent = events.TutorialEvent

class SfLobbyProxy(GUIProxy):

    def __init__(self, effectPlayer):
        super(SfLobbyProxy, self).__init__()
        self.config = None
        self.items = ItemsManager()
        self.effects = effectPlayer
        return

    @sf_lobby
    def app(self):
        return None

    @proto_getter(PROTO_TYPE.BW)
    def proto(self):
        return None

    def getViewSettings(self):
        raise Exception, 'Routine getViewSettings must be implemented'

    def getViewsAliases(self):
        raise Exception, 'Routine getViewsAliases must be implemented'

    def init(self):
        result = False
        addListener = g_eventBus.addListener
        addListener(_TEvent.ON_COMPONENT_FOUND, self.__onComponentFound, scope=EVENT_BUS_SCOPE.GLOBAL)
        addListener(_TEvent.ON_COMPONENT_LOST, self.__onComponentLost, scope=EVENT_BUS_SCOPE.GLOBAL)
        addListener(_TEvent.ON_TRIGGER_ACTIVATED, self.__onTriggerActivated, scope=EVENT_BUS_SCOPE.GLOBAL)
        if self.app is not None:
            loader = self.app.loaderManager
            loader.onViewLoadInit += self.__onViewLoadInit
            loader.onViewLoadError += self.__onViewLoadError
            addSettings = g_entitiesFactories.addSettings
            try:
                for settings in self.getViewSettings():
                    addSettings(settings)

                result = True
            except Exception:
                LOG_CURRENT_EXCEPTION()

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

        removeListener = g_eventBus.removeListener
        removeListener(_TEvent.ON_COMPONENT_FOUND, self.__onComponentFound, scope=EVENT_BUS_SCOPE.GLOBAL)
        removeListener(_TEvent.ON_COMPONENT_LOST, self.__onComponentLost, scope=EVENT_BUS_SCOPE.GLOBAL)
        removeListener(_TEvent.ON_TRIGGER_ACTIVATED, self.__onTriggerActivated, scope=EVENT_BUS_SCOPE.GLOBAL)
        return

    def clear(self):
        self.clearChapterInfo()
        self.effects.stopAll()

    def lock(self):
        self.showWaiting('update-scene', isSingle=True)

    def release(self):
        self.hideWaiting('update-scene')

    def loadConfig(self, filePath):
        self.config = gui_config.readConfig(filePath)

    def reloadConfig(self, filePath):
        self.config = gui_config.readConfig(filePath, forced=True)

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
        event = self.config.getSceneEvent(sceneID)
        if event:
            g_eventBus.handleEvent(events.LoadViewEvent(event), scope=EVENT_BUS_SCOPE.LOBBY)

    def playEffect(self, effectName, args, itemRef = None, containerRef = None):
        return self.effects.play(effectName, args)

    def stopEffect(self, effectName, effectID):
        self.effects.stop(effectName, effectID)

    def isEffectRunning(self, effectName, effectID = None):
        return self.effects.isStillRunning(effectName, effectID=effectID)

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
        if 'msgType' in kwargs:
            guiType = SystemMessages.SM_TYPE.lookup(kwargs['msgType'])
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

    def showAwardWindow(self, windowID, windowType, content):
        aliasMap = self.getViewsAliases()
        if windowType in aliasMap:
            alias = aliasMap[windowType]
            self.app.loadView(alias, windowID, content)

    def getItemsOnScene(self):
        if self.app is not None and self.app.tutorialManager is not None:
            return self.app.tutorialManager.getFoundComponentsIDs()
        else:
            return set()
            return

    def clearScene(self):
        app = self.app
        if app is None or app.containerManager is None:
            return
        else:
            app.containerManager.clear()
            return

    def isGuiDialogDisplayed(self):
        app = self.app
        if app is None or app.containerManager is None:
            return False
        else:
            container = app.containerManager.getContainer(ViewTypes.TOP_WINDOW)
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
            for effectName in (GUI_EFFECT_NAME.SHOW_DIALOG, GUI_EFFECT_NAME.SHOW_WINDOW):
                if self.effects.isStillRunning(effectName, effectID=effectID):
                    self.effects.stop(effectName, effectID=effectID)
                    break

        return

    def __onComponentFound(self, event):
        if not event.targetID:
            LOG_ERROR('Key targetID is not defined in the event ON_COMPONENT_FOUND')
            return
        self.onItemFound(event.targetID)

    def __onComponentLost(self, event):
        if not event.targetID:
            LOG_ERROR('Key targetID is not defined in the event ON_COMPONENT_LOST')
            return
        itemID = event.targetID
        self.effects.cancel(GUI_EFFECT_NAME.SHOW_HINT, itemID)
        self.onItemLost(itemID)

    def __onTriggerActivated(self, event):
        if not event.targetID:
            LOG_ERROR('Key targetID is not defined in the event ON_TRIGGER_ACTIVATED')
            return
        if not event.settingsID:
            LOG_ERROR('Key settingsID is not defined in the event ON_TRIGGER_ACTIVATED')
            return
        triggerType = event.settingsID
        componentID = event.targetID
        if triggerType == TUTORIAL_TRIGGER_TYPES.CLICK_TYPE:
            LOG_DEBUG('Player has clicked', componentID)
            self.onGUIInput(ClickEvent(componentID))
        elif triggerType == TUTORIAL_TRIGGER_TYPES.CLICK_OUTSIDE_TYPE:
            LOG_DEBUG('Player has clicked outside', componentID)
            self.onGUIInput(ClickOutsideEvent(componentID))
        elif triggerType == TUTORIAL_TRIGGER_TYPES.ESCAPE:
            LOG_DEBUG('Player has pressed ESC', componentID)
            self.onGUIInput(EscEvent(componentID))
        else:
            LOG_ERROR('Type of event is not supported', triggerType)
