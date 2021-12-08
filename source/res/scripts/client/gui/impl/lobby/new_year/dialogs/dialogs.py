# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/dialogs/dialogs.py
from async import async, await
from BWUtil import AsyncReturn
from frameworks.wulf import WindowLayer
from gui.impl.dialogs import dialogs
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
from gui.impl.lobby.new_year.dialogs.install_to_unprofitable_slot_dialog_builder import InstallToUnprofitableSlotDialogBuilder
from gui.impl.lobby.new_year.dialogs.vehicle_branch_dialog_builder import VehicleBranchDialogBuilder
from gui.impl.lobby.new_year.dialogs.vehicle_hint_dialog_builder import VehicleHintDialogBuilder

@async
def showSetVehicleBranchConfirm(invID, slotID):
    builder = VehicleBranchDialogBuilder(invID, slotID)
    result = yield await(dialogs.show(FullScreenDialogWindowWrapper(builder.buildView(), doBlur=True, layer=WindowLayer.OVERLAY)))
    raise AsyncReturn(result)


@async
def showSetVehicleHint():
    builder = VehicleHintDialogBuilder()
    result = yield await(dialogs.show(FullScreenDialogWindowWrapper(builder.buildView(), doBlur=True, layer=WindowLayer.OVERLAY)))
    raise AsyncReturn(result)


@async
def showBuyDialog(window):
    result = yield await(dialogs.show(window))
    raise AsyncReturn(result)


@async
def showInstallToUnprofitableSlotConfirm():
    builder = InstallToUnprofitableSlotDialogBuilder()
    result = yield await(dialogs.show(builder.build(withBlur=True)))
    raise AsyncReturn(result)
