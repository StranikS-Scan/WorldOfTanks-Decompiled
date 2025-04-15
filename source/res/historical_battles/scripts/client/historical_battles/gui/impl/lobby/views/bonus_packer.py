# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/views/bonus_packer.py
import typing
from historical_battles.skeletons.game_controller import IHBProgressionOnTokensController
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from gui.battle_pass.battle_pass_bonuses_packers import getBattlePassBonusPacker
from gui.impl import backport
from gui.impl.backport import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel
from gui.server_events.formatters import COMPLEX_TOKEN
from gui.shared.missions.packers.bonus import SimpleBonusUIPacker, getLocalizedBonusName, TokenBonusUIPacker
from gui.shared.money import Currency
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from gui.battle_pass.battle_pass_bonuses_packers import TmanTemplateBonusPacker
from gui.server_events.recruit_helper import getRecruitInfo
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from historical_battles.hb_constants import ORDER_TOKEN_NAME_TO_ORDER_TYPE
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


HB_PROGRESSION_TOKEN = 'HBProgressionToken'
HB_UNLOCK_VEHICLES_TOKEN = 'hbUnlockVehicles'
HB_COUPON_TOKEN = 'hb_front_coupon'
HB_MAIN_DISCOUNT_TOKEN = 'historical_battles_main_discount'

class HBTokenBonusUIPacker(TokenBonusUIPacker):
    _HBProgressionController = dependency.descriptor(IHBProgressionOnTokensController)
    _gameEventController = dependency.descriptor(IGameEventController)

    @classmethod
    def _getTokenBonusType(cls, tokenID, complexToken):
        if tokenID.startswith(cls._HBProgressionController.progressionToken):
            return HB_PROGRESSION_TOKEN
        if tokenID.startswith(HB_UNLOCK_VEHICLES_TOKEN):
            return HB_UNLOCK_VEHICLES_TOKEN
        if tokenID.startswith(HB_COUPON_TOKEN):
            return HB_COUPON_TOKEN
        if tokenID == cls._gameEventController.getMainDiscount().get('tokenName'):
            return HB_MAIN_DISCOUNT_TOKEN
        super(HBTokenBonusUIPacker, cls)._getTokenBonusType(tokenID, complexToken)

    @classmethod
    def _getTooltipsPackers(cls):
        pakers = super(HBTokenBonusUIPacker, cls)._getTooltipsPackers()
        pakers.update({HB_PROGRESSION_TOKEN: cls.__getHBProgressionTooltip,
         HB_UNLOCK_VEHICLES_TOKEN: cls.__getHBVehiclesTooltip,
         HB_COUPON_TOKEN: cls.__getHBCouponsTooltip,
         HB_MAIN_DISCOUNT_TOKEN: cls.__getHBMainDiscountTooltip})
        return pakers

    @classmethod
    def _getTokenBonusPackers(cls):
        tokenBonusPackers = super(HBTokenBonusUIPacker, cls)._getTokenBonusPackers()
        complexPaker = tokenBonusPackers.get(COMPLEX_TOKEN)
        tokenBonusPackers.update({HB_PROGRESSION_TOKEN: complexPaker,
         HB_UNLOCK_VEHICLES_TOKEN: cls.__packVehiclesBonus,
         HB_COUPON_TOKEN: cls.__packCouponBonus,
         HB_MAIN_DISCOUNT_TOKEN: cls.__packMainDiscountBonus})
        return tokenBonusPackers

    @classmethod
    def _getContentId(cls, bonus):
        result = super(HBTokenBonusUIPacker, cls)._getContentId(bonus)
        bonusNames = bonus.getValue().keys()
        for bonusName in bonusNames:
            if bonusName.startswith(HB_COUPON_TOKEN):
                index = bonusNames.index(bonusName)
                result[index] = R.views.historical_battles.lobby.tooltips.OrderTooltip()
                continue

        if HB_MAIN_DISCOUNT_TOKEN in bonusNames:
            index = bonusNames.index(HB_MAIN_DISCOUNT_TOKEN)
            result[index] = R.views.historical_battles.lobby.tooltips.HbMainDiscountTooltipView()
        if HB_UNLOCK_VEHICLES_TOKEN in bonusNames:
            vehiclesIdx = bonusNames.index(HB_UNLOCK_VEHICLES_TOKEN)
            result[vehiclesIdx] = R.views.historical_battles.lobby.tooltips.HbSpecialVehiclesTooltip()
        return result

    @classmethod
    def _packToken(cls, bonusPacker, bonus, *args):
        if bonus.getName() == 'HBCoupon':
            model = RewardItemModel()
            cls._packCommon(bonus, model)
            return bonusPacker(model, bonus, *args)
        return super(HBTokenBonusUIPacker, cls)._packToken(bonusPacker, bonus, *args)

    @classmethod
    def __getHBProgressionTooltip(cls, *_):
        tokenBase = R.strings.historical_battles_progression.quests.bonuses.progressionToken
        return createTooltipData(makeTooltip(backport.text(tokenBase.header()), backport.text(tokenBase.body())))

    @classmethod
    def __getHBVehiclesTooltip(cls, *_):
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.HB_SPECIAL_VEHICLES_TOOLTIP)

    @classmethod
    def __getHBCouponsTooltip(cls, *args):
        orderType = ORDER_TOKEN_NAME_TO_ORDER_TYPE.get(args[0].styleID, None)
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.HB_ORDER_TOOLTIP, specialArgs={'orderType': orderType.value if orderType else None})

    @classmethod
    def __getHBMainDiscountTooltip(cls, *_):
        return createTooltipData(tooltip='', isSpecial=True)

    @classmethod
    def __packVehiclesBonus(cls, model, bonus, *_):
        keys = bonus.getValue().keys()
        if keys:
            model.setName(keys[0])
            model.setUserName(backport.text(R.strings.quests.bonusName.dyn(keys[0])()))
        model.setValue(str(bonus.getCount()))
        model.setIconSmall(backport.image(R.images.gui.maps.icons.quests.bonuses.small.hbUnlockVehicles()))
        model.setIconBig(backport.image(R.images.gui.maps.icons.quests.bonuses.big.hbUnlockVehicles()))
        return model

    @classmethod
    def __packCouponBonus(cls, model, bonus, *_):
        keys = bonus.getValue().keys()
        if keys:
            couponName = keys[0]
            model.setName(couponName)
            model.setUserName(backport.text(R.strings.quests.bonusName.dyn(couponName)()))
            model.setIcon(backport.image(R.images.gui.maps.icons.quests.bonuses.small.dyn(couponName)()))
            model.setBigIcon(backport.image(R.images.gui.maps.icons.quests.bonuses.big.dyn(couponName)()))
            count = bonus.getCount()
            if count > 1:
                model.setValue(str(count))
        return model

    @classmethod
    def __packMainDiscountBonus(cls, model, bonus, *_):
        heroTankController = cls._gameEventController.heroTank
        heroTankVehicle = heroTankController.getVehicle()
        discountPerToken = cls._gameEventController.getMainDiscount()['discountPerToken']
        keys = bonus.getValue().keys()
        if keys:
            model.setName(keys[0])
        model.setIconSmall(backport.image(R.images.gui.maps.icons.quests.bonuses.small.historical_battles_main_discount()))
        model.setIconBig(backport.image(R.images.gui.maps.icons.quests.bonuses.big.historical_battles_main_discount()))
        model.setTankUserName(heroTankVehicle.userName)
        model.setTankLevel(heroTankVehicle.level)
        model.setTankType(heroTankVehicle.type)
        model.setDiscountPercent(discountPerToken)
        model.setLabel(model.getUserName())
        return model


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


def getBonusPacker():
    packer = getBattlePassBonusPacker()
    currencyBonusUIPacker = ExtendedCurrencyBonusUIPacker()
    tokenBonusPacker = HBTokenBonusUIPacker()
    packer.getPackers().update({'currencies': CurrenciesBonusUIPacker(),
     Currency.CREDITS: currencyBonusUIPacker,
     Currency.CRYSTAL: currencyBonusUIPacker,
     'token': tokenBonusPacker,
     'battleToken': tokenBonusPacker,
     'tmanToken': HBTmanTemplateBonusPacker(),
     'HBCoupon': tokenBonusPacker})
    return packer
