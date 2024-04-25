# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/dialogs/sub_views/content/order_with_bonuses.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.gen.view_models.views.lobby.historical_battles.dialogs.content.order_with_bonuses_model import OrderWithBonusesModel
from historical_battles.gui.impl.gen.view_models.views.lobby.shop_views.bundle_bonus_view_model import BundleBonusViewModel
from historical_battles.gui.impl.lobby.tooltips.order_tooltip import OrderTooltip

class Bonus(object):
    __slots__ = ('iconName', 'count', 'preformattedBonus')

    def __init__(self, iconName, count, preformattedBonus):
        super(Bonus, self).__init__()
        self.iconName = iconName
        self.count = count
        self.preformattedBonus = preformattedBonus


class Order(object):
    __slots__ = ('type', 'count')

    def __init__(self, orderType, count):
        super(Order, self).__init__()
        self.type = orderType
        self.count = count


class OrderWithBonuses(ViewImpl):
    _LAYOUT_DYN_ACCESSOR = R.views.lobby.historical_battles.dialogs.sub_views.content.OrderWithBonusesContent

    def __init__(self, order, bonusList, layoutID=None):
        settings = ViewSettings(layoutID or self._LAYOUT_DYN_ACCESSOR())
        settings.model = OrderWithBonusesModel()
        self._order = order
        settings.kwargs = {'order': order,
         'bonusList': bonusList}
        self.__bonusCache = {}
        super(OrderWithBonuses, self).__init__(settings)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.dialogs.common.DialogTemplateGenericTooltip():
            tooltipID = event.getArgument('tooltipID')
            if tooltipID == OrderWithBonusesModel.TOOLTIP_BONUS:
                bonus = self.__bonusCache.get(int(event.getArgument('id')), None)
                if bonus:
                    return createBackportTooltipContent(tooltip=bonus.tooltip, isSpecial=bonus.isSpecial, specialAlias=bonus.specialAlias, specialArgs=bonus.specialArgs)
            elif tooltipID == OrderWithBonusesModel.TOOLTIP_ORDER:
                return OrderTooltip(self._order.type.value, True, False)
        return super(OrderWithBonuses, self).createToolTipContent(event, contentID)

    def _onLoading(self, order, bonusList, *args, **kwargs):
        super(OrderWithBonuses, self)._onLoading(*args, **kwargs)
        with self.getViewModel().transaction() as viewModel:
            viewModel.order.setCount(order.count)
            viewModel.order.setType(order.type)
            bonuses = viewModel.getBonuses()
            for i, bonus in enumerate(bonusList):
                self.__bonusCache[i] = bonus.preformattedBonus
                vm = BundleBonusViewModel()
                vm.setAmount(bonus.count)
                vm.setIconName(bonus.iconName)
                vm.tooltip.setId(i)
                bonuses.addViewModel(vm)

            bonuses.invalidate()

    def _finalize(self):
        self.__bonusCache.clear()
        super(OrderWithBonuses, self)._finalize()
