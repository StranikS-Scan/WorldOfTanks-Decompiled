# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/lobby/dialogs/trade_in_confirmation_dialog.py
from gui.impl.dialogs.builders import SimpleDialogBuilder
from gui.impl.gen import R
from gui.impl.gen.view_models.constants.dialog_presets import DialogPresets
from gui.impl.pub.dialog_window import DialogFlags, DialogButtons
from gui.impl.pub.simple_dialog_window import SimpleDialogWindow
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader

class TradeInConfirmationDialogBuilder(SimpleDialogBuilder):

    def __init__(self):
        super(TradeInConfirmationDialogBuilder, self).__init__()
        self._windowClass = TradeInConfirmationDialog
        self.setPreset(DialogPresets.WARNING)
        self.setTitle(R.strings.tech_tree_trade_in.exchangeConfirmation.title())
        self.setMessage(R.strings.tech_tree_trade_in.exchangeConfirmation.message())
        self.addButton(DialogButtons.PURCHASE, R.strings.tech_tree_trade_in.exchangeConfirmation.purchase(), True)
        self.addButton(DialogButtons.CANCEL, R.strings.tech_tree_trade_in.exchangeConfirmation.cancel(), False)


class TradeInConfirmationDialog(SimpleDialogWindow):
    __appLoader = dependency.descriptor(IAppLoader)
    __slots__ = ('__customBlur',)

    def __init__(self, bottomContent=None, parent=None, balanceContent=None, preset=DialogPresets.DEFAULT, flags=DialogFlags.TOP_WINDOW):
        super(TradeInConfirmationDialog, self).__init__(bottomContent=bottomContent, parent=parent, balanceContent=balanceContent, enableBlur=False, preset=preset, flags=flags)
        self.__customBlur = CachedBlur(enabled=True, fadeTime=0, ownLayer=self.layer, blurAnimRepeatCount=20, blurRadius=None, uiBlurRadius=40)
        return

    @property
    def inputManager(self):
        app = self.__appLoader.getApp()
        return app.gameInputManager

    def __handleEscape(self):
        self.destroy()

    def _initialize(self):
        self.inputManager.addEscapeListener(self.__handleEscape)
        super(TradeInConfirmationDialog, self)._initialize()

    def _finalize(self):
        self.__customBlur.fini()
        self.inputManager.removeEscapeListener(self.__handleEscape)
        super(TradeInConfirmationDialog, self)._finalize()
