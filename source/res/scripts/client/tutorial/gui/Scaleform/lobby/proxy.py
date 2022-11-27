# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/gui/Scaleform/lobby/proxy.py
import weakref
from debug_utils import LOG_CURRENT_EXCEPTION
from frameworks.wulf import WindowLayer
from gui import SystemMessages
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.framework import g_entitiesFactories
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.TUTORIAL_TRIGGER_TYPES import TUTORIAL_TRIGGER_TYPES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from helpers.statistics import HANGAR_LOADING_STATE
from messenger.m_constants import PROTO_TYPE, SCH_CLIENT_MSG_TYPE
from messenger.proto import proto_getter
from skeletons.helpers.statistics import IStatisticsCollector
from skeletons.tutorial import ITutorialLoader
from tutorial.data.events import ClickEvent, ClickOutsideEvent, EscEvent, EnableEvent, DisableEvent
from tutorial.data.events import EnabledChangeEvent, VisibleChangeEvent
from tutorial.doc_loader import gui_config
from tutorial.gui import GUIProxy, GUI_EFFECT_NAME
from tutorial.gui.commands import GUICommandsFactory
from tutorial.gui.Scaleform.items_manager import ItemsManager
from tutorial.gui.Scaleform.effects_player import GUIEffectScope
from tutorial.logger import LOG_DEBUG, LOG_ERROR, LOG_WARNING
from gui.app_loader import sf_lobby
from soft_exception import SoftException
_TEvent = events.TutorialEvent
_AppEvent = events.AppLifeCycleEvent
_EventClassByTriggerType = {TUTORIAL_TRIGGER_TYPES.CLICK_TYPE: (ClickEvent, 'Player has clicked'),
 TUTORIAL_TRIGGER_TYPES.CLICK_OUTSIDE_TYPE: (ClickOutsideEvent, 'Player has clicked outside'),
 TUTORIAL_TRIGGER_TYPES.ESCAPE: (EscEvent, 'Player has pressed ESC'),
 TUTORIAL_TRIGGER_TYPES.ENABLED: (EnableEvent, 'Button has been enabled'),
 TUTORIAL_TRIGGER_TYPES.DISABLED: (DisableEvent, 'Button has been disabled'),
 TUTORIAL_TRIGGER_TYPES.VISIBLE_CHANGE: (VisibleChangeEvent, 'Component visibility has been changed'),
 TUTORIAL_TRIGGER_TYPES.ENABLED_CHANGE: (EnabledChangeEvent, 'Component enables has been changed')}
CLIENT_CHECKED_TRIGGERS = frozenset([TUTORIAL_TRIGGER_TYPES.VISIBLE_CHANGE, TUTORIAL_TRIGGER_TYPES.ENABLED_CHANGE])

class SfLobbyProxy(GUIProxy):
    statsCollector = dependency.descriptor(IStatisticsCollector)
    __tutorialLoader = dependency.descriptor(ITutorialLoader)

    def __init__(self, effectPlayer):
        super(SfLobbyProxy, self).__init__()
        self.config = None
        self.items = ItemsManager()
        self.effects = effectPlayer
        self._commands = GUICommandsFactory()
        return

    @sf_lobby
    def app(self):
        return None

    @proto_getter(PROTO_TYPE.BW)
    def proto(self):
        return None

    def getViewSettings(self):
        raise SoftException('Routine getViewSettings must be implemented')

    def getViewsAliases(self):
        raise SoftException('Routine getViewsAliases must be implemented')

    def invokeCommand(self, command):
        self._commands.invoke(None, command)
        return

    def init(self):
        addListener = g_eventBus.addListener
        addListener(_AppEvent.INITIALIZED, self.__onAppInitialized, scope=EVENT_BUS_SCOPE.GLOBAL)
        addListener(_TEvent.ON_COMPONENT_FOUND, self.__onComponentFound, scope=EVENT_BUS_SCOPE.GLOBAL)
        addListener(_TEvent.ON_COMPONENT_LOST, self.__onComponentLost, scope=EVENT_BUS_SCOPE.GLOBAL)
        addListener(_TEvent.ON_TRIGGER_ACTIVATED, self.__onTriggerActivated, scope=EVENT_BUS_SCOPE.GLOBAL)
        addListener(_TEvent.ON_ANIMATION_COMPLETE, self.__onAnimationComplete, scope=EVENT_BUS_SCOPE.GLOBAL)
        if self.app is not None and self.app.initialized:
            self.__load()
        return True

    def fini(self):
        self._commands = None
        self.eManager.clear()
        self.effects.stopAll()
        self.effects.clear()
        if self.app is not None and self.app.initialized:
            self.__unload()
        removeListener = g_eventBus.removeListener
        removeListener(_AppEvent.INITIALIZED, self.__onAppInitialized, scope=EVENT_BUS_SCOPE.GLOBAL)
        removeListener(_TEvent.ON_COMPONENT_FOUND, self.__onComponentFound, scope=EVENT_BUS_SCOPE.GLOBAL)
        removeListener(_TEvent.ON_COMPONENT_LOST, self.__onComponentLost, scope=EVENT_BUS_SCOPE.GLOBAL)
        removeListener(_TEvent.ON_TRIGGER_ACTIVATED, self.__onTriggerActivated, scope=EVENT_BUS_SCOPE.GLOBAL)
        removeListener(_TEvent.ON_ANIMATION_COMPLETE, self.__onAnimationComplete, scope=EVENT_BUS_SCOPE.GLOBAL)
        return

    def clear(self):
        self.clearChapterInfo()
        self.effects.stopAll()

    def lock(self):
        self.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.START_LOADING_TUTORIAL)
        self.showWaiting('update-scene', isSingle=True)

    def release(self):
        self.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.FINISH_LOADING_TUTORIAL, showSummaryNow=True)
        self.hideWaiting('update-scene')

    def loadConfig(self, filePath):
        self.config = gui_config.readConfig(filePath)

    def reloadConfig(self, filePath):
        self.config = gui_config.readConfig(filePath, forced=True)

    def getSceneID(self):
        sceneID = None
        container = self.app.containerManager.getContainer(WindowLayer.SUB_VIEW)
        if container is not None:
            pyView = container.getView()
            if pyView is not None:
                sceneID = self.config.getSceneID(pyView.alias)
        LOG_DEBUG('GUI.getSceneID', sceneID)
        return sceneID

    def goToScene(self, sceneID):
        event = self.config.getSceneEvent(sceneID)
        if event:
            g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(event)), scope=EVENT_BUS_SCOPE.LOBBY)

    def isViewPresent(self, layer, criteria):
        return self.__findView(layer, criteria) is not None

    def closeView(self, layer, criteria):
        view = self.__findView(layer, criteria)
        if view is not None:
            view.destroy()
        return

    def playEffect(self, effectName, args):
        return self.effects.play(effectName, args)

    def stopEffect(self, effectName, effectID, effectSubType=None):
        self.effects.stop(effectName, effectID, effectSubType)

    def isEffectRunning(self, effectName, effectID=None, effectSubType=None):
        return self.effects.isStillRunning(effectName, effectID=effectID, effectSubType=effectSubType)

    def showWaiting(self, messageID, isSingle=False):
        Waiting.show('tutorial-{0:>s}'.format(messageID), isSingle=isSingle)

    def hideWaiting(self, messageID=None):
        if messageID is not None:
            Waiting.hide('tutorial-{0:>s}'.format(messageID))
        else:
            Waiting.close()
        return

    def showMessage(self, text, lookupType=None):
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
            self.app.loadView(SFViewLoadParams(alias, windowID), content)

    def getItemsOnScene(self):
        return self.__tutorialLoader.gui.getFoundComponentsIDs()

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
            container = app.containerManager.getContainer(WindowLayer.TOP_WINDOW)
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

    def __load(self):
        proxy = weakref.proxy(self.app)
        for _, effect in self.effects.iterEffects():
            effect.setApplication(proxy)

        loader = self.app.loaderManager
        loader.onViewLoadInit += self.__onViewLoadInit
        loader.onViewLoaded += self.__onViewLoaded
        loader.onViewLoadError += self.__onViewLoadError
        addSettings = g_entitiesFactories.addSettings
        try:
            for settings in self.getViewSettings():
                addSettings(settings)

        except Exception:
            LOG_CURRENT_EXCEPTION()

        self.onGUILoaded()

    def __unload(self):
        loader = self.app.loaderManager
        loader.onViewLoadInit -= self.__onViewLoadInit
        loader.onViewLoaded -= self.__onViewLoaded
        loader.onViewLoadError -= self.__onViewLoadError
        removeSettings = g_entitiesFactories.removeSettings
        for settings in self.getViewSettings():
            removeSettings(settings.alias)

    def __onAppInitialized(self, event):
        if event.ns == APP_NAME_SPACE.SF_LOBBY:
            self.__load()

    def __onViewLoadInit(self, pyEntity):
        if pyEntity.layer == WindowLayer.SUB_VIEW:
            pageName = pyEntity.alias
            sceneID = self.config.getSceneID(pageName)
            prevSceneID = self.getSceneID()
            LOG_DEBUG('GUI.onPageChanging', prevSceneID, '->', sceneID)
            if prevSceneID is not None:
                self.effects.cancel(GUIEffectScope.SCENE, prevSceneID)
            if sceneID is None:
                self.clear()
                LOG_WARNING('Scene alias not found, page:', pageName)
            else:
                self.onPageChanging(sceneID)
        return

    def __onViewLoaded(self, pyEntity, _):
        if pyEntity.layer == WindowLayer.SUB_VIEW:
            pageName = pyEntity.alias
            sceneID = self.config.getSceneID(pageName)
            LOG_DEBUG('GUI.onPageReady', sceneID)
            if sceneID is not None:
                self.onPageReady(sceneID)
        self.onViewLoaded(pyEntity.alias)
        pyEntity.onDispose += self.__onViewDisposed
        return

    def __onViewDisposed(self, pyEntity):
        pyEntity.onDispose -= self.__onViewDisposed
        self.onViewDisposed(pyEntity.alias)

    def __onViewLoadError(self, key, msg, item):
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
        self.effects.cancel(GUIEffectScope.COMPONENT, itemID)
        self.onItemLost(itemID)

    def __onTriggerActivated(self, event):
        if not event.targetID:
            LOG_ERROR('Key targetID is not defined in the event ON_TRIGGER_ACTIVATED')
            return
        elif not event.settingsID:
            LOG_ERROR('Key settingsID is not defined in the event ON_TRIGGER_ACTIVATED')
            return
        else:
            triggerType = event.settingsID
            componentID = event.targetID
            eventClass, logMessage = _EventClassByTriggerType.get(triggerType, (None, None))
            if eventClass is not None:
                LOG_DEBUG(logMessage, componentID)
                self.onGUIInput(eventClass(componentID))
            else:
                LOG_ERROR('Type of event is not supported', triggerType)
            return

    def __onAnimationComplete(self, event):
        if not event.targetID:
            LOG_ERROR('Key targetID is not defined in event ON_ANIMATION_COMPLETE')
            return
        if not event.settingsID:
            LOG_ERROR('Key settingsID is not defined in event ON_ANIMATION_COMPLETE')
            return
        componentID, animID = event.targetID, event.settingsID
        self.stopEffect(GUI_EFFECT_NAME.PLAY_ANIMATION, componentID, animID)

    def __findView(self, layer, criteria):
        app = self.app
        if app is None or app.containerManager is None:
            return
        else:
            container = app.containerManager.getContainer(layer)
            return None if container is None else container.getView(criteria)
