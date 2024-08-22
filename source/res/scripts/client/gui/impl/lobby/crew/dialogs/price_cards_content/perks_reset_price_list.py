# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/price_cards_content/perks_reset_price_list.py
import typing
from frameworks.wulf import ViewSettings, Array
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.goodies import IGoodiesCache
from gui.impl.auxiliary.tankman_operations import packSkillReset
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.dialogs.price_list_model import PriceListModel
from gui.impl.lobby.crew.dialogs.price_cards_content.base_price_list import BasePriceList
from gui.shared.gui_items.Tankman import Tankman
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.money import Currency, DynamicMoney
from helpers import dependency
from items.tankmen import TankmanDescr, MIN_XP_REUSE_FRACTION, MAX_XP_REUSE_FRACTION
from skeletons.gui.lobby_context import ILobbyContext
from constants import SwitchState
from gui.impl.lobby.crew.crew_helpers.tankman_helpers import getPerksResetGracePeriod
if typing.TYPE_CHECKING:
    from gui.shared.utils.requesters import ShopRequester
    from gui.impl.gen.view_models.views.lobby.crew.dialogs.price_card_model import PriceCardModel

class PerksResetPriceList(BasePriceList):
    __slots__ = ('_tankman', '_goldOptionKey')
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, tankmanId):
        self._goldOptionKey = None
        self._tankman = self._itemsCache.items.getTankman(tankmanId)
        settings = ViewSettings(R.views.lobby.crew.widgets.PriceList())
        settings.model = PriceListModel()
        super(PerksResetPriceList, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def isRecertification(self):
        return self._selectedCardIndex == self.recertificationIndex

    @property
    def recertificationIndex(self):
        return len(self.viewModel.getCardsList()) - 1

    def createToolTipContent(self, event, contentID):
        index = int(event.getArgument('index'))
        if contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent() and index == self.recertificationIndex:
            form = self.__goodiesCache.getRecertificationForm(currency='gold')
            return createBackportTooltipContent(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.EPIC_BATTLE_RECERTIFICATION_FORM_TOOLTIP, specialArgs=[form.intCD])
        return super(PerksResetPriceList, self).createToolTipContent(event, contentID)

    @property
    def goldOptionKey(self):
        return self._goldOptionKey

    @property
    def _priceListPacker(self):
        return packSkillReset

    def _getCallbacks(self):
        callbacks = typing.cast(typing.Tuple, super(PerksResetPriceList, self)._getCallbacks())
        return callbacks + (('goodies', self._onGoodiesUpdate),)

    def _onGoodiesUpdate(self, *_):
        self._updateViewModel()

    def _fillPrices(self):
        shopRequester = self._itemsCache.items.shop
        dropSkillsCost = shopRequester.dropSkillsCost
        defaultDropSkillsCost = shopRequester.defaults.dropSkillsCost
        recertificationFormState = self.__lobbyContext.getServerSettings().recertificationFormState()
        needRecertificationForm = recertificationFormState == SwitchState.ENABLED.value and self.__goodiesCache.getRecertificationForm(currency='gold')
        self._priceData = []
        isFreeReset = getPerksResetGracePeriod() > 0 or not self._tankman.descriptor.firstSkillResetDisabled
        if isFreeReset:
            self._selectedCardIndex = next((idx for idx, cost in dropSkillsCost.items() if cost and cost['gold'] > 0), None)
        for key, cost in dropSkillsCost.iteritems():
            if not needRecertificationForm and cost.get('recertificationForm') > 0:
                continue
            if cost['gold'] > 0:
                self._goldOptionKey = key
            defCost = defaultDropSkillsCost.get(key, {})
            priceArgs = {}
            recertificationForms = cost.get('recertificationForm')
            if recertificationForms:
                priceArgs['recertificationForm'] = recertificationForms
            if isFreeReset:
                priceArgs['isFreeReset'] = True
            itemPrice = ItemPrice(price=DynamicMoney(credits=cost.get(Currency.CREDITS, 0), gold=cost.get(Currency.GOLD, 0), **priceArgs), defPrice=DynamicMoney(credits=defCost.get(Currency.CREDITS, 0), gold=defCost.get(Currency.GOLD, 0)))
            self._priceData.append((itemPrice, self.__getOperationData(cost), key))

        return

    def _onTankmanChanged(self, data):
        tankmanId = self._tankman.invID
        if tankmanId in data:
            if data[tankmanId] is None:
                self.destroyWindow()
                return
            self._fillPrices()
            self._updateViewModel()
        return

    def __getOperationData(self, cost):
        tmanDescr = TankmanDescr(self._tankman.strCD)
        xpReuseFraction = cost.get('xpReuseFraction', MIN_XP_REUSE_FRACTION)
        if xpReuseFraction < MAX_XP_REUSE_FRACTION:
            prevTmanXP = tmanDescr.totalXP()
            prevSkillsCount = tmanDescr.getFullSkillsCount()
            maxAvailbleSkillsNum = self._tankman.maxSkillsCount
            tmanDescr.dropSkills(xpReuseFraction)
            if prevSkillsCount < maxAvailbleSkillsNum:
                return (xpReuseFraction, prevTmanXP - tmanDescr.totalXP(), prevSkillsCount - tmanDescr.getFullSkillsCount())
            return (xpReuseFraction, prevTmanXP - tmanDescr.totalXP(), 0)
        return (xpReuseFraction, 0, 0)
