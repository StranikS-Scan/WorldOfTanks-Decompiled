# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/battle_entry.py
import weakref
import BigWorld
from frameworks.wulf import WindowLayer
from gui import DEPTH_OF_Battle
from gui.Scaleform import SCALEFORM_SWF_PATH_V3
from gui.Scaleform.daapi.settings.config import BATTLE_TOOLTIPS_BUILDERS_PATHS
from gui.Scaleform.flash_wrapper import InputKeyMode
from gui.Scaleform.framework.managers.TutorialManager import ScaleformTutorialManager
from gui.Scaleform.framework.tooltip_mgr import ToolTip
from gui.Scaleform.framework.ui_logging_manager import UILoggerManager
from gui.Scaleform.framework.application import AppEntry, DAAPIRootBridge
from gui.Scaleform.framework.managers import LoaderManager, ContainerManager
from gui.Scaleform.framework.managers.containers import DefaultContainer
from gui.Scaleform.framework.managers.containers import PopUpContainer
from gui.Scaleform.framework.managers.context_menu import ContextMenuManager
from gui.Scaleform.framework.managers.optimization_manager import GraphicsOptimizationManager, OptimizationSetting
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.managers.ColorSchemeManager import BattleColorSchemeManager
from gui.Scaleform.managers.cursor_mgr import CursorManager
from gui.Scaleform.managers.GlobalVarsManager import GlobalVarsManager
from gui.Scaleform.managers.PopoverManager import PopoverManager
from gui.Scaleform.framework.managers.ImageManager import ImageManager
from gui.sounds.SoundManager import SoundManager
from gui.Scaleform.managers.TweenSystem import TweenManager
from gui.Scaleform.managers.UtilsManager import UtilsManager
from gui.Scaleform.managers.battle_input import BattleGameInputMgr
from gui.Scaleform.managers.voice_chat import BattleVoiceChatManager
from gui.impl.gen import R
from gui.shared import EVENT_BUS_SCOPE
from helpers import uniprof
from skeletons.gui.app_loader import GuiGlobalSpaceID

class TopWindowContainer(PopUpContainer):

    def __init__(self, layer, app, manager=None):
        super(TopWindowContainer, self).__init__(layer, manager)
        self.__app = app

    def clear(self):
        self.__app = None
        super(TopWindowContainer, self).clear()
        return

    def addView(self, pyView):
        result = super(TopWindowContainer, self).addView(pyView)
        if result and self.__app is not None:
            self.__app.enterGuiControlMode(pyView.uniqueName)
        return result

    def removeView(self, pyView):
        result = super(TopWindowContainer, self).removeView(pyView)
        if self.__app is not None:
            self.__app.leaveGuiControlMode(pyView.uniqueName)
        return result


BATTLE_OPTIMIZATION_CONFIG = {BATTLE_VIEW_ALIASES.MINIMAP: OptimizationSetting('minimapAlphaEnabled', True),
 BATTLE_VIEW_ALIASES.DAMAGE_PANEL: OptimizationSetting()}

class BattleEntry(AppEntry):

    def __init__(self, appNS, ctrlModeFlags):
        super(BattleEntry, self).__init__(R.entries.battle(), appNS, ctrlModeFlags, daapiBridge=DAAPIRootBridge(initCallback='registerBattleTest'))
        self.__input = None
        return

    @uniprof.regionDecorator(label='gui.battle', scope='enter')
    def afterCreate(self):
        super(BattleEntry, self).afterCreate()
        self.__input = BattleGameInputMgr()
        self.__input.start()

    @uniprof.regionDecorator(label='gui.battle', scope='exit')
    def beforeDelete(self):
        if self.__input is not None:
            self.__input.stop()
            self.__input = None
        super(BattleEntry, self).beforeDelete()
        return

    def handleKey(self, isDown, key, mods):
        return self.__input.handleKey(isDown, key, mods) if self.__input is not None else False

    def enterGuiControlMode(self, consumerID, cursorVisible=True, enableAiming=True):
        if self.__input is not None:
            self.__input.enterGuiControlMode(consumerID, cursorVisible=cursorVisible, enableAiming=enableAiming)
        return

    def leaveGuiControlMode(self, consumerID):
        if self.__input is not None:
            self.__input.leaveGuiControlMode(consumerID)
        return

    def hasGuiControlModeConsumers(self, *consumersIDs):
        return self.__input.hasGuiControlModeConsumers(*consumersIDs) if self.__input is not None else False

    def registerGuiKeyHandler(self, handler):
        if self.__input is not None:
            self.__input.registerGuiKeyHandler(handler)
        return

    def unregisterGuiKeyHandler(self, handler):
        if self.__input is not None:
            self.__input.unregisterGuiKeyHandler(handler)
        return

    def _createLoaderManager(self):
        return LoaderManager(weakref.proxy(self))

    def _createContainerManager(self):
        return ContainerManager(self._loaderMgr, DefaultContainer(WindowLayer.HIDDEN_SERVICE_LAYOUT), DefaultContainer(WindowLayer.VIEW), DefaultContainer(WindowLayer.CURSOR), PopUpContainer(WindowLayer.WINDOW), PopUpContainer(WindowLayer.FULLSCREEN_WINDOW), TopWindowContainer(WindowLayer.TOP_WINDOW, weakref.proxy(self)), DefaultContainer(WindowLayer.SERVICE_LAYOUT), PopUpContainer(WindowLayer.OVERLAY))

    def _createToolTipManager(self):
        tooltip = ToolTip(BATTLE_TOOLTIPS_BUILDERS_PATHS, {}, GuiGlobalSpaceID.BATTLE_LOADING)
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
        return BattleColorSchemeManager()

    def _createVoiceChatManager(self):
        return BattleVoiceChatManager(weakref.proxy(self))

    def _createUtilsManager(self):
        return UtilsManager()

    def _createContextMenuManager(self):
        return ContextMenuManager(self.proxy)

    def _createTutorialManager(self):
        return ScaleformTutorialManager()

    def _createUILoggerManager(self):
        return UILoggerManager()

    def _createImageManager(self):
        return ImageManager()

    def _createPopoverManager(self):
        return PopoverManager(EVENT_BUS_SCOPE.BATTLE)

    def _createTweenManager(self):
        return TweenManager()

    def _createGraphicsOptimizationManager(self):
        return GraphicsOptimizationManager(config=BATTLE_OPTIMIZATION_CONFIG)

    def _setup(self):
        self.component.wg_inputKeyMode = InputKeyMode.IGNORE_RESULT
        self.component.position.z = DEPTH_OF_Battle
        self.movie.backgroundAlpha = 0.0
        self.movie.setFocused(SCALEFORM_SWF_PATH_V3)
        BigWorld.wg_setRedefineKeysMode(False)

    def _loadWaiting(self):
        pass

    def _getRequiredLibraries(self):
        pass

    def __getCursorFromContainer(self):
        return self._containerMgr.getView(WindowLayer.CURSOR) if self._containerMgr is not None else None
