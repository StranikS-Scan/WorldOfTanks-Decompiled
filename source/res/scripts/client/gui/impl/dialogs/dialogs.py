# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/dialogs.py
from typing import Any, Optional, Iterable, Union, TYPE_CHECKING
from async import async, await
from BWUtil import AsyncReturn
from gui.impl.lobby.blueprints.blueprints_conversion_view import BlueprintsConversionView
from gui.impl.lobby.crew_books.crew_books_buy_dialog import CrewBooksBuyDialog
from gui.impl.lobby.crew_books.crew_books_dialog import CrewBooksDialog
from gui.impl.lobby.dialogs.quit_game_dialog import QuitGameDialogWindow
from gui.impl.lobby.premacc.maps_blacklist_confirm_view import MapsBlacklistConfirmView
from gui.impl.new_year.dialogs.buy_collection_item_dialog import BuyCollectionItemDialogWindow
from gui.impl.new_year.dialogs.buy_full_collection_dialog import BuyFullCollectionDialogWindow
from gui.impl.new_year.dialogs.set_vehicle_branch_dialog import SetVehicleBranchDialogWindow
from gui.impl.new_year.dialogs.new_year_talisman_select_confirm_dialog import NewYearTalismanSelectConfirmDialog
from gui.impl.new_year.dialogs.new_year_talisman_gift_dialog import NewYearTalismanGiftDialog
from gui.impl.pub.dialog_window import DialogButtons
if TYPE_CHECKING:
    from gui.impl.pub.dialog_window import DialogWindow
    from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView

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
    result = yield await(show(dialog))
    raise AsyncReturn((result.result == DialogButtons.SUBMIT, result.data))
    return


@async
def useCrewBook(parent, crewBookCD, vehicleIntCD, tankmanInvId):
    dialog = CrewBooksDialog(parent.getParentWindow(), crewBookCD, vehicleIntCD, tankmanInvId)
    result = yield await(showSimple(dialog))
    raise AsyncReturn(result)


@async
def buyCrewBook(parent, crewBookCD):
    dialog = CrewBooksBuyDialog(parent.getParentWindow(), crewBookCD)
    result = yield await(showSimple(dialog))
    raise AsyncReturn(result)


@async
def newYearCollectionBuyItem(toy, parent=None):
    dialog = BuyCollectionItemDialogWindow(toy, parent)
    dialog.load()
    result = yield await(dialog.wait())
    dialog.destroy()
    raise AsyncReturn(result.result == DialogButtons.PURCHASE)


@async
def newYearBuyCollection(collectionID, parent=None):
    dialog = BuyFullCollectionDialogWindow(collectionID, parent)
    dialog.load()
    result = yield await(dialog.wait())
    dialog.destroy()
    raise AsyncReturn(result.result == DialogButtons.PURCHASE)


@async
def showNYTalismanSelectConfirm(talismanType):
    dialog = NewYearTalismanSelectConfirmDialog(talismanType)
    result = yield await(showSimple(dialog, DialogButtons.PURCHASE))
    raise AsyncReturn(result)


@async
def showNYTalismanGiftDialog(talismanType):
    dialog = NewYearTalismanGiftDialog(talismanType)
    result = yield await(showSimple(dialog, DialogButtons.PURCHASE))
    raise AsyncReturn(result)


@async
def showSetVehicleBranchConfirm(invID, slotID):
    dialog = SetVehicleBranchDialogWindow(invID, slotID)
    result = yield await(showSimple(dialog, DialogButtons.PURCHASE))
    raise AsyncReturn(result)
