# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/dialogs.py
import typing
from BWUtil import AsyncReturn
from th_async import th_async, th_await
from helpers import dependency
from gui.impl.gen import R
from gui.impl.lobby.battle_pass.trophy_device_confirm_view import TrophyDeviceUpgradeConfirmView
from gui.impl.lobby.blueprints.blueprints_conversion_view import BlueprintsConversionView
from gui.impl.lobby.dialogs.exchange_with_items import ExchangeToBuyItems, ExchangeToUpgradeDevice
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
from gui.impl.lobby.dialogs.quit_game_dialog import QuitGameDialogWindow
from gui.impl.lobby.premacc.maps_blacklist_confirm_view import MapsBlacklistConfirmView
from gui.impl.lobby.crew.free_skill_confirmation_dialog import FreeSkillConfirmationDialog
from gui.impl.lobby.tank_setup.upgradable_device.UpgradeDeviceView import UpgradableDeviceUpgradeConfirmView
from gui.impl.pub.dialog_window import DialogButtons, DialogWindow, SingleDialogResult
from skeletons.gui.impl import IGuiLoader
from frameworks.wulf import WindowStatus, WindowLayer
if typing.TYPE_CHECKING:
    from typing import Any, Optional, Iterable, Union
    from frameworks.wulf import View

@th_async
def show(dialog, loadCallback=None, destroyCallback=None):
    dialog.load()
    if loadCallback is not None:
        loadCallback()
    result = yield th_await(dialog.wait())
    dialog.destroy()
    if destroyCallback is not None:
        destroyCallback()
    raise AsyncReturn(result)
    return


@th_async
def showSimpleWithResultData(dialog, submitResults=DialogButtons.ACCEPT_BUTTONS):
    result = yield th_await(show(dialog))
    raise AsyncReturn((result.result in submitResults, result.data))


@th_async
def showSimple(dialog, submitResult=DialogButtons.SUBMIT, loadCallback=None, destroyCallback=None):
    result = yield th_await(show(dialog, loadCallback=loadCallback, destroyCallback=destroyCallback))
    raise AsyncReturn(result.result == submitResult)


@th_async
@dependency.replace_none_kwargs(guiLoader=IGuiLoader)
def quitGame(parent=None, guiLoader=None):

    def predicate(w):
        return isinstance(w, QuitGameDialogWindow) and w.windowStatus in (WindowStatus.LOADED, WindowStatus.LOADING)

    if guiLoader.windowsManager.findWindows(predicate):
        raise AsyncReturn(False)
    dialog = QuitGameDialogWindow(parent)
    result = yield th_await(showSimple(dialog))
    raise AsyncReturn(result)


@th_async
def blueprintsConversion(vehicleCD, fragmentCount=1, parent=None):
    result = yield th_await(showSingleDialogWithResultData(layoutID=R.views.lobby.blueprints.Confirm(), wrappedViewClass=BlueprintsConversionView, parent=parent, vehicleCD=vehicleCD, fragmentsCount=fragmentCount))
    raise AsyncReturn(result.result)


@th_async
def mapsBlacklistConfirm(mapId, cooldownTime, disabledMaps=(), parent=None):
    dialog = MapsBlacklistConfirmView(mapId=mapId, disabledMaps=disabledMaps, cooldownTime=cooldownTime, parent=parent.getParentWindow() if parent is not None else None)
    result = yield th_await(show(dialog))
    raise AsyncReturn((result.result == DialogButtons.SUBMIT, result.data))
    return


@th_async
def trophyDeviceUpgradeConfirm(trophyBasicModule, parent=None):
    dialog = TrophyDeviceUpgradeConfirmView(trophyBasicModule=trophyBasicModule, parent=parent.getParentWindow() if parent is not None else None)
    result = yield th_await(show(dialog))
    raise AsyncReturn((result.result == DialogButtons.SUBMIT, result.data))
    return


@th_async
def modernizedDeviceUpgradeConfirm(currentModule, vehicle=None, onDeconstructed=None, parent=None):
    _, result = yield th_await(showSingleDialogWithResultData(currentModule=currentModule, vehicle=vehicle, onDeconstructed=onDeconstructed, layoutID=UpgradableDeviceUpgradeConfirmView.LAYOUT_ID, wrappedViewClass=UpgradableDeviceUpgradeConfirmView, parent=parent))
    raise AsyncReturn(result)


@th_async
def showExchangeToBuyItemsDialog(itemsCountMap, parent=None):
    result = yield th_await(showSingleDialog(layoutID=R.views.lobby.tanksetup.dialogs.ExchangeToBuyItems(), parent=parent, wrappedViewClass=ExchangeToBuyItems, itemsCountMap=itemsCountMap))
    raise AsyncReturn(result)


@th_async
def showSingleDialog(wrappedViewClass, layoutID, parent=None, *args, **kwargs):
    dialog = FullScreenDialogWindowWrapper.createIfNotExist(layoutID, wrappedViewClass, parent, *args, **kwargs)
    if dialog is not None:
        result = yield th_await(showSimple(dialog))
        raise AsyncReturn(SingleDialogResult(busy=False, result=result))
    raise AsyncReturn(SingleDialogResult(busy=True, result=None))
    return


@th_async
def showSingleDialogWithResultData(wrappedViewClass, layoutID, parent=None, layer=WindowLayer.UNDEFINED, *args, **kwargs):
    dialog = FullScreenDialogWindowWrapper.createIfNotExist(layoutID, wrappedViewClass, parent, layer, *args, **kwargs)
    if dialog is not None:
        result = yield th_await(showSimpleWithResultData(dialog))
        raise AsyncReturn(SingleDialogResult(busy=False, result=result))
    raise AsyncReturn(SingleDialogResult(busy=True, result=None))
    return


@th_async
def showExchangeToUpgradeDeviceDialog(device, parent=None):
    result = yield th_await(showSingleDialog(layoutID=R.views.lobby.tanksetup.dialogs.ExchangeToUpgradeItems(), parent=parent, wrappedViewClass=ExchangeToUpgradeDevice, device=device))
    raise AsyncReturn(result)


@th_async
def showFreeSkillConfirmationDialog(skill):
    result = yield th_await(showSingleDialogWithResultData(skill=skill, layoutID=FreeSkillConfirmationDialog.LAYOUT_ID, wrappedViewClass=FreeSkillConfirmationDialog))
    raise AsyncReturn(result)


@th_async
def showLearnPerkConfirmationDialog(skill, level):
    from gui.impl.lobby.crew.dialogs.perk_learn_confirmation_dialog import PerkLearnConfirmationDialog
    result = yield th_await(showSingleDialogWithResultData(skill=skill, level=level, layoutID=PerkLearnConfirmationDialog.LAYOUT_ID, wrappedViewClass=PerkLearnConfirmationDialog))
    raise AsyncReturn(result)


@th_async
def showPerksDropDialog(tankmanId):
    from gui.impl.lobby.crew.dialogs.perks_reset_dialog import PerksResetDialog
    result = yield th_await(showSingleDialog(layoutID=PerksResetDialog.LAYOUT_ID, wrappedViewClass=PerksResetDialog, tankmanId=tankmanId))
    raise AsyncReturn(result)


@th_async
def showCrewMemberTankChangeDialog(tankmanId, vehicleCurrent=None, vehicleNew=None, parentViewKey=None):
    from gui.impl.lobby.crew.dialogs.crew_member_tank_change_dialog import CrewMemberTankChangeDialog
    result = yield th_await(showSingleDialog(layoutID=CrewMemberTankChangeDialog.LAYOUT_ID, wrappedViewClass=CrewMemberTankChangeDialog, tankmanId=tankmanId, vehicleCurrent=vehicleCurrent, vehicleNew=vehicleNew, parentViewKey=parentViewKey))
    raise AsyncReturn(result)


@th_async
def showCrewMemberRoleChangeDialog(tankmanId, vehicleCurrent=None, vehicleNew=None, role=None, parentViewKey=None):
    from gui.impl.lobby.crew.dialogs.crew_member_role_change_dialog import CrewMemberRoleChangeDialog
    result = yield th_await(showSingleDialog(layoutID=CrewMemberRoleChangeDialog.LAYOUT_ID, wrappedViewClass=CrewMemberRoleChangeDialog, tankmanId=tankmanId, vehicleCurrent=vehicleCurrent, vehicleNew=vehicleNew, role=role, parentViewKey=parentViewKey))
    raise AsyncReturn(result)


@th_async
def showRetrainDialog(tankmenIds, vehicleCD):
    from gui.impl.lobby.crew.dialogs.retrain_dialog import RetrainDialog
    result = yield th_await(showSingleDialog(layoutID=RetrainDialog.LAYOUT_ID, wrappedViewClass=RetrainDialog, tankmenIds=tankmenIds, vehicleCD=vehicleCD))
    raise AsyncReturn(result)


@th_async
def showRetrainingTankmanWindowDialog():
    from gui.impl.lobby.crew.dialogs.change_tankman_training import ChangeTankmanTrainingDialog
    result = yield th_await(showSingleDialogWithResultData(layoutID=ChangeTankmanTrainingDialog.LAYOUT_ID, wrappedViewClass=ChangeTankmanTrainingDialog))
    raise AsyncReturn(result)


@th_async
def showRecruitNewTankmanDialog(vehicleCD, slotIdx, putInTank=False):
    from gui.impl.lobby.crew.dialogs.recruit_new_tankman_dialog import RecruitNewTankmanDialog
    result = yield th_await(showSingleDialog(layoutID=RecruitNewTankmanDialog.LAYOUT_ID, wrappedViewClass=RecruitNewTankmanDialog, vehicleCD=vehicleCD, slotIdx=slotIdx, putInTank=putInTank))
    raise AsyncReturn(result)


@th_async
def showEnlargeBarracksDialog():
    from gui.impl.lobby.crew.dialogs.enlarge_barracks_dialog import EnlargeBarracksDialog
    result = yield th_await(showSimple(FullScreenDialogWindowWrapper(EnlargeBarracksDialog(), layer=WindowLayer.FULLSCREEN_WINDOW)))
    raise AsyncReturn(result)


@th_async
def showCrewBooksPurchaseDialog(crewBookCD):
    from gui.impl.lobby.crew.dialogs.crew_books_purchase_dialog import CrewBooksPurchaseDialog
    result = yield th_await(showSingleDialog(layoutID=CrewBooksPurchaseDialog.LAYOUT_ID, wrappedViewClass=CrewBooksPurchaseDialog, crewBookCD=crewBookCD))
    raise AsyncReturn(result)


@th_async
def showDocumentChangeDialog(tankmanInvID, ctx=None):
    from gui.impl.lobby.crew.dialogs.skin_change_dialog import SkinChangeDialog
    result = yield th_await(showSingleDialogWithResultData(layoutID=SkinChangeDialog.LAYOUT_ID, wrappedViewClass=SkinChangeDialog, tankmanInvID=tankmanInvID, ctx=ctx))
    raise AsyncReturn(result)


@th_async
def showSkinApplyDialog(crewSkinID, tankManInvID):
    from gui.impl.lobby.crew.dialogs.skin_apply_dialog import SkinApplyDialog
    result = yield th_await(showSingleDialogWithResultData(crewSkinID=crewSkinID, tankManInvID=tankManInvID, layoutID=SkinApplyDialog.LAYOUT_ID, wrappedViewClass=SkinApplyDialog))
    raise AsyncReturn(result)


@th_async
def showDismissTankmanDialog(tankmanId, parentViewKey=None):
    from gui.impl.lobby.crew.dialogs.dismiss_tankman_dialog import DismissTankmanDialog
    result = yield th_await(showSingleDialog(layoutID=DismissTankmanDialog.LAYOUT_ID, wrappedViewClass=DismissTankmanDialog, tankmanId=tankmanId, parentViewKey=parentViewKey))
    raise AsyncReturn(result)


@th_async
def showRestoreTankmanDialog(tankmanId, vehicleId, slotIdx, parentViewKey=None):
    from gui.impl.lobby.crew.dialogs.restore_tankman_dialog import RestoreTankmanDialog
    result = yield th_await(showSingleDialog(layoutID=RestoreTankmanDialog.LAYOUT_ID, wrappedViewClass=RestoreTankmanDialog, tankmanId=tankmanId, vehicleId=vehicleId, slotIdx=slotIdx, parentViewKey=parentViewKey))
    raise AsyncReturn(result)


@th_async
def showDismissSelectedTankmansDialog(tankmans, parentViewKey=None):
    from gui.impl.lobby.crew.dialogs.dismiss_selected_tankmans import DismissSelectedTankmans
    result = yield th_await(showSingleDialog(layoutID=DismissSelectedTankmans.LAYOUT_ID, wrappedViewClass=DismissSelectedTankmans, tankmans=tankmans, parentViewKey=parentViewKey))
    raise AsyncReturn(result)


@th_async
def showRestoreSelectedTankmansDialog(tankmans, parentViewKey=None):
    from gui.impl.lobby.crew.dialogs.restore_selected_tankmans import RestoreSelectedTankmans
    result = yield th_await(showSingleDialog(layoutID=RestoreSelectedTankmans.LAYOUT_ID, wrappedViewClass=RestoreSelectedTankmans, tankmans=tankmans, parentViewKey=parentViewKey))
    raise AsyncReturn(result)
