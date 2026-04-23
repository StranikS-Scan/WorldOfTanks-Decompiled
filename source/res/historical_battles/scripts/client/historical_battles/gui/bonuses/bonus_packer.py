# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/bonuses/bonus_packer.py
import typing
from gui.battle_pass.battle_pass_bonuses_packers import getBattlePassBonusPacker, ExtendedItemBonusUIPacker
from gui.impl import backport
from gui.impl.backport import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel
from gui.server_events.formatters import COMPLEX_TOKEN
from gui.shared.missions.packers.bonus import SimpleBonusUIPacker, getLocalizedBonusName, TokenBonusUIPacker, BattlePassPointsBonusPacker
from gui.shared.money import Currency
from gui.shared.utils.functions import makeTooltip
from gui.battle_pass.battle_pass_bonuses_packers import TmanTemplateBonusPacker
from gui.server_events.recruit_helper import getRecruitInfo
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from helpers import dependency
from historical_battles_common.hb_constants import HBTokens, FRONT_COUPON_TOKEN_PREFIX
from historical_battles_common.helpers_common import parseCompensationToken
from historical_battles.gui.bonuses import VehicleDiscountBonusModel, VehicleDiscountCompensationBonusModel
from historical_battles.hb_constants import ORDER_TOKEN_NAME_TO_ORDER_TYPE
from historical_battles.skeletons.game_controller import IHBProgressionOnTokensController
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import CurrenciesBonus, EntitlementBonus, TokensBonus

class ExtendedCurrencyBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus, '')]

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        model.setIcon(bonus.getName())
        model.setValue(str(bonus.getValue()))
        model.setUserName(getLocalizedBonusName(bonus.getName()))
        model.setBigIcon(bonus.getName())
        return model

    @classmethod
    def _getBonusModel(cls):
        return RewardItemModel()


class EntitlementBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus, '')]

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        entitlementID = bonus.getValue().id
        model.setIconSmall(entitlementID)
        model.setIconBig(entitlementID)
        model.setUserName(bonus.getUserName(entitlementID))
        model.setLabel(model.getUserName())
        model.setName(entitlementID)
        return model

    @classmethod
    def _getBonusModel(cls):
        return TokenBonusModel()

    @classmethod
    def getToolTip(cls, bonus):
        entitlementID = bonus.getValue().id
        header = backport.text(R.strings.hb_tooltips.entitlement.dyn(entitlementID).header())
        body = backport.text(R.strings.hb_tooltips.entitlement.dyn(entitlementID).body())
        tooltipData = makeTooltip(header or None, body or None)
        return [createTooltipData(tooltipData)]


class CurrenciesBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        label = getLocalizedBonusName(bonus.getCode())
        return [cls._packSingleBonus(bonus, label if label else '')]

    @classmethod
    def _packCommon(cls, bonus, model):
        model.setName(bonus.getCode())
        model.setIsCompensation(bonus.isCompensation())
        return model

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(bonus.getValue()))
        model.setLabel(label)
        model.setUserName(label)
        model.setBigIcon(bonus.getName())
        return model

    @classmethod
    def _getBonusModel(cls):
        return RewardItemModel()


class HBTokenBonusType(object):
    PROGRESSION_TOKEN = 'HBProgressionToken'
    COUPON_TOKEN = 'hb_front_coupon'
    MAIN_DISCOUNT_TOKEN = 'historical_battles_main_discount'
    MAIN_DISCOUNT_COMPENSATION = 'historical_battles_main_discount_compensation'


class HBTokenBonusUIPacker(TokenBonusUIPacker):
    _HBProgressionController = dependency.descriptor(IHBProgressionOnTokensController)
    _gameEventController = dependency.descriptor(IGameEventController)

    @classmethod
    def _getTokenBonusType(cls, tokenID, complexToken):
        if tokenID.startswith(cls._HBProgressionController.progressionToken):
            return HBTokenBonusType.PROGRESSION_TOKEN
        if tokenID.startswith(FRONT_COUPON_TOKEN_PREFIX):
            return HBTokenBonusType.COUPON_TOKEN
        if tokenID == cls._gameEventController.getMainDiscount().get('tokenName'):
            return HBTokenBonusType.MAIN_DISCOUNT_TOKEN
        if tokenID.startswith(HBTokens.MAIN_VEHICLE_DISCOUNT_COMPENSATION):
            return HBTokenBonusType.MAIN_DISCOUNT_COMPENSATION
        super(HBTokenBonusUIPacker, cls)._getTokenBonusType(tokenID, complexToken)

    @classmethod
    def _getTooltipsPackers(cls):
        pakers = super(HBTokenBonusUIPacker, cls)._getTooltipsPackers()
        pakers.update({HBTokenBonusType.PROGRESSION_TOKEN: cls.__getHBProgressionTooltip,
         HBTokenBonusType.COUPON_TOKEN: cls.__getHBCouponsTooltip,
         HBTokenBonusType.MAIN_DISCOUNT_TOKEN: cls.__getHBMainDiscountTooltip,
         HBTokenBonusType.MAIN_DISCOUNT_COMPENSATION: cls.__getMainDiscountCompensationTooltip})
        return pakers

    @classmethod
    def _getTokenBonusPackers(cls):
        tokenBonusPackers = super(HBTokenBonusUIPacker, cls)._getTokenBonusPackers()
        complexPaker = tokenBonusPackers.get(COMPLEX_TOKEN)
        tokenBonusPackers.update({HBTokenBonusType.PROGRESSION_TOKEN: complexPaker,
         HBTokenBonusType.COUPON_TOKEN: cls.__packCouponBonus,
         HBTokenBonusType.MAIN_DISCOUNT_TOKEN: cls.__packMainDiscountBonus,
         HBTokenBonusType.MAIN_DISCOUNT_COMPENSATION: cls.__packMainDiscountCompensationBonus})
        return tokenBonusPackers

    @classmethod
    def _getContentId(cls, bonus):
        result = super(HBTokenBonusUIPacker, cls)._getContentId(bonus)
        bonusNames = bonus.getValue().keys()
        for bonusName in bonusNames:
            tooltipView = None
            if bonusName.startswith(HBTokenBonusType.COUPON_TOKEN):
                tooltipView = R.views.historical_battles.lobby.tooltips.OrderTooltip()
            elif bonusName == HBTokenBonusType.MAIN_DISCOUNT_TOKEN:
                tooltipView = R.views.historical_battles.lobby.tooltips.HbMainDiscountTooltipView()
            elif bonusName.startswith(HBTokenBonusType.MAIN_DISCOUNT_COMPENSATION):
                tooltipView = R.views.historical_battles.lobby.tooltips.HbCompensationRewardTooltip()
            if tooltipView:
                index = bonusNames.index(bonusName)
                result[index] = tooltipView

        return result

    @classmethod
    def __getHBProgressionTooltip(cls, *_):
        tokenBase = R.strings.historical_battles_progression.quests.bonuses.progressionToken
        return createTooltipData(makeTooltip(backport.text(tokenBase.header()), backport.text(tokenBase.body())))

    @classmethod
    def __getHBCouponsTooltip(cls, *args):
        orderType = ORDER_TOKEN_NAME_TO_ORDER_TYPE.get(args[0].styleID, None)
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.HB_ORDER_TOOLTIP, specialArgs={'orderType': orderType.value if orderType else None})

    @classmethod
    def __getHBMainDiscountTooltip(cls, *_):
        return createTooltipData(tooltip='', isSpecial=True)

    @classmethod
    def __getMainDiscountCompensationTooltip(cls, *args):
        compensationToken = args[1].id
        return createTooltipData(tooltip='', isSpecial=True, specialArgs={'tokenID': compensationToken})

    @classmethod
    def __packCouponBonus(cls, tokenBonusModel, bonus, *_):
        model = RewardItemModel()
        keys = bonus.getValue().keys()
        if keys:
            couponName = keys[0]
            model.setName(couponName)
            model.setUserName(backport.text(R.strings.quests.bonusName.dyn(couponName)()))
            model.setIcon(couponName)
            model.setBigIcon(backport.image(R.images.gui.maps.icons.quests.bonuses.big.dyn(couponName)()))
            count = bonus.getCount()
            if count > 1:
                model.setValue(str(count))
        tokenBonusModel.unbind()
        return model

    @classmethod
    def __packMainDiscountBonus(cls, tokenBonusModel, bonus, *_):
        model = VehicleDiscountBonusModel()
        cls.__fillVehicleDiscountBonus(model, bonus)
        tokenBonusModel.unbind()
        return model

    @classmethod
    def __packMainDiscountCompensationBonus(cls, tokenBonusModel, bonus, *_):
        model = VehicleDiscountCompensationBonusModel()
        cls.__fillVehicleDiscountBonus(model, bonus)
        token = next(bonus.getValue().iterkeys(), '')
        currency, amount = parseCompensationToken(token)
        model.setCompensationAmount(amount)
        model.setCompensationCurrency(currency)
        tokenBonusModel.unbind()
        return model

    @classmethod
    def __fillVehicleDiscountBonus(cls, model, bonus):
        heroTankController = cls._gameEventController.heroTank
        heroTankVehicle = heroTankController.getVehicle()
        discountPerToken = cls._gameEventController.getMainDiscount()['discountPerToken']
        keys = bonus.getValue().keys()
        if not keys:
            return
        name = keys[0].split(':')[0]
        model.setName(name)
        model.setLabel(model.getUserName())
        model.setIconSmall(backport.image(R.images.gui.maps.icons.quests.bonuses.small.dyn(name)()))
        model.setIconBig(backport.image(R.images.gui.maps.icons.quests.bonuses.big.dyn(name)()))
        model.setTankUserName(heroTankVehicle.userName)
        model.setTankLevel(heroTankVehicle.level)
        model.setTankType(heroTankVehicle.type)
        model.setIsElite(heroTankVehicle.isElite)
        model.setDiscountPercent(discountPerToken)


class HBTmanTemplateBonusPacker(TmanTemplateBonusPacker):

    @classmethod
    def _packTmanTemplateToken(cls, tokenID, bonus):
        recruitInfo = getRecruitInfo(tokenID)
        if recruitInfo is None:
            return
        else:
            model = RewardItemModel()
            cls._packCommon(bonus, model)
            bonusImageName = recruitInfo.getSourceID()
            model.setIcon(bonusImageName)
            tankManFullName = recruitInfo.getFullUserName()
            model.setUserName(tankManFullName)
            model.setLabel(tankManFullName)
            model.setBigIcon('_'.join([bonusImageName, recruitInfo.getGroupName()]))
            model.setIsCollectionEntity(cls._isCollectionItem(recruitInfo.getGroupName()))
            cls._injectAwardID(model, recruitInfo.getGroupName())
            return model


class HBBattlePassPointsBonusPacker(BattlePassPointsBonusPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = super(HBBattlePassPointsBonusPacker, cls)._packSingleBonus(bonus, label)
        model.setIcon(bonus.getName())
        return model

    @classmethod
    def _getBonusModel(cls):
        return IconBonusModel()


class HBExtendedItemBonusUIPacker(ExtendedItemBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, count):
        model = super(HBExtendedItemBonusUIPacker, cls)._packSingleBonus(bonus, item, count)
        if not model.getIcon():
            model.setIcon(model.getBigIcon())
        return model


def getBonusPacker():
    packer = getBattlePassBonusPacker()
    currencyBonusUIPacker = ExtendedCurrencyBonusUIPacker()
    tokenBonusPacker = HBTokenBonusUIPacker()
    packer.getPackers().update({'battlePassPoints': HBBattlePassPointsBonusPacker(),
     'currencies': CurrenciesBonusUIPacker(),
     Currency.CREDITS: currencyBonusUIPacker,
     Currency.CRYSTAL: currencyBonusUIPacker,
     'items': HBExtendedItemBonusUIPacker(),
     'token': tokenBonusPacker,
     'battleToken': tokenBonusPacker,
     'tmanToken': HBTmanTemplateBonusPacker(),
     'HBCoupon': tokenBonusPacker})
    return packer
