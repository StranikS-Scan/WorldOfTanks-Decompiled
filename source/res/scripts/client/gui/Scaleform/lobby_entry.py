# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/lobby_entry.py
import BigWorld
from frameworks.wulf import WindowLayer
from gui.shared.system_factory import collectLobbyTooltipsBuilders
from gui.Scaleform import SCALEFORM_SWF_PATH_V3
from gui.Scaleform.daapi.settings.config import ADVANCED_COMPLEX_TOOLTIPS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.tooltip_mgr import ToolTip
from gui.Scaleform.framework.ui_logging_manager import UILoggerManager
from gui.Scaleform.framework.application import AppEntry
from gui.Scaleform.framework.managers import LoaderManager, ContainerManager
from gui.Scaleform.framework.managers.CacheManager import CacheManager
from gui.Scaleform.framework.managers.ImageManager import ImageManager
from gui.Scaleform.framework.managers.TutorialManager import ScaleformTutorialManager
from gui.Scaleform.framework.managers.containers import DefaultContainer
from gui.Scaleform.framework.managers.containers import PopUpContainer
from gui.Scaleform.framework.managers.context_menu import ContextMenuManager
from gui.Scaleform.framework.managers.event_logging import EventLogManager
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.framework.managers.optimization_manager import GraphicsOptimizationManager, OptimizationSetting
from gui.Scaleform.genConsts.GRAPHICS_OPTIMIZATION_ALIASES import GRAPHICS_OPTIMIZATION_ALIASES
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.managers.ColorSchemeManager import ColorSchemeManager
from gui.Scaleform.managers.cursor_mgr import CursorManager
from gui.Scaleform.managers.GameInputMgr import GameInputMgr
from gui.Scaleform.managers.GlobalVarsManager import GlobalVarsManager
from gui.Scaleform.managers.PopoverManager import PopoverManager
from gui.Scaleform.required_libraries_config import LOBBY_REQUIRED_LIBRARIES
from gui.sounds.SoundManager import SoundManager
from gui.Scaleform.managers.TweenSystem import TweenManager
from gui.Scaleform.managers.UtilsManager import UtilsManager
from gui.Scaleform.managers.voice_chat import LobbyVoiceChatManager
from gui.impl.gen import R
from gui.shared import EVENT_BUS_SCOPE
from helpers import dependency, uniprof
from skeletons.gui.app_loader import GuiGlobalSpaceID
from skeletons.gui.game_control import IBootcampController
LOBBY_OPTIMIZATION_CONFIG = {VIEW_ALIAS.LOBBY_HEADER: OptimizationSetting(),
 VIEW_ALIAS.LOBBY_TECHTREE: OptimizationSetting(),
 VIEW_ALIAS.LOBBY_RESEARCH: OptimizationSetting(),
 HANGAR_ALIASES.TANK_CAROUSEL: OptimizationSetting(),
 HANGAR_ALIASES.RANKED_TANK_CAROUSEL: OptimizationSetting(),
 HANGAR_ALIASES.BATTLEPASS_TANK_CAROUSEL: OptimizationSetting(),
 HANGAR_ALIASES.ROYALE_TANK_CAROUSEL: OptimizationSetting(),
 HANGAR_ALIASES.MAPBOX_TANK_CAROUSEL: OptimizationSetting(),
 HANGAR_ALIASES.FUN_RANDOM_TANK_CAROUSEL: OptimizationSetting(),
 HANGAR_ALIASES.COMP7_TANK_CAROUSEL: OptimizationSetting(),
 GRAPHICS_OPTIMIZATION_ALIASES.CUSTOMISATION_BOTTOM_PANEL: OptimizationSetting()}

class LobbyEntry(AppEntry):
    bootcampCtrl = dependency.descriptor(IBootcampController)

    def __init__(self, appNS, ctrlModeFlags):
        super(LobbyEntry, self).__init__(R.entries.lobby(), appNS, ctrlModeFlags)

    @property
    def waitingManager(self):
        return self.__getWaitingFromContainer()

    @uniprof.regionDecorator(label='gui.lobby', scope='enter')
    def afterCreate(self):
        super(LobbyEntry, self).afterCreate()

    @uniprof.regionDecorator(label='gui.lobby', scope='exit')
    def beforeDelete(self):
        from gui.Scaleform.Waiting import Waiting
        Waiting.close()
        super(LobbyEntry, self).beforeDelete()

    def _createLoaderManager(self):
        return LoaderManager(self.proxy)

    def _createContainerManager(self):
        return ContainerManager(self._loaderMgr, DefaultContainer(WindowLayer.HIDDEN_SERVICE_LAYOUT), DefaultContainer(WindowLayer.MARKER), DefaultContainer(WindowLayer.VIEW), DefaultContainer(WindowLayer.CURSOR), DefaultContainer(WindowLayer.WAITING), PopUpContainer(WindowLayer.WINDOW), PopUpContainer(WindowLayer.FULLSCREEN_WINDOW), PopUpContainer(WindowLayer.TOP_WINDOW), PopUpContainer(WindowLayer.OVERLAY), DefaultContainer(WindowLayer.SERVICE_LAYOUT))

    def _createToolTipManager(self):
        builders = collectLobbyTooltipsBuilders()
        tooltip = ToolTip(builders, ADVANCED_COMPLEX_TOOLTIPS, GuiGlobalSpaceID.BATTLE_LOADING)
        tooltip.setEnvironment(self)
        return tooltip

    def _createGlobalVarsManager(self):
        return GlobalVarsManager()

    def _createSoundManager(self):
        return SoundManager()

    def _createCursorManager(self):
        cursor = CursorManager()
        cursor.setEnvironment(self)
        return cursor

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

    def _createUILoggerManager(self):
        return UILoggerManager()

    def _createTutorialManager(self):
        return ScaleformTutorialManager()

    def _createGraphicsOptimizationManager(self):
        return GraphicsOptimizationManager(config=LOBBY_OPTIMIZATION_CONFIG)

    def _setup(self):
        self.movie.backgroundAlpha = 0.0
        self.movie.setFocused(SCALEFORM_SWF_PATH_V3)
        BigWorld.wg_setRedefineKeysMode(True)

    def _loadWaiting(self):
        self._containerMgr.load(SFViewLoadParams(VIEW_ALIAS.WAITING))

    def _getRequiredLibraries(self):
        return LOBBY_REQUIRED_LIBRARIES

    def __getWaitingFromContainer(self):
        return self._containerMgr.getView(WindowLayer.WAITING) if self._containerMgr is not None else None
