# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/dialogs/dialogs.py
from BWUtil import AsyncReturn
from frameworks.wulf import WindowLayer
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.dialogs import showSimple
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
from gui.impl.lobby.new_year.dialogs.challenge.challenge_confirm_dialog import ChallengeConfirmDialogView
from gui.impl.lobby.new_year.dialogs.glade.customization_buy_dialog import CustomizationBuyDialogView
from gui.impl.lobby.new_year.dialogs.glade.enable_autocollect_dialog import SetAutoCollectingDialogView
from gui.impl.lobby.new_year.dialogs.resources_converter.resources_convert_dialog import ResourcesConvertDialogView
from wg_async import wg_async, wg_await

@wg_async
def showCelebrityChallengeConfirmDialog(viewType, parent=None, **kwargs):
    view = ChallengeConfirmDialogView(viewType=viewType, **kwargs)
    dialog = FullScreenDialogWindowWrapper(view, parent=parent)
    result = yield wg_await(dialogs.show(dialog))
    raise AsyncReturn(result)


@wg_async
def showResourcesConvertDialog(fromResourceType, fromValue, toResourceType, toValue, parent=None):
    view = ResourcesConvertDialogView(fromResourceType, fromValue, toResourceType, toValue)
    dialog = FullScreenDialogWindowWrapper(view, layer=WindowLayer.FULLSCREEN_WINDOW, parent=parent)
    result = yield wg_await(showSimple(dialog))
    raise AsyncReturn(result)


@wg_async
def showSetAutoCollectingDialog(parent=None, *args, **kwargs):
    dialog = FullScreenDialogWindowWrapper(SetAutoCollectingDialogView(*args, **kwargs), layer=WindowLayer.FULLSCREEN_WINDOW, parent=parent)
    result = yield wg_await(showSimple(dialog))
    raise AsyncReturn(result)


@wg_async
def showCustomizationBuyDialog(toyID, parent=None, *args, **kwargs):
    dialog = FullScreenDialogWindowWrapper(CustomizationBuyDialogView(toyID=toyID, *args, **kwargs), layer=WindowLayer.FULLSCREEN_WINDOW, parent=parent)
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
