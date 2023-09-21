# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_lootboxes/scripts/client/event_lootboxes/gui/event_lootboxes/bonuses_packers.py
import logging
import typing
import constants
from event_lootboxes.gui.impl.gen.view_models.views.lobby.event_lootboxes.reward_model import RewardModel
from event_lootboxes.gui.impl.gen.view_models.views.lobby.event_lootboxes.tooltips.infotype_reward_model import InfotypeRewardModel
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import TooltipData, createTooltipData
from gui.impl.gen import R
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
_R_BONUS_ICONS = R.images.gui.maps.icons.quests.bonuses
_R_CREW_BOOKS_ICONS = R.images.gui.maps.icons.crewBooks

def getEventLootBoxesBonusPacker():
    mapping = getDefaultBonusPackersMap()
    simplePacker = EventLootBoxSimpleBonusUIPacker()
    blueprintPacker = EventLootBoxBlueprintBonusUIPacker()
    mapping.update({'battleToken': EventLootBoxTokenBonusUIPacker,
     'blueprints': blueprintPacker,
     'blueprintsAny': blueprintPacker,
     'crewBooks': EventLootBoxCrewBookBonusUIPacker(),
     'customizations': EventLootBoxCustomizationBonusUIPacker,
     'finalBlueprints': blueprintPacker,
     'goodies': EventLootBoxGoodiesBonusUIPacker(),
     'items': EventLootBoxItemBonusUIPacker(),
     'slots': simplePacker,
     'tmanToken': TmanTemplateBonusPacker(),
     'tokens': EventLootBoxTokenBonusUIPacker,
     'vehicles': EventLootBoxVehiclesBonusUIPacker(),
     Currency.CREDITS: simplePacker,
     Currency.GOLD: simplePacker,
     Currency.FREE_XP: simplePacker,
     constants.PREMIUM_ENTITLEMENTS.PLUS: EventLootBoxPremiumBonusUIPacker})
    return BonusUIPacker(mapping)


def getEventLootBoxesInfoTypeBonusPacker():
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
        recruit = getRecruitInfo(tokenID)
        if recruit is None:
            return
        else:
            model = RewardModel()
            cls._packCommon(bonus, model)
            model.setIconSource(_R_BONUS_ICONS.s600x450.dyn('tankwoman' if recruit.isFemale() else 'tankman')())
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


class EventLootBoxSimpleBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = RewardModel()
        cls._packCommon(bonus, model)
        model.setCount(bonus.getValue())
        model.setIconSource(_R_BONUS_ICONS.s600x450.dyn(bonus.getName())())
        return model


class EventLootBoxCustomizationBonusUIPacker(CustomizationBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = RewardModel()
        cls._packCommon(bonus, model)
        model.setCount(item.get('value', 0))
        model.setIconSource(_R_BONUS_ICONS.s600x450.dyn(bonus.getC11nItem(item).itemTypeName)())
        return model


class EventLootBoxGoodiesBonusUIPacker(GoodiesBonusUIPacker):

    @classmethod
    def _packIconBonusModel(cls, bonus, icon, count, label):
        model = RewardModel()
        cls._packCommon(bonus, model)
        model.setCount(count)
        model.setIconSource(_R_BONUS_ICONS.s600x450.dyn(icon)())
        return model


class EventLootBoxBlueprintBonusUIPacker(BlueprintBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        model = RewardModel()
        cls._packCommon(bonus, model)
        model.setCount(bonus.getCount())
        model.setIconSource(R.images.gui.maps.icons.blueprints.fragment.s600x450.dyn(bonus.getImageCategory())())
        return [model]


class EventLootBoxItemBonusUIPacker(ItemBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, count):
        model = RewardModel()
        cls._packCommon(bonus, model)
        model.setCount(count)
        model.setIconSource(_R_BONUS_ICONS.s600x450.dyn(item.getGUIEmblemID())())
        model.setOverlayType(item.getOverlayType())
        return model


class EventLootBoxCrewBookBonusUIPacker(CrewBookBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, book, count):
        model = RewardModel()
        cls._packCommon(bonus, model)
        model.setCount(count)
        iconSource = R.images.gui.maps.icons.crewBooks.books.s600x450.dyn(getIconResourceName(book.icon))()
        model.setIconSource(iconSource)
        return model


class EventLootBoxTokenBonusUIPacker(TokenBonusUIPacker):

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
        model.setCount(bonus.getCount())
        model.setIconSource(_R_BONUS_ICONS.s600x450.bonus_battle_task())
        return model


class EventLootBoxPremiumBonusUIPacker(EventLootBoxSimpleBonusUIPacker):
    _SPEC_ICON_FOR_COUNT = 3

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = RewardModel()
        cls._packCommon(bonus, model)
        if bonus.getValue() <= cls._SPEC_ICON_FOR_COUNT:
            model.setCount(1)
            model.setIconSource(_R_BONUS_ICONS.s600x450.dyn('_'.join((bonus.getName(), str(bonus.getValue()))))())
        else:
            model.setCount(int(bonus.getValue()))
            model.setIconSource(_R_BONUS_ICONS.s600x450.dyn('{}_1'.format(bonus.getName()))())
        return model


class EventLootBoxVehiclesBonusUIPacker(VehiclesBonusUIPacker):

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vehInfo, isRent, vehicle):
        model = RewardModel()
        model.setName(bonus.getName() + VEHICLE_RENT_ICON_POSTFIX if isRent else bonus.getName())
        model.setIsCompensation(bonus.isCompensation())
        if bonus.isCompensation():
            model.setIconSource(R.images.event_lootboxes.gui.maps.rewards.s600x450.gold())
        return model

    @classmethod
    def _packVehicles(cls, bonus, vehicles):
        packedVehicles = []
        for vehicle, vehInfo in vehicles:
            compensation = bonus.compensation(vehicle, bonus)
            if compensation:
                packer = EventLootBoxSimpleBonusUIPacker()
                for bonusComp in compensation:
                    packedVehicles.extend(packer.pack(bonusComp))

            packedVehicles.append(cls._packVehicle(bonus, vehInfo, vehicle))

        return packedVehicles


class VehicleBlueprintsPacker(object):

    @staticmethod
    def pack(bonuses):
        model = RewardModel()
        if any([ bonus.getBlueprintName() == BlueprintsBonusSubtypes.VEHICLE_FRAGMENT for bonus in bonuses ]):
            iconSource = R.images.gui.maps.icons.blueprints.fragment.s600x450.vehicle
        else:
            iconSource = R.images.gui.maps.icons.blueprints.fragment.s600x450.vehicle_complete
        model.setIconSource(iconSource())
        count = sum((bonus.getCount() for bonus in bonuses))
        model.setCount(count)
        model.setIsCompensation(False)
        return model

    @staticmethod
    def getTooltip(bonuses):
        fragmentCDs = [ bonus.getBlueprintSpecialArgs() for bonus in bonuses ]
        return TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.EVENT_LOOT_BOXES_VEHICLE_BLUEPRINT_FRAGMENT, specialArgs=[fragmentCDs])


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
            model.setIcon(R.images.gui.maps.icons.blueprints.fragment.small.randomNational())
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
        model.setIcon(_R_BONUS_ICONS.dyn(AWARDS_SIZES.SMALL).dyn(item.getGUIEmblemID())())
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
        recruit = getRecruitInfo(tokenID)
        if recruit is None:
            return
        else:
            model = InfotypeRewardModel()
            cls._packCommon(bonus, model)
            model.setIcon(_R_BONUS_ICONS.dyn(AWARDS_SIZES.SMALL).dyn('tankwoman' if recruit.isFemale() else 'tankman')())
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
        model.setIcon(_R_BONUS_ICONS.small.dyn(icon)())
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
            model.setIcon(R.images.gui.maps.icons.crewBooks.books.small.dyn(getIconResourceName(item.icon))())
        return model

    @classmethod
    def _pack(cls, bonus):
        return [ cls._packSingleItem(item, count) for item, count in bonus.getItems() ]


class InfoTypeCrewSkinsPacker(InfoTypeCrewBooksPacker):

    @classmethod
    def _packSingleItem(cls, item, count):
        model = InfotypeRewardModel()
        model.setCount(count)
        model.setIcon(_R_BONUS_ICONS.small.dyn('{}{}'.format(item.itemTypeName, item.getRarity()))())
        return model


class InfoTypeTokenPacker(EventLootBoxTokenBonusUIPacker):

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
    packer = getEventLootBoxesBonusPacker()
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
