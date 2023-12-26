# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/dialogs/dialogs.py
from BWUtil import AsyncReturn
from frameworks.wulf import WindowLayer
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.dialogs import showSimple
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
from gui.impl.lobby.new_year.dialogs.challenge.discount_dialog import DiscountDialogView
from gui.impl.lobby.new_year.dialogs.challenge.replacement_dialog import ReplacementDialogView
from gui.impl.lobby.new_year.dialogs.hangar_name.name_change_dialog import NameChangeDialog
from gui.impl.lobby.new_year.dialogs.resources_converter.resources_convert_dialog import ResourcesConvertDialogView
from wg_async import wg_async, wg_await

@wg_async
def showReplacementDialog(questID, parent=None, *args, **kwargs):
    dialog = FullScreenDialogWindowWrapper(ReplacementDialogView(questID, *args, **kwargs), layer=WindowLayer.FULLSCREEN_WINDOW, parent=parent)
    result = yield wg_await(showSimple(dialog))
    raise AsyncReturn(result)


@wg_async
def showDiscountDialog(vehicle, discountValue, parent=None, *args, **kwargs):
    dialog = FullScreenDialogWindowWrapper(DiscountDialogView(vehicle, discountValue, *args, **kwargs), layer=WindowLayer.FULLSCREEN_WINDOW, parent=parent)
    result = yield wg_await(showSimple(dialog))
    raise AsyncReturn(result)


@wg_async
def showResourcesConvertDialog(fromResourceType, fromValue, toResourceType, toValue, parent=None, layer=WindowLayer.FULLSCREEN_WINDOW):
    view = ResourcesConvertDialogView(fromResourceType, fromValue, toResourceType, toValue)
    dialog = FullScreenDialogWindowWrapper(view, layer=layer, parent=parent)
    result = yield wg_await(showSimple(dialog))
    raise AsyncReturn(result)


@wg_async
def showBuyDialog(window):
    result = yield wg_await(dialogs.show(window))
    raise AsyncReturn(result)


@wg_async
def showFullscreenConfirmDialog(wrappedView, parent=None):
    dialog = FullScreenDialogWindowWrapper(wrappedView, layer=WindowLayer.FULLSCREEN_WINDOW, parent=parent, doBlur=True)
    result = yield wg_await(dialogs.show(dialog))
    raise AsyncReturn(result)


@wg_async
def showHangarNameChangeConfirmDialog(parent=None, **kwargs):
    view = NameChangeDialog(**kwargs)
    dialog = FullScreenDialogWindowWrapper(view, parent=parent, layer=WindowLayer.OVERLAY)
    result = yield wg_await(dialogs.show(dialog))
    raise AsyncReturn(result)
