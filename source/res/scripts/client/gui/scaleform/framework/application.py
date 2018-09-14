# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/application.py
import weakref
from account_helpers.settings_core.SettingsCore import g_settingsCore
from account_helpers.settings_core import settings_constants
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui import g_guiResetters, g_repeatKeyHandlers, GUI_CTRL_MODE_FLAG
from gui.Scaleform import SCALEFORM_SWF_PATH_V3
from gui.Scaleform.Flash import Flash
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.abstract.ApplicationMeta import ApplicationMeta
from gui.shared.events import AppLifeCycleEvent, GameEvent
from gui.shared import EVENT_BUS_SCOPE

class DAAPIRootBridge(object):
    __slots__ = ('__pyScript', '__rootPath', '__initCallback', '__isInited')

    def __init__(self, rootPath='root', initCallback='registerApplication'):
        self.__pyScript = None
        self.__rootPath = rootPath
        self.__initCallback = initCallback
        self.__isInited = False
        return

    def clear(self):
        self.__isInited = False
        if self.__pyScript:
            self.__pyScript.removeExternalCallback(self.__initCallback, self._onSWFInited)
            self.__pyScript.destroy()
            self.__pyScript = None
        return

    def setPyScript(self, pyScript):
        self.__pyScript = pyScript
        self.__pyScript.addExternalCallback(self.__initCallback, self._onSWFInited)

    def _onSWFInited(self):
        if self.__isInited:
            return
        self.__isInited = True
        root = self.__pyScript.getMember(self.__rootPath)
        if root:
            self.__pyScript.setFlashObject(root)
            self.__pyScript.afterCreate()
        else:
            LOG_ERROR('Flash root is not found', self.__rootPath)


class SFApplication(Flash, ApplicationMeta):

    def __init__(self, swfName, appNS, daapiBridge=None):
        super(SFApplication, self).__init__(swfName, path=SCALEFORM_SWF_PATH_V3)
        self.proxy = weakref.proxy(self)
        self._loaderMgr = None
        self._containerMgr = None
        self._toolTip = None
        self._varsMgr = None
        self._soundMgr = None
        self._colorSchemeMgr = None
        self._eventLogMgr = None
        self._contextMgr = None
        self._popoverManager = None
        self._voiceChatMgr = None
        self._utilsMgr = None
        self._tweenMgr = None
        self._gameInputMgr = None
        self._cacheMgr = None
        self._tutorialMgr = None
        self._imageManager = None
        self.__initialized = False
        self.__ns = appNS
        self.__geShowed = False
        self.__firingsAfterInit = {}
        self.__guiCtrlModeFlags = GUI_CTRL_MODE_FLAG.CURSOR_DETACHED
        self.__aliasToLoad = []
        self.__daapiBridge = daapiBridge or DAAPIRootBridge()
        self.__daapiBridge.setPyScript(self.proxy)
        return

    @property
    def loaderManager(self):
        return self._loaderMgr

    @property
    def containerManager(self):
        return self._containerMgr

    @property
    def varsManager(self):
        return self._varsMgr

    @property
    def soundManager(self):
        return self._soundMgr

    @property
    def colorManager(self):
        return self._colorSchemeMgr

    @property
    def eventLogMgr(self):
        return self._eventLogMgr

    @property
    def contextMenuManager(self):
        return self._contextMgr

    @property
    def popoverManager(self):
        return self._popoverManager

    @property
    def voiceChatManager(self):
        return self._voiceChatMgr

    @property
    def utilsManager(self):
        return self._utilsMgr

    @property
    def gameInputManager(self):
        return self._gameInputMgr

    @property
    def cacheManager(self):
        return self._cacheMgr

    @property
    def tutorialManager(self):
        return self._tutorialMgr

    @property
    def waitingManager(self):
        return None

    @property
    def cursorMgr(self):
        return None

    @property
    def imageManager(self):
        return self._imageManager

    @property
    def initialized(self):
        return self.__initialized

    @property
    def appNS(self):
        return self.__ns

    @property
    def ctrlModeFlags(self):
        return self.__guiCtrlModeFlags

    def isModalViewShown(self):
        """ Is any modal window shown.
        For example, this routine is needed to avoid key handling in battle UI if modal window is shown.
        :return: return True if some modal window is shown.
        """
        manager = self._containerMgr
        if manager is not None:
            result = manager.isModalViewsIsExists()
        else:
            result = False
        return result

    def toggleEditor(self):
        from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
        from gui.shared.events import LoadViewEvent, GUIEditorEvent
        if not self.__geShowed:
            self.updateStage(1024, 768, 1)
            self.component.movie.x = 320
            self.component.movie.y = 100
            self.fireEvent(LoadViewEvent(VIEW_ALIAS.G_E_INSPECT_WINDOW), scope=EVENT_BUS_SCOPE.GLOBAL)
            self.__geShowed = True
        else:
            self.component.movie.x = 0
            self.component.movie.y = 0
            self.fireEvent(GUIEditorEvent(GUIEditorEvent.HIDE_GUIEditor), scope=EVENT_BUS_SCOPE.GLOBAL)
            self.__geShowed = False
            self.updateScale()

    def active(self, state):
        if state is not self.isActive:
            if state:
                self._setup()
            super(SFApplication, self).active(state)

    def afterCreate(self):
        self.fireEvent(AppLifeCycleEvent(self.__ns, AppLifeCycleEvent.INITIALIZING))
        LOG_DEBUG('[SFApplication] afterCreate', self.__ns)
        super(SFApplication, self).afterCreate()
        self._createManagers()
        self.as_registerManagersS()
        libraries = self._getRequiredLibraries()
        if libraries:
            self.as_setLibrariesListS(libraries)
        self._addGameCallbacks()
        self.addListener(GameEvent.CHANGE_APP_RESOLUTION, self.__onAppResolutionChanged, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.updateScale()
        while len(self.__aliasToLoad):
            alias, name, args, kwargs = self.__aliasToLoad.pop(0)
            self.loadView(alias, name, *args, **kwargs)

        self._loadCursor()
        self._loadWaiting()

    def beforeDelete(self):
        LOG_DEBUG('[SFApplication] beforeDelete', self.__ns)
        self.removeListener(GameEvent.CHANGE_APP_RESOLUTION, self.__onAppResolutionChanged, scope=EVENT_BUS_SCOPE.GLOBAL)
        self._removeGameCallbacks()
        if self._containerMgr is not None:
            self._containerMgr.destroy()
            self._containerMgr = None
        if self._loaderMgr is not None:
            self._loaderMgr.destroy()
            self._loaderMgr = None
        if self._cacheMgr is not None:
            self._cacheMgr.destroy()
            self._cacheMgr = None
        if self._contextMgr is not None:
            self._contextMgr.destroy()
            self._contextMgr = None
        if self._popoverManager is not None:
            self._popoverManager.destroy()
            self._popoverManager = None
        if self._soundMgr is not None:
            self._soundMgr.destroy()
            self._soundMgr = None
        if self._varsMgr is not None:
            self._varsMgr.destroy()
            self._varsMgr = None
        if self._toolTip is not None:
            self._toolTip.destroy()
            self._toolTip = None
        if self._colorSchemeMgr is not None:
            self._colorSchemeMgr.destroy()
            self._colorSchemeMgr = None
        if self._eventLogMgr is not None:
            self._eventLogMgr.destroy()
            self._eventLogMgr = None
        if self._tweenMgr is not None:
            self._tweenMgr.destroy()
            self._tweenMgr = None
        if self._voiceChatMgr is not None:
            self._voiceChatMgr.destroy()
            self._voiceChatMgr = None
        if self._gameInputMgr is not None:
            self._gameInputMgr.destroy()
            self._gameInputMgr = None
        if self._utilsMgr is not None:
            self._utilsMgr.destroy()
            self._utilsMgr = None
        if self._tutorialMgr is not None:
            self._tutorialMgr.destroy()
            self._tutorialMgr = None
        if self.__daapiBridge is not None:
            self.__daapiBridge.clear()
            self.__daapiBridge = None
        if self._imageManager is not None:
            self._imageManager.destroy()
            self._imageManager = None
        super(SFApplication, self).beforeDelete()
        self.proxy = None
        self.fireEvent(AppLifeCycleEvent(self.__ns, AppLifeCycleEvent.DESTROYED))
        return

    def loadView(self, newViewAlias, name=None, *args, **kwargs):
        if self._containerMgr:
            self._containerMgr.load(newViewAlias, name, *args, **kwargs)
        else:
            self.__aliasToLoad.append((newViewAlias,
             name,
             args,
             kwargs))

    def attachCursor(self, flags=GUI_CTRL_MODE_FLAG.GUI_ENABLED):
        if self.__guiCtrlModeFlags == flags:
            return
        else:
            self.__guiCtrlModeFlags = flags
            if self.cursorMgr is not None:
                self.cursorMgr.attachCursor(flags)
            return

    def detachCursor(self):
        self.__guiCtrlModeFlags = GUI_CTRL_MODE_FLAG.CURSOR_DETACHED
        if self.cursorMgr is not None:
            self.cursorMgr.detachCursor()
        return

    def syncCursor(self, flags=GUI_CTRL_MODE_FLAG.GUI_ENABLED):
        if self.__guiCtrlModeFlags == flags:
            return
        else:
            self.__guiCtrlModeFlags = flags
            if self.cursorMgr is not None:
                self.cursorMgr.syncCursor(flags=flags)
            return

    def setLoaderMgr(self, flashObject):
        self._loaderMgr.setFlashObject(flashObject)

    def setCacheMgr(self, flashObject):
        if self._cacheMgr and flashObject:
            self._cacheMgr.setFlashObject(flashObject)

    def setContainerMgr(self, flashObject):
        if self._containerMgr and flashObject:
            self._containerMgr.setFlashObject(flashObject)

    def setColorSchemeMgr(self, flashObject):
        if self._colorSchemeMgr and flashObject:
            self._colorSchemeMgr.setFlashObject(flashObject)

    def setEventLogMgr(self, flashObject):
        if self._eventLogMgr and flashObject:
            self._eventLogMgr.setFlashObject(flashObject)

    def setGlobalVarsMgr(self, flashObject):
        if self._varsMgr and flashObject:
            self._varsMgr.setFlashObject(flashObject)

    def setContextMenuMgr(self, flashObject):
        if self._contextMgr and flashObject:
            self._contextMgr.setFlashObject(flashObject)

    def setPopoverMgr(self, flashObject):
        if self._popoverManager and flashObject:
            self._popoverManager.setFlashObject(flashObject)

    def setSoundMgr(self, flashObject):
        if self._soundMgr and flashObject:
            self._soundMgr.setFlashObject(flashObject)

    def setTooltipMgr(self, flashObject):
        if self._toolTip and flashObject:
            self._toolTip.setFlashObject(flashObject)

    def setGameInputMgr(self, flashObject):
        if self._gameInputMgr and flashObject:
            self._gameInputMgr.setFlashObject(flashObject)

    def setVoiceChatMgr(self, flashObject):
        if self._voiceChatMgr and flashObject:
            self._voiceChatMgr.setFlashObject(flashObject)

    def setUtilsMgr(self, flashObject):
        if self._utilsMgr and flashObject:
            self._utilsMgr.setFlashObject(flashObject)

    def setTweenMgr(self, flashObject):
        if self._tweenMgr and flashObject:
            self._tweenMgr.setFlashObject(flashObject)

    def setTextMgr(self, flashObject):
        self._utilsMgr.registerTextManager(flashObject)

    def setTutorialMgr(self, flashObject):
        self._tutorialMgr.setFlashObject(flashObject)

    def setImageManager(self, flashObject):
        if self._imageManager and flashObject:
            self._imageManager.setFlashObject(flashObject)

    def onAsInitializationCompleted(self):
        self.__initialized = True
        self.fireEvent(AppLifeCycleEvent(self.__ns, AppLifeCycleEvent.INITIALIZED))

    def updateScale(self):
        index = g_settingsCore.getSetting(settings_constants.GRAPHICS.INTERFACE_SCALE)
        g_settingsCore.options.getSetting('interfaceScale').setSystemValue(index)

    def updateStage(self, w, h, scale):
        if not self.__geShowed:
            self.as_updateStageS(w, h, scale)

    def fireEventAfterInitialization(self, event, scope=EVENT_BUS_SCOPE.DEFAULT):
        if self.__initialized:
            self.fireEvent(event, scope=scope)
        else:
            self.__firingsAfterInit[event.eventType] = {'event': event,
             'scope': scope}

    def setBackgroundAlpha(self, value):
        self.movie.backgroundAlpha = value

    def _createManagers(self):
        self._loaderMgr = self._createLoaderManager()
        self._containerMgr = self._createContainerManager()
        self._toolTip = self._createToolTipManager()
        self._varsMgr = self._createGlobalVarsManager()
        self._soundMgr = self._createSoundManager()
        self._colorSchemeMgr = self._createColorSchemeManager()
        self._eventLogMgr = self._createEventLogMgr()
        self._contextMgr = self._createContextMenuManager()
        self._popoverManager = self._createPopoverManager()
        self._voiceChatMgr = self._createVoiceChatManager()
        self._utilsMgr = self._createUtilsManager()
        self._tweenMgr = self._createTweenManager()
        self._gameInputMgr = self._createGameInputManager()
        self._cacheMgr = self._createCacheManager()
        self._tutorialMgr = self._createTutorialManager()
        self._imageManager = self._createImageManager()

    def _addGameCallbacks(self):
        g_guiResetters.add(self.__onScreenResolutionChanged)
        g_repeatKeyHandlers.add(self.component.handleKeyEvent)

    def _removeGameCallbacks(self):
        g_guiResetters.discard(self.__onScreenResolutionChanged)
        g_repeatKeyHandlers.discard(self.component.handleKeyEvent)

    def _getRequiredLibraries(self):
        pass

    def _createLoaderManager(self):
        return None

    def _createContainerManager(self):
        return None

    def _createToolTipManager(self):
        return None

    def _createGlobalVarsManager(self):
        return None

    def _createSoundManager(self):
        return None

    def _createColorSchemeManager(self):
        return None

    def _createEventLogMgr(self):
        return None

    def _createContextMenuManager(self):
        return None

    def _createPopoverManager(self):
        return None

    def _createVoiceChatManager(self):
        return None

    def _createUtilsManager(self):
        return None

    def _createTweenManager(self):
        return None

    def _createGameInputManager(self):
        return None

    def _createCacheManager(self):
        return None

    def _createImageManager(self):
        return None

    def _createTutorialManager(self):
        return None

    def _setup(self):
        raise NotImplementedError('App._setup must be overridden')

    def _loadCursor(self):
        self._containerMgr.load(VIEW_ALIAS.CURSOR)

    def _loadWaiting(self):
        raise NotImplementedError('App._loadWaiting must be overridden')

    def __onScreenResolutionChanged(self):
        self.updateScale()

    def __onAppResolutionChanged(self, event):
        ctx = event.ctx
        if 'width' not in ctx:
            LOG_ERROR('Application width is not found', ctx)
            return
        if 'height' not in ctx:
            LOG_ERROR('Application height is not found', ctx)
            return
        if 'scale' not in ctx:
            LOG_ERROR('Application scale is not found', ctx)
            return
        self.updateStage(ctx['width'], ctx['height'], ctx['scale'])
