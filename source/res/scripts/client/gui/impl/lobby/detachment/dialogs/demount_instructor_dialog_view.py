# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/dialogs/demount_instructor_dialog_view.py
import typing
import nations
from crew2 import settings_globals
from frameworks.wulf import ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.auxiliary.instructors_helper import getInstructorPageBackground
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.gen import R
from gui.impl.gen.view_models.common.format_resource_string_arg_model import FormatResourceStringArgModel
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.demount_instructor_dialog_view_model import DemountInstructorDialogViewModel
from gui.impl.gen.view_models.windows.selector_dialog_item_model import SelectorDialogItemModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.shared.gui_items.detachment import Detachment
from gui.shared.gui_items.instructor import Instructor
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.money import Currency, Money
from gui.shop import showBuyGoldForDetachmentDemountInstructor
from helpers.dependency import descriptor
from helpers.time_utils import HOURS_IN_DAY
from items.components.detachment_constants import ExcludeInstructorOption, DetachmentOperations, PROGRESS_MAX, NO_INSTRUCTOR_ID
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.shared import IItemsCache

class DemountInstructorDialogView(FullScreenDialogView):
    __itemsCache = descriptor(IItemsCache)
    __detachmentCache = descriptor(IDetachmentCache)
    __slots__ = ('_detachment', '_instructorInvID', '_isInOtherDetachment', '_instructor', '_instructorSlotID', '_blankCount', '_selectedItem')

    def __init__(self, ctx):
        settings = ViewSettings(R.views.lobby.detachment.dialogs.DemountInstructorDialogView())
        settings.model = DemountInstructorDialogViewModel()
        super(DemountInstructorDialogView, self).__init__(settings)
        self._detachment = None
        self._instructorInvID = ctx.get('instructorInvID', NO_INSTRUCTOR_ID)
        self._isInOtherDetachment = ctx.get('isInOtherDetachment', False)
        self._instructor = None
        self._instructorSlotID = None
        self._selectedItem = DemountInstructorDialogViewModel.GOLD if self._isInOtherDetachment else DemountInstructorDialogViewModel.WAIT
        return

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY:
                currency = event.getArgument('currency')
                value = int(event.getArgument('value', 0))
                shortage = max(value - self.__itemsCache.items.stats.money.get(currency, 0), 0)
                return createBackportTooltipContent(TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY, (shortage, currency))
        return super(DemountInstructorDialogView, self).createToolTipContent(event, contentID)

    @property
    def viewModel(self):
        return super(DemountInstructorDialogView, self).getViewModel()

    @property
    def actualPrice(self):
        actualPriceGroups = self.__itemsCache.items.shop.detachmentPriceGroups
        return self._getPaidExcludeInstructorPrice(actualPriceGroups)

    @property
    def defaultPrice(self):
        defaultPriceGroups = self.__itemsCache.items.shop.defaults.detachmentPriceGroups
        return self.actualPrice if defaultPriceGroups is None else self._getPaidExcludeInstructorPrice(defaultPriceGroups)

    @property
    def isEnoughMoney(self):
        actualPrice, actualCurrency = self.actualPrice
        return self.__itemsCache.items.stats.money.get(actualCurrency) >= actualPrice

    def _getAdditionalData(self):
        return self._selectedItem

    def _addListeners(self):
        super(DemountInstructorDialogView, self)._addListeners()
        self.viewModel.selector.onSelectItem += self.__onSelectItem
        g_clientUpdateManager.addMoneyCallback(self._onMoneyUpdate)

    def _removeListeners(self):
        self.viewModel.selector.onSelectItem -= self.__onSelectItem
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(DemountInstructorDialogView, self)._removeListeners()

    def _onMoneyUpdate(self, *args, **kwargs):
        self._setBaseParams(self.viewModel)

    def _updateContext(self):
        self._instructor = self.__detachmentCache.getInstructor(self._instructorInvID)
        self._detachment = self.__detachmentCache.getDetachment(self._instructor.detInvID)
        instructorsIDs = self._detachment.getInstructorsIDs()
        self._instructorSlotID = instructorsIDs.index(self._instructorInvID)

    def _getPaidExcludeInstructorPrice(self, priceGroups):
        priceGroup = priceGroups[self._detachment.progression.priceGroup]
        excludeOption = priceGroup[DetachmentOperations.REMOVE_INSTRUCTOR_FROM_SLOT][ExcludeInstructorOption.PAID]
        money = Money(**excludeOption)
        currency = money.getCurrency(byWeight=True)
        price = int(money.get(currency))
        return (price, currency)

    def _setBaseParams(self, model):
        with model.transaction() as viewModel:
            self._updateContext()
            exclusionHours = settings_globals.g_instructorSettingsProvider.exclusionHours
            model.setAvailableAfterDays(exclusionHours / HOURS_IN_DAY)
            viewModel.setBackground(getInstructorPageBackground(self._instructor.pageBackground))
            viewModel.setIcon(self._instructor.getPortraitName())
            viewModel.setName(self._instructor.fullName)
            viewModel.setNation(nations.MAP[self._instructor.nationID])
            viewModel.setIsInOtherDetachment(self._isInOtherDetachment)
            selector = viewModel.selector
            selectorItems = selector.getItems()
            selectorItems.clear()
            actualPrice, actualCurrency = self.actualPrice
            firstItem = SelectorDialogItemModel()
            firstItem.setType(DemountInstructorDialogViewModel.WAIT)
            firstItem.setIsSelected(self._selectedItem == DemountInstructorDialogViewModel.WAIT)
            firstItem.setCurrencyType(actualCurrency)
            firstItem.setItemPrice(actualPrice)
            selectorItems.addViewModel(firstItem)
            defPrice, defCurrency = self.defaultPrice
            secondItem = SelectorDialogItemModel()
            secondItem.setIsItemEnough(self.isEnoughMoney)
            secondItem.setCurrencyType(actualCurrency)
            secondItem.setIsDiscount(actualCurrency == defCurrency and actualPrice < defPrice)
            secondItem.setDiscountValue(int(round(PROGRESS_MAX * (defPrice - actualPrice) / defPrice)))
            secondItem.setItemPrice(actualPrice)
            secondItem.setType(DemountInstructorDialogViewModel.GOLD)
            secondItem.setIsSelected(self._selectedItem == DemountInstructorDialogViewModel.GOLD)
            selectorItems.addViewModel(secondItem)
            selectorItems.invalidate()
        super(DemountInstructorDialogView, self)._setBaseParams(model)

    def _setTitleArgs(self, arrModel, frmtArgs):
        for name, resource in frmtArgs:
            frmtModel = FormatResourceStringArgModel()
            frmtModel.setName(name)
            frmtModel.setValue(resource)
            arrModel.addViewModel(frmtModel)

        arrModel.invalidate()

    def _onAcceptClicked(self):
        if self._selectedItem == DemountInstructorDialogViewModel.WAIT:
            optionID = ExcludeInstructorOption.FREE
        elif self._selectedItem == DemountInstructorDialogViewModel.GOLD:
            optionID = ExcludeInstructorOption.PAID
        self._updateContext()
        if optionID == ExcludeInstructorOption.PAID:
            price, currency = self.actualPrice
            playerCurrencyAmount = int(self.__itemsCache.items.stats.money.get(currency))
            if price > playerCurrencyAmount:
                if currency == Currency.GOLD:
                    showBuyGoldForDetachmentDemountInstructor(price)
                return
        ItemsActionsFactory.doAction(ItemsActionsFactory.REMOVE_INSTRUCTOR, self._instructor.detInvID, self._instructorSlotID, optionID)
        super(DemountInstructorDialogView, self)._onAcceptClicked()

    def __onSelectItem(self, args):
        if args is not None:
            self._selectedItem = args.get('type')
            with self.viewModel.transaction() as vm:
                selectorItems = vm.selector.getItems()
                for item in selectorItems:
                    item.setIsSelected(item.getType() == self._selectedItem)

                selectorItems.invalidate()
                vm.setIsAcceptDisabled(False)
        return
