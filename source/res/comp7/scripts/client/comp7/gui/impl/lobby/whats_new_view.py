# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/whats_new_view.py
import typing
import SoundGroups
from comp7.gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as COMP7_TOOLTIPS
from comp7.gui.impl.gen.view_models.views.lobby.whats_new_view_model import WhatsNewViewModel
from comp7.gui.impl.lobby.comp7_helpers import comp7_model_helpers
from comp7.gui.impl.lobby.comp7_helpers.comp7_gui_helpers import updateComp7LastSeason
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport.backport_tooltip import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.tooltips.vehicle_role_descr_view import VehicleRolesTooltipView
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
SOUND_NAME = 'comp_7_whatsnew_appear'
RENT_VEHICLES_CDS = [66593, 22097, 53137]

class WhatsNewView(ViewImpl, IGlobalListener):
    __slots__ = ()
    __settingsCore = dependency.descriptor(ISettingsCore)
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __itemsCache = dependency.descriptor(IItemsCache)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.model = WhatsNewViewModel()
        super(WhatsNewView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WhatsNewView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == COMP7_TOOLTIPS.COMP7_CALENDAR_DAY_INFO:
                tooltipData = createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(None,))
            elif tooltipId == TOOLTIPS_CONSTANTS.SHOP_VEHICLE:
                vehicleCD = int(event.getArgument('vehicleCD'))
                tooltipData = createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(vehicleCD,))
            else:
                tooltipData = None
            if tooltipData:
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                if window is None:
                    return
                window.load()
                return window
        return super(WhatsNewView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.ranked.tooltips.RankedBattlesRolesTooltipView():
            vehicleCD = int(event.getArgument('vehicleCD'))
            return VehicleRolesTooltipView(vehicleCD)
        else:
            return None

    def onPrbEntitySwitched(self):
        if not self.__comp7Controller.isComp7PrbActive():
            self.destroyWindow()

    def _finalize(self):
        self.__removeListeners()

    def _onLoading(self, *_, **__):
        self.__addListeners()
        self.__updateData()
        self.__playSound()

    def _onLoaded(self):
        updateComp7LastSeason()

    def __addListeners(self):
        self.viewModel.onClose += self.__onClose
        self.viewModel.onVideoOpen += self.__onVideoOpen
        self.viewModel.scheduleInfo.season.pollServerTime += self.__onPollServerTime
        self.__comp7Controller.onStatusUpdated += self.__onStatusUpdated
        self.__comp7Controller.onComp7ConfigChanged += self.__onConfigChanged
        self.__eventsCache.onSyncCompleted += self.__onEventsSyncCompleted
        self.startGlobalListening()

    def __removeListeners(self):
        self.viewModel.onClose -= self.__onClose
        self.viewModel.onVideoOpen -= self.__onVideoOpen
        self.viewModel.scheduleInfo.season.pollServerTime -= self.__onPollServerTime
        self.__comp7Controller.onStatusUpdated -= self.__onStatusUpdated
        self.__comp7Controller.onComp7ConfigChanged -= self.__onConfigChanged
        self.__eventsCache.onSyncCompleted -= self.__onEventsSyncCompleted
        self.stopGlobalListening()

    def __onStatusUpdated(self, status):
        if comp7_model_helpers.isModeForcedDisabled(status):
            self.destroyWindow()
        else:
            self.__updateData()

    def __onConfigChanged(self):
        if self.viewModel is not None:
            self.__updateData()
        return

    def __onEventsSyncCompleted(self):
        with self.viewModel.transaction() as vm:
            self.__setVehicles(vm)

    def __onPollServerTime(self):
        self.__updateData()

    def __updateData(self):
        with self.viewModel.transaction() as vm:
            comp7_model_helpers.setElitePercentage(vm)
            comp7_model_helpers.setScheduleInfo(vm.scheduleInfo)
            self.__setVehicles(vm)

    def __setVehicles(self, viewModel):
        vehiclesList = viewModel.getVehicles()
        vehiclesList.clear()
        for vehicleCD in RENT_VEHICLES_CDS:
            vehicleItem = self.__itemsCache.items.getItemByCD(vehicleCD)
            vehicleModel = VehicleModel()
            fillVehicleModel(vehicleModel, vehicleItem)
            vehiclesList.addViewModel(vehicleModel)

        vehiclesList.invalidate()

    def __onClose(self):
        self.destroyWindow()

    def __onVideoOpen(self):
        url = GUI_SETTINGS.lookup(self.__getWhatsNewPageKey())
        showBrowserOverlayView(url, VIEW_ALIAS.WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW), parent=self.getParentWindow())

    @staticmethod
    def __playSound():
        SoundGroups.g_instance.playSound2D(SOUND_NAME)

    @staticmethod
    def __getWhatsNewPageKey():
        pass


class WhatsNewViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(WhatsNewViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WhatsNewView(R.views.comp7.lobby.WhatsNewView()), parent=parent)
