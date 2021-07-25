# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/sub_views/content/select_option_content.py
import typing
from Event import Event
from frameworks.wulf import ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.framework.entities import View
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.goodies.demount_kit import getDemountKitForOptDevice
from gui.impl import backport
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.dialogs.dialog_template_utils import getCurrencyTooltipAlias
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.dialog_template_generic_tooltip_view_model import TooltipType
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencyType, CurrencySize
from gui.impl.gen.view_models.views.dialogs.sub_views.select_demount_kit_view_model import SelectDemountKitViewModel
from gui.impl.gen.view_models.views.dialogs.sub_views.select_money_view_model import SelectMoneyViewModel
from gui.impl.gen.view_models.views.dialogs.sub_views.select_option_base_item_view_model import SelectOptionBaseItemViewModel, ComponentType
from gui.impl.gen.view_models.views.dialogs.sub_views.select_option_view_model import SelectOptionViewModel
from gui.impl.pub import ViewImpl
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from typing import List, Optional, Callable
    from gui.shared.gui_items.gui_item_economics import ItemPrice
    from gui.shared.money import Money
    from gui.goodies.goodie_items import DemountKit

class SelectOptionBasePresenter(object):
    __slots__ = ('__viewModel', '__isDisabled', 'tooltipFactory')
    _VIEW_MODEL = SelectOptionBaseItemViewModel

    def __init__(self):
        super(SelectOptionBasePresenter, self).__init__()
        self.__viewModel = self._VIEW_MODEL()
        self.__viewModel.tooltip.setType(TooltipType.ABSENT)
        self.__isDisabled = False
        self.viewModel.setComponentType(ComponentType.BASE)
        self.tooltipFactory = None
        return

    @property
    def viewModel(self):
        return self.__viewModel

    def initialize(self):
        pass

    def dispose(self):
        self.__viewModel = None
        self.tooltipFactory = None
        return


class SelectOptionContent(ViewImpl):
    __slots__ = ('__presenterList', 'onSelectionChanged', '__selectedIndex')

    def __init__(self, layoutID=None):
        settings = ViewSettings(layoutID or R.views.dialogs.sub_views.content.SelectOptionContent())
        settings.model = SelectOptionViewModel()
        super(SelectOptionContent, self).__init__(settings)
        self.__presenterList = []
        self.onSelectionChanged = Event()
        self.selectedIndex = -1

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def selectedIndex(self):
        return self.__selectedIndex

    @selectedIndex.setter
    def selectedIndex(self, value):
        self.__selectedIndex = value
        indexes = self.viewModel.getSelectedIndexes()
        indexes.clear()
        indexes.addNumber(value)
        indexes.invalidate()

    def setMessage(self, value):
        self.viewModel.setMessage(value)

    def addOption(self, controller):
        self.__presenterList.append(controller)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.dialogs.common.DialogTemplateGenericTooltip():
            index = int(event.getArgument('index', -1))
            if -1 < index < len(self.__presenterList):
                tooltipFactory = self.__presenterList[index].tooltipFactory
                if tooltipFactory:
                    return tooltipFactory()
        return super(SelectOptionContent, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(SelectOptionContent, self)._onLoading(*args, **kwargs)
        items = self.viewModel.getItems()
        for presenter in self.__presenterList:
            items.addViewModel(presenter.viewModel)
            presenter.initialize()

        self.viewModel.onClicked += self.__itemClickHandler

    def _finalize(self):
        super(SelectOptionContent, self)._finalize()
        self.viewModel.onClicked -= self.__itemClickHandler
        for controller in self.__presenterList:
            controller.dispose()

        self.__presenterList = []

    def __itemClickHandler(self, args):
        index = int(args.get('index', -1))
        if index != self.selectedIndex:
            self.selectedIndex = index
            self.onSelectionChanged()


class MoneyOption(SelectOptionBasePresenter):
    __slots__ = ('__price',)
    _VIEW_MODEL = SelectMoneyViewModel
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, price):
        super(MoneyOption, self).__init__()
        self.__price = price
        self.viewModel.setComponentType(ComponentType.MONEY)
        self.viewModel.cost.setSize(CurrencySize.SMALL)
        self.viewModel.tooltip.setType(TooltipType.BACKPORT)
        self.tooltipFactory = self._tooltipFactory

    @property
    def viewModel(self):
        return super(MoneyOption, self).viewModel

    def initialize(self):
        super(MoneyOption, self).initialize()
        g_clientUpdateManager.addMoneyCallback(self._moneyChangeHandler)
        self._moneyChangeHandler()
        self._updateMoney()
        self._updateIcon()

    def dispose(self):
        super(MoneyOption, self).dispose()
        g_clientUpdateManager.removeObjectCallbacks(self)

    def _moneyChangeHandler(self, *_):
        self._updateShortage()

    def updatePrice(self, newPrice):
        if newPrice != self.__price:
            self.__price = newPrice
            self._updateMoney()
            self._updateShortage()

    @property
    def shortage(self):
        return self._itemsCache.items.stats.money.getShortage(self.__price.price)

    def _updateShortage(self):
        with self.viewModel.transaction() as vm:
            cost = vm.cost
            hasShortage = bool(self.shortage)
            cost.setIsEnough(not hasShortage)
            vm.setIsDisabled(hasShortage)

    def _updateMoney(self):
        with self.viewModel.transaction() as vm:
            cost = vm.cost
            currency = self.__price.getCurrency()
            cost.setType(CurrencyType(currency))
            cost.setValue(int(self.__price.price.get(currency)))
            cost.setIsDiscount(self.__price.isActionPrice())

    def _updateIcon(self):
        currency = self.__price.getCurrency()
        if currency == Currency.GOLD:
            self.viewModel.setIcon(R.images.gui.maps.uiKit.dialog_templates.select_option.iconGold())
        else:
            raise SoftException('Given currency (%s) is not supported. Please provide an icon' % currency)

    def _tooltipFactory(self):
        currency = self.__price.getCurrency()
        return createBackportTooltipContent(isSpecial=True, specialAlias=getCurrencyTooltipAlias(currency))


class DemountKitOption(SelectOptionBasePresenter):
    __slots__ = ('__demountKit',)
    _VIEW_MODEL = SelectDemountKitViewModel
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, itemCD):
        super(DemountKitOption, self).__init__()
        item = self._itemsCache.items.getItemByCD(itemCD)
        self.__demountKit, _ = getDemountKitForOptDevice(item)
        self.viewModel.setIcon(R.images.gui.maps.icons.demountKit.common_150x150())
        self.viewModel.setText(backport.text(R.strings.demount_kit.equipmentDemount.optionFree()))
        self.viewModel.setComponentType(ComponentType.DEMOUNT_KIT)
        self.viewModel.tooltip.setType(TooltipType.BACKPORT)
        self.tooltipFactory = self._tooltipFactory

    @property
    def viewModel(self):
        return super(DemountKitOption, self).viewModel

    def initialize(self):
        super(DemountKitOption, self).initialize()
        g_clientUpdateManager.addCallbacks({'goodies': self._goodiesChangeHandler})
        self._goodiesChangeHandler()

    def dispose(self):
        super(DemountKitOption, self).dispose()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__demountKit = None
        return

    def _goodiesChangeHandler(self, *_):
        with self.viewModel.transaction() as vm:
            vm.setIsDisabled(self.__demountKit.inventoryCount == 0)
            vm.setStorageCount(self.__demountKit.inventoryCount)

    def _tooltipFactory(self):
        return createBackportTooltipContent(TOOLTIPS_CONSTANTS.AWARD_DEMOUNT_KIT, (self.__demountKit.goodieID,))
