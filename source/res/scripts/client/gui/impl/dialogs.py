# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs.py
from async import async, await
from BWUtil import AsyncReturn
from gui.impl.gen import R
from gui.impl.gen.view_models.constants.dialog_presets import DialogPresets
from gui.impl.lobby.blueprints.blueprints_conversion_view import BlueprintsConversionView
from gui.impl.lobby.dialogs.quit_game_dialog import QuitGameDialogWindow
from gui.impl.lobby.dialogs.contents.common_balance_content import CommonBalanceContent
from gui.impl.lobby.premacc.maps_blacklist_confirm_view import MapsBlacklistConfirmView
from gui.impl.pub.dialog_window import DialogButtons, DialogLayer
from gui.impl.pub.simple_dialog_window import SimpleDialogWindow

@async
def simple(parent, message, titleArgs=None, titleFmtArgs=None, messageArgs=None, messageFmtArgs=None, icon=None, backImg=None, showBalance=False, buttons=R.strings.dialogs.common, focused=DialogButtons.SUBMIT, preset=DialogPresets.DEFAULT, layer=DialogLayer.TOP_WINDOW):
    balance = CommonBalanceContent() if showBalance else None
    dialog = SimpleDialogWindow(parent=parent.getParentWindow(), preset=preset, balanceContent=balance, layer=layer)
    for name in DialogButtons.ALL:
        button = message.dyn(name) or buttons.dyn(name)
        isFocused = name == focused
        if button.exists():
            dialog.addButton(name, button(), isFocused)

    dialog.setTitle(message.dyn('title')(), titleArgs, titleFmtArgs)
    dialog.setMessage(message.dyn('message')(), messageArgs, messageFmtArgs)
    if icon is not None:
        dialog.setIcon(icon)
    if backImg is not None:
        dialog.setBackground(backImg)
    dialog.load()
    result = yield await(dialog.wait())
    dialog.destroy()
    raise AsyncReturn(result == DialogButtons.SUBMIT)
    return


@async
def info(parent, message, titleArgs=None, titleFmtArgs=None, messageArgs=None, messageFmtArgs=None, showBalance=False, buttons=R.strings.dialogs.common, focused=DialogButtons.SUBMIT):
    result = yield await(simple(parent, message, titleArgs, titleFmtArgs, messageArgs, messageFmtArgs, None, None, showBalance, buttons, focused, DialogPresets.INFO))
    raise AsyncReturn(result)
    return


@async
def warning(parent, message, titleArgs=None, titleFmtArgs=None, messageArgs=None, messageFmtArgs=None, showBalance=False, buttons=R.strings.dialogs.common, focused=DialogButtons.SUBMIT):
    result = yield await(simple(parent, message, titleArgs, titleFmtArgs, messageArgs, messageFmtArgs, None, None, showBalance, buttons, focused, DialogPresets.WARNING))
    raise AsyncReturn(result)
    return


@async
def error(parent, message, titleArgs=None, titleFmtArgs=None, messageArgs=None, messageFmtArgs=None, showBalance=False, buttons=R.strings.dialogs.common, focused=DialogButtons.SUBMIT):
    result = yield await(simple(parent, message, titleArgs, titleFmtArgs, messageArgs, messageFmtArgs, None, None, showBalance, buttons, focused, DialogPresets.ERROR))
    raise AsyncReturn(result)
    return


@async
def quitGame(parent):
    dialog = QuitGameDialogWindow(parent.getParentWindow())
    dialog.load()
    result = yield await(dialog.wait())
    dialog.destroy()
    raise AsyncReturn(result == DialogButtons.SUBMIT)


@async
def blueprintsConversion(vehicleCD, fragmentCount=1, parent=None):
    dialog = BlueprintsConversionView(vehicleCD, fragmentCount, parent.getParentWindow() if parent is not None else None)
    dialog.load()
    result = yield await(dialog.wait())
    dialog.destroy()
    raise AsyncReturn(result == DialogButtons.RESEARCH)
    return


@async
def mapsBlacklistConfirm(mapId, cooldownTime, disabledMaps=(), parent=None):
    dialog = MapsBlacklistConfirmView(mapId=mapId, disabledMaps=disabledMaps, cooldownTime=cooldownTime, parent=parent.getParentWindow() if parent is not None else None)
    dialog.load()
    result = yield await(dialog.wait())
    choice = dialog.getSelectedMap()
    dialog.destroy()
    raise AsyncReturn((result == DialogButtons.SUBMIT, choice))
    return
