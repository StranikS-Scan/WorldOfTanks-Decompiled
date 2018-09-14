# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/LobbyEntry.py
import BigWorld
from gui.Scaleform import SCALEFORM_SWF_PATH_V3
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers import LoaderManager, ContainerManager
from gui.Scaleform.framework.managers.CacheManager import CacheManager
from gui.Scaleform.framework.managers.TutorialManager import TutorialManager
from gui.Scaleform.framework.managers.event_logging import EventLogManager
from gui.Scaleform.managers.context_menu import ContextMenuManager
from gui.Scaleform.managers.PopoverManager import PopoverManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.application import SFApplication
from gui.Scaleform.framework.ToolTip import ToolTip
from gui.Scaleform.managers.GlobalVarsManager import GlobalVarsManager
from gui.Scaleform.managers.SoundManager import SoundManager
from gui.Scaleform.managers.ColorSchemeManager import ColorSchemeManager
from gui.Scaleform.managers.VoiceChatManager import VoiceChatManager
from gui.Scaleform.managers.UtilsManager import UtilsManager
from gui.Scaleform.managers.GameInputMgr import GameInputMgr
from gui.Scaleform.managers.TweenSystem import TweenManager
from gui.shared import EVENT_BUS_SCOPE

class LobbyEntry(SFApplication):

    def __init__(self, appNS):
        super(LobbyEntry, self).__init__('lobby.swf', appNS)

    @property
    def cursorMgr(self):
        return self.__getCursorFromContainer()

    @property
    def waitingManager(self):
        return self.__getWaitingFromContainer()

    def afterCreate(self):
        super(LobbyEntry, self).afterCreate()
        from gui.Scaleform.Waiting import Waiting
        Waiting.setWainingViewGetter(self.__getWaitingFromContainer)

    def beforeDelete(self):
        from gui.Scaleform.Waiting import Waiting
        Waiting.setWainingViewGetter(None)
        super(LobbyEntry, self).beforeDelete()
        return

    def _createLoaderManager(self):
        return LoaderManager(self.proxy)

    def _createContainerManager(self):
        return ContainerManager(self._loaderMgr)

    def _createToolTipManager(self):
        return ToolTip()

    def _createGlobalVarsManager(self):
        return GlobalVarsManager()

    def _createSoundManager(self):
        return SoundManager()

    def _createColorSchemeManager(self):
        return ColorSchemeManager()

    def _createEventLogMgr(self):
        return EventLogManager()

    def _createContextMenuManager(self):
        return ContextMenuManager(self.proxy)

    def _createPopoverManager(self):
        return PopoverManager(EVENT_BUS_SCOPE.LOBBY)

    def _createVoiceChatManager(self):
        return VoiceChatManager(self.proxy)

    def _createUtilsManager(self):
        return UtilsManager()

    def _createTweenManager(self):
        return TweenManager()

    def _createGameInputManager(self):
        return GameInputMgr()

    def _createCacheManager(self):
        return CacheManager()

    def _createTutorialManager(self):
        return TutorialManager(self.proxy, True, 'gui/tutorial-lobby-gui.xml')

    def _setup(self):
        self.movie.backgroundAlpha = 0.0
        self.movie.setFocussed(SCALEFORM_SWF_PATH_V3)
        BigWorld.wg_setRedefineKeysMode(True)

    def _loadCursor(self):
        self._containerMgr.load(VIEW_ALIAS.CURSOR)

    def _loadWaiting(self):
        self._containerMgr.load(VIEW_ALIAS.WAITING)

    def _getRequiredLibraries(self):
        pass

    def __getCursorFromContainer(self):
        return self._containerMgr.getView(ViewTypes.CURSOR) if self._containerMgr is not None else None

    def __getWaitingFromContainer(self):
        return self._containerMgr.getView(ViewTypes.WAITING) if self._containerMgr is not None else None
