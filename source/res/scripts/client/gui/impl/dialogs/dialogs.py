# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/dialogs.py
from collections import namedtuple
import typing
from BWUtil import AsyncReturn
from async import async, await
from frameworks.wulf.gui_constants import WindowLayer
from helpers import dependency
from gui.impl.gen import R
from gui.impl.lobby.battle_pass.trophy_device_confirm_view import TrophyDeviceUpgradeConfirmView
from gui.impl.lobby.blueprints.blueprints_conversion_view import BlueprintsConversionView
from gui.impl.lobby.crew_books.crew_books_buy_dialog import CrewBooksBuyDialog
from gui.impl.lobby.crew_books.crew_books_dialog import CrewBooksDialog
from gui.impl.lobby.detachment.dialogs.buy_carousel_slot_dialog_view import BuyCarouselSlotDialogView
from gui.impl.lobby.detachment.dialogs.buy_dormitory_dialog_view import BuyDormitoryDialogView, BuyDormitoryReason
from gui.impl.lobby.detachment.dialogs.buy_vehicle_slot_dialog_view import BuyVehicleSlotDialogView
from gui.impl.lobby.detachment.dialogs.confirm_instructor_nation_change_view import ConfirmInstructorNationChangeView
from gui.impl.lobby.detachment.dialogs.convert_currency_view import ConvertCurrencyForVehicleView, ConvertCurrencyForRestoreDetachmentView, ConvertCurrencyForCrewbookView, ConvertCurrencyForRestoreTankmanView, ConvertCurrencyForSaveMatrixView
from gui.impl.lobby.detachment.dialogs.demount_instructor_dialog_view import DemountInstructorDialogView
from gui.impl.lobby.detachment.dialogs.recover_instructor_dialog_view import RecoverInstructorDialogView
from gui.impl.lobby.dialogs.exchange_with_items import ExchangeToBuyItems, ExchangeToUpgradeDevice
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
from gui.impl.lobby.dialogs.quit_game_dialog import QuitGameDialogWindow
from gui.impl.lobby.premacc.maps_blacklist_confirm_view import MapsBlacklistConfirmView
from gui.impl.pub.dialog_window import DialogButtons, DialogWindow
from skeletons.gui.impl import IGuiLoader
from frameworks.wulf import WindowStatus
if typing.TYPE_CHECKING:
    from typing import Any, Optional, Iterable, Union
    from frameworks.wulf import View
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
@dependency.replace_none_kwargs(guiLoader=IGuiLoader)
def quitGame(parent=None, guiLoader=None):

    def predicate(w):
        return isinstance(w, QuitGameDialogWindow) and w.windowStatus in (WindowStatus.LOADED, WindowStatus.LOADING)

    if guiLoader.windowsManager.findWindows(predicate):
        raise AsyncReturn(False)
    dialog = QuitGameDialogWindow(parent)
    result = yield await(showSimple(dialog))
    raise AsyncReturn(result)


@async
def blueprintsConversion(vehicleCD, fragmentCount=1, parent=None):
    result = yield await(showSingleDialogWithResultData(layoutID=R.views.lobby.blueprints.Confirm(), wrappedViewClass=BlueprintsConversionView, parent=parent, vehicleCD=vehicleCD, fragmentsCount=fragmentCount))
    raise AsyncReturn(result.result)


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
def showExchangeToBuyItemsDialog(itemsCountMap, parent=None):
    result = yield await(showSingleDialog(layoutID=R.views.lobby.tanksetup.dialogs.ExchangeToBuyItems(), parent=parent, wrappedViewClass=ExchangeToBuyItems, itemsCountMap=itemsCountMap))
    raise AsyncReturn(result)


@async
def _showDialog(showFunc, wrappedViewClass, layoutID, parent, blurLayers, *args, **kwargs):
    dialog = FullScreenDialogWindowWrapper.createIfNotExist(layoutID, wrappedViewClass, parent, blurLayers, *args, **kwargs)
    if dialog is not None:
        result = yield await(showFunc(dialog))
        raise AsyncReturn(SingleDialogResult(busy=False, result=result))
    raise AsyncReturn(SingleDialogResult(busy=True, result=None))
    return


@async
def showDialog(wrappedViewClass, layoutID, parent=None, blurLayers=True, *args, **kwargs):
    result = yield await(_showDialog(show, wrappedViewClass, layoutID, parent, blurLayers, *args, **kwargs))
    raise AsyncReturn(result)


@async
def showSingleDialog(wrappedViewClass, layoutID, parent=None, blurLayers=True, *args, **kwargs):
    result = yield await(_showDialog(showSimple, wrappedViewClass, layoutID, parent, blurLayers, *args, **kwargs))
    raise AsyncReturn(result)


@async
def showSingleDialogWithResultData(wrappedViewClass, layoutID, parent=None, blurLayers=True, *args, **kwargs):
    result = yield await(_showDialog(showSimpleWithResultData, wrappedViewClass, layoutID, parent, blurLayers, *args, **kwargs))
    raise AsyncReturn(result)


@async
def showExchangeToUpgradeDeviceDialog(device, parent=None):
    result = yield await(showSingleDialog(layoutID=R.views.lobby.tanksetup.dialogs.ExchangeToUpgradeItems(), parent=parent, wrappedViewClass=ExchangeToUpgradeDevice, device=device))
    raise AsyncReturn(result)


@async
def buyDormitory(parent, countBlocks=1, reason=BuyDormitoryReason.GENERAL_BUY):
    result = yield await(showSingleDialog(layoutID=R.views.lobby.detachment.dialogs.BuyDormitoryDialogView(), parent=parent, blurLayers=False, wrappedViewClass=BuyDormitoryDialogView, countBlocks=countBlocks, reason=reason))
    raise AsyncReturn(result)


@async
def buyVehicleSlot(parent, ctx):
    result = yield await(showSingleDialog(layoutID=R.views.lobby.detachment.dialogs.BuyVehicleSlotDialogView(), parent=parent, blurLayers=False, wrappedViewClass=BuyVehicleSlotDialogView, ctx=ctx))
    raise AsyncReturn(result)


@async
def demountInstructor(parent, ctx, returnSelectedItem=False):
    wrapper = FullScreenDialogWindowWrapper(DemountInstructorDialogView(ctx), parent=parent)
    if returnSelectedItem:
        result = yield await(showSimpleWithResultData(wrapper))
    else:
        result = yield await(showSimple(wrapper))
    raise AsyncReturn(result)


@async
def confirmInstructorNationChange(parent, ctx):
    wrapper = FullScreenDialogWindowWrapper(ConfirmInstructorNationChangeView(ctx), parent=parent)
    result = yield await(showSimple(wrapper))
    raise AsyncReturn(result)


@async
def recoverInstructor(parent, ctx):
    wrapper = FullScreenDialogWindowWrapper(RecoverInstructorDialogView(ctx), parent=parent)
    result = yield await(showSimple(wrapper))
    raise AsyncReturn(result)


@async
def saveMatrix(parent, ctx):
    from gui.impl.lobby.detachment.dialogs.save_matrix_dialog_view import SaveMatrixDialogView
    result = yield await(showDialog(layoutID=R.views.lobby.detachment.dialogs.SaveMatrixDialogView(), parent=parent, wrappedViewClass=SaveMatrixDialogView, ctx=ctx))
    raise AsyncReturn(result)


@async
def showConvertCurrencyForSaveMatrixView(ctx):
    result = yield await(showDialog(layoutID=R.views.lobby.detachment.dialogs.ConvertCurrencyView(), wrappedViewClass=ConvertCurrencyForSaveMatrixView, blurLayers=False, ctx=ctx, layer=WindowLayer.OVERLAY))
    raise AsyncReturn(result)


@async
def showDetachmentChangeCommanderDialogView(parent, ctx):
    from gui.impl.lobby.detachment.dialogs.change_commander_dialog_view import ChangeCommanderDialogView
    result = yield await(showDialog(layoutID=R.views.lobby.detachment.dialogs.ChangeCommanderDialogView(), wrappedViewClass=ChangeCommanderDialogView, parent=parent, blurLayers=False, ctx=ctx))
    raise AsyncReturn(result)


@async
def showDetachmentNewCommanderDialogView(parent, ctx):
    from gui.impl.lobby.detachment.dialogs.change_commander_dialog_view import NewCommanderDialogView
    result = yield await(showDialog(layoutID=R.views.lobby.detachment.dialogs.ChangeCommanderDialogView(), wrappedViewClass=NewCommanderDialogView, parent=parent, ctx=ctx))
    raise AsyncReturn(result)


@async
def showDetachmentDemobilizeDialogView(detInvID, reason):
    from gui.impl.lobby.detachment.dialogs.demobilize_detachment_dialog_view import DemobilizeDetachmentDialogView
    sdr = yield await(showDialog(layoutID=R.views.lobby.detachment.dialogs.DemobilizeDetachmentDialogView(), wrappedViewClass=DemobilizeDetachmentDialogView, blurLayers=False, ctx={'detInvID': detInvID,
     'reason': reason}))
    raise AsyncReturn(sdr)


@async
def showDetachmentRestoreDialogView(detInvID):
    from gui.impl.lobby.detachment.dialogs.restore_detachment_dialog_view import RestoreDetachmentDialogView
    sdr = yield await(showDialog(layoutID=R.views.lobby.detachment.dialogs.RestoreDetachmentDialogView(), wrappedViewClass=RestoreDetachmentDialogView, blurLayers=False, ctx={'detInvID': detInvID}))
    raise AsyncReturn(sdr)


@async
def showReplaceDetachmentDialogView():
    from gui.impl.lobby.detachment.dialogs.replace_detachment_dialog_view import ReplaceDetachmentDialogView
    wrapper = FullScreenDialogWindowWrapper(ReplaceDetachmentDialogView(), blurLayers=False)
    result = yield showSimple(wrapper)
    raise AsyncReturn(result)


@async
def showApplyCrewBookDetachmentDialogView(detInvID, bookCD):
    from gui.impl.lobby.detachment.dialogs.apply_crew_book_dialog_view import ApplyCrewBookDialogView
    sdr = yield await(showDialog(layoutID=R.views.lobby.detachment.dialogs.ApplyCrewBookDialogView(), wrappedViewClass=ApplyCrewBookDialogView, blurLayers=False, ctx={'detInvID': detInvID,
     'bookCD': bookCD}))
    raise AsyncReturn(sdr)


@async
def showApplyExpExchangeDetachmentDialogView(freeXP, detachXPRate, isMaxLevel):
    from gui.impl.lobby.detachment.dialogs.apply_exp_exchange_dialog_view import ApplyExpExchangeDialogView
    dialog = ApplyExpExchangeDialogView(freeXP, detachXPRate, isMaxLevel)
    wrapper = FullScreenDialogWindowWrapper(dialog, blurLayers=False)
    result = yield showSimple(wrapper)
    raise AsyncReturn(result)


@async
def showConfirmCrewBookPurchaseDetachmentDialogView(bookCD):
    from gui.impl.lobby.detachment.dialogs.confirm_crew_book_purchase_dialog_view import ConfirmCrewBookPurchaseDialogView
    sdr = yield await(showDialog(layoutID=R.views.lobby.detachment.dialogs.ConfirmCrewBookPurchaseDialogView(), wrappedViewClass=ConfirmCrewBookPurchaseDialogView, blurLayers=False, ctx={'bookCD': bookCD}))
    raise AsyncReturn(sdr)


@async
def showIntroVideoDialogView(withClosingDialog=False):
    from gui.impl.lobby.detachment.intro_video_window_view import DetachmentIntroVideoWindow
    window = DetachmentIntroVideoWindow(withClosingDialog=withClosingDialog)
    result = yield await(showSimple(window))
    raise AsyncReturn(result)


@async
def showCloseIntroVideoDialogView(blurLayers=False):
    from gui.impl.lobby.detachment.dialogs.close_intro_video_dialog_view import CloseIntroVideoDialogView
    wrapper = FullScreenDialogWindowWrapper(CloseIntroVideoDialogView(), blurLayers=blurLayers)
    result = yield await(showSimple(wrapper))
    raise AsyncReturn(result)


@async
def showConvertCurrencyForVehicleView(ctx):
    result = yield await(showDialog(layoutID=R.views.lobby.detachment.dialogs.ConvertCurrencyView(), wrappedViewClass=ConvertCurrencyForVehicleView, blurLayers=False, ctx=ctx, layer=WindowLayer.OVERLAY))
    raise AsyncReturn(result)


@async
def showBuyCarouselSlotView():
    result = yield await(showSingleDialog(layoutID=R.views.lobby.detachment.dialogs.BuyCarouselSlotDialogView(), wrappedViewClass=BuyCarouselSlotDialogView, blurLayers=False))
    raise AsyncReturn(result)


@async
def showConvertCurrencyForCrewBookView(ctx):
    result = yield await(showDialog(layoutID=R.views.lobby.detachment.dialogs.ConvertCurrencyView(), wrappedViewClass=ConvertCurrencyForCrewbookView, blurLayers=False, ctx=ctx, layer=WindowLayer.OVERLAY))
    raise AsyncReturn(result)


@async
def showConvertCurrencyForRestoreDetachmentView(ctx):
    result = yield await(showDialog(layoutID=R.views.lobby.detachment.dialogs.ConvertCurrencyView(), wrappedViewClass=ConvertCurrencyForRestoreDetachmentView, blurLayers=False, ctx=ctx, layer=WindowLayer.OVERLAY))
    raise AsyncReturn(result)


@async
def showConvertCurrencyForRestoreTankmanView(ctx):
    result = yield await(showDialog(layoutID=R.views.lobby.detachment.dialogs.ConvertCurrencyView(), wrappedViewClass=ConvertCurrencyForRestoreTankmanView, blurLayers=False, ctx=ctx, layer=WindowLayer.OVERLAY))
    raise AsyncReturn(result)


@async
def showRestoreRecruitDialogView(parent, recruitID):
    from gui.impl.lobby.detachment.dialogs.restore_recruit_dialog_view import RestoreRecruitDialogView
    result = yield await(showSingleDialogWithResultData(layoutID=R.views.lobby.detachment.dialogs.RestoreRecruitDialogView(), parent=parent, wrappedViewClass=RestoreRecruitDialogView, recruitID=recruitID))
    raise AsyncReturn(result)


@async
def showTrainVehicleConfirmView(parent, detachmentInvID, slotIndex, selectedVehicleCD):
    from gui.impl.lobby.detachment.dialogs.train_vehicle_confirm_view import TrainVehicleConfirmView
    result = yield await(showSingleDialogWithResultData(layoutID=R.views.lobby.detachment.dialogs.TrainVehicleConfirmView(), parent=parent, blurLayers=False, wrappedViewClass=TrainVehicleConfirmView, detachmentInvID=detachmentInvID, slotIndex=slotIndex, selectedVehicleCD=selectedVehicleCD))
    raise AsyncReturn(result)


@async
def showSelectAssignMethodView(parent, detachmentInvID, vehicle):
    from gui.impl.lobby.detachment.dialogs.select_assign_method_view import SelectAssignMethodView
    result = yield await(showSingleDialogWithResultData(wrappedViewClass=SelectAssignMethodView, layoutID=R.views.lobby.detachment.dialogs.SelectAssignMethodView(), parent=parent, detachmentInvID=detachmentInvID, vehicle=vehicle))
    raise AsyncReturn(result)


@async
def showDetachmentConfrimExpOverflowDialogView(experienceOverflow):
    from gui.impl.lobby.detachment.dialogs.confirm_exp_overflow_dialog_view import ConfirmExpOverflowDialogView
    result = yield await(showSingleDialogWithResultData(wrappedViewClass=ConfirmExpOverflowDialogView, layoutID=R.views.lobby.detachment.dialogs.ConfirmExpOverflowView(), blurLayers=False, ctx={'xpOverflow': experienceOverflow}))
    raise AsyncReturn(result)


@async
def showDetachmentConfirmUnpackingDialogView(ctx):
    from gui.impl.lobby.detachment.dialogs.confirm_unpacking_dialog_view import ConfirmUnpackingDialogView
    result = yield await(showSingleDialogWithResultData(wrappedViewClass=ConfirmUnpackingDialogView, layoutID=R.views.lobby.detachment.dialogs.ConfirmUnpackingDialogView(), blurLayers=False, ctx=ctx))
    raise AsyncReturn(result)
