# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/battle_entry.py
import weakref
import BigWorld
from gui import DEPTH_OF_Battle
from gui.Scaleform import SCALEFORM_SWF_PATH_V3
from gui.Scaleform.daapi.view.battle.shared.crosshair_panel import CrosshairPanel
from gui.Scaleform.daapi.view.battle.shared.markers2d.manager import MarkersManager
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.ToolTip import ToolTip
from gui.Scaleform.framework.application import SFApplication, DAAPIRootBridge
from gui.Scaleform.framework.managers import LoaderManager, ContainerManager
from gui.Scaleform.framework.managers.TutorialManager import TutorialManager
from gui.Scaleform.framework.managers.containers import DefaultContainer
from gui.Scaleform.framework.managers.containers import PopUpContainer
from gui.Scaleform.framework.managers.context_menu import ContextMenuManager
from gui.Scaleform.managers.ColorSchemeManager import BattleColorSchemeManager
from gui.Scaleform.managers.GlobalVarsManager import GlobalVarsManager
from gui.Scaleform.managers.SoundManager import SoundManager
from gui.Scaleform.managers.UtilsManager import UtilsManager
from gui.Scaleform.managers.voice_chat import BattleVoiceChatManager
from gui.Scaleform.managers.battle_input import BattleGameInputMgr
from gui.app_loader.settings import GUI_GLOBAL_SPACE_ID

class TopWindowContainer(PopUpContainer):

    def __init__(self, viewType, app, manager=None):
        super(TopWindowContainer, self).__init__(viewType, manager)
        self.__app = app

    def clear(self):
        self.__app = None
        super(TopWindowContainer, self).clear()
        return

    def add(self, pyView):
        result = super(TopWindowContainer, self).add(pyView)
        if result and self.__app is not None:
            self.__app.enterGuiControlMode(pyView.uniqueName)
        return result

    def remove(self, pyView):
        super(TopWindowContainer, self).remove(pyView)
        if self.__app is not None:
            self.__app.leaveGuiControlMode(pyView.uniqueName)
        return


class BattleEntry(SFApplication):

    def __init__(self, appNS):
        super(BattleEntry, self).__init__('battle.swf', appNS, DAAPIRootBridge(initCallback='registerBattleTest'))
        self.__markers2D = None
        self.__crosshairPanel = None
        self.__input = None
        return

    @property
    def cursorMgr(self):
        return self.__getCursorFromContainer()

    @property
    def markersManager(self):
        return self.__markers2D

    @property
    def crosshairPanel(self):
        return self.__crosshairPanel

    def afterCreate(self):
        super(BattleEntry, self).afterCreate()
        self.__markers2D = MarkersManager(self.proxy)
        self.__markers2D.active(True)
        self.__crosshairPanel = CrosshairPanel()
        self.__crosshairPanel.active(True)
        self.__input = BattleGameInputMgr()
        self.__input.start()

    def beforeDelete(self):
        if self.__markers2D is not None:
            self.__markers2D.close()
            self.__markers2D = None
        if self.__crosshairPanel is not None:
            self.__crosshairPanel.close()
            self.__crosshairPanel = None
        if self.__input is not None:
            self.__input.stop()
            self.__input = None
        super(BattleEntry, self).beforeDelete()
        return

    def handleKey(self, isDown, key, mods):
        if self.__input is not None:
            return self.__input.handleKey(isDown, key, mods)
        else:
            return False
            return

    def enterGuiControlMode(self, consumerID, cursorVisible=True, enableAiming=True):
        if self.__input is not None:
            self.__input.enterGuiControlMode(consumerID, cursorVisible=cursorVisible, enableAiming=enableAiming)
        return

    def leaveGuiControlMode(self, consumerID):
        if self.__input is not None:
            self.__input.leaveGuiControlMode(consumerID)
        return

    def hasGuiControlModeConsumers(self, *consumersIDs):
        if self.__input is not None:
            return self.__input.hasGuiControlModeConsumers(*consumersIDs)
        else:
            return False
            return

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
        return ContainerManager(self._loaderMgr, DefaultContainer(ViewTypes.DEFAULT), DefaultContainer(ViewTypes.CURSOR), PopUpContainer(ViewTypes.WINDOW), TopWindowContainer(ViewTypes.TOP_WINDOW, weakref.proxy(self)))

    def _createToolTipManager(self):
        return ToolTip(GUI_GLOBAL_SPACE_ID.BATTLE_LOADING)

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
