# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/shared/bonus_packers.py
import logging
import typing
from armory_yard.gui.shared.bonuses_sorter import bonusesSortKeyFunc
from constants import PREMIUM_ENTITLEMENTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_rewards_vehicle_model import ArmoryYardRewardsVehicleModel
from armory_yard_constants import isArmoryYardBattleToken, FEATURE_NAME_BASE
from gui.impl.backport import createTooltipData, TooltipData
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.server_events.bonuses import getNonQuestBonuses, splitBonuses, mergeBonuses, VehiclesBonus, TokensBonus
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.shared.missions.packers.bonus import getDefaultBonusPackersMap, BaseBonusUIPacker, BonusUIPacker, BACKPORT_TOOLTIP_CONTENT_ID, TokenBonusUIPacker, SimpleBonusUIPacker, VehiclesBonusUIPacker, getDefaultBonusPacker
from items.vehicles import getVehicleClassFromVehicleType
from gui.battle_pass.battle_pass_bonuses_packers import TmanTemplateBonusPacker
if typing.TYPE_CHECKING:
    BonusModelType = typing.TypeVar('BonusModelType', bound=BonusModel)
    from gui.shared.gui_items.Vehicle import Vehicle
    from frameworks.wulf import Array
    from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel
_logger = logging.getLogger(__name__)
_ARMORY_YARD_REST_ICON_NAME = 'default'

class ArmoryYardTokenBonusUIPacker(TokenBonusUIPacker):

    @classmethod
    def _getTokenBonusPackers(cls):
        packers = super(ArmoryYardTokenBonusUIPacker, cls)._getTokenBonusPackers()
        packers[FEATURE_NAME_BASE] = cls.__packArmoryYardToken
        return packers

    @classmethod
    def _getToolTip(cls, bonus):
        return [TooltipData(tooltip=None, isSpecial=True, specialAlias=None, specialArgs=[])]

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.armory_yard.lobby.feature.tooltips.ArmoryYardCurrencyTooltipView()]

    @classmethod
    def _getTokenBonusType(cls, tokenID, complexToken):
        if isArmoryYardBattleToken(tokenID):
            return FEATURE_NAME_BASE
        return '' if tokenID == 'ny24_yaga' else super(ArmoryYardTokenBonusUIPacker, cls)._getTokenBonusType(tokenID, complexToken)

    @classmethod
    def __packArmoryYardToken(cls, model, _, *args):
        model.setIconSmall(backport.image(R.images.armory_yard.gui.maps.icons.token.s20()))
        model.setIconBig(backport.image(R.images.armory_yard.gui.maps.icons.token.s44()))
        return model


class ArmoryYardMainVehiclesBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [ cls._packVehicle(vehicle, vehicleInfo) for vehicle, vehicleInfo in bonus.getVehicles() ]

    @classmethod
    def _getToolTip(cls, bonus):
        return [ createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.ARMORY_YARD_AWARD_VEHICLE, specialArgs=[vehicle.intCD]) for vehicle, _ in bonus.getVehicles() ]

    @classmethod
    def _getContentId(cls, bonus):
        return [ BACKPORT_TOOLTIP_CONTENT_ID for _ in bonus.getVehicles() ]

    @classmethod
    def _packVehicle(cls, vehicle, _):
        vehicleModel = ArmoryYardRewardsVehicleModel()
        packVehicleModel(vehicleModel, vehicle)
        return vehicleModel


class ArmoryYardVehiclesBonusUIPacker(VehiclesBonusUIPacker):

    @classmethod
    def _packTooltip(cls, bonus, vehicle, vehInfo):
        tmanRoleLevel = bonus.getTmanRoleLevel(vehInfo)
        rentDays = bonus.getRentDays(vehInfo)
        rentBattles = bonus.getRentBattles(vehInfo)
        rentWins = bonus.getRentWins(vehInfo)
        rentSeason = bonus.getRentSeason(vehInfo)
        rentCycle = bonus.getRentCycle(vehInfo)
        rentExpiryTime = cls._getRentExpiryTime(rentDays)
        return TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.ARMORY_YARD_AWARD_VEHICLE, specialArgs=[vehicle.intCD,
         tmanRoleLevel,
         rentExpiryTime,
         rentBattles,
         rentWins,
         rentSeason,
         rentCycle])


class ArmoryYardTmanTemplateBonusPacker(TmanTemplateBonusPacker):

    @classmethod
    def _packTmanTemplateToken(cls, tokenID, bonus):
        model = super(ArmoryYardTmanTemplateBonusPacker, cls)._packTmanTemplateToken(tokenID, bonus)
        tokenRecord = bonus.getTokens()[tokenID]
        if tokenRecord.count > 1:
            model.setValue(str(tokenRecord.count))
        return model


class ArmoryYardPremiumDaysPacker(SimpleBonusUIPacker):

    @classmethod
    def _packCommon(cls, bonus, model):
        model.setName('premium_universal')
        model.setIsCompensation(bonus.isCompensation())
        return model


def getArmoryYardBonusPackersMap():
    packersMap = getDefaultBonusPackersMap()
    packersMap.update({'vehicles': ArmoryYardMainVehiclesBonusUIPacker,
     'battleToken': ArmoryYardTokenBonusUIPacker,
     'tmanToken': ArmoryYardTmanTemplateBonusPacker,
     PREMIUM_ENTITLEMENTS.PLUS: ArmoryYardPremiumDaysPacker})
    return packersMap


def getArmoryYardBuyViewBonusPackersMap():
    packersMap = getArmoryYardBonusPackersMap()
    packersMap.update({'vehicles': ArmoryYardVehiclesBonusUIPacker})
    return packersMap


def getArmoryYardBonusPacker():
    return BonusUIPacker(getArmoryYardBonusPackersMap())


def getArmoryYardBuyViewPacker():
    return BonusUIPacker(getArmoryYardBuyViewBonusPackersMap())


def packVehicleModel(vehicleModel, vehicle):
    vehicleModel.setVehicleImg(getNationLessName(vehicle.name))
    vehicleModel.setVehicleName(vehicle.userName)
    vehicleModel.setVehicleLvl(vehicle.level)
    vehicleModel.setVehicleType(getVehicleClassFromVehicleType(vehicle.descriptor.type))
    vehicleModel.setIsElite(vehicle.isElite)


def packRestModel(rewardsList, rewardListModel, tooltipData, index, restRewardsTextId=None):
    model = BonusModel()
    model.setName(_ARMORY_YARD_REST_ICON_NAME)
    model.setValue(backport.text(restRewardsTextId or R.strings.armory_yard.buyView.reward.rest(), count=len(rewardsList)))
    model.setTooltipContentId(str(R.views.armory_yard.lobby.feature.tooltips.RestRewardTooltipView()))
    tooltipID = str(len(tooltipData))
    tooltipData[tooltipID] = TooltipData(tooltip=None, isSpecial=True, specialAlias=None, specialArgs=[rewardsList])
    model.setTooltipId(tooltipID)
    model.setIndex(index)
    rewardListModel.addViewModel(model)
    return


def packBonuses(rewards, packer=None):
    bonuses = []
    for rewardType, rewardValue in rewards.items():
        bonuses.extend(getNonQuestBonuses(rewardType, rewardValue))

    bonuses = splitBonuses(mergeBonuses(bonuses))
    bonuses.sort(key=bonusesSortKeyFunc)
    packer = packer or getDefaultBonusPacker()
    return [ packedBonus for bonus in bonuses for packedBonus in packer.pack(bonus) ]
