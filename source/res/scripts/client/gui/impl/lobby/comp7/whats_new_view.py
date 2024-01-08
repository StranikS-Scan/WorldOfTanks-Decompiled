# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/whats_new_view.py
import typing
import SoundGroups
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior
from battle_modifiers_common import BattleModifiers, BattleParams
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui import GUI_SETTINGS
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport.backport_tooltip import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.comp7.whats_new_view_model import WhatsNewViewModel
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.comp7 import comp7_model_helpers
from gui.impl.lobby.tooltips.vehicle_role_descr_view import VehicleRolesTooltipView
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.event_dispatcher import showBrowserOverlayView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from helpers import dependency
from math_common import round_int
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
_EQUIPMENT_COOLDOWN_SECONDS = 90
SOUND_NAME = 'comp_7_whatsnew_appear'

class WhatsNewView(ViewImpl, IGlobalListener):
    __slots__ = ()
    __settingsCore = dependency.descriptor(ISettingsCore)
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.model = WhatsNewViewModel()
        super(WhatsNewView, self).__init__(settings)
        self.__vehicles = [57665, 52369, 52641]

    @property
    def viewModel(self):
        return super(WhatsNewView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TOOLTIPS_CONSTANTS.COMP7_CALENDAR_DAY_INFO:
                tooltipData = createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(None,))
            elif tooltipId == TOOLTIPS_CONSTANTS.SHOP_VEHICLE:
                vehicleCD = int(event.getArgument('vehicleCD'))
                tooltipData = createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(vehicleCD,))
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
        self.__vehicles = None
        self.__removeListeners()
        return

    def _onLoading(self, *_, **__):
        self.__addListeners()
        self.__updateData()
        self.__playSound()

    def _onLoaded(self):
        self.__setComp7WhatsNewShown()

    def __addListeners(self):
        self.viewModel.onClose += self.__onClose
        self.viewModel.onVideoOpen += self.__onVideoOpen
        self.viewModel.scheduleInfo.season.pollServerTime += self.__onPollServerTime
        self.__comp7Controller.onStatusUpdated += self.__onStatusUpdated
        self.__comp7Controller.onComp7ConfigChanged += self.__onConfigChanged
        self.startGlobalListening()

    def __removeListeners(self):
        self.viewModel.onClose -= self.__onClose
        self.viewModel.onVideoOpen -= self.__onVideoOpen
        self.viewModel.scheduleInfo.season.pollServerTime -= self.__onPollServerTime
        self.__comp7Controller.onStatusUpdated -= self.__onStatusUpdated
        self.__comp7Controller.onComp7ConfigChanged -= self.__onConfigChanged
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

    def __onPollServerTime(self):
        self.__updateData()

    def __updateData(self):
        with self.viewModel.transaction() as vm:
            comp7_model_helpers.setScheduleInfo(vm.scheduleInfo)
            self.__setVehicles(vm)
            self.__setModifiersData(vm)

    def __setVehicles(self, viewModel):
        vehiclesList = viewModel.getVehicles()
        vehiclesList.clear()
        for vehicleCD in self.__vehicles:
            vehicleItem = self.__itemsCache.items.getItemByCD(vehicleCD)
            vehicleModel = VehicleModel()
            fillVehicleModel(vehicleModel, vehicleItem)
            vehiclesList.addViewModel(vehicleModel)

        vehiclesList.invalidate()

    def __setModifiersData(self, viewModel):
        modifiers = BattleModifiers(self.__comp7Controller.battleModifiers)
        for param, modifier in modifiers:
            if param == BattleParams.VEHICLE_HEALTH:
                viewModel.setVehicleHealth(self.__toPercents(modifier.value))
            if param == BattleParams.EQUIPMENT_COOLDOWN:
                viewModel.setEquipmentCooldown(round_int(modifier.value * _EQUIPMENT_COOLDOWN_SECONDS))
            if param == BattleParams.SHOT_DISPERSION_RADIUS:
                viewModel.setShotDispersionRadius(modifier.value)
            if param == BattleParams.VISION_TIME:
                viewModel.setVisionTime(round_int(modifier.value))
            if param == BattleParams.VISION_MIN_RADIUS:
                viewModel.setVisionMinRadius(round_int(modifier.value))

    def __setComp7WhatsNewShown(self):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        stateFlags = self.__settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        stateFlags[GuiSettingsBehavior.COMP7_WHATS_NEW_SHOWN] = True
        self.__settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, stateFlags)

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

    @staticmethod
    def __toPercents(value):
        return round_int(100.0 * value)


class WhatsNewViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(WhatsNewViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WhatsNewView(R.views.lobby.comp7.WhatsNewView()), parent=parent)
