# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs.py
from async import async, await
from BWUtil import AsyncReturn
from gui.impl.gen import R
from gui.impl.lobby.dialogs.quit_game_dialog import QuitGameDialogWindow
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.pub.simple_dialog_window import SimpleDialogWindow
from gui.impl.pub.dialog_window import DialogShine

@async
def simple(parent, message, buttons=R.strings.dialogs.common, focused=DialogButtons.SUBMIT, shine=DialogShine.NONE):
    dialog = SimpleDialogWindow(parent.getParentWindow(), shine)
    for name in DialogButtons.ALL:
        button = message.dyn(name) or buttons.dyn(name)
        isFocused = name == focused
        if button.exists():
            dialog.addButton(name, button(), isFocused)

    dialog.setText(message.dyn('title')(), message.dyn('message')())
    dialog.load()
    result = yield await(dialog.wait())
    dialog.destroy()
    raise AsyncReturn(result == DialogButtons.SUBMIT)


@async
def info(parent, message, buttons=R.strings.dialogs.common, focused=DialogButtons.SUBMIT):
    result = yield await(simple(parent, message, buttons, focused, DialogShine.NORMAL))
    raise AsyncReturn(result)


@async
def warning(parent, message, buttons=R.strings.dialogs.common, focused=DialogButtons.SUBMIT):
    result = yield await(simple(parent, message, buttons, focused, DialogShine.YELLOW))
    raise AsyncReturn(result)


@async
def error(parent, message, buttons=R.strings.dialogs.common, focused=DialogButtons.SUBMIT):
    result = yield await(simple(parent, message, buttons, focused, DialogShine.RED))
    raise AsyncReturn(result)


@async
def quitGame(parent):
    dialog = QuitGameDialogWindow(parent.getParentWindow())
    dialog.load()
    result = yield await(dialog.wait())
    dialog.destroy()
    raise AsyncReturn(result == DialogButtons.SUBMIT)
