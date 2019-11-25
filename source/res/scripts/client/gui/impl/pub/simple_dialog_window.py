# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/simple_dialog_window.py
import typing
from frameworks.wulf import ViewModel, Array, ViewSettings
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.constants.dialog_presets import DialogPresets
from gui.impl.gen.view_models.windows.simple_dialog_window_model import SimpleDialogWindowModel
from gui.impl.pub.dialog_window import DialogWindow, DialogContent, DialogLayer

class SimpleDialogWindow(DialogWindow):

    def __init__(self, bottomContent=None, parent=None, balanceContent=None, enableBlur=True, preset=DialogPresets.DEFAULT, layer=DialogLayer.TOP_WINDOW):
        contentSettings = ViewSettings(R.views.common.dialog_view.simple_dialog_content.SimpleDialogContent())
        contentSettings.model = SimpleDialogWindowModel()
        super(SimpleDialogWindow, self).__init__(bottomContent=bottomContent, parent=parent, balanceContent=balanceContent, enableBlur=enableBlur, content=DialogContent(contentSettings), layer=layer)
        self._setPreset(preset)

    @property
    def contentViewModel(self):
        content = self.content
        return content.getViewModel() if content is not None else None

    def setTitle(self, title=R.invalid(), args=None, fmtArgs=None, namedFmtArgs=True):
        model = self.viewModel
        if title != R.invalid():
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

    def addButton(self, name, label, isFocused=False, invalidateAll=False, soundDown=None):
        self._addButton(name, label, isFocused, invalidateAll, soundDown=soundDown)

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
