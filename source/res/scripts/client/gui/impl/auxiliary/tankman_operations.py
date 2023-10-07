# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/tankman_operations.py
import json
import typing
from typing import TYPE_CHECKING
from constants import SwitchState
from frameworks.wulf import Array
from gui.customization.shared import getPurchaseMoneyState, isTransactionValid, MoneyForPurchase
from gui.goodies import IGoodiesCache
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.dialog_template_generic_tooltip_view_model import TooltipType
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencyType, CurrencySize
from gui.impl.gen.view_models.views.lobby.crew.common.crew_widget_tankman_skill_model import CrewWidgetTankmanSkillModel, SkillType
from gui.impl.gen.view_models.views.lobby.crew.dialogs.price_card_model import PriceCardModel, CardType, CardState
from gui.impl.lobby.crew.crew_helpers.skill_helpers import getTmanNewSkillCount
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.money import Currency, Money, MONEY_ZERO_CREDITS, MONEY_ZERO_GOLD
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from gui.impl.lobby.crew.crew_helpers.model_setters import setTmanSkillsModel
if TYPE_CHECKING:
    from gui.shared.gui_items import Tankman
    from gui.impl.gen.view_models.views.lobby.crew.common.crew_widget_tankman_model import CrewWidgetTankmanModel
_CARD_LOC = R.strings.dialogs.priceCard
_RESET_LOC = R.strings.dialogs.perksRest.priceCard
_RETRAIN_LOC = R.strings.dialogs.retrain.priceCard
_RECRUIT_LOC = R.strings.dialogs.recruit.priceCard
_IMAGE = R.images.gui.maps.icons.common.components.price_card
_LEVEL_TO_HIGHLIGHT = 100
_MINIMUM_TO_HIGHLIGHT = 100
FREE = 'free'
MONEY_FREE = Money(credits=0, gold=0)
ITEM_PRICE_FREE = ItemPrice(price=MONEY_FREE, defPrice=MONEY_FREE)

def _toPercents(value):
    return int(value * 100)


def getPriceData(itemPrice):
    if itemPrice.price > MONEY_ZERO_GOLD:
        return (backport.image(_IMAGE.gold()), backport.text(_CARD_LOC.gold.title()), Currency.GOLD)
    if itemPrice.price > MONEY_ZERO_CREDITS:
        return (backport.image(_IMAGE.credit()), backport.text(_CARD_LOC.credits.title()), Currency.CREDITS)
    return (backport.image(_IMAGE.free()), backport.text(_CARD_LOC.free.title()), FREE) if itemPrice == ITEM_PRICE_FREE else ('', '', '')


def getOperationCardState(itemPrice):
    purchaseMoneyState = getPurchaseMoneyState(itemPrice.price)
    cardState = CardState.DISABLED if not isTransactionValid(purchaseMoneyState, itemPrice.price) else CardState.DEFAULT
    return (cardState, purchaseMoneyState)


def getPriceDescriptionData(itemPrice, value, descLoc, isHighlight=False):
    args = json.dumps({'value': value,
     'isHighlight': isHighlight}, True)
    if itemPrice.price > MONEY_ZERO_GOLD:
        return (str(backport.text(descLoc.gold.description())), args)
    if itemPrice.price > MONEY_ZERO_CREDITS:
        return (str(backport.text(descLoc.credits.description())), args)
    return (str(backport.text(descLoc.free.description())), args) if itemPrice == ITEM_PRICE_FREE else ('', '')


def packPriceList(wulfList, priceData, packCustomValues=None):
    for itemPrice, customData, key in priceData:
        isDiscount = itemPrice.isActionPrice()
        icon, title, currency = getPriceData(itemPrice)
        cardState, purchaseMoneyState = getOperationCardState(itemPrice)
        isEnough = purchaseMoneyState == MoneyForPurchase.ENOUGH
        cardModel = PriceCardModel()
        cardModel.setId(str(key))
        cardModel.setIcon(icon)
        cardModel.setTitle(title)
        cardModel.setCardState(cardState)
        cardModel.tooltip.setType(TooltipType.BACKPORT if isDiscount or not isEnough else TooltipType.ABSENT)
        cardModel.setCardType(CardType.DEFAULT)
        if Currency.hasValue(currency):
            priceModel = cardModel.price
            priceModel.setType(CurrencyType(currency))
            priceModel.setValue(int(itemPrice.price.get(currency, 0)))
            priceModel.setIsDiscount(isDiscount)
            priceModel.setSize(CurrencySize.BIG)
            priceModel.setDiscountValue(itemPrice.getActionPrc())
            priceModel.setIsEnough(isEnough)
        if packCustomValues:
            packCustomValues(cardModel, (itemPrice, customData, key))
        wulfList.addViewModel(cardModel)


@dependency.replace_none_kwargs(goodiesCache=IGoodiesCache, lobbyContext=ILobbyContext)
def packSkillReset(wulfList, priceData, goodiesCache=None, lobbyContext=None):

    def _packCustomValues(cardVM, customData):
        itemPrice, xpReuseFraction, _ = customData
        description, kwargs = getPriceDescriptionData(itemPrice, _toPercents(xpReuseFraction), _RESET_LOC, xpReuseFraction == 100)
        cardVM.setDescription(description)
        cardVM.setKwargs(kwargs)
        cardVM.setCardType(CardType.RESET)

    packPriceList(wulfList, priceData, _packCustomValues)
    form = goodiesCache.getRecertificationForm(currency='gold')
    if SwitchState.ENABLED.value == lobbyContext.getServerSettings().recertificationFormState() and form.enabled:
        formsCount = form.count
        cardModel = PriceCardModel()
        cardModel.setIcon(backport.image(_IMAGE.recertification()))
        cardModel.setTitle(backport.text(_CARD_LOC.recertification.title()))
        cardModel.setCardState(CardState.DISABLED if formsCount == 0 else CardState.DEFAULT)
        cardModel.setDescription(str(backport.text(_RESET_LOC.gold.description())))
        cardModel.setKwargs(json.dumps({'value': 100,
         'storageCount': formsCount,
         'isHighlight': True}, True))
        cardModel.setCardType(CardType.RESET)
        cardModel.setDescription(str(backport.text(_RESET_LOC.gold.description())))
        wulfList.addViewModel(cardModel)


def packPerksResetTankmanBefore(vmTankman, tankman):
    vmSkillsList = vmTankman.getSkills()
    setTmanSkillsModel(vmSkillsList, tankman)
    _, lastNewSkillLvl = getTmanNewSkillCount(tankman)
    vmTankman.setLastSkillLevel(lastNewSkillLvl.intSkillLvl)


def packPerksResetTankmanAfter(vm, tankman):
    vmTankman = vm
    vmSkillsList = vmTankman.getSkills()
    vmSkillsList.clear()
    for skill in tankman.skills:
        vmSkill = CrewWidgetTankmanSkillModel()
        vmSkill.setName(skill.name)
        vmSkill.setIcon(skill.extensionLessIconName)
        skillType = SkillType.LEARNING if skill.level < 100 else SkillType.LEARNED
        vmSkill.setType(skillType)
        vmSkillsList.addViewModel(vmSkill)

    vmSkillsList.invalidate()
    newSkillsCount, lastNewSkillLvl = getTmanNewSkillCount(tankman)
    newSkillsCount += tankman.newFreeSkillsCount
    vmTankman.setNewSkillsAmount(newSkillsCount)
    lastSkillLevel = lastNewSkillLvl.intSkillLvl if newSkillsCount > 0 else tankman.descriptor.lastSkillLevel
    vmTankman.setLastSkillLevel(lastSkillLevel)


def packRetrain(wulfList, priceData):

    def _packCustomValues(cardVM, customData):
        itemPrice, (minLevel, maxLevel, isUselessForTankman), _ = customData
        isUseless = all((isUseless for isUseless in isUselessForTankman))
        isRange = minLevel != maxLevel
        roleLevel = '{}-{}'.format(minLevel, maxLevel) if isRange else minLevel
        description, kwargs = getPriceDescriptionData(itemPrice, roleLevel, _RETRAIN_LOC, minLevel == _MINIMUM_TO_HIGHLIGHT)
        cardVM.setDescription(description)
        cardVM.setKwargs(kwargs)
        cardVM.setCardType(CardType.RETRAIN)
        if isUseless:
            cardVM.setCardState(CardState.DISABLED)

    packPriceList(wulfList, priceData, _packCustomValues)


def packRecruit(wulfList, priceData):

    def _packCustomValues(cardVM, customData):
        itemPrice, cost, _ = customData
        roleLevel = cost.get('roleLevel', 0)
        description, kwargs = getPriceDescriptionData(itemPrice, roleLevel, _RECRUIT_LOC, roleLevel == _LEVEL_TO_HIGHLIGHT)
        cardVM.setDescription(description)
        cardVM.setKwargs(kwargs)
        cardVM.setCardType(CardType.RECRUIT)

    packPriceList(wulfList, priceData, _packCustomValues)
