# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/summer_sale/tooltips/event_currency_tooltip.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.summer_sale.event_currency_tooltip_model import EventCurrencyTooltipModel
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.pub import ViewImpl
from gui.summer_sale.bonus_packers import getSummerSaleRewardsBonusPacker
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import ISummerSaleController
from skeletons.gui.shared import IItemsCache

class EventCurrencyTooltip(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __summerSale = dependency.descriptor(ISummerSaleController)
    __slots__ = ('__lootBox', '__currencyType')

    def __init__(self, currencyType):
        settings = ViewSettings(R.views.lobby.summer_sale.EventCurrencyTooltip())
        settings.flags = ViewFlags.VIEW
        settings.model = EventCurrencyTooltipModel()
        super(EventCurrencyTooltip, self).__init__(settings)
        self.__lootBox = first((lb for lb in self.__itemsCache.items.tokens.getLootBoxes().itervalues() if lb.getCategory() == self.__summerSale.getSummerSaleSetCategory()))
        self.__currencyType = currencyType

    @property
    def viewModel(self):
        return super(EventCurrencyTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        slots = self.__lootBox.getBonusSlots()
        foundBonuses = []
        for slot in slots.itervalues():
            for bonus in slot.get('bonuses', []):
                if any((wrappedBonus['type'] == self.__currencyType for wrappedBonus in bonus.getWrappedEpicBonusList())):
                    foundBonuses.append(bonus)

        with self.getViewModel().transaction() as tx:
            bonusModel = tx.getRewards()
            bonusModel.clear()
            packBonusModelAndTooltipData(foundBonuses, bonusModel, packer=getSummerSaleRewardsBonusPacker())
            bonusModel.invalidate()
            tx.setRewardsGroup(self.__currencyType.split('/')[-1])
