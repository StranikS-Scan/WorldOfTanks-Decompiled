# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/dialogs.py
import typing
from BWUtil import AsyncReturn
from frameworks.wulf import WindowStatus
from gui.impl.gen import R
from gui.impl.lobby.battle_pass.trophy_device_confirm_view import TrophyDeviceUpgradeConfirmView
from gui.impl.lobby.blueprints.blueprints_conversion_view import BlueprintsConversionView
from gui.impl.lobby.crew.crew_helpers.tankman_helpers import isPremiumRetrainWarning
from gui.impl.lobby.crew.dialogs.skills_training_confirm_dialog import SkillsTrainingConfirmDialog
from gui.impl.lobby.crew.free_skill_confirmation_dialog import FreeSkillConfirmationDialog
from gui.impl.lobby.dialogs.exchange_with_items import ExchangeToBuyItems, ExchangeToUpgradeDevice
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
from gui.impl.lobby.dialogs.quit_game_dialog import QuitGameDialogWindow
from gui.impl.lobby.premacc.maps_blacklist_confirm_view import MapsBlacklistConfirmView
from gui.impl.lobby.tank_setup.upgradable_device.UpgradeDeviceView import UpgradableDeviceUpgradeConfirmView
from gui.impl.pub.dialog_window import DialogButtons, DialogWindow, SingleDialogResult
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from wg_async import wg_async, wg_await
if typing.TYPE_CHECKING:
    from typing import Any, Optional, Iterable, Union, List

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
def modernizedDeviceUpgradeConfirm(currentModule, vehicle=None, onDeconstructed=None, parent=None):
    _, result = yield wg_await(showSingleDialogWithResultData(currentModule=currentModule, vehicle=vehicle, onDeconstructed=onDeconstructed, layoutID=UpgradableDeviceUpgradeConfirmView.LAYOUT_ID, wrappedViewClass=UpgradableDeviceUpgradeConfirmView, parent=parent))
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
@dependency.replace_none_kwargs(gui=IGuiLoader)
def showCustomBlurSingleDialog(wrappedViewClass, layoutID, parent=None, gui=None, *args, **kwargs):
    result = None
    dialog = gui.windowsManager.getViewByLayoutID(layoutID)
    if dialog is None:
        dialog = FullScreenDialogWindowWrapper(wrappedViewClass(*args, **kwargs), parent, doBlur=False)
    if dialog is not None:
        result = yield wg_await(showSimpleWithResultData(dialog))
    raise AsyncReturn(SingleDialogResult(busy=True, result=result))
    return


@wg_async
def showExchangeToUpgradeDeviceDialog(device, parent=None):
    result = yield wg_await(showSingleDialog(layoutID=R.views.lobby.tanksetup.dialogs.ExchangeToUpgradeItems(), parent=parent, wrappedViewClass=ExchangeToUpgradeDevice, device=device))
    raise AsyncReturn(result)


@wg_async
def showFreeSkillConfirmationDialog(skill):
    result = yield wg_await(showSingleDialogWithResultData(skill=skill, layoutID=FreeSkillConfirmationDialog.LAYOUT_ID, wrappedViewClass=FreeSkillConfirmationDialog))
    raise AsyncReturn(result)


@wg_async
def showLearnPerkConfirmationDialog(skill, level):
    from gui.impl.lobby.crew.dialogs.perk_learn_confirmation_dialog import PerkLearnConfirmationDialog
    result = yield wg_await(showSingleDialogWithResultData(skill=skill, level=level, layoutID=PerkLearnConfirmationDialog.LAYOUT_ID, wrappedViewClass=PerkLearnConfirmationDialog))
    raise AsyncReturn(result)


@wg_async
def showPerksDropDialog(tankmanId):
    from gui.impl.lobby.crew.dialogs.perks_reset_dialog import PerksResetDialog
    result = yield wg_await(showSingleDialog(layoutID=PerksResetDialog.LAYOUT_ID, wrappedViewClass=PerksResetDialog, tankmanId=tankmanId))
    raise AsyncReturn(result)


@wg_async
def showRetrainMassiveDialog(tankmenIds, vehicleCD):
    from gui.impl.lobby.crew.dialogs.retrain_massive_dialog import RetrainMassiveDialog
    if isPremiumRetrainWarning(tankmenIds, vehicleCD):
        result = yield wg_await(showRetrainPremiumVehicleDialog(vehicleCD, True))
        if not result.result:
            raise AsyncReturn(result)
    result = yield wg_await(showSingleDialog(layoutID=RetrainMassiveDialog.LAYOUT_ID, wrappedViewClass=RetrainMassiveDialog, tankmenIds=tankmenIds, vehicleCD=vehicleCD))
    raise AsyncReturn(result)


@wg_async
def showRetrainSingleDialog(tankmanId, vehicleCD, targetRole=None, targetSlotIdx=None, isChangeRoleVisible=False, beforeActions=None, parentViewKey=None):
    from gui.impl.lobby.crew.dialogs.retrain_single_dialog import RetrainSingleDialog
    if isPremiumRetrainWarning([tankmanId], vehicleCD):
        result = yield wg_await(showRetrainPremiumVehicleDialog(vehicleCD))
        if not result.result:
            raise AsyncReturn(result)
    result = yield wg_await(showSingleDialog(layoutID=RetrainSingleDialog.LAYOUT_ID, wrappedViewClass=RetrainSingleDialog, tankmanId=tankmanId, vehicleCD=vehicleCD, targetRole=targetRole, targetSlotIdx=targetSlotIdx, isChangeRoleVisible=isChangeRoleVisible, beforeActions=beforeActions, parentViewKey=parentViewKey))
    raise AsyncReturn(result)


@wg_async
def showRetrainPremiumVehicleDialog(vehicleCD, isMassive=False, parentViewKey=None):
    from gui.impl.lobby.crew.dialogs.retrain_premium_vehicle_dialog import RetrainPremiumVehicleDialog
    result = yield wg_await(showSingleDialog(layoutID=RetrainPremiumVehicleDialog.LAYOUT_ID, wrappedViewClass=RetrainPremiumVehicleDialog, vehicleCD=vehicleCD, isMassive=isMassive, parentViewKey=parentViewKey))
    raise AsyncReturn(result)


@wg_async
def showRecruitNewTankmanDialog(vehicleCD, slotIdx, putInTank=False):
    from gui.impl.lobby.crew.dialogs.recruit_new_tankman_dialog import RecruitNewTankmanDialog
    result = yield wg_await(showSingleDialog(layoutID=RecruitNewTankmanDialog.LAYOUT_ID, wrappedViewClass=RecruitNewTankmanDialog, vehicleCD=vehicleCD, slotIdx=slotIdx, putInTank=putInTank))
    raise AsyncReturn(result)


@wg_async
def showEnlargeBarracksDialog():
    from gui.impl.lobby.crew.dialogs.enlarge_barracks_dialog import EnlargeBarracksDialog
    result = yield wg_await(showSimple(FullScreenDialogWindowWrapper(EnlargeBarracksDialog())))
    raise AsyncReturn(result)


@wg_async
def showCrewBooksPurchaseDialog(crewBookCD):
    from gui.impl.lobby.crew.dialogs.crew_books_purchase_dialog import CrewBooksPurchaseDialog
    result = yield wg_await(showSingleDialog(layoutID=CrewBooksPurchaseDialog.LAYOUT_ID, wrappedViewClass=CrewBooksPurchaseDialog, crewBookCD=crewBookCD))
    raise AsyncReturn(result)


@wg_async
def showDocumentChangeDialog(tankmanInvID, ctx=None):
    from gui.impl.lobby.crew.dialogs.document_change_dialog import DocumentChangeDialog
    result = yield wg_await(showSingleDialog(layoutID=DocumentChangeDialog.LAYOUT_ID, wrappedViewClass=DocumentChangeDialog, tankmanInvID=tankmanInvID, ctx=ctx))
    raise AsyncReturn(result)


@wg_async
def showSkinApplyDialog(crewSkinID, tankManInvID):
    from gui.impl.lobby.crew.dialogs.skin_apply_dialog import SkinApplyDialog
    result = yield wg_await(showSingleDialogWithResultData(crewSkinID=crewSkinID, tankManInvID=tankManInvID, layoutID=SkinApplyDialog.LAYOUT_ID, wrappedViewClass=SkinApplyDialog))
    raise AsyncReturn(result)


@wg_async
def showDismissTankmanDialog(tankmanId, parentViewKey=None):
    from gui.impl.lobby.crew.dialogs.dismiss_tankman_dialog import DismissTankmanDialog
    result = yield wg_await(showSingleDialog(layoutID=DismissTankmanDialog.LAYOUT_ID, wrappedViewClass=DismissTankmanDialog, tankmanId=tankmanId, parentViewKey=parentViewKey))
    raise AsyncReturn(result)


@wg_async
def showRestoreTankmanDialog(tankmanId, vehicleId, slotIdx, parentViewKey=None):
    from gui.impl.lobby.crew.dialogs.restore_tankman_dialog import RestoreTankmanDialog
    result = yield wg_await(showSingleDialog(layoutID=RestoreTankmanDialog.LAYOUT_ID, wrappedViewClass=RestoreTankmanDialog, tankmanId=tankmanId, vehicleId=vehicleId, slotIdx=slotIdx, parentViewKey=parentViewKey))
    raise AsyncReturn(result)


@wg_async
def showSkillsTrainingConfirmDialog(tankman, skillsList, availableSkillsData):
    result = yield wg_await(showSingleDialogWithResultData(layoutID=SkillsTrainingConfirmDialog.LAYOUT_ID, wrappedViewClass=SkillsTrainingConfirmDialog, tankman=tankman, skillsList=skillsList, availableSkillsData=availableSkillsData))
    raise AsyncReturn(result)
