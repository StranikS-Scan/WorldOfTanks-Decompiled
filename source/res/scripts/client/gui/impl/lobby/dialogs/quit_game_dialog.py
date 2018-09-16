# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/quit_game_dialog.py
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.windows.simple_dialog_window_model import SimpleDialogWindowModel
from gui.impl.pub.dialog_window import DialogWindow, DialogShine, DialogButtons, DialogContent

class QuitGameDialogWindow(DialogWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(QuitGameDialogWindow, self).__init__(content=DialogContent(R.views.quitGameDialogContent, SimpleDialogWindowModel), parent=parent)
        self._setBackgroundShine(DialogShine.NONE)
        self._addButton(DialogButtons.SUBMIT, R.strings.dialogs.quit.submit)
        self._addButton(DialogButtons.CANCEL, R.strings.dialogs.quit.cancel, True)
        self.viewModel.setBackgroundImage(R.images.gui.maps.uiKit.dialogs.quit_bg)
        self.contentViewModel.setHeader(R.strings.dialogs.quit.title)
