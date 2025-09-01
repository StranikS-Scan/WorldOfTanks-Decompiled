# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/lobby/navigation_presenter.py
import logging
import typing
from functools import partial
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.page.header.navigation_bar_info_button import NavigationBarInfoButton, ButtonType
from gui.impl.gen.view_models.views.lobby.page.header.navigation_bar_model import NavigationBarModel
from gui.impl.pub.view_component import ViewComponent
from helpers.events_handler import EventsHandler
if typing.TYPE_CHECKING:
    from typing import Callable, Optional
_logger = logging.getLogger(__name__)

class OneTimeGiftNavigationPresenter(ViewComponent[NavigationBarModel], EventsHandler):

    def __init__(self, onNavigateCallback=None, onInfoActionCallback=None):
        super(OneTimeGiftNavigationPresenter, self).__init__(model=NavigationBarModel)
        self.__onNavigateCallback = onNavigateCallback
        self.__onInfoActionCallback = onInfoActionCallback

    def _getEvents(self):
        model = self.getViewModel()
        events = ((model.onNavigate, partial(self.__safeCall, self.__onNavigateCallback)), (model.onInfoAction, partial(self.__safeCall, self.__onInfoActionCallback)))
        return events

    def _onLoading(self, *args, **kwargs):
        super(OneTimeGiftNavigationPresenter, self)._onLoading(*args, **kwargs)
        self.__update()

    def _finalize(self):
        self.__onNavigateCallback = None
        self.__onInfoActionCallback = None
        super(OneTimeGiftNavigationPresenter, self)._finalize()
        return

    def __update(self):
        with self.getViewModel().transaction() as model:
            infoButtons = model.getInfoButtons()
            infoButtons.clear()
            navigationText = R.strings.one_time_gift.branchSelection.navigationPanel
            model.setPageTitle(backport.text(navigationText.pageTitle()))
            infoButton = NavigationBarInfoButton()
            infoButton.setType(ButtonType.INFO)
            infoButton.setTooltipBody(backport.text(navigationText.tooltip()))
            infoButtons.addViewModel(infoButton)
            model.setBackNavigationAllowed(False)
            infoButtons.invalidate()

    @staticmethod
    def __safeCall(callback, *_, **__):
        _logger.debug('__safeCall: %s', callback)
        if callable(callback):
            callback()
