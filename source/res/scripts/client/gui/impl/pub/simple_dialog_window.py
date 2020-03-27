# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/simple_dialog_window.py
import typing
from frameworks.wulf import ViewModel, ViewSettings
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.constants.dialog_presets import DialogPresets
from gui.impl.gen.view_models.windows.simple_dialog_window_model import SimpleDialogWindowModel
from gui.impl.pub.dialog_window import DialogContent, DialogLayer
from gui.impl.pub.pure_dialog_window import PureDialogWindow

class SimpleDialogWindow(PureDialogWindow):

    def __init__(self, bottomContent=None, parent=None, balanceContent=None, enableBlur=True, preset=DialogPresets.DEFAULT, layer=DialogLayer.TOP_WINDOW):
        contentSettings = ViewSettings(R.views.common.dialog_view.simple_dialog_content.SimpleDialogContent())
        contentSettings.model = SimpleDialogWindowModel()
        super(SimpleDialogWindow, self).__init__(bottomContent=bottomContent, parent=parent, balanceContent=balanceContent, enableBlur=enableBlur, content=DialogContent(contentSettings), layer=layer)
        self._setPreset(preset)

    @property
    def contentViewModel(self):
        content = self.content
        return content.getViewModel() if content is not None else None

    def setFormattedMessage(self, formattedMessage=''):
        if formattedMessage != '':
            self.contentViewModel.setFormattedMessage(formattedMessage)

    def setMessage(self, message, args=None, fmtArgs=None, namedFmtArgs=True):
        model = self.contentViewModel
        model.setMessage(message)
        if fmtArgs:
            self._addArgsOfModel(model.getMessageFmtArgs(), fmtArgs)
            model.setIsMessageFmtArgsNamed(namedFmtArgs)
        elif args:
            self._addArgsOfString(model.getMessageArgs(), args)
