# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/ApplicationMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class ApplicationMeta(BaseDAAPIModule):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIModule
    null
    """

    def setLoaderMgr(self, mgr):
        """
        :param mgr:
        :return :
        """
        self._printOverrideError('setLoaderMgr')

    def setGlobalVarsMgr(self, mgr):
        """
        :param mgr:
        :return :
        """
        self._printOverrideError('setGlobalVarsMgr')

    def setSoundMgr(self, mgr):
        """
        :param mgr:
        :return :
        """
        self._printOverrideError('setSoundMgr')

    def setContainerMgr(self, mgr):
        """
        :param mgr:
        :return :
        """
        self._printOverrideError('setContainerMgr')

    def setContextMenuMgr(self, mgr):
        """
        :param mgr:
        :return :
        """
        self._printOverrideError('setContextMenuMgr')

    def setPopoverMgr(self, mgr):
        """
        :param mgr:
        :return :
        """
        self._printOverrideError('setPopoverMgr')

    def setColorSchemeMgr(self, mgr):
        """
        :param mgr:
        :return :
        """
        self._printOverrideError('setColorSchemeMgr')

    def setEventLogMgr(self, mgr):
        """
        :param mgr:
        :return :
        """
        self._printOverrideError('setEventLogMgr')

    def setTooltipMgr(self, mgr):
        """
        :param mgr:
        :return :
        """
        self._printOverrideError('setTooltipMgr')

    def setVoiceChatMgr(self, mgr):
        """
        :param mgr:
        :return :
        """
        self._printOverrideError('setVoiceChatMgr')

    def setUtilsMgr(self, mgr):
        """
        :param mgr:
        :return :
        """
        self._printOverrideError('setUtilsMgr')

    def setTweenMgr(self, mgr):
        """
        :param mgr:
        :return :
        """
        self._printOverrideError('setTweenMgr')

    def setGameInputMgr(self, mgr):
        """
        :param mgr:
        :return :
        """
        self._printOverrideError('setGameInputMgr')

    def setCacheMgr(self, mgr):
        """
        :param mgr:
        :return :
        """
        self._printOverrideError('setCacheMgr')

    def setTextMgr(self, mgr):
        """
        :param mgr:
        :return :
        """
        self._printOverrideError('setTextMgr')

    def setTutorialMgr(self, mgr):
        """
        :param mgr:
        :return :
        """
        self._printOverrideError('setTutorialMgr')

    def setImageManager(self, mgr):
        """
        :param mgr:
        :return :
        """
        self._printOverrideError('setImageManager')

    def handleGlobalKeyEvent(self, command):
        """
        :param command:
        :return :
        """
        self._printOverrideError('handleGlobalKeyEvent')

    def onAsInitializationCompleted(self):
        """
        :return :
        """
        self._printOverrideError('onAsInitializationCompleted')

    def as_isDAAPIInitedS(self):
        """
        :return Boolean:
        """
        return self.flashObject.as_isDAAPIInited() if self._isDAAPIInited() else None

    def as_populateS(self):
        """
        :return :
        """
        return self.flashObject.as_populate() if self._isDAAPIInited() else None

    def as_disposeS(self):
        """
        :return :
        """
        return self.flashObject.as_dispose() if self._isDAAPIInited() else None

    def as_registerManagersS(self):
        """
        :return :
        """
        return self.flashObject.as_registerManagers() if self._isDAAPIInited() else None

    def as_setLibrariesListS(self, list):
        """
        :param list:
        :return :
        """
        return self.flashObject.as_setLibrariesList(list) if self._isDAAPIInited() else None

    def as_updateStageS(self, w, h, scale):
        """
        :param w:
        :param h:
        :param scale:
        :return :
        """
        return self.flashObject.as_updateStage(w, h, scale) if self._isDAAPIInited() else None
