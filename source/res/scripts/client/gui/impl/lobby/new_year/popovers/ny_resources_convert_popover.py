# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/popovers/ny_resources_convert_popover.py
from adisp import adisp_process
from frameworks.wulf import ViewSettings
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_resource_converter_info_tooltip_model import ConverterInfoTooltipType
from gui.impl.lobby.new_year.tooltips.ny_resource_converter_info_tooltip import NyResourceConverterInfoTooltip
from gui.impl.new_year.sounds import NewYearSoundsManager
from gui.impl.pub import PopOverViewImpl
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resource_model import NyResourceModel
from gui.impl.gen.view_models.views.lobby.new_year.popovers.ny_resources_convert_popover_model import NyResourcesConvertPopoverModel
from gui.impl.lobby.missions.daily_quests_view import DailyTabs
from gui.server_events.events_dispatcher import showDailyQuests
from gui.shared import g_eventBus
from gui.shared.events import NyResourcesConverterPopup
from gui.shared.event_dispatcher import showLootBoxBuyWindow
from helpers import dependency
from new_year.ny_constants import RESOURCES_ORDER
from new_year.ny_processor import NewYearConvertResourcesProcessor
from skeletons.new_year import INewYearController
from skeletons.gui.system_messages import ISystemMessages

class NyResourcesConvertPopover(PopOverViewImpl):
    __slots__ = ()
    __nyController = dependency.descriptor(INewYearController)
    __systemMessages = dependency.descriptor(ISystemMessages)
    __resourceUnit = 1

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.popovers.NyResourcesConvertPopover())
        settings.model = NyResourcesConvertPopoverModel()
        super(NyResourcesConvertPopover, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyResourcesConvertPopover, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.NyResourceConverterInfoTooltip():
            tooltipType = ConverterInfoTooltipType(event.getArgument('tooltipType'))
            return NyResourceConverterInfoTooltip(tooltipType)
        return super(NyResourcesConvertPopover, self).createToolTipContent(event, contentID)

    def _initialize(self, *args, **kwargs):
        super(NyResourcesConvertPopover, self)._initialize()
        g_eventBus.handleEvent(NyResourcesConverterPopup(eventType=NyResourcesConverterPopup.SHOW))

    def _onLoading(self, *args, **kwargs):
        super(NyResourcesConvertPopover, self)._initialize(*args, **kwargs)
        self.viewModel.onConvertClick += self.__onConvertClick
        self.viewModel.onGoToQuests += self.__onGoToQuests
        self.viewModel.onGoToRewardKits += self.__onGoToRewardKits
        with self.viewModel.transaction() as model:
            availableResources = model.getAvailableResources()
            availableResources.clear()
            for resource in RESOURCES_ORDER:
                amount = self.__nyController.currencies.getResouceBalance(resource.value)
                resourceModel = NyResourceModel()
                resourceModel.setType(resource.value)
                resourceModel.setValue(amount)
                availableResources.addViewModel(resourceModel)

            availableResources.invalidate()
            convertRate = model.convertRate
            initialValueCoeff, receivedValueCoeff = self.__nyController.currencies.getResourceConverterCoefficients()
            convertRate.setFrom(initialValueCoeff)
            convertRate.setTo(receivedValueCoeff)

    def _onLoaded(self, *args, **kwargs):
        super(NyResourcesConvertPopover, self)._onLoaded(*args, **kwargs)
        self.getParentWindow().bringToFront()

    def _finalize(self):
        self.viewModel.onConvertClick -= self.__onConvertClick
        self.viewModel.onGoToQuests -= self.__onGoToQuests
        self.viewModel.onGoToRewardKits -= self.__onGoToRewardKits
        g_eventBus.handleEvent(NyResourcesConverterPopup(eventType=NyResourcesConverterPopup.HIDE))
        super(NyResourcesConvertPopover, self)._finalize()

    def __onGoToQuests(self):
        showDailyQuests(DailyTabs.QUESTS)

    def __onGoToRewardKits(self):
        showLootBoxBuyWindow()

    def __onConvertClick(self, args):
        fromResourceType = args.get('fromResource')
        toResourceType = args.get('toResource')
        toValue = int(args.get('value'))
        fromValue = int(self.__nyController.currencies.calculateInitialValueByReceived(toValue))
        self.__convert(fromResourceType, fromValue, toResourceType, toValue)

    @adisp_process
    def __convert(self, fromResourceType, fromValue, toResourceType, toValue):
        result = yield NewYearConvertResourcesProcessor(fromResourceType, fromValue, toResourceType, toValue).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            NewYearSoundsManager.playEvent(backport.sound(R.sounds.hangar_newyear_level_points_anim()))
