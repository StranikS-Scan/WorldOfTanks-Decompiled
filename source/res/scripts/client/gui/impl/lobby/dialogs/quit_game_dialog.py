# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/quit_game_dialog.py
import logging
import GUI
from gui.Scaleform.managers.battle_input import BattleGUIKeyHandler
from gui.app_loader.settings import APP_NAME_SPACE
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.constants.dialog_presets import DialogPresets
from gui.impl.pub.dialog_window import DialogWindow, DialogButtons
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
_logger = logging.getLogger(__name__)
_RESIZE_TRIGER_WIDTH = 1450

class QuitGameDialogWindow(DialogWindow, BattleGUIKeyHandler):
    __appLoader = dependency.descriptor(IAppLoader)
    __slots__ = ()

    def __init__(self, parent=None):
        super(QuitGameDialogWindow, self).__init__(parent=parent, enableBlur=False)

    def handleEscKey(self, isDown):
        if isDown:
            self.destroy()
        return isDown

    def _initialize(self):
        super(QuitGameDialogWindow, self)._initialize()
        g_eventBus.addListener(events.GameEvent.CHANGE_APP_RESOLUTION, self.__onResize, scope=EVENT_BUS_SCOPE.GLOBAL)
        battleApp = self._battleApp
        if battleApp:
            battleApp.registerGuiKeyHandler(self)
            battleApp.enterGuiControlMode(self.uniqueID)
        with self.viewModel.transaction() as model:
            self._addButton(DialogButtons.SUBMIT, R.strings.dialogs.quit.submit())
            self._addButton(DialogButtons.CANCEL, R.strings.dialogs.quit.cancel(), isFocused=True, invalidateAll=True)
            width = GUI.screenResolution()
            if width > _RESIZE_TRIGER_WIDTH:
                image = R.images.gui.maps.uiKit.dialogs.quit_bg_big()
            else:
                image = R.images.gui.maps.uiKit.dialogs.quit_bg()
            model.setBackgroundImage(image)
            model.setPreset(DialogPresets.QUIT_GAME)
            model.setTitle(R.strings.dialogs.quit.title())

    def _finalize(self):
        g_eventBus.removeListener(events.GameEvent.CHANGE_APP_RESOLUTION, self.__onResize, scope=EVENT_BUS_SCOPE.GLOBAL)
        battleApp = self._battleApp
        if battleApp:
            battleApp.unregisterGuiKeyHandler(self)
            battleApp.leaveGuiControlMode(self.uniqueID)
        super(QuitGameDialogWindow, self)._finalize()

    @property
    def _battleApp(self):
        return self.__appLoader.getApp(APP_NAME_SPACE.SF_BATTLE)

    def __onResize(self, event):
        ctx = event.ctx
        if 'width' not in ctx:
            _logger.error('Window width is not found: %r', ctx)
            return
        if 'height' not in ctx:
            _logger.error('Window height is not found: %r', ctx)
            return
        if ctx['width'] > _RESIZE_TRIGER_WIDTH:
            image = R.images.gui.maps.uiKit.dialogs.quit_bg_big()
        else:
            image = R.images.gui.maps.uiKit.dialogs.quit_bg()
        self.viewModel.setBackgroundImage(image)
