# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/lobby/awards/packers.py
import logging
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.backport import createTooltipData
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from gui.impl.lobby.awards.packers import _AdditionalCustomizationBonusUIPacker, _convertRentType
from gui.impl.lobby.platoon.platoon_helpers import removeNationFromTechName
from gui.server_events.awards_formatters import AWARDS_SIZES, ItemsBonusFormatter
from gui.server_events.bonuses import getNonQuestBonuses, getSplitBonusFunction, ItemsBonus, mergeBonuses, TokensBonus, splitBonuses, X3CrewTokensBonus, X5BattleTokensBonus, DossierBonus, VehiclesBonus
from gui.shared.gui_items.artefacts import OptionalDevice
from gui.shared.gui_items.fitting_item import FittingItem
from gui.shared.missions.packers.bonus import BACKPORT_TOOLTIP_CONTENT_ID, DOSSIER_ACHIEVEMENT_POSTFIX, DOSSIER_BADGE_ICON_PREFIX, DOSSIER_BADGE_POSTFIX, ItemBonusUIPacker, TokenBonusUIPacker, getDefaultBonusPackersMap, BonusUIPacker, DossierBonusUIPacker, VehiclesBonusUIPacker
from gui.shared.utils.functions import replaceHyphenToUnderscore
from helpers import dependency
from one_time_gift.gui.gui_constants import OTG_EQUIPMENT_SET_BONUS_NAME, OTG_MISSION_TOKEN_PREFIX, OTG_MISSION_TOKEN_BONUS_NAME, TOOLTIP_CONSTANTS
from one_time_gift.gui.impl.gen.view_models.views.lobby.vehicle_bonus_model import VehicleBonusModel
from one_time_gift.skeletons.gui.game_control import IOneTimeGiftController
if typing.TYPE_CHECKING:
    from gui.impl.backport import TooltipData
    from gui.shared.gui_items.Vehicle import Vehicle
_logger = logging.getLogger(__name__)
DEFAULT_COLLECTORS_COMP_ORDER = ('playerBadges', 'singleAchievements')
OTG_EQUIPMENT_SET_COUNT_VAL = '1'

@dependency.replace_none_kwargs(oneTimeGiftController=IOneTimeGiftController)
def _getCollectorsCompensationOrder(oneTimeGiftController=None):
    order = oneTimeGiftController.getConfig().collectorsCompensation['layout'].get('order')
    return order or DEFAULT_COLLECTORS_COMP_ORDER


def _getOTGSplitBonusFunction(bonus):
    return getSplitBonusFunction(bonus) if not isinstance(bonus, ItemsBonus) else None


def _splitBonuses(bonuses):
    split = []
    for bonus in bonuses:
        splitFunc = _getOTGSplitBonusFunction(bonus)
        if splitFunc:
            split.extend(splitFunc(bonus))
        split.append(bonus)

    return split


def composeBonuses(rewards, ctx=None):
    bonuses = []
    for reward in rewards:
        for key, value in reward.iteritems():
            bonuses.extend(getNonQuestBonuses(key, value, ctx))

    return _splitBonuses(mergeBonuses(bonuses))


def composeVehicleBonuses(rewards, ctx=None):
    bonuses = []
    for reward in rewards:
        vehicleBonuses = reward.get(VehiclesBonus.VEHICLES_BONUS, [])
        bonuses.extend(getNonQuestBonuses(VehiclesBonus.VEHICLES_BONUS, vehicleBonuses, ctx))

    return splitBonuses(mergeBonuses(bonuses))


def filterNonOwnedVehicles(vehicleBonus):
    for _, vehInfo in vehicleBonus.getVehicles():
        compensatedNumber = vehInfo.get('compensatedNumber', 0)
        if compensatedNumber > 0:
            return False

    return True


def getOTGVehicleRewardsBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'vehicles': OneTimeGiftExtendedVehiclesBonusUIPacker()})
    return BonusUIPacker(mapping)


def getOTGMixedRewardsBonusPacker():
    mapping = getDefaultBonusPackersMap()
    tokensUIPacker = OneTimeGiftTokensBonusUIPacker()
    mapping.update({'dossier': OneTimeGiftDossierBonusUIPacker(),
     'vehicles': OneTimeGiftSimpleVehiclesBonusUIPacker(),
     'tokens': tokensUIPacker,
     'battleToken': tokensUIPacker,
     'customizations': _AdditionalCustomizationBonusUIPacker(),
     'items': OneTimeGiftItemBonusUIPacker()})
    return BonusUIPacker(mapping)


class OneTimeGiftDossierBonusUIPacker(DossierBonusUIPacker):

    @classmethod
    def _getBadgeTooltip(cls, bonus):
        return [ createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BADGE, specialArgs=[badge.badgeID, badge.isSuffixLayout()]) for badge in cls.__getSortedBadges(bonus) ]

    @classmethod
    def _getToolTip(cls, bonus):
        methodMapping = {'playerBadges': cls._getBadgeTooltip,
         'singleAchievements': cls._getAchievementTooltip}
        return cls.__applyPackMethodsInOrder(bonus, methodMapping)

    @classmethod
    def _pack(cls, bonus):
        methodMapping = {'playerBadges': cls._packBadges,
         'singleAchievements': cls._packAchievements}
        return cls.__applyPackMethodsInOrder(bonus, methodMapping)

    @classmethod
    def _packBadges(cls, bonus):
        result = []
        for badge in cls.__getSortedBadges(bonus):
            dossierIconName = DOSSIER_BADGE_ICON_PREFIX + str(badge.badgeID)
            dossierValue = 0
            if badge.isSuffixLayout():
                template = backport.text(R.strings.one_time_gift.awardNameTemplate.stripe())
            else:
                template = backport.text(R.strings.one_time_gift.awardNameTemplate.badge())
            dossierLabel = template.format(name=badge.getUserName())
            result.append(cls._packSingleBonus(bonus, dossierIconName, DOSSIER_BADGE_POSTFIX, dossierValue, dossierLabel))

        return result

    @classmethod
    def _packSingleAchievement(cls, achievement, bonus):
        dossierIconName = achievement.getName()
        dossierValue = achievement.getValue()
        template = backport.text(R.strings.one_time_gift.awardNameTemplate.medal())
        dossierLabel = template.format(name=achievement.getUserName())
        return cls._packSingleBonus(bonus, dossierIconName, DOSSIER_ACHIEVEMENT_POSTFIX, dossierValue, dossierLabel)

    @classmethod
    def __applyPackMethodsInOrder(cls, bonus, methodMapping):
        order = _getCollectorsCompensationOrder()
        result = []
        for dossierBonusName in order:
            method = methodMapping.get(dossierBonusName)
            if method:
                result += method(bonus)
            _logger.warning('Unsupported dossier bonus: %s', dossierBonusName)

        return result

    @staticmethod
    def __getSortedBadges(bonus):
        return sorted(bonus.getBadges(), key=lambda bdg: not bdg.isSuffixLayout())


class OneTimeGiftSimpleVehiclesBonusUIPacker(VehiclesBonusUIPacker):

    @classmethod
    def _getLabel(cls, vehicle):
        return vehicle.shortUserName


class OneTimeGiftExtendedVehiclesBonusUIPacker(VehiclesBonusUIPacker):
    _SPECIAL_ALIAS = TOOLTIP_CONSTANTS.ONE_TIME_GIFT_VEHICLE_TOOLTIP

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vehInfo, isRent, vehicle):
        model = VehicleBonusModel()
        model.setIsElite(vehicle.isElite)
        model.setVehicleLvl(vehicle.level)
        model.setVehicleName(vehicle.shortUserName)
        model.setVehicleType(vehicle.type)
        model.setTechName(replaceHyphenToUnderscore(removeNationFromTechName(vehicle.name)))
        model.setNation(vehicle.nationName)
        model.setName(cls._createUIName(bonus, isRent))
        model.setLabel(cls._getLabel(vehicle))
        gpRentType, rentValue = bonus.getRentInfo(vehInfo)
        if rentValue:
            model.setVehicleRentType(_convertRentType(gpRentType))
            model.setVehicleRentValue(rentValue)
        return model


class OneTimeGiftTokensBonusUIPacker(TokenBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = super(OneTimeGiftTokensBonusUIPacker, cls)._pack(bonus)
        for token in sorted(bonus.getTokens().itervalues()):
            if cls.__isOTGMissionsToken(token.id, token):
                model = TokenBonusModel()
                cls._packCommon(bonus, model)
                cls.__packOTGMissionsToken(model)
                result.append(model)

        return result

    @classmethod
    def _packCommon(cls, bonus, model):
        model.setName(bonus.getName())
        model.setIsCompensation(bonus.isCompensation())
        if isinstance(bonus, X3CrewTokensBonus):
            label = backport.text(R.strings.quests.bonusName.crew_bonus_x3())
            model.setLabel(label)
        elif isinstance(bonus, X5BattleTokensBonus):
            label = backport.text(R.strings.quests.bonusName.battle_bonus_x5())
            model.setLabel(label)
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        result = super(OneTimeGiftTokensBonusUIPacker, cls)._getToolTip(bonus)
        for token in sorted(bonus.getTokens().itervalues()):
            if cls.__isOTGMissionsToken(token.id, token):
                result.append(createTooltipData(specialArgs=[token.id]))

        return result

    @classmethod
    def _getContentId(cls, bonus):
        result = super(OneTimeGiftTokensBonusUIPacker, cls)._getContentId(bonus)
        for token in sorted(bonus.getTokens().itervalues()):
            if cls.__isOTGMissionsToken(token.id, token):
                result.append(R.views.one_time_gift.mono.lobby.one_time_gift_quest_tooltip())

        return result

    @classmethod
    def __isOTGMissionsToken(cls, tokenID, token):
        return tokenID.startswith(OTG_MISSION_TOKEN_PREFIX) and token.count > 0

    @classmethod
    def __packOTGMissionsToken(cls, model):
        model.setName(OTG_MISSION_TOKEN_BONUS_NAME)
        model.setIconSmall(backport.image(R.images.gui.maps.icons.quests.bonuses.dyn(AWARDS_SIZES.SMALL).dyn(OTG_MISSION_TOKEN_BONUS_NAME)()))
        model.setIconBig(backport.image(R.images.gui.maps.icons.quests.bonuses.dyn(AWARDS_SIZES.BIG).dyn(OTG_MISSION_TOKEN_BONUS_NAME)()))
        model.setLabel(backport.text(R.strings.one_time_gift.awards.additionalRewardFull.reward.missions()))
        return model


class OneTimeGiftItemBonusUIPacker(ItemBonusUIPacker):

    @classmethod
    def packSingleBonus(cls, bonus, item, count):
        return cls._packSingleBonus(bonus, item, count)

    @classmethod
    def _pack(cls, bonus):
        result = []
        equipmentSet = cls.__packEquipmentSet(bonus)
        if equipmentSet is not None:
            result.append(equipmentSet)
        for item, count in cls.__filterBonusItems(bonus, lambda i: not isinstance(i, OptionalDevice)):
            result.append(cls._packSingleBonus(bonus, item, count))

        return result

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        if any(cls.__filterBonusItems(bonus, lambda i: isinstance(i, OptionalDevice))):
            result.append(R.aliases.one_time_gift.default.EquipmentSetTooltip())
        for _ in cls.__filterBonusItems(bonus, lambda i: not isinstance(i, OptionalDevice)):
            result.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return result

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        equipmentSetItems = [ (item, count) for item, count in cls.__filterBonusItems(bonus, lambda i: isinstance(i, OptionalDevice)) ]
        if equipmentSetItems:
            tooltipData.append(createTooltipData(isSpecial=True, specialArgs={'itemsForTooltip': equipmentSetItems,
             'bonus': bonus}))
        for item, _ in cls.__filterBonusItems(bonus, lambda i: not isinstance(i, OptionalDevice)):
            tooltipData.append(createTooltipData(isSpecial=True, specialAlias=ItemsBonusFormatter.getTooltip(item), specialArgs=[item.intCD]))

        return tooltipData

    @classmethod
    def __filterBonusItems(cls, bonus, filter):
        for item, count in sorted(bonus.getItems().iteritems(), key=cls._itemsSortFunction):
            if item is not None and count and filter(item):
                yield (item, count)

        return

    @classmethod
    def __packEquipmentSet(cls, bonus):
        count = len(list(cls.__filterBonusItems(bonus, lambda i: isinstance(i, OptionalDevice))))
        if not count:
            return None
        else:
            model = cls._getBonusModel()
            model.setName(bonus.getName())
            model.setIsCompensation(False)
            model.setValue(OTG_EQUIPMENT_SET_COUNT_VAL)
            model.setItem(OTG_EQUIPMENT_SET_BONUS_NAME)
            model.setLabel(backport.text(R.strings.one_time_gift.equipmentSet.rewards.label(), count=count))
            return model
