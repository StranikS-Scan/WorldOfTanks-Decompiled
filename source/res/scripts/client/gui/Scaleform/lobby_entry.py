# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/lobby_entry.py
import BigWorld
from gui.Scaleform import SCALEFORM_SWF_PATH_V3
from gui.Scaleform.daapi.settings.config import LOBBY_TOOLTIPS_BUILDERS_PATHS, ADVANCED_COMPLEX_TOOLTIPS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.tooltip_mgr import ToolTip
from gui.Scaleform.framework.application import AppEntry
from gui.Scaleform.framework.managers import LoaderManager, ContainerManager
from gui.Scaleform.framework.managers.CacheManager import CacheManager
from gui.Scaleform.framework.managers.ImageManager import ImageManager
from gui.Scaleform.framework.managers.TutorialManager import TutorialManager
from gui.Scaleform.framework.managers.containers import DefaultContainer
from gui.Scaleform.framework.managers.containers import PopUpContainer
from gui.Scaleform.framework.managers.context_menu import ContextMenuManager
from gui.Scaleform.framework.managers.event_logging import EventLogManager
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.framework.managers.optimization_manager import GraphicsOptimizationManager, OptimizationSetting
from gui.Scaleform.genConsts.GRAPHICS_OPTIMIZATION_ALIASES import GRAPHICS_OPTIMIZATION_ALIASES
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.managers.ColorSchemeManager import ColorSchemeManager
from gui.Scaleform.managers.GameInputMgr import GameInputMgr
from gui.Scaleform.managers.GlobalVarsManager import GlobalVarsManager
from gui.Scaleform.managers.PopoverManager import PopoverManager
from gui.Scaleform.managers.SoundManager import SoundManager
from gui.Scaleform.managers.TweenSystem import TweenManager
from gui.Scaleform.managers.UtilsManager import UtilsManager
from gui.Scaleform.managers.voice_chat import LobbyVoiceChatManager
from gui.impl.gen import R
from gui.shared import EVENT_BUS_SCOPE
from gui.app_loader import settings as app_settings
from helpers import dependency, uniprof
from skeletons.gui.game_control import IBootcampController
LOBBY_OPTIMIZATION_CONFIG = {VIEW_ALIAS.LOBBY_HEADER: OptimizationSetting(),
 HANGAR_ALIASES.TANK_CAROUSEL: OptimizationSetting(),
 GRAPHICS_OPTIMIZATION_ALIASES.CUSTOMISATION_BOTTOM_PANEL: OptimizationSetting()}

class LobbyEntry(AppEntry):
    bootcampCtrl = dependency.descriptor(IBootcampController)

    def __init__(self, appNS):
        super(LobbyEntry, self).__init__(R.entries.lobby(), appNS)

    @property
    def cursorMgr(self):
        return self.__getCursorFromContainer()

    @property
    def waitingManager(self):
        return self.__getWaitingFromContainer()

    @uniprof.regionDecorator(label='gui.lobby', scope='enter')
    def afterCreate(self):
        super(LobbyEntry, self).afterCreate()
        from gui.Scaleform.Waiting import Waiting
        Waiting.setWaitingViewGetter(self.__getWaitingFromContainer)

    @uniprof.regionDecorator(label='gui.lobby', scope='exit')
    def beforeDelete(self):
        from gui.Scaleform.Waiting import Waiting
        Waiting.setWaitingViewGetter(None)
        Waiting.close()
        super(LobbyEntry, self).beforeDelete()
        return

    def _createLoaderManager(self):
        return LoaderManager(self.proxy)

    def _createContainerManager(self):
        return ContainerManager(self._loaderMgr, DefaultContainer(ViewTypes.MARKER), DefaultContainer(ViewTypes.DEFAULT), DefaultContainer(ViewTypes.CURSOR), DefaultContainer(ViewTypes.WAITING), PopUpContainer(ViewTypes.WINDOW), PopUpContainer(ViewTypes.BROWSER), PopUpContainer(ViewTypes.TOP_WINDOW), PopUpContainer(ViewTypes.OVERLAY), DefaultContainer(ViewTypes.SERVICE_LAYOUT))

    def _createToolTipManager(self):
        tooltip = ToolTip(LOBBY_TOOLTIPS_BUILDERS_PATHS, ADVANCED_COMPLEX_TOOLTIPS, app_settings.GUI_GLOBAL_SPACE_ID.BATTLE_LOADING)
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

    def _createGraphicsOptimizationManager(self):
        return GraphicsOptimizationManager(config=LOBBY_OPTIMIZATION_CONFIG)

    def _setup(self):
        self.movie.backgroundAlpha = 0.0
        self.movie.setFocussed(SCALEFORM_SWF_PATH_V3)
        BigWorld.wg_setRedefineKeysMode(True)

    def _loadWaiting(self):
        self._containerMgr.load(SFViewLoadParams(VIEW_ALIAS.WAITING))

    def _getRequiredLibraries(self):
        pass

    def __getCursorFromContainer(self):
        return self._containerMgr.getView(ViewTypes.CURSOR) if self._containerMgr is not None else None

    def __getWaitingFromContainer(self):
        return self._containerMgr.getView(ViewTypes.WAITING) if self._containerMgr is not None else None
