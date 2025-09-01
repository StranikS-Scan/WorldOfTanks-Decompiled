# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/shared/event_dispatcher.py
import logging
import typing
from BWUtil import AsyncReturn
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from wg_async import wg_async, wg_await
if typing.TYPE_CHECKING:
    from typing import Callable, Optional
    from one_time_gift_common.one_time_gift_constants import BranchListType
_logger = logging.getLogger(__name__)

def _switchOrLoadOneTimeGiftView(viewType, *args, **kwargs):
    guiLoader = dependency.instance(IGuiLoader)
    view = guiLoader.windowsManager.getViewByLayoutID(R.views.one_time_gift.mono.lobby.one_time_gift_view())
    if view is not None:
        _logger.info('Found existing OTG view, switching content to %s', viewType)
        view.switchContent(viewType, *args, **kwargs)
        return
    else:
        from one_time_gift.gui.impl.lobby.meta_view.one_time_gift_view import OneTimeGiftViewWindow
        OneTimeGiftViewWindow(viewType, *args, **kwargs).load()
        return


def showBranchSelectionWindow(branchListType, allVehiclesPurchased=False, onConfirmCallback=None, onCloseCallback=None, onErrorCallback=None):
    _logger.debug('showBranchSelectionWindow(%s, %s, %s, %s, %s)', branchListType, allVehiclesPurchased, onConfirmCallback, onCloseCallback, onErrorCallback)
    from one_time_gift.gui.impl.gen.view_models.views.lobby.one_time_gift_view_model import MainViews
    _switchOrLoadOneTimeGiftView(MainViews.BRANCH_SELECTION, branchListType, allVehiclesPurchased, onConfirmCallback, onCloseCallback, onErrorCallback)


def showNewbieBranchRewardWindow(rewards, onCloseCallback=None):
    _logger.debug('showNewbieBranchRewardWindow(%s, %s)', rewards, onCloseCallback)
    from one_time_gift.gui.impl.gen.view_models.views.lobby.one_time_gift_view_model import MainViews
    _switchOrLoadOneTimeGiftView(MainViews.BRANCH_REWARD, rewards, onCloseCallback=onCloseCallback)


def showFullBranchRewardWindow(rewards, onCloseCallback=None):
    _logger.debug('showFullBranchRewardWindow(%s, %s)', rewards, onCloseCallback)
    from one_time_gift.gui.impl.gen.view_models.views.lobby.one_time_gift_view_model import MainViews
    _switchOrLoadOneTimeGiftView(MainViews.BRANCH_REWARD, rewards, onCloseCallback=onCloseCallback)


def showNewbieAdditionalRewardWindow(rewards, onCloseCallback=None):
    _logger.debug('showNewbieAdditionalRewardWindow(%s, %s)', rewards, onCloseCallback)
    from one_time_gift.gui.impl.lobby.awards.packers import composeVehicleBonuses, filterNonOwnedVehicles
    from one_time_gift.gui.impl.gen.view_models.views.lobby.one_time_gift_view_model import MainViews
    vehicles = list(filter(filterNonOwnedVehicles, composeVehicleBonuses(rewards)))
    if vehicles:
        _switchOrLoadOneTimeGiftView(MainViews.PREMIUM_VEHICLES_REWARD, rewards, onCloseCallback=onCloseCallback)
    elif onCloseCallback is not None:
        onCloseCallback()
    return


def showFullAdditionalRewardWindow(rewards, onCloseCallback=None):
    _logger.debug('showFullAdditionalRewardWindow(%s, %s)', rewards, onCloseCallback)
    from one_time_gift.gui.impl.gen.view_models.views.lobby.one_time_gift_view_model import MainViews
    _switchOrLoadOneTimeGiftView(MainViews.ADDITIONAL_REWARD, rewards, onCloseCallback=onCloseCallback)


def showCollectorsCompensationWindow(rewards, onCloseCallback=None):
    _logger.debug('showCollectorsCompensationWindow(%s, %s)', rewards, onCloseCallback)
    from one_time_gift.gui.impl.gen.view_models.views.lobby.one_time_gift_view_model import MainViews
    _switchOrLoadOneTimeGiftView(MainViews.COLLECTORS_COMPENSATION_REWARD, rewards, onCloseCallback=onCloseCallback)


def showIntroWindow(onConfirmCallback=None, onCloseCallback=None, onErrorCallback=None, showIntroVideo=False):
    _logger.debug('showIntroWindow(%s, %s, %s, %s)', onConfirmCallback, onErrorCallback, onCloseCallback, showIntroVideo)
    from one_time_gift.gui.impl.gen.view_models.views.lobby.one_time_gift_view_model import MainViews
    _switchOrLoadOneTimeGiftView(MainViews.INTRO, onConfirmCallback, onCloseCallback, onErrorCallback, showIntroVideo=showIntroVideo)


@wg_async
def showConfirmSelectionDialog(vehCDs, parent=None):
    from gui.impl.dialogs import dialogs
    from one_time_gift.gui.impl.lobby.awards.confirm_selection_view import ConfirmSelectionView
    result = yield wg_await(dialogs.showCustomBlurSingleDialog(layoutID=R.views.one_time_gift.mono.lobby.confirm_selection_view(), parent=parent, wrappedViewClass=ConfirmSelectionView, vehCDs=vehCDs))
    raise AsyncReturn(result)


def closeOneTimeGiftWindow():
    _logger.debug('closeOneTimeGiftWindow()')
    guiLoader = dependency.instance(IGuiLoader)
    view = guiLoader.windowsManager.getViewByLayoutID(R.views.one_time_gift.mono.lobby.one_time_gift_view())
    if view is None:
        _logger.debug('OneTimeGiftView is not found')
        return
    else:
        view.destroyWindow()
        return
