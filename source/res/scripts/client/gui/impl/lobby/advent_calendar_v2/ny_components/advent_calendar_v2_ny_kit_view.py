# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/advent_calendar_v2/ny_components/advent_calendar_v2_ny_kit_view.py
import logging
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.advent_calendar.components.advent_calendar_ny_kit_model import AdventCalendarNyKitModel
from gui.impl.lobby.advent_calendar_v2.advent_calendar_v2_helper import getMaxResource
from gui.impl.lobby.new_year.tooltips.ny_resource_tooltip import NyResourceTooltip
from helpers import dependency
from items.components.ny_constants import NyCurrency
from gui.impl.gen.view_models.views.lobby.new_year.ny_constants import Resource
from shared_utils import first
from skeletons.new_year import INewYearController
_logger = logging.getLogger(__name__)

class AdventCalendarNYKit(SubModelPresenter):
    __slots__ = ('__price', '__currentResource')
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self, viewModel, parentView, price):
        super(AdventCalendarNYKit, self).__init__(viewModel, parentView)
        self.__price = price
        self.__currentResource = NyCurrency.CRYSTAL

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, *args, **kwargs):
        super(AdventCalendarNYKit, self).initialize(*args, **kwargs)
        self.__currentResource = getMaxResource().resourceName
        self.__updateKitModel()

    def _getEvents(self):
        return ((self.__nyController.currencies.onBalanceUpdated, self.__onBalanceUpdated), (self.viewModel.onSwitchResource, self.__onKitSwitchResource))

    def createToolTipContent(self, event, contentID):
        tooltips = R.views.lobby.new_year.tooltips
        if contentID == tooltips.NyResourceTooltip():
            resourceType = event.getArgument('type')
            return NyResourceTooltip(resourceType)
        return super(AdventCalendarNYKit, self).createToolTipContent(event, contentID)

    def __updateKitModel(self):
        with self.viewModel.transaction() as model:
            resources = model.getResources()
            resources.clear()
            for currency in NyCurrency.ALL:
                resources.addString(currency)

            resources.invalidate()
        self.__updatePrice()

    def __updatePrice(self):
        with self.viewModel.transaction() as model:
            currency = self.__currentResource.value
            balance = self.__nyController.currencies.getResouceBalance(currency)
            model.setCurrentResource(currency)
            model.setPrice(self.__price)
            model.setNotEnoughResource(self.__price > balance)

    def __onKitSwitchResource(self, args):
        resourceValue = args.get('resource', '')
        if not resourceValue:
            _logger.error('Argument - "resource" is ommited for command - "onSwitchResource"')
            return
        resource = first([ item for item in Resource if item.value == resourceValue ], Resource.CRYSTAL)
        _logger.debug('Switching to resource with name=%s, required resource=%s', resource, resourceValue)
        self.__currentResource = resource
        self.__updatePrice()

    def __updateResources(self):
        self.__updatePrice()

    def __onBalanceUpdated(self):
        self.__updateResources()
