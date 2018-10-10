# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/battle_entry.py
import weakref
import BigWorld
from gui import DEPTH_OF_Battle
from gui.Scaleform import SCALEFORM_SWF_PATH_V3
from gui.Scaleform.daapi.settings.config import BATTLE_TOOLTIPS_BUILDERS_PATHS
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.tooltip_mgr import ToolTip
from gui.Scaleform.framework.application import AppEntry, DAAPIRootBridge
from gui.Scaleform.framework.managers import LoaderManager, ContainerManager
from gui.Scaleform.framework.managers.TutorialManager import TutorialManager
from gui.Scaleform.framework.managers.containers import DefaultContainer
from gui.Scaleform.framework.managers.containers import PopUpContainer
from gui.Scaleform.framework.managers.context_menu import ContextMenuManager
from gui.Scaleform.framework.managers.optimization_manager import GraphicsOptimizationManager, OptimizationSetting
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.managers.ColorSchemeManager import BattleColorSchemeManager
from gui.Scaleform.managers.GlobalVarsManager import GlobalVarsManager
from gui.Scaleform.managers.PopoverManager import PopoverManager
from gui.Scaleform.framework.managers.ImageManager import ImageManager
from gui.Scaleform.managers.SoundManager import SoundManager
from gui.Scaleform.managers.TweenSystem import TweenManager
from gui.Scaleform.managers.UtilsManager import UtilsManager
from gui.Scaleform.managers.battle_input import BattleGameInputMgr
from gui.Scaleform.managers.voice_chat import BattleVoiceChatManager
from gui.app_loader import settings as app_settings
from gui.impl.pub import UserWindowFlags
from gui.shared import EVENT_BUS_SCOPE
from helpers import uniprof

class TopWindowContainer(PopUpContainer):

    def __init__(self, viewType, app, manager=None):
        super(TopWindowContainer, self).__init__(viewType, manager)
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

    def __init__(self, appNS):
        super(BattleEntry, self).__init__(UserWindowFlags.MAIN_WINDOW, 'battle.swf', appNS, DAAPIRootBridge(initCallback='registerBattleTest'))
        self.__input = None
        return

    @property
    def cursorMgr(self):
        return self.__getCursorFromContainer()

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
        return ContainerManager(self._loaderMgr, DefaultContainer(ViewTypes.DEFAULT), DefaultContainer(ViewTypes.CURSOR), PopUpContainer(ViewTypes.WINDOW), TopWindowContainer(ViewTypes.TOP_WINDOW, weakref.proxy(self)), DefaultContainer(ViewTypes.SERVICE_LAYOUT), PopUpContainer(ViewTypes.OVERLAY))

    def _createToolTipManager(self):
        tooltip = ToolTip(BATTLE_TOOLTIPS_BUILDERS_PATHS, {}, app_settings.GUI_GLOBAL_SPACE_ID.BATTLE_LOADING)
        tooltip.setEnvironment(self)
        return tooltip

    def _createGlobalVarsManager(self):
        return GlobalVarsManager()

    def _createSoundManager(self):
        return SoundManager()

    def _createColorSchemeManager(self):
        return BattleColorSchemeManager()

    def _createVoiceChatManager(self):
        return BattleVoiceChatManager(weakref.proxy(self))

    def _createUtilsManager(self):
        return UtilsManager()

    def _createContextMenuManager(self):
        return ContextMenuManager(self.proxy)

    def _createTutorialManager(self):
        return TutorialManager(None, False, {})

    def _createImageManager(self):
        return ImageManager()

    def _createPopoverManager(self):
        return PopoverManager(EVENT_BUS_SCOPE.BATTLE)

    def _createTweenManager(self):
        return TweenManager()

    def _createGraphicsOptimizationManager(self):
        return GraphicsOptimizationManager(config=BATTLE_OPTIMIZATION_CONFIG)

    def _setup(self):
        self.component.wg_inputKeyMode = 1
        self.component.position.z = DEPTH_OF_Battle
        self.movie.backgroundAlpha = 0.0
        self.movie.setFocussed(SCALEFORM_SWF_PATH_V3)
        BigWorld.wg_setRedefineKeysMode(False)

    def _loadWaiting(self):
        pass

    def _getRequiredLibraries(self):
        pass

    def __getCursorFromContainer(self):
        return self._containerMgr.getView(ViewTypes.CURSOR) if self._containerMgr is not None else None
