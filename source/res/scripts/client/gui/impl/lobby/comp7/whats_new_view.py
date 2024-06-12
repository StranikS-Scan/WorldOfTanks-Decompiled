# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/whats_new_view.py
import typing
import logging
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior
from frameworks.wulf import ViewSettings, WindowFlags
from gui.comp7.comp7_helpers import getWhatsNewSeasonVehicles, getWhatsNewMapsAdded, getWhatsNewMapsDeleted, getWhatsNewPages, getIntroVehicles, getIntroPages
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport.backport_tooltip import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.comp7.maps_model import MapsModel
from gui.impl.gen.view_models.views.lobby.comp7.page_model import PageModel
from gui.impl.gen.view_models.views.lobby.comp7.pages_model import Types
from gui.impl.gen.view_models.views.lobby.comp7.whats_new_view_model import WhatsNewViewModel
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.comp7 import comp7_model_helpers
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import event_dispatcher
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
    from frameworks.wulf import Array
    from typing import Callable
    from gui.impl.wrappers.user_list_model import UserListModel
_TYPE_TO_GF_ENUM = {'page': Types.PAGE,
 'maps': Types.MAPS,
 'seasonVehicles': Types.SEASONVEHICLES}

class WhatsNewView(ViewImpl, IGlobalListener):
    __slots__ = ('__isIntro',)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, isIntro, layoutID):
        settings = ViewSettings(layoutID)
        settings.model = WhatsNewViewModel()
        self.__isIntro = isIntro
        super(WhatsNewView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WhatsNewView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TOOLTIPS_CONSTANTS.COMP7_CALENDAR_DAY_INFO:
                tooltipData = createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(None,))
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
        return super(WhatsNewView, self).createToolTip(event)

    def onPrbEntitySwitched(self):
        if not self.__comp7Controller.isComp7PrbActive():
            self.destroyWindow()

    def _finalize(self):
        self._unsubscribe()
        self.stopGlobalListening()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.viewModel.scheduleInfo.season.pollServerTime, self.__onPollServerTime), (self.__comp7Controller.onStatusUpdated, self.__onStatusUpdated))

    def _onLoading(self, *_, **__):
        self.startGlobalListening()
        self._subscribe()
        self.__updateData()

    def _onLoaded(self):
        if self.__isIntro:
            self.__setComp7IntroShown()
        else:
            self.__setComp7WhatsNewShown()

    def __onStatusUpdated(self, status):
        if comp7_model_helpers.isModeForcedDisabled(status):
            self.destroyWindow()
        else:
            self.__updateData()

    def __onPollServerTime(self):
        self.__updateData()

    @replaceNoneKwargsModel
    def __updateData(self, model=None):
        comp7_model_helpers.setScheduleInfo(model.scheduleInfo)
        self.__setVehicles(model)
        if not self.__isIntro:
            self.__setMaps(model.newMaps, getWhatsNewMapsAdded)
            self.__setMaps(model.depricatedMaps, getWhatsNewMapsDeleted)
        if self.__isIntro:
            self.__setPages(model, getIntroPages)
        else:
            self.__setPages(model, getWhatsNewPages)

    def __setVehicles(self, viewModel):
        vehiclesList = viewModel.getVehicles()
        vehiclesList.clear()
        if self.__isIntro:
            self.__fillViheclesModel(vehiclesList, vehs=getIntroVehicles)
        else:
            self.__fillViheclesModel(vehiclesList, vehs=getWhatsNewSeasonVehicles)
        vehiclesList.invalidate()

    def __fillViheclesModel(self, vehiclesList, vehs):
        for vehicleCD in vehs():
            vehicleItem = self.__itemsCache.items.getItemByCD(vehicleCD)
            vehicleModel = VehicleModel()
            fillVehicleModel(vehicleModel, vehicleItem)
            vehiclesList.addViewModel(vehicleModel)

    def __setMaps(self, mapsModel, maps):
        mapsModel.clearItems()
        for mapInfo in maps():
            mapModel = MapsModel()
            mapModel.setName(mapInfo)
            mapsModel.addViewModel(mapModel)

        mapsModel.invalidate()

    def __setPages(self, viewModel, pages):
        pagesModel = viewModel.pages
        pagesModel.clearItems()
        self.__fillPages(pagesModel, pages)
        pagesModel.invalidate()

    def __fillPages(self, pagesModel, pages):
        for name, value in pages():
            mapModel = PageModel()
            mapModel.setPageType(_TYPE_TO_GF_ENUM.get(value))
            mapModel.setName(name)
            pagesModel.addViewModel(mapModel)

    def __setComp7WhatsNewShown(self):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        stateFlags = self.__settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        stateFlags[GuiSettingsBehavior.COMP7_WHATS_NEW_SHOWN] = True
        self.__settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, stateFlags)

    def __setComp7IntroShown(self):
        if not self.__settingsCore.isReady:
            _logger.error('Can not save Comp7IntroShown settings: settings are not ready')
            return
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        stateFlags = self.__settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        stateFlags[GuiSettingsBehavior.COMP7_INTRO_SHOWN] = True
        stateFlags[GuiSettingsBehavior.COMP7_WHATS_NEW_SHOWN] = True
        self.__settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, stateFlags)

    def __onClose(self):
        event_dispatcher.showHangar()
        self.destroyWindow()

    @staticmethod
    def __getWhatsNewPageKey():
        pass


class WhatsNewViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, isIntro, parent=None):
        super(WhatsNewViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WhatsNewView(isIntro, R.views.lobby.comp7.WhatsNewView()), parent=parent)
