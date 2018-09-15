# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/lobby_entry.py
import BigWorld
from gui.Scaleform import SCALEFORM_SWF_PATH_V3
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.ToolTip import ToolTip
from gui.Scaleform.framework.application import SFApplication
from gui.Scaleform.framework.managers import LoaderManager, ContainerManager
from gui.Scaleform.framework.managers.CacheManager import CacheManager
from gui.Scaleform.framework.managers.ImageManager import ImageManager
from gui.Scaleform.framework.managers.TutorialManager import TutorialManager
from gui.Scaleform.framework.managers.BootcampManager import BootcampManager
from gui.Scaleform.framework.managers.containers import DefaultContainer
from gui.Scaleform.framework.managers.containers import PopUpContainer
from gui.Scaleform.framework.managers.context_menu import ContextMenuManager
from gui.Scaleform.framework.managers.event_logging import EventLogManager
from gui.Scaleform.framework.managers.loaders import ViewLoadParams
from gui.Scaleform.managers.ColorSchemeManager import ColorSchemeManager
from gui.Scaleform.managers.GameInputMgr import GameInputMgr
from gui.Scaleform.managers.GlobalVarsManager import GlobalVarsManager
from gui.Scaleform.managers.PopoverManager import PopoverManager
from gui.Scaleform.managers.SoundManager import SoundManager
from gui.Scaleform.managers.TweenSystem import TweenManager
from gui.Scaleform.managers.UtilsManager import UtilsManager
from gui.Scaleform.managers.voice_chat import LobbyVoiceChatManager
from gui.Scaleform.managers.fader_manager import FaderManager
from gui.shared import EVENT_BUS_SCOPE
from gui.app_loader.settings import GUI_GLOBAL_SPACE_ID
from helpers import dependency
from skeletons.gui.game_control import IBootcampController

class LobbyEntry(SFApplication):
    bootcampCtrl = dependency.descriptor(IBootcampController)

    def __init__(self, appNS):
        super(LobbyEntry, self).__init__('lobby.swf', appNS)
        self.__faderManager = None
        return

    @property
    def cursorMgr(self):
        return self.__getCursorFromContainer()

    @property
    def waitingManager(self):
        return self.__getWaitingFromContainer()

    @property
    def faderManager(self):
        return self.__faderManager

    def afterCreate(self):
        super(LobbyEntry, self).afterCreate()
        from gui.Scaleform.Waiting import Waiting
        Waiting.setWainingViewGetter(self.__getWaitingFromContainer)

    def beforeDelete(self):
        from gui.Scaleform.Waiting import Waiting
        Waiting.setWainingViewGetter(None)
        Waiting.close()
        if self.__faderManager:
            self.__faderManager.destroy()
            self.__faderManager = None
        super(LobbyEntry, self).beforeDelete()
        return

    def _createLoaderManager(self):
        return LoaderManager(self.proxy)

    def _createContainerManager(self):
        return ContainerManager(self._loaderMgr, DefaultContainer(ViewTypes.DEFAULT), DefaultContainer(ViewTypes.CURSOR), DefaultContainer(ViewTypes.WAITING), PopUpContainer(ViewTypes.WINDOW), PopUpContainer(ViewTypes.BROWSER), PopUpContainer(ViewTypes.TOP_WINDOW), PopUpContainer(ViewTypes.OVERLAY), DefaultContainer(ViewTypes.SERVICE_LAYOUT))

    def _createManagers(self):
        super(LobbyEntry, self)._createManagers()
        self.__faderManager = FaderManager()

    def _createToolTipManager(self):
        tooltip = ToolTip(GUI_GLOBAL_SPACE_ID.BATTLE_LOADING)
        tooltip.setEnvironment(self)
        return tooltip

    def _createGlobalVarsManager(self):
        return GlobalVarsManager()

    def _createSoundManager(self):
        return SoundManager()

    def _createColorSchemeManager(self):
        return ColorSchemeManager()

    def _createEventLogMgr(self):
        return EventLogManager(False)

    def _createContextMenuManager(self):
        return ContextMenuManager(self.proxy)

    def _createPopoverManager(self):
        return PopoverManager(EVENT_BUS_SCOPE.LOBBY)

    def _createVoiceChatManager(self):
        return LobbyVoiceChatManager(self.proxy)

    def _createUtilsManager(self):
        return UtilsManager()

    def _createTweenManager(self):
        return TweenManager()

    def _createGameInputManager(self):
        return GameInputMgr()

    def _createCacheManager(self):
        return CacheManager()

    def _createImageManager(self):
        return ImageManager()

    def _createTutorialManager(self):
        return TutorialManager(self.proxy, True, 'gui/tutorial-lobby-gui.xml')

    def _createBootcampManager(self):
        return BootcampManager(self.bootcampCtrl.isInBootcamp(), 'scripts/bootcamp_docs/bootcamp_manager.xml')

    def _setup(self):
        self.movie.backgroundAlpha = 0.0
        self.movie.setFocussed(SCALEFORM_SWF_PATH_V3)
        BigWorld.wg_setRedefineKeysMode(True)

    def _loadWaiting(self):
        self._containerMgr.load(ViewLoadParams(VIEW_ALIAS.WAITING))

    def _getRequiredLibraries(self):
        pass

    def __getCursorFromContainer(self):
        return self._containerMgr.getView(ViewTypes.CURSOR) if self._containerMgr is not None else None

    def __getWaitingFromContainer(self):
        return self._containerMgr.getView(ViewTypes.WAITING) if self._containerMgr is not None else None

    def _addGameCallbacks(self):
        super(LobbyEntry, self)._addGameCallbacks()
        self.__faderManager.setup()
