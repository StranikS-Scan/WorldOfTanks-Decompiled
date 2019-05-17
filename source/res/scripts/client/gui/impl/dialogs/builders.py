# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/builders.py
from collections import namedtuple
import logging
from typing import Iterable, Any, Optional
from gui.impl.pub.simple_dialog_window import SimpleDialogWindow
from gui.impl.gen import R
from gui.impl.pub.dialog_window import DialogButtons, DialogLayer
from gui.impl.lobby.dialogs.contents.common_balance_content import CommonBalanceContent
from gui.impl.gen.view_models.constants.dialog_presets import DialogPresets
from gui.impl.gen_utils import DynAccessor
from gui.impl.gen.view_models.common.format_string_arg_model import FormatStringArgModel
_logger = logging.getLogger(__name__)
_MessageArgs = namedtuple('_MessageArgs', ('args', 'fmtArgs', 'namedFmtArgs'))
_DialogButton = namedtuple('DialogButton', ('name', 'label', 'isFocused', 'soundDown'))

def _makeMessageArgs(args=None, fmtArgs=None, namedFmtArgs=None):
    return _MessageArgs(args, fmtArgs, namedFmtArgs)


class SimpleDialogBuilder(object):
    __slots__ = ('__message', '__title', '__messageArgs', '__titleArgs', '__buttons', '__icon', '__backImg', '__showBalance', '__preset', '__layer')

    def __init__(self):
        super(SimpleDialogBuilder, self).__init__()
        self.__message = R.invalid()
        self.__title = R.invalid()
        self.__messageArgs = _makeMessageArgs()
        self.__titleArgs = _makeMessageArgs()
        self.__buttons = []
        self.__icon = R.invalid()
        self.__backImg = R.invalid()
        self.__showBalance = False
        self.__preset = DialogPresets.DEFAULT
        self.__layer = DialogLayer.TOP_WINDOW

    def build(self, parent):
        if self.__message == R.invalid():
            _logger.error("Dialog message can't be empty")
            return
        elif not self.__buttons:
            _logger.error("Dialog buttons can't be empty")
            return
        else:
            dialog = SimpleDialogWindow(parent=parent.getParentWindow(), preset=self.__preset, balanceContent=CommonBalanceContent() if self.__showBalance else None, layer=self.__layer)
            for btn in self.__buttons:
                dialog.addButton(btn.name, btn.label, btn.isFocused, soundDown=btn.soundDown)

            messageArgs = self.__messageArgs
            titleArgs = self.__titleArgs
            dialog.setTitle(self.__title, titleArgs.args, titleArgs.fmtArgs, titleArgs.namedFmtArgs)
            dialog.setMessage(self.__message, messageArgs.args, messageArgs.fmtArgs, messageArgs.namedFmtArgs)
            if self.__icon is not None:
                dialog.setIcon(self.__icon)
            if self.__backImg is not None:
                dialog.setBackground(self.__backImg)
            return dialog

    def setMessage(self, message):
        self.__message = message
        return self

    def setMessageArgs(self, args=None, fmtArgs=None, namedFmtArgs=True):
        self.__messageArgs = _MessageArgs(args, fmtArgs, namedFmtArgs)
        return self

    def setTitle(self, title):
        self.__title = title
        return self

    def setTitleArgs(self, args=None, fmtArgs=None, namedFmtArgs=True):
        self.__titleArgs = _MessageArgs(args, fmtArgs, namedFmtArgs)
        return self

    def addButton(self, name, label, isFocused, soundDown=None):
        self.__buttons.append(_DialogButton(name, label, isFocused, soundDown))
        return self

    def setIcon(self, icon):
        self.__icon = icon
        return self

    def setBackImg(self, image):
        self.__backImg = image
        return self

    def setPreset(self, preset):
        self.__preset = preset
        return self

    def setLayer(self, layer):
        self.__layer = layer
        return self

    def setShowBalance(self, showBalance):
        self.__showBalance = showBalance
        return self


class ResSimpleDialogBuilder(SimpleDialogBuilder):

    def setMessagesAndButtons(self, message, buttons=R.strings.dialogs.common, focused=DialogButtons.SUBMIT, btnDownSounds=None):
        self.setMessage(message.dyn('message')())
        self.setTitle(message.dyn('title')())
        for _id in DialogButtons.ALL:
            button = message.dyn(_id) or buttons.dyn(_id)
            if button.exists():
                soundDown = None if not btnDownSounds else btnDownSounds.get(_id, None)
                self.addButton(_id, button(), _id == focused, soundDown=soundDown)

        return self


class InfoDialogBuilder(ResSimpleDialogBuilder):

    def __init__(self):
        super(InfoDialogBuilder, self).__init__()
        self.setPreset(DialogPresets.INFO)


class WarningDialogBuilder(ResSimpleDialogBuilder):

    def __init__(self):
        super(WarningDialogBuilder, self).__init__()
        self.setPreset(DialogPresets.WARNING)


class ErrorDialogBuilder(ResSimpleDialogBuilder):

    def __init__(self):
        super(ErrorDialogBuilder, self).__init__()
        self.setPreset(DialogPresets.ERROR)
