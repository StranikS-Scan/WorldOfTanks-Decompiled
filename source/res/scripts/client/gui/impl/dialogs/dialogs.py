# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/dialogs.py
from typing import Any, Optional, Iterable
from async import async, await
from BWUtil import AsyncReturn
from gui.impl.lobby.blueprints.blueprints_conversion_view import BlueprintsConversionView
from gui.impl.lobby.dialogs.quit_game_dialog import QuitGameDialogWindow
from gui.impl.lobby.premacc.maps_blacklist_confirm_view import MapsBlacklistConfirmView
from gui.impl.pub.dialog_window import DialogWindow
from gui.impl.pub.dialog_window import DialogButtons

@async
def show(dialog):
    dialog.load()
    result = yield await(dialog.wait())
    dialog.destroy()
    raise AsyncReturn(result)


@async
def showSimple(dialog, submitResult=DialogButtons.SUBMIT):
    result = yield await(show(dialog))
    raise AsyncReturn(result.result == submitResult)


@async
def quitGame(parent):
    dialog = QuitGameDialogWindow(parent.getParentWindow())
    result = yield await(showSimple(dialog))
    raise AsyncReturn(result)


@async
def blueprintsConversion(vehicleCD, fragmentCount=1, parent=None):
    dialog = BlueprintsConversionView(vehicleCD, fragmentCount, parent.getParentWindow() if parent is not None else None)
    result = yield await(showSimple(dialog, DialogButtons.RESEARCH))
    raise AsyncReturn(result)
    return


@async
def mapsBlacklistConfirm(mapId, cooldownTime, disabledMaps=(), parent=None):
    dialog = MapsBlacklistConfirmView(mapId=mapId, disabledMaps=disabledMaps, cooldownTime=cooldownTime, parent=parent.getParentWindow() if parent is not None else None)
    result = yield await(show(dialog.wait()))
    raise AsyncReturn((result.result == DialogButtons.SUBMIT, result.data))
    return
