# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/ApplicationMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ApplicationMeta(BaseDAAPIComponent):

    def setLoaderMgr(self, mgr):
        self._printOverrideError('setLoaderMgr')

    def setGlobalVarsMgr(self, mgr):
        self._printOverrideError('setGlobalVarsMgr')

    def setSoundMgr(self, mgr):
        self._printOverrideError('setSoundMgr')

    def setContainerMgr(self, mgr):
        self._printOverrideError('setContainerMgr')

    def setContextMenuMgr(self, mgr):
        self._printOverrideError('setContextMenuMgr')

    def setPopoverMgr(self, mgr):
        self._printOverrideError('setPopoverMgr')

    def setColorSchemeMgr(self, mgr):
        self._printOverrideError('setColorSchemeMgr')

    def setEventLogMgr(self, mgr):
        self._printOverrideError('setEventLogMgr')

    def setTooltipMgr(self, mgr):
        self._printOverrideError('setTooltipMgr')

    def setVoiceChatMgr(self, mgr):
        self._printOverrideError('setVoiceChatMgr')

    def setUtilsMgr(self, mgr):
        self._printOverrideError('setUtilsMgr')

    def setTweenMgr(self, mgr):
        self._printOverrideError('setTweenMgr')

    def setGameInputMgr(self, mgr):
        self._printOverrideError('setGameInputMgr')

    def setCacheMgr(self, mgr):
        self._printOverrideError('setCacheMgr')

    def setTextMgr(self, mgr):
        self._printOverrideError('setTextMgr')

    def setTutorialMgr(self, mgr):
        self._printOverrideError('setTutorialMgr')

    def setImageManager(self, mgr):
        self._printOverrideError('setImageManager')

    def setGraphicsOptimizationManager(self, mgr):
        self._printOverrideError('setGraphicsOptimizationManager')

    def handleGlobalKeyEvent(self, command):
        self._printOverrideError('handleGlobalKeyEvent')

    def onAsInitializationCompleted(self):
        self._printOverrideError('onAsInitializationCompleted')

    def as_isDAAPIInitedS(self):
        return self.flashObject.as_isDAAPIInited() if self._isDAAPIInited() else None

    def as_populateS(self):
        return self.flashObject.as_populate() if self._isDAAPIInited() else None

    def as_disposeS(self):
        return self.flashObject.as_dispose() if self._isDAAPIInited() else None

    def as_registerManagersS(self):
        return self.flashObject.as_registerManagers() if self._isDAAPIInited() else None

    def as_loadLibrariesS(self, list):
        return self.flashObject.as_loadLibraries(list) if self._isDAAPIInited() else None

    def as_updateStageS(self, w, h, scale):
        return self.flashObject.as_updateStage(w, h, scale) if self._isDAAPIInited() else None

    def as_blurBackgroundViewsS(self, ownLayer, layersToBlur, blurAnimRepeatCount):
        return self.flashObject.as_blurBackgroundViews(ownLayer, layersToBlur, blurAnimRepeatCount) if self._isDAAPIInited() else None

    def as_unblurBackgroundViewsS(self):
        return self.flashObject.as_unblurBackgroundViews() if self._isDAAPIInited() else None
