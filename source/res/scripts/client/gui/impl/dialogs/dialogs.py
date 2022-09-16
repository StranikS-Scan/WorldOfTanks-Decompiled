# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/dialogs.py
from collections import namedtuple
import typing
from BWUtil import AsyncReturn
from wg_async import wg_async, wg_await
from helpers import dependency
from gui.impl.gen import R
from gui.impl.lobby.battle_pass.trophy_device_confirm_view import TrophyDeviceUpgradeConfirmView
from gui.impl.lobby.blueprints.blueprints_conversion_view import BlueprintsConversionView
from gui.impl.lobby.crew_books.crew_books_buy_dialog import CrewBooksBuyDialog
from gui.impl.lobby.crew_books.crew_books_dialog import CrewBooksDialog
from gui.impl.lobby.dialogs.exchange_with_items import ExchangeToBuyItems, ExchangeToUpgradeDevice
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
from gui.impl.lobby.dialogs.quit_game_dialog import QuitGameDialogWindow
from gui.impl.lobby.premacc.maps_blacklist_confirm_view import MapsBlacklistConfirmView
from gui.impl.lobby.frontline.skill_drop_dialog import SkillDropDialog
from gui.impl.lobby.crew.free_skill_confirmation_dialog import FreeSkillConfirmationDialog
from gui.impl.pub.dialog_window import DialogButtons, DialogWindow
from skeletons.gui.impl import IGuiLoader
from frameworks.wulf import WindowStatus
if typing.TYPE_CHECKING:
    from typing import Any, Optional, Iterable, Union
    from frameworks.wulf import View
SingleDialogResult = namedtuple('SingleDialogResult', ('busy', 'result'))

@wg_async
def show(dialog):
    dialog.load()
    result = yield wg_await(dialog.wait())
    dialog.destroy()
    raise AsyncReturn(result)


@wg_async
def showSimpleWithResultData(dialog, submitResults=DialogButtons.ACCEPT_BUTTONS):
    result = yield wg_await(show(dialog))
    raise AsyncReturn((result.result in submitResults, result.data))


@wg_async
def showSimple(dialog, submitResult=DialogButtons.SUBMIT):
    result = yield wg_await(show(dialog))
    raise AsyncReturn(result.result == submitResult)


@wg_async
@dependency.replace_none_kwargs(guiLoader=IGuiLoader)
def quitGame(parent=None, guiLoader=None):

    def predicate(w):
        return isinstance(w, QuitGameDialogWindow) and w.windowStatus in (WindowStatus.LOADED, WindowStatus.LOADING)

    if guiLoader.windowsManager.findWindows(predicate):
        raise AsyncReturn(False)
    dialog = QuitGameDialogWindow(parent)
    result = yield wg_await(showSimple(dialog))
    raise AsyncReturn(result)


@wg_async
def blueprintsConversion(vehicleCD, fragmentCount=1, parent=None):
    result = yield wg_await(showSingleDialogWithResultData(layoutID=R.views.lobby.blueprints.Confirm(), wrappedViewClass=BlueprintsConversionView, parent=parent, vehicleCD=vehicleCD, fragmentsCount=fragmentCount))
    raise AsyncReturn(result.result)


@wg_async
def mapsBlacklistConfirm(mapId, cooldownTime, disabledMaps=(), parent=None):
    dialog = MapsBlacklistConfirmView(mapId=mapId, disabledMaps=disabledMaps, cooldownTime=cooldownTime, parent=parent.getParentWindow() if parent is not None else None)
    result = yield wg_await(show(dialog))
    raise AsyncReturn((result.result == DialogButtons.SUBMIT, result.data))
    return


@wg_async
def trophyDeviceUpgradeConfirm(trophyBasicModule, parent=None):
    dialog = TrophyDeviceUpgradeConfirmView(trophyBasicModule=trophyBasicModule, parent=parent.getParentWindow() if parent is not None else None)
    result = yield wg_await(show(dialog))
    raise AsyncReturn((result.result == DialogButtons.SUBMIT, result.data))
    return


@wg_async
def useCrewBook(parent, crewBookCD, vehicleIntCD, tankmanInvId):
    dialog = CrewBooksDialog(parent.getParentWindow(), crewBookCD, vehicleIntCD, tankmanInvId)
    result = yield wg_await(showSimple(dialog))
    raise AsyncReturn(result)


@wg_async
def buyCrewBook(parent, crewBookCD):
    dialog = CrewBooksBuyDialog(parent.getParentWindow(), crewBookCD)
    result = yield wg_await(showSimple(dialog))
    raise AsyncReturn(result)


@wg_async
def showExchangeToBuyItemsDialog(itemsCountMap, parent=None):
    result = yield wg_await(showSingleDialog(layoutID=R.views.lobby.tanksetup.dialogs.ExchangeToBuyItems(), parent=parent, wrappedViewClass=ExchangeToBuyItems, itemsCountMap=itemsCountMap))
    raise AsyncReturn(result)


@wg_async
def showSingleDialog(wrappedViewClass, layoutID, parent=None, *args, **kwargs):
    dialog = FullScreenDialogWindowWrapper.createIfNotExist(layoutID, wrappedViewClass, parent, *args, **kwargs)
    if dialog is not None:
        result = yield wg_await(showSimple(dialog))
        raise AsyncReturn(SingleDialogResult(busy=False, result=result))
    raise AsyncReturn(SingleDialogResult(busy=True, result=None))
    return


@wg_async
def showSingleDialogWithResultData(wrappedViewClass, layoutID, parent=None, *args, **kwargs):
    dialog = FullScreenDialogWindowWrapper.createIfNotExist(layoutID, wrappedViewClass, parent, *args, **kwargs)
    if dialog is not None:
        result = yield wg_await(showSimpleWithResultData(dialog))
        raise AsyncReturn(SingleDialogResult(busy=False, result=result))
    raise AsyncReturn(SingleDialogResult(busy=True, result=None))
    return


@wg_async
def showExchangeToUpgradeDeviceDialog(device, parent=None):
    result = yield wg_await(showSingleDialog(layoutID=R.views.lobby.tanksetup.dialogs.ExchangeToUpgradeItems(), parent=parent, wrappedViewClass=ExchangeToUpgradeDevice, device=device))
    raise AsyncReturn(result)


@wg_async
def showDropSkillDialog(tankman, price=None, isBlank=False, freeDropSave100=False):
    result = yield wg_await(showSingleDialogWithResultData(price=price, isBlank=isBlank, tankman=tankman, freeDropSave100=freeDropSave100, layoutID=SkillDropDialog.LAYOUT_ID, wrappedViewClass=SkillDropDialog))
    if result.busy:
        raise AsyncReturn((False, {}))
    else:
        isOk, _ = result.result
        raise AsyncReturn((isOk, {}))


@wg_async
def showFreeSkillConfirmationDialog(skillName, isAlreadyEarned=False):
    result = yield wg_await(showSingleDialogWithResultData(skillName=skillName, isAlreadyEarned=isAlreadyEarned, layoutID=FreeSkillConfirmationDialog.LAYOUT_ID, wrappedViewClass=FreeSkillConfirmationDialog))
    raise AsyncReturn(result)
