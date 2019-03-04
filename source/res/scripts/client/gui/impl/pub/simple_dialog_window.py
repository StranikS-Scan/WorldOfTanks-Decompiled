# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/simple_dialog_window.py
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.constants.dialog_presets import DialogPresets
from gui.impl.gen.view_models.windows.simple_dialog_window_model import SimpleDialogWindowModel
from gui.impl.pub.dialog_window import DialogWindow, DialogContent, DialogLayer

class SimpleDialogWindow(DialogWindow):

    def __init__(self, bottomContent=None, parent=None, balanceContent=None, enableBlur=True, preset=DialogPresets.DEFAULT, layer=DialogLayer.TOP_WINDOW):
        super(SimpleDialogWindow, self).__init__(bottomContent=bottomContent, parent=parent, balanceContent=balanceContent, enableBlur=enableBlur, content=DialogContent(R.views.simpleDialogContent(), SimpleDialogWindowModel), layer=layer)
        self._setPreset(preset)

    @property
    def contentViewModel(self):
        return self._getDecoratorViewModel().getContent().getViewModel()

    def setTitle(self, title, args=None, fmtArgs=None, namedFmtArgs=True):
        model = self.viewModel
        model.setTitle(title)
        if fmtArgs:
            self.__addArgsOfModel(model.getTitleFmtArgs(), fmtArgs)
            model.setIsTitleFmtArgsNamed(namedFmtArgs)
        elif args:
            self.__addArgsOfString(model.getTitleArgs(), args)

    def setMessage(self, message, args=None, fmtArgs=None, namedFmtArgs=True):
        model = self.contentViewModel
        model.setMessage(message)
        if fmtArgs:
            self.__addArgsOfModel(model.getMessageFmtArgs(), fmtArgs)
            model.setIsMessageFmtArgsNamed(namedFmtArgs)
        elif args:
            self.__addArgsOfString(model.getMessageArgs(), args)

    def setIcon(self, icon):
        self.viewModel.setIcon(icon)

    def addButton(self, name, label, isFocused=False, invalidateAll=False):
        self._addButton(name, label, isFocused, invalidateAll)

    def setBackground(self, backImg):
        self.viewModel.setBackgroundImage(backImg)

    @staticmethod
    def __addArgsOfModel(arrModel, args):
        for arg in args:
            arrModel.addViewModel(arg)

        arrModel.invalidate()

    @staticmethod
    def __addArgsOfString(arrModel, args):
        for arg in args:
            arrModel.addString(arg)

        arrModel.invalidate()
