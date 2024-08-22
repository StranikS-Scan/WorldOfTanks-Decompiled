# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/tankman_operations.py
import json
import typing
from typing import TYPE_CHECKING
from frameworks.wulf import Array
from gui.customization.shared import getPurchaseMoneyState, isTransactionValid, MoneyForPurchase
from gui.goodies import IGoodiesCache
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.dialog_template_generic_tooltip_view_model import TooltipType
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencyType, CurrencySize
from gui.impl.gen.view_models.views.lobby.crew.common.crew_skill_model import CrewSkillModel
from gui.impl.gen.view_models.views.lobby.crew.common.dynamic_tooltip_model import DynamicTooltipModel
from gui.impl.gen.view_models.views.lobby.crew.crew_constants import CrewConstants
from gui.impl.gen.view_models.views.lobby.crew.dialogs.dialog_tankman_model import DialogTankmanModel
from gui.impl.gen.view_models.views.lobby.crew.dialogs.price_card_model import PriceCardModel, CardType, CardState
from gui.shared.gui_items.Tankman import TankmanSkill
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.money import Currency, Money, MONEY_ZERO_CREDITS, MONEY_ZERO_GOLD
from helpers import dependency
from items.tankmen import TankmanDescr, MAX_SKILL_LEVEL, MAX_SKILLS_EFFICIENCY
from skeletons.gui.lobby_context import ILobbyContext
if TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.crew.common.crew_skill_list_model import CrewSkillListModel
    from gui.impl.gen.view_models.views.lobby.crew.dialogs.dialog_tankman_base_model import DialogTankmanBaseModel
    from gui.shared.gui_items import Tankman
_DEFAULT_TITLE_LOC = R.strings.dialogs.priceCard
_RESET_LOC = R.strings.dialogs.perksReset.priceCard
_RETRAIN_LOC = R.strings.dialogs.retrain.priceCard
_RECRUIT_LOC = R.strings.dialogs.recruit.priceCard
_IMAGE = R.images.gui.maps.icons.common.components.price_card
_LEVEL_TO_HIGHLIGHT = 100
_MINIMUM_TO_HIGHLIGHT = 1
FREE = 'free'
MONEY_FREE = Money(credits=0, gold=0)
ITEM_PRICE_FREE = ItemPrice(price=MONEY_FREE, defPrice=MONEY_FREE)

def _toPercents(value):
    return int(value * 100)


def getPriceData(itemPrice, rIconPath, rTitlePath, isFreeReset):
    if itemPrice.defPrice > MONEY_ZERO_GOLD:
        return (backport.image(rIconPath.gold()), backport.text(rTitlePath.gold.title()), Currency.GOLD)
    if itemPrice.defPrice > MONEY_ZERO_CREDITS:
        return (backport.image(rIconPath.credit()), backport.text(rTitlePath.credits.title()), Currency.CREDITS)
    return (backport.image(rIconPath.free()), backport.text(rTitlePath.free.title()), FREE) if itemPrice == ITEM_PRICE_FREE or isFreeReset else ('', '', '')


def getOperationCardState(itemPrice):
    purchaseMoneyState = getPurchaseMoneyState(itemPrice.price)
    cardState = CardState.DISABLED if not isTransactionValid(purchaseMoneyState, itemPrice.price) else CardState.DEFAULT
    return (cardState, purchaseMoneyState)


def getPriceDescriptionData(itemPrice, value, descLoc, isHighlight=False, **kwargs):
    isFreeReset = kwargs.get('isFreeReset')
    defaultKwargs = {'value': value,
     'isHighlight': isHighlight}
    defaultKwargs.update(kwargs)
    args = json.dumps(defaultKwargs, True)
    if itemPrice.defPrice > MONEY_ZERO_GOLD:
        return (str(backport.text(descLoc.gold.description())), args)
    if itemPrice.defPrice > MONEY_ZERO_CREDITS:
        return (str(backport.text(descLoc.credits.description())), args)
    return (str(backport.text(descLoc.free.description())), args) if itemPrice == ITEM_PRICE_FREE or isFreeReset else ('', '')


@dependency.replace_none_kwargs(goodiesCache=IGoodiesCache)
def packRecertificationForm(wulfList, goodiesCache=None, isFreeReset=False):
    form = goodiesCache.getRecertificationForm(currency='gold')
    formsCount = form.count
    cardModel = PriceCardModel()
    cardModel.setIcon(backport.image(_IMAGE.perk_reset.recertification()))
    cardModel.setTitle(backport.text(_DEFAULT_TITLE_LOC.recertification.title()))
    cardModel.setCardState(CardState.DISABLED if formsCount == 0 or isFreeReset else CardState.DEFAULT)
    cardModel.setDescription(str(backport.text(_RESET_LOC.gold.description())))
    if isFreeReset:
        cardModel.cardTooltip.setHeader(R.strings.dialogs.perksReset.discountTooltip.header())
        cardModel.cardTooltip.setBody(R.strings.dialogs.perksReset.discountTooltip.body())
    else:
        cardModel.cardTooltip.setContentId(R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent())
        cardModel.cardTooltip.setTargetId(R.views.lobby.crew.widgets.PriceList())
    cardModel.setKwargs(json.dumps({'value': 100,
     'storageCount': formsCount,
     'isHighlight': True,
     'isRecertificationCard': True}, True))
    cardModel.setCardType(CardType.RESET)
    cardModel.setDescription(str(backport.text(_RESET_LOC.gold.description())))
    wulfList.addViewModel(cardModel)


def packPriceList(wulfList, priceData, packCustomValues=None, rIconPath=_IMAGE.default, rTitlePath=_DEFAULT_TITLE_LOC):
    for itemPrice, customData, key in priceData:
        price = itemPrice.price
        isFreeReset = price.get('isFreeReset')
        if price.get('recertificationForm'):
            packRecertificationForm(wulfList, isFreeReset=isFreeReset)
            continue
        isDiscount = False if isFreeReset else itemPrice.isActionPrice()
        icon, title, currency = getPriceData(itemPrice, rIconPath, rTitlePath, isFreeReset)
        cardState, purchaseMoneyState = getOperationCardState(itemPrice)
        isEnough = purchaseMoneyState == MoneyForPurchase.ENOUGH
        cardModel = PriceCardModel()
        cardModel.setId(str(key))
        cardModel.setIcon(icon)
        cardModel.setTitle(title)
        if isFreeReset and currency != Currency.GOLD:
            cardModel.setCardState(CardState.DISABLED)
        else:
            cardModel.setCardState(cardState)
        cardModel.priceTooltip.setType(TooltipType.BACKPORT if isDiscount or not isEnough else TooltipType.ABSENT)
        cardModel.setCardType(CardType.DEFAULT)
        if Currency.hasValue(currency):
            priceModel = cardModel.price
            priceModel.setType(CurrencyType(currency))
            if isFreeReset and currency == Currency.GOLD:
                priceModel.setValue(0)
                priceModel.setIsDiscount(False)
            else:
                priceModel.setValue(int(price.get(currency, 0)))
                priceModel.setIsDiscount(isDiscount)
            priceModel.setSize(CurrencySize.BIG)
            priceModel.setIsEnough(isEnough)
        if packCustomValues:
            packCustomValues(cardModel, (itemPrice, customData, key))
        wulfList.addViewModel(cardModel)


def packTooltipModel(model, data):
    if not data:
        return
    contentId = data.get('contentId', 0)
    header = data.get('header', R.invalid)
    body = data.get('body', R.invalid)
    model.setContentId(contentId)
    model.setHeader(header)
    model.setBody(body)


def packSkillReset(wulfList, priceData):

    def _packCustomValues(cardVM, customData):
        itemPrice, (xpReuseFraction, xpLossAmount, _), _ = customData
        isGoldCard = itemPrice.defPrice > MONEY_ZERO_GOLD
        isFreeReset = itemPrice.price.get('isFreeReset')
        withSpecialDiscount = isGoldCard and isFreeReset
        description, kwargs = getPriceDescriptionData(itemPrice, _toPercents(xpReuseFraction), _RESET_LOC, bool(xpLossAmount), xpLossAmount=xpLossAmount, withSpecialDiscount=withSpecialDiscount, isFreeReset=isFreeReset)
        cardVM.setDescription(description)
        cardVM.setKwargs(kwargs)
        cardVM.setCardType(CardType.RESET)
        if isFreeReset:
            if cardVM.getCardState() == CardState.DISABLED:
                cardVM.cardTooltip.setHeader(R.strings.dialogs.perksReset.discountTooltip.header())
                cardVM.cardTooltip.setBody(R.strings.dialogs.perksReset.discountTooltip.body())
            elif itemPrice.defPrice > MONEY_ZERO_GOLD:
                cardVM.setCardState(CardState.SELECTED)

    packPriceList(wulfList, priceData, _packCustomValues, _IMAGE.perk_reset)


def packBaseTankman(vmTankman, tankman):
    descr = tankman.descriptor
    vmTankman.setInvId(tankman.invID)
    vmTankman.setRole(tankman.role)
    vmTankman.setIconName(tankman.getExtensionLessIconWithSkin())
    vmTankman.setIsInSkin(tankman.isInSkin)
    vmTankman.setIsFemale(descr.isFemale)


def packRetrainTankman(vmTankman, tankman, skillEfficiency=None):
    descr = tankman.descriptor
    packBaseTankman(vmTankman, tankman)
    vmTankman.setSkillEfficiency(tankman.currentVehicleSkillsEfficiency if skillEfficiency is None else skillEfficiency)
    vmTankman.setFullSkillsCount(descr.getFullSkillsCount())
    return


def packSkills(skillsData, tankman, skillEfficiency=None):
    skillsData.setSkillsEfficiency(tankman.currentVehicleSkillsEfficiency if skillEfficiency is None else skillEfficiency)
    packMajorSkills(skillsData, tankman)
    packBonusSkills(skillsData, tankman)
    return


def packMajorSkills(skillsData, tankman, skipIrrelevantCheck=False):
    notFullEarnedSkillMdl = None
    majorSkills = skillsData.getMajorSkills()
    majorSkills.clear()
    for skill in tankman.skills:
        skillModel = getSkillModel(skill=skill, tman=tankman, skipIrrelevantCheck=skipIrrelevantCheck)
        if skill.isMaxLevel:
            majorSkills.addViewModel(skillModel)
        notFullEarnedSkillMdl = skillModel

    for _ in xrange(tankman.newFreeSkillsCount):
        majorSkills.addViewModel(getSkillModel())

    if notFullEarnedSkillMdl:
        majorSkills.addViewModel(notFullEarnedSkillMdl)
    else:
        count, lastSkillLevel = tankman.newSkillsCount
        maxAvailbleSkillsNum = tankman.maxSkillsCount
        lastIdx = count - 1
        for idx in xrange(count):
            if idx == lastIdx >= maxAvailbleSkillsNum and not lastSkillLevel:
                break
            majorSkills.addViewModel(getSkillModel(level=lastSkillLevel if idx == lastIdx else MAX_SKILL_LEVEL))

    majorSkills.invalidate()
    return


def packBonusSkills(skillsData, tankman):
    bonusSkills = skillsData.getBonusSkills()
    bonusSkills.clear()
    skillModels = []
    for role, skills in tankman.bonusSkills.iteritems():
        for skill, level in zip(skills, tankman.bonusSlotsLevels):
            if level is None:
                continue
            skillModels.append(getSkillModel(level=level, skill=skill, tman=tankman, role=role))

    skillModels.sort(key=lambda sm: MAX_SKILL_LEVEL - sm.getLevel() + int(sm.getName() == CrewConstants.NEW_SKILL))
    for model in skillModels:
        bonusSkills.addViewModel(model)

    bonusSkills.invalidate()
    return


def getSkillModel(level=MAX_SKILL_LEVEL, skill=None, tman=None, role=None, skipIrrelevantCheck=False):
    skillModel = CrewSkillModel()
    skillModel.setLevel(level)
    if skill:
        skillModel.setName(skill.name)
        skillModel.setIcon(skill.extensionLessIconName)
        skillModel.setLevel(skill.level)
    else:
        skillModel.setName(CrewConstants.NEW_SKILL)
        skillModel.setIcon(CrewConstants.NEW_SKILL)
    if skill and tman and not skipIrrelevantCheck:
        skillModel.setIsIrrelevant(not skill.isRelevantForRole(role or tman.descriptor.role))
    return skillModel


def packMassRetrain(wulfList, priceData):

    def _packCustomValues(cardVM, customData):
        itemPrice, itemData, _ = customData
        efficiency = itemData['cost']['skillsEfficiency']
        description, kwargs = getPriceDescriptionData(itemPrice, _toPercents(efficiency), _RETRAIN_LOC, efficiency == _MINIMUM_TO_HIGHLIGHT)
        cardVM.setDescription(description)
        cardVM.setKwargs(kwargs)
        cardVM.setCardType(CardType.RETRAIN)
        if all(itemData['isCardDisabled']):
            cardVM.setCardState(CardState.DISABLED)

    packPriceList(wulfList, priceData, _packCustomValues, _IMAGE.retrain, _RETRAIN_LOC)


def packSingleRetrain(wulfList, priceData):

    def _packCustomValues(cardVM, customData):
        itemPrice, (isOperationDisable, skillEfficiency, cost, tooltipData), _ = customData
        debuffValue = _toPercents(cost['skillsEfficiencyWithRoleChange'])
        if cost['skillsEfficiencyWithRoleChange'] < 0 or cost['skillsEfficiencyWithRoleChange'] == cost['skillsEfficiency'] or skillEfficiency == MAX_SKILLS_EFFICIENCY:
            debuffValue = None
        description, kwargs = getPriceDescriptionData(itemPrice, _toPercents(skillEfficiency), _RETRAIN_LOC, skillEfficiency == _MINIMUM_TO_HIGHLIGHT, debuffValue=debuffValue)
        cardVM.setDescription(description)
        cardVM.setKwargs(kwargs)
        cardVM.setCardType(CardType.RETRAIN)
        packTooltipModel(cardVM.cardTooltip, tooltipData)
        if isOperationDisable:
            cardVM.setCardState(CardState.DISABLED)
            cardVM.cardTooltip.setHeader(R.strings.dialogs.retrain.discountTooltip.header())
            cardVM.cardTooltip.setBody(R.strings.dialogs.retrain.discountTooltip.body())
        return

    packPriceList(wulfList, priceData, _packCustomValues, _IMAGE.retrain, _RETRAIN_LOC)


def packRecruit(wulfList, priceData):

    def _packCustomValues(cardVM, customData):
        itemPrice, cardData, _ = customData
        xp = cardData['xp']
        skillLevel = TankmanDescr.getSkillLevelFromXp(1, xp)
        description, _ = getPriceDescriptionData(itemPrice, skillLevel, _RECRUIT_LOC)
        kwargs = json.dumps({'value': skillLevel,
         'isFreeCrew': cardData.get('isFreeCrew', False),
         'isHighlight': skillLevel == _LEVEL_TO_HIGHLIGHT}, True)
        cardVM.setDescription(description)
        cardVM.setKwargs(kwargs)
        cardVM.setCardType(CardType.RECRUIT)
        if cardData.get('disabled', False):
            cardVM.setCardState(CardState.DISABLED)

    packPriceList(wulfList, priceData, _packCustomValues, rTitlePath=_RECRUIT_LOC)
