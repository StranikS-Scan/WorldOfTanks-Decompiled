# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/secret_event/action_about_view.py
import logging
from adisp import process
from frameworks.wulf import ViewSettings, ViewFlags
from gui.Scaleform import MENU
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.secret_event.action_about_model import ActionAboutModel
from gui.impl.gen.view_models.views.lobby.secret_event.action_menu_model import ActionMenuModel
from gui.impl.lobby.secret_event.action_view_with_menu import ActionViewWithMenu
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import dependency, i18n
from helpers.time_utils import getTimeStructInLocal
from skeletons.gui.game_control import IExternalLinksController
from skeletons.gui.game_event_controller import IGameEventController
from gui.impl.lobby.secret_event import getCallbackOnVideo
_logger = logging.getLogger(__name__)

class ActionAboutView(ActionViewWithMenu):
    gameEventController = dependency.descriptor(IGameEventController)
    externalLinksController = dependency.descriptor(IExternalLinksController)

    def __init__(self, layoutID, ctx=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = ActionAboutModel()
        super(ActionAboutView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getFormattedEndDate(self):
        finishDate = self.gameEventController.getEventFinishTime()
        finishDateStruct = getTimeStructInLocal(finishDate)
        finishDateText = backport.text(R.strings.event.about.endDate(), day=finishDateStruct.tm_mday, month=i18n.makeString(MENU.datetime_months(finishDateStruct.tm_mon)), year=finishDateStruct.tm_year, hour=finishDateStruct.tm_hour, minutes=i18n.makeString('%02d', finishDateStruct.tm_min))
        return finishDateText

    def _onLoading(self):
        super(ActionAboutView, self)._onLoading()
        self.__fillViewModel()

    def _initialize(self):
        super(ActionAboutView, self)._initialize()
        self.viewModel.onGotoExternalVideo += self.__gotoExternalVideo

    def _finalize(self):
        self.viewModel.onGotoExternalVideo -= self.__gotoExternalVideo
        super(ActionAboutView, self)._finalize()

    def __fillViewModel(self):
        self.viewModel.setCurrentView(ActionMenuModel.ABOUT)
        self.viewModel.setEndDate(self._getFormattedEndDate())

    @process
    def __gotoExternalVideo(self):
        url = yield self.externalLinksController.getURL('secretEvent2020')
        showBrowserOverlayView(url, VIEW_ALIAS.BROWSER_OVERLAY, callbackOnLoad=getCallbackOnVideo())
