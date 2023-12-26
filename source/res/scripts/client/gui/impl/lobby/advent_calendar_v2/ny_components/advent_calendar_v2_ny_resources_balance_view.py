# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/advent_calendar_v2/ny_components/advent_calendar_v2_ny_resources_balance_view.py
from functools import partial
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from frameworks.wulf import WindowLayer
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resource_model import NyResourceModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resources_balance_model import NyResourcesBalanceModel
from gui.impl.gen.view_models.views.lobby.new_year.ny_constants import TutorialStates
from gui.impl.lobby.new_year.dialogs.dialogs import showResourcesConvertDialog
from gui.impl.lobby.new_year.popovers.ny_resources_convert_popover import NyResourcesConvertPopover
from gui.impl.lobby.new_year.tooltips.ny_resource_tooltip import NyResourceTooltip
from gui.impl.new_year.navigation import ViewAliases
from gui.shared.utils import decorators
from helpers import dependency
from new_year.ny_constants import NYObjects, RESOURCES_ORDER
from new_year.ny_navigation_helper import switchNewYearView
from new_year.ny_processor import NewYearConvertResourcesProcessor
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IWalletController
from skeletons.new_year import INewYearController
from uilogging.ny.loggers import NyResourcesLogger

class AdventCalendarNyResourcesConvertPopover(NyResourcesConvertPopover):
    __slots__ = ('__closeClb', '__parentView')

    def __init__(self, closeClb=None, parentView=None):
        super(AdventCalendarNyResourcesConvertPopover, self).__init__()
        self.__closeClb = closeClb
        self.__parentView = parentView

    def _onGoToQuests(self):
        super(AdventCalendarNyResourcesConvertPopover, self)._onGoToQuests()
        if self.__closeClb is not None:
            self.__closeClb()
        return

    def _onGoToRewardKits(self):
        super(AdventCalendarNyResourcesConvertPopover, self)._onGoToRewardKits()
        if self.__closeClb is not None:
            self.__closeClb()
        return

    @decorators.adisp_process('newYear/resourcesConverter')
    def _convert(self, fromResourceType, fromValue, toResourceType, toValue, callback):
        result = yield NewYearConvertResourcesProcessor(fromResourceType, fromValue, toResourceType, toValue, self.__getConfirmator).request()
        callback(result=result)

    @property
    def __getConfirmator(self):
        return partial(showResourcesConvertDialog, parent=self.__parentView, layer=WindowLayer.TOP_WINDOW)


class AdventCalendarNYResourceBalance(SubModelPresenter):
    __slots__ = ('__closeClb', '__updateClb', '__isConvertPopoverAvailable')
    __nyController = dependency.descriptor(INewYearController)
    __wallet = dependency.descriptor(IWalletController)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, viewModel, parentView, closeClb, updateClb, isConvertPopoverAvailabl=None):
        super(AdventCalendarNYResourceBalance, self).__init__(viewModel, parentView)
        self.__closeClb = closeClb
        self.__updateClb = updateClb
        self.__isConvertPopoverAvailable = isConvertPopoverAvailabl or (lambda : True)

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, *args, **kwargs):
        super(AdventCalendarNYResourceBalance, self).initialize(*args, **kwargs)
        self.__updateResources()

    def _getEvents(self):
        return ((self.viewModel.onCollectResources, self.__onCollectResources),
         (self.viewModel.onConvertResources, self.__onConvertResources),
         (self.viewModel.onGoToResources, self.__onGoToResources),
         (self.__wallet.onWalletStatusChanged, self.__onWalletChanged),
         (self.__nyController.currencies.onBalanceUpdated, self.__onBalanceUpdated))

    def __onCollectResources(self):
        logger = NyResourcesLogger()
        logger.logMenuClick('button')
        if self.__settingsCore.serverSettings.getNewYearStorage().get(NewYearStorageKeys.TUTORIAL_STATE) < TutorialStates.UI:
            switchNewYearView(NYObjects.TOWN, ViewAliases.GLADE_VIEW, instantly=True)
        else:
            switchNewYearView(NYObjects.RESOURCES, ViewAliases.GLADE_VIEW, instantly=True)
        self.__closeClb()

    def __onConvertResources(self):
        pass

    def __onGoToResources(self):
        self.__onCollectResources()

    def createToolTipContent(self, event, contentID):
        tooltips = R.views.lobby.new_year.tooltips
        if contentID == tooltips.NyResourceTooltip():
            resourceType = event.getArgument('type')
            return NyResourceTooltip(resourceType)
        return super(AdventCalendarNYResourceBalance, self).createToolTipContent(event, contentID)

    def createPopOverContent(self, event):
        return AdventCalendarNyResourcesConvertPopover(self.__closeClb, self.parentView.getParentWindow()) if event.contentID == R.views.lobby.new_year.popovers.NyResourcesConvertPopover() and self.__isConvertPopoverAvailable() else super(AdventCalendarNYResourceBalance, self).createPopOverContent(event)

    def __updateResources(self):
        with self.viewModel.transaction() as model:
            model.setIsWalletAvailable(self.__wallet.isAvailable)
            resources = model.getResources()
            resources.clear()
            for resource in RESOURCES_ORDER:
                amount = self.__nyController.currencies.getResouceBalance(resource.value)
                resourceModel = NyResourceModel()
                resourceModel.setType(resource.value)
                resourceModel.setValue(amount)
                resources.addViewModel(resourceModel)

            resources.invalidate()

    def __onBalanceUpdated(self):
        self.__updateResources()
        self.__updateClb()

    def __onWalletChanged(self, _):
        self.viewModel.setIsWalletAvailable(self.__wallet.isAvailable)
        self.__updateClb()
