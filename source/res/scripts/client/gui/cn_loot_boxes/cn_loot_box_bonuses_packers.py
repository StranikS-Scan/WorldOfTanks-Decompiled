# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/cn_loot_boxes/cn_loot_box_bonuses_packers.py
import logging
import typing
import constants
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import TooltipData, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.cn_loot_boxes.reward_model import RewardModel
from gui.impl.gen.view_models.views.lobby.cn_loot_boxes.tooltips.infotype_reward_model import InfotypeRewardModel
from gui.server_events.awards_formatters import AWARDS_SIZES, BATTLE_BONUS_X5_TOKEN, TokenBonusFormatter
from gui.server_events.bonuses import BlueprintsBonusSubtypes, IntelligenceBlueprintBonus, VehicleBlueprintBonus
from gui.server_events.formatters import parseComplexToken
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.gui_items.Vehicle import getIconResourceName
from gui.shared.missions.packers.bonus import BACKPORT_TOOLTIP_CONTENT_ID, BlueprintBonusUIPacker, BonusUIPacker, CrewBookBonusUIPacker, CustomizationBonusUIPacker, GoodiesBonusUIPacker, ItemBonusUIPacker, SimpleBonusUIPacker, TokenBonusUIPacker, VEHICLE_RENT_ICON_POSTFIX, VehiclesBonusUIPacker, getDefaultBonusPackersMap
from gui.shared.money import Currency
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus
_logger = logging.getLogger(__name__)
_R_BONUS_ICONS_LB = R.images.gui.maps.icons.cnLootBoxes.rewards
_R_BONUS_ICONS = R.images.gui.maps.icons.quests.bonuses
_R_CREW_BOOKS_ICONS = R.images.gui.maps.icons.crewBooks

def getCNLootBoxBonusPacker():
    mapping = getDefaultBonusPackersMap()
    simplePacker = CNLootBoxSimpleBonusUIPacker()
    blueprintPacker = CNLootBoxBlueprintBonusUIPacker()
    mapping.update({'battleToken': CNLootBoxTokenBonusUIPacker,
     'blueprints': blueprintPacker,
     'blueprintsAny': blueprintPacker,
     'crewBooks': CNLootBoxCrewBookBonusUIPacker(),
     'customizations': CNLootBoxCustomizationBonusUIPacker,
     'finalBlueprints': blueprintPacker,
     'goodies': CNLootBoxGoodiesBonusUIPacker(),
     'items': CNLootBoxItemBonusUIPacker(),
     'slots': simplePacker,
     'tmanToken': TmanTemplateBonusPacker(),
     'tokens': CNLootBoxTokenBonusUIPacker,
     'vehicles': CNLootBoxVehiclesBonusUIPacker(),
     Currency.CREDITS: simplePacker,
     Currency.GOLD: simplePacker,
     constants.PREMIUM_ENTITLEMENTS.PLUS: CNLootBoxPremiumBonusUIPacker})
    return BonusUIPacker(mapping)


def getCNLBInfoTypeBonusPacker():
    defaultMapper = getDefaultBonusPackersMap()
    infoTypeRewardPacker = InfoTypeRewardPacker()
    blueprintPacker = InfoTypeBlueprintRewardPacker()
    mapping = {k:infoTypeRewardPacker for k in defaultMapper}
    mapping.update({'battleToken': InfoTypeTokenPacker(),
     'blueprints': blueprintPacker,
     'blueprintsAny': blueprintPacker,
     'finalBlueprints': blueprintPacker,
     'crewBooks': InfoTypeCrewBooksPacker(),
     'crewSkins': InfoTypeCrewSkinsPacker(),
     'customizations': InfoTypeCustomizationPacker(),
     'goodies': InfoTypeGoodiesPacker(),
     'items': InfoTypeItemPacker(),
     'tmanToken': InfoTypeTmanTemplateBonusPacker(),
     'tokens': InfoTypeTokenPacker(),
     'vehicles': InfoTypeVehiclePacker()})
    return BonusUIPacker(mapping)


class TmanTemplateBonusPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                packed = cls.__packTmanTemplateToken(tokenID, bonus)
                if packed is None:
                    _logger.error('Received wrong tman_template token from server: %s', tokenID)
                else:
                    result.append(packed)

        return result

    @classmethod
    def __packTmanTemplateToken(cls, tokenID, bonus):
        recruitInfo = getRecruitInfo(tokenID)
        if recruitInfo is None:
            return
        else:
            if recruitInfo.isFemale():
                bonusName = 'tankwoman'
            else:
                bonusName = 'tankman'
            model = RewardModel()
            cls._packCommon(bonus, model)
            model.setIconSource(_R_BONUS_ICONS_LB.dyn(bonusName)())
            return model

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED, specialArgs=[tokenID]))

        return tooltipData

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                result.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return result


class CNLootBoxSimpleBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = RewardModel()
        cls._packCommon(bonus, model)
        model.setCount(bonus.getValue())
        iconSource = _R_BONUS_ICONS_LB.dyn(bonus.getName())
        model.setIconSource(iconSource() if iconSource.isValid() else bonus.getIconResource(AWARDS_SIZES.BIG))
        return model


class CNLootBoxCustomizationBonusUIPacker(CustomizationBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = RewardModel()
        cls._packCommon(bonus, model)
        model.setCount(item.get('value', 0))
        model.setIconSource(_R_BONUS_ICONS_LB.dyn(bonus.getC11nItem(item).itemTypeName, default=R.invalid)())
        return model


class CNLootBoxGoodiesBonusUIPacker(GoodiesBonusUIPacker):

    @classmethod
    def _packIconBonusModel(cls, bonus, icon, count, label):
        model = RewardModel()
        cls._packCommon(bonus, model)
        model.setCount(count)
        iconSource = _R_BONUS_ICONS_LB.dyn(icon)
        if iconSource.isValid():
            iconSource = iconSource()
        else:
            iconSource = _R_BONUS_ICONS.big.dyn(icon, default=R.invalid)()
        model.setIconSource(iconSource)
        return model


class CNLootBoxBlueprintBonusUIPacker(BlueprintBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        model = RewardModel()
        cls._packCommon(bonus, model)
        model.setCount(bonus.getCount())
        if bonus.getBlueprintName() == BlueprintsBonusSubtypes.NATION_FRAGMENT:
            iconSource = R.images.gui.maps.icons.blueprints.fragment.s600x450.dyn(bonus.getImageCategory())
        else:
            iconSource = _R_BONUS_ICONS_LB.dyn(bonus.getImageCategory())
        model.setIconSource(iconSource() if iconSource.isValid() else bonus.getIconResource(AWARDS_SIZES.BIG))
        return [model]


class CNLootBoxItemBonusUIPacker(ItemBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, count):
        model = RewardModel()
        cls._packCommon(bonus, model)
        model.setCount(count)
        iconSource = _R_BONUS_ICONS_LB.dyn(item.getGUIEmblemID())
        if iconSource.isValid():
            iconSource = iconSource()
        else:
            iconSource = _R_BONUS_ICONS.dyn(AWARDS_SIZES.BIG).dyn(item.getGUIEmblemID(), default=R.invalid)()
        model.setIconSource(iconSource)
        return model


class CNLootBoxCrewBookBonusUIPacker(CrewBookBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, book, count):
        model = RewardModel()
        cls._packCommon(bonus, model)
        model.setCount(count)
        if book.isCommon:
            iconSource = _R_CREW_BOOKS_ICONS.books.s600x450.dyn(getIconResourceName(book.icon))
        else:
            iconSource = _R_BONUS_ICONS_LB.dyn(book.getBonusIconName())
        if iconSource.isValid():
            iconSource = iconSource()
        else:
            iconSource = _R_CREW_BOOKS_ICONS.books.big.dyn(getIconResourceName(book.icon), default=R.invalid)()
        model.setIconSource(iconSource)
        return model


class CNLootBoxTokenBonusUIPacker(TokenBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        bonusTokens = bonus.getTokens()
        result = []
        for tokenID, token in bonusTokens.iteritems():
            complexToken = parseComplexToken(tokenID)
            if tokenID.startswith(BATTLE_BONUS_X5_TOKEN):
                packedBonus = cls._packToken(bonus, complexToken, token)
                if packedBonus is not None:
                    result.append(packedBonus)

        return result

    @classmethod
    def _getToolTip(cls, bonus):
        bonusTokens = bonus.getTokens()
        result = []
        for tokenID, _ in bonusTokens.iteritems():
            complexToken = parseComplexToken(tokenID)
            if tokenID.startswith(BATTLE_BONUS_X5_TOKEN):
                tooltip = TokenBonusFormatter.getBattleBonusX5Tooltip(complexToken)
                result.append(createTooltipData(tooltip))

        return result

    @classmethod
    def _packToken(cls, bonus, *args):
        model = RewardModel()
        cls._packCommon(bonus, model)
        model.setValue(str(bonus.getCount()))
        model.setIconSource(_R_BONUS_ICONS_LB.bonus_battle_task())
        return model


class CNLootBoxPremiumBonusUIPacker(CNLootBoxSimpleBonusUIPacker):
    _SPEC_ICON_FOR_COUNT = 3

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = RewardModel()
        cls._packCommon(bonus, model)
        if bonus.getValue() <= cls._SPEC_ICON_FOR_COUNT:
            model.setCount(1)
            model.setIconSource(_R_BONUS_ICONS_LB.dyn('_'.join((bonus.getName(), str(bonus.getValue()))), default=R.invalid)())
        else:
            model.setCount(int(bonus.getValue()))
            model.setIconSource(_R_BONUS_ICONS_LB.dyn('{}_1'.format(bonus.getName()), default=R.invalid)())
        return model


class CNLootBoxVehiclesBonusUIPacker(VehiclesBonusUIPacker):

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vehInfo, isRent, vehicle):
        model = RewardModel()
        model.setName(bonus.getName() + VEHICLE_RENT_ICON_POSTFIX if isRent else bonus.getName())
        model.setIsCompensation(bonus.isCompensation())
        if bonus.isCompensation():
            model.setIconSource(_R_BONUS_ICONS_LB.credits())
        return model

    @classmethod
    def _packVehicles(cls, bonus, vehicles):
        packedVehicles = []
        for vehicle, vehInfo in vehicles:
            compensation = bonus.compensation(vehicle, bonus)
            if compensation:
                packer = CNLootBoxSimpleBonusUIPacker()
                for bonusComp in compensation:
                    packedVehicles.extend(packer.pack(bonusComp))

            packedVehicles.append(cls._packVehicle(bonus, vehInfo, vehicle))

        return packedVehicles


class VehicleBlueprintsPacker(object):

    @staticmethod
    def pack(bonuses):
        model = RewardModel()
        if any([ bonus.getBlueprintName() == BlueprintsBonusSubtypes.VEHICLE_FRAGMENT for bonus in bonuses ]):
            iconSource = _R_BONUS_ICONS_LB.vehicle()
        else:
            iconSource = _R_BONUS_ICONS_LB.vehicle_complete()
        model.setIconSource(iconSource)
        count = sum((bonus.getCount() for bonus in bonuses))
        model.setCount(count)
        model.setIsCompensation(False)
        return model

    @staticmethod
    def getTooltip(bonuses):
        fragmentCDs = [ bonus.getBlueprintSpecialArgs() for bonus in bonuses ]
        return TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.CN_LOOT_BOXES_VEHICLE_BLUEPRINT_FRAGMENT, specialArgs=[fragmentCDs])


class InfoTypeRewardPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus, '')]

    @classmethod
    def _packCommon(cls, bonus, model):
        model.setName(bonus.getName())

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = InfotypeRewardModel()
        cls._packCommon(bonus, model)
        model.setIcon(bonus.getIconResource(AWARDS_SIZES.SMALL))
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        return []


class InfoTypeBlueprintRewardPacker(InfoTypeRewardPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = InfotypeRewardModel()
        model.setName(bonus.getBlueprintName())
        if bonus.getBlueprintName() == BlueprintsBonusSubtypes.NATION_FRAGMENT:
            model.setIcon(R.images.gui.maps.icons.blueprints.fragment.small.random())
        else:
            model.setIcon(bonus.getIconResource(AWARDS_SIZES.SMALL))
        model.setCount(bonus.getCount())
        return model


class InfoTypeVehiclePacker(InfoTypeRewardPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = InfotypeRewardModel()
        model.setName(bonus.formatValue())
        model.setIcon(bonus.getIconResource(AWARDS_SIZES.SMALL))
        return model


class InfoTypeItemPacker(InfoTypeRewardPacker):

    @classmethod
    def _packSingleItem(cls, item, count):
        model = InfotypeRewardModel()
        model.setName(item.userName)
        model.setCount(count)
        model.setIcon(_R_BONUS_ICONS.dyn(AWARDS_SIZES.SMALL).dyn(item.getGUIEmblemID(), default=R.invalid)())
        return model

    @classmethod
    def _pack(cls, bonus):
        return [ cls._packSingleItem(item, count) for item, count in bonus.getItems().iteritems() ]


class InfoTypeTmanTemplateBonusPacker(InfoTypeRewardPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                packed = cls.__packTmanTemplateToken(tokenID, bonus)
                if packed is None:
                    _logger.error('Received wrong tman_template token from server: %s', tokenID)
                else:
                    result.append(packed)

        return result

    @classmethod
    def __packTmanTemplateToken(cls, tokenID, bonus):
        recruitInfo = getRecruitInfo(tokenID)
        if recruitInfo is None:
            return
        else:
            if recruitInfo.isFemale():
                bonusName = 'tankwoman'
            else:
                bonusName = 'tankman'
            model = InfotypeRewardModel()
            cls._packCommon(bonus, model)
            model.setIcon(_R_BONUS_ICONS.dyn(AWARDS_SIZES.SMALL).dyn(bonusName, default=R.invalid)())
            return model

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED, specialArgs=[tokenID]))

        return tooltipData

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                result.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return result


class InfoTypeCustomizationPacker(InfoTypeRewardPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = InfotypeRewardModel()
        model.setName(bonus.getName())
        model.setCount(sum((item.get('value', 1) for item in bonus.getCustomizations())))
        model.setIcon(_R_BONUS_ICONS.small.style())
        return model


class InfoTypeGoodiesPacker(GoodiesBonusUIPacker):

    @classmethod
    def _packIconBonusModel(cls, bonus, icon, count, label):
        model = InfotypeRewardModel()
        model.setName(bonus.getName())
        model.setCount(count)
        model.setIcon(_R_BONUS_ICONS.small.dyn(icon, default=R.invalid)())
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        return []


class InfoTypeCrewBooksPacker(InfoTypeItemPacker):

    @classmethod
    def _packSingleItem(cls, item, count):
        model = InfotypeRewardModel()
        model.setName(item.getBookType())
        model.setCount(count)
        if item.isCommon():
            model.setIcon(R.images.gui.maps.icons.crewBooks.books.big.brochure_random())
        else:
            model.setIcon(R.images.gui.maps.icons.crewBooks.books.small.dyn(getIconResourceName(item.icon), default=R.invalid)())
        return model

    @classmethod
    def _pack(cls, bonus):
        return [ cls._packSingleItem(item, count) for item, count in bonus.getItems() ]


class InfoTypeCrewSkinsPacker(InfoTypeCrewBooksPacker):

    @classmethod
    def _packSingleItem(cls, item, count):
        model = InfotypeRewardModel()
        model.setCount(count)
        model.setIcon(_R_BONUS_ICONS.small.dyn('{}{}'.format(item.itemTypeName, item.getRarity()), default=R.invalid)())
        return model


class InfoTypeTokenPacker(CNLootBoxTokenBonusUIPacker):

    @classmethod
    def _getToolTip(cls, bonus):
        return []

    @classmethod
    def _packToken(cls, bonus, *args):
        model = InfotypeRewardModel()
        model.setName(bonus.getName())
        model.setCount(bonus.getCount())
        model.setIcon(bonus.getIconResource(AWARDS_SIZES.SMALL))
        return model


def packBonusModelAndTooltipData(bonuses, rewardModels, tooltipData, vehicleModel):
    bonusIndexTotal = 0
    if tooltipData is not None:
        bonusIndexTotal = len(tooltipData)
    vehicleBlueprints = [ bonus for bonus in bonuses if _isVehicleBlueprintBonus(bonus) ]
    if len(vehicleBlueprints) > 1:
        bonuses = [ bonus for bonus in bonuses if bonus not in vehicleBlueprints ]
        model = VehicleBlueprintsPacker.pack(vehicleBlueprints)
        rewardModels.addViewModel(model)
        tooltipIdx = str(bonusIndexTotal)
        model.setTooltipId(tooltipIdx)
        tooltipData[tooltipIdx] = VehicleBlueprintsPacker.getTooltip(vehicleBlueprints)
        bonusIndexTotal += 1
    universalBlueprints = [ bonus for bonus in bonuses if isinstance(bonus, IntelligenceBlueprintBonus) ]
    if len(universalBlueprints) > 1:
        bonuses = [ bonus for bonus in bonuses if bonus not in universalBlueprints ]
        bonuses.append(IntelligenceBlueprintBonus('blueprints', (universalBlueprints[0].getValue()[0], sum((b.getCount() for b in universalBlueprints)))))
    packer = getCNLootBoxBonusPacker()
    for bonus in bonuses:
        if bonus.isShowInGUI():
            bonusList = packer.pack(bonus)
            bonusTooltipList = []
            if bonusList and tooltipData is not None:
                bonusTooltipList = packer.getToolTip(bonus)
            for bonusIndex, item in enumerate(bonusList):
                item.setIndex(bonusIndex)
                if bonus.getName() == 'vehicles' and item.getIsCompensation() or bonus.getName() != 'vehicles':
                    rewardModels.addViewModel(item)
                if tooltipData is not None and bonusTooltipList:
                    tooltipIdx = str(bonusIndexTotal)
                    item.setTooltipId(tooltipIdx)
                    tooltipData[tooltipIdx] = bonusTooltipList[bonusIndex]
                    bonusIndexTotal += 1
                    if bonus.getName() == 'vehicles' and not item.getIsCompensation():
                        vehicleModel.setTooltipId(tooltipIdx)

    return


def _isVehicleBlueprintBonus(bonus):
    return isinstance(bonus, VehicleBlueprintBonus) and bonus.getBlueprintName() in (BlueprintsBonusSubtypes.FINAL_FRAGMENT, BlueprintsBonusSubtypes.VEHICLE_FRAGMENT)
