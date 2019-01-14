# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/simple_dialog_window.py
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.windows.simple_dialog_window_model import SimpleDialogWindowModel
from gui.impl.pub.dialog_window import DialogWindow, DialogShine, DialogContent

class SimpleDialogWindow(DialogWindow):

    def __init__(self, parent=None, shine=DialogShine.NORMAL):
        super(SimpleDialogWindow, self).__init__(content=DialogContent(R.views.simpleDialogContent(), SimpleDialogWindowModel), parent=parent)
        self._setBackgroundShine(shine)

    @property
    def contentViewModel(self):
        return self._getDecoratorViewModel().getContent().getViewModel()

    def setText(self, header, description):
        self.contentViewModel.setHeader(header)
        self.contentViewModel.setDescription(description)

    def addButton(self, name, label, isFocused=False):
        self._addButton(name, label, isFocused)
