# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/dialogs.py
from collections import namedtuple
import typing
from BWUtil import AsyncReturn
from async import async, await
from gui.impl.gen import R
from gui.impl.lobby.battle_pass.trophy_device_confirm_view import TrophyDeviceUpgradeConfirmView
from gui.impl.lobby.blueprints.blueprints_conversion_view import BlueprintsConversionView
from gui.impl.lobby.crew_books.crew_books_buy_dialog import CrewBooksBuyDialog
from gui.impl.lobby.crew_books.crew_books_dialog import CrewBooksDialog
from gui.impl.lobby.dialogs.exchange_with_items import ExchangeToBuyItems, ExchangeToUpgradeDevice
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
from gui.impl.lobby.dialogs.quit_game_dialog import QuitGameDialogWindow
from gui.impl.lobby.premacc.maps_blacklist_confirm_view import MapsBlacklistConfirmView
from gui.impl.lobby.battle_pass.battle_pass_voting_confirm_view import BattlePassVotingConfirmView
from gui.impl.pub.dialog_window import DialogButtons, DialogWindow
if typing.TYPE_CHECKING:
    from typing import Any, Optional, Iterable, Union
    from frameworks.wulf import View, Window
SingleDialogResult = namedtuple('SingleDialogResult', ('busy', 'result'))

@async
def show(dialog):
    dialog.load()
    result = yield await(dialog.wait())
    dialog.destroy()
    raise AsyncReturn(result)


@async
def showSimpleWithResultData(dialog, submitResults=DialogButtons.ACCEPT_BUTTONS):
    result = yield await(show(dialog))
    raise AsyncReturn((result.result in submitResults, result.data))


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
def trophyDeviceUpgradeConfirm(trophyBasicModule, parent=None):
    dialog = TrophyDeviceUpgradeConfirmView(trophyBasicModule=trophyBasicModule, parent=parent.getParentWindow() if parent is not None else None)
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
def chooseFinalRewardBattlePass(parent, data):
    dialog = FullScreenDialogWindowWrapper(BattlePassVotingConfirmView(data), parent)
    result = yield await(showSimple(dialog))
    raise AsyncReturn(result)


@async
def showExchangeToBuyItemsDialog(itemsCountMap, parent=None):
    result = yield await(showSingleDialog(layoutID=R.views.lobby.tanksetup.dialogs.ExchangeToBuyItems(), parent=parent, wrappedViewClass=ExchangeToBuyItems, itemsCountMap=itemsCountMap))
    raise AsyncReturn(result)


@async
def showSingleDialog(wrappedViewClass, layoutID, parent=None, *args, **kwargs):
    dialog = FullScreenDialogWindowWrapper.createIfNotExist(layoutID, wrappedViewClass, parent, *args, **kwargs)
    if dialog is not None:
        result = yield await(showSimple(dialog))
        raise AsyncReturn(SingleDialogResult(busy=False, result=result))
    raise AsyncReturn(SingleDialogResult(busy=True, result=None))
    return


@async
def showSingleDialogWithResultData(wrappedViewClass, layoutID, parent=None, *args, **kwargs):
    dialog = FullScreenDialogWindowWrapper.createIfNotExist(layoutID, wrappedViewClass, parent, *args, **kwargs)
    if dialog is not None:
        result = yield await(showSimpleWithResultData(dialog))
        raise AsyncReturn(SingleDialogResult(busy=False, result=result))
    raise AsyncReturn(SingleDialogResult(busy=True, result=None))
    return


@async
def showExchangeToUpgradeDeviceDialog(device, parent=None):
    result = yield await(showSingleDialog(layoutID=R.views.lobby.tanksetup.dialogs.ExchangeToUpgradeItems(), parent=parent, wrappedViewClass=ExchangeToUpgradeDevice, device=device))
    raise AsyncReturn(result)
