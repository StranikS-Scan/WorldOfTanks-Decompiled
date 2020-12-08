# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/missions/packers/bonus.py
import logging
import typing
import constants
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl import backport
from gui.impl.backport import TooltipData, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.blueprint_bonus_model import BlueprintBonusModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from gui.server_events.awards_formatters import TOKEN_SIZES, BATTLE_BONUS_X5_TOKEN, ItemsBonusFormatter, TokenBonusFormatter
from gui.server_events.formatters import COMPLEX_TOKEN, parseComplexToken, TokenComplex
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.money import Currency
from gui.shared.utils.functions import makeTooltip
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from helpers import i18n, dependency
from items.components.ny_constants import TOKEN_TALISMAN_BONUS
from skeletons.gui.server_events import IEventsCache
from helpers import time_utils
from skeletons.gui.shared import IItemsCache
DOSSIER_BADGE_ICON_PREFIX = 'badge_'
DOSSIER_ACHIEVEMENT_POSTFIX = '_achievement'
DOSSIER_BADGE_POSTFIX = '_badge'
VEHICLE_RENT_ICON_POSTFIX = '_rent'
if typing.TYPE_CHECKING:
    from frameworks.wulf.view.array import Array
    from gui.goodies.goodie_items import BoosterUICommon
    from gui.server_events.bonuses import CustomizationsBonus, CrewSkinsBonus, TokensBonus, SimpleBonus, ItemsBonus, DossierBonus, VehicleBlueprintBonus, CrewBooksBonus, GoodiesBonus, TankmenBonus, VehiclesBonus
    from gui.shared.gui_items.fitting_item import FittingItem
    from gui.shared.gui_items.Vehicle import Vehicle
_logger = logging.getLogger(__name__)

def getDefaultBonusPackersMap():
    simpleBonusPacker = SimpleBonusUIPacker()
    tokenBonusPacker = TokenBonusUIPacker()
    blueprintBonusPacker = BlueprintBonusUIPacker()
    return {'battleToken': tokenBonusPacker,
     'berths': simpleBonusPacker,
     'blueprints': blueprintBonusPacker,
     'blueprintsAny': blueprintBonusPacker,
     'creditsFactor': simpleBonusPacker,
     'crewBooks': CrewBookBonusUIPacker(),
     'crewSkins': CrewSkinBonusUIPacker(),
     'customizations': CustomizationBonusUIPacker(),
     'dailyXPFactor': simpleBonusPacker,
     'dossier': DossierBonusUIPacker(),
     'finalBlueprints': blueprintBonusPacker,
     'freeXP': simpleBonusPacker,
     'freeXPFactor': simpleBonusPacker,
     'goodies': GoodiesBonusUIPacker(),
     'items': ItemBonusUIPacker(),
     'meta': simpleBonusPacker,
     'slots': simpleBonusPacker,
     'strBonus': simpleBonusPacker,
     'tankmen': TankmenBonusUIPacker(),
     'tankmenXP': simpleBonusPacker,
     'tankmenXPFactor': simpleBonusPacker,
     'tokens': tokenBonusPacker,
     'vehicles': VehiclesBonusUIPacker(),
     'xp': simpleBonusPacker,
     'xpFactor': simpleBonusPacker,
     'groups': GroupsBonusUIPacker(),
     'progressionXPToken': tokenBonusPacker,
     Currency.CREDITS: simpleBonusPacker,
     Currency.CRYSTAL: simpleBonusPacker,
     Currency.GOLD: simpleBonusPacker,
     constants.PREMIUM_ENTITLEMENTS.BASIC: simpleBonusPacker,
     constants.PREMIUM_ENTITLEMENTS.PLUS: simpleBonusPacker}


class BaseBonusUIPacker(object):

    @classmethod
    def pack(cls, bonus):
        return cls._pack(bonus)

    @classmethod
    def getToolTip(cls, bonus):
        return cls._getToolTip(bonus)

    @classmethod
    def _pack(cls, bonus):
        return []

    @classmethod
    def _packCommon(cls, bonus, model):
        model.setName(bonus.getName())
        model.setIsCompensation(bonus.isCompensation())
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        return [createTooltipData(bonus.getTooltip())]


class SimpleBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus):
        model = BonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(bonus.getValue()))
        return model


class TokenBonusUIPacker(BaseBonusUIPacker):
    _eventsCache = dependency.descriptor(IEventsCache)
    _itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def _pack(cls, bonus):
        bonusTokens = bonus.getTokens()
        result = []
        bonusPackers = cls.__getTokenBonusPackers()
        for tokenID, token in bonusTokens.iteritems():
            complexToken = parseComplexToken(tokenID)
            tokenType = cls.__getTokenBonusType(tokenID, complexToken)
            specialPacker = bonusPackers.get(tokenType)
            if specialPacker is None:
                continue
            packedBonus = cls.__packToken(specialPacker, bonus, complexToken, token)
            if packedBonus is not None:
                result.append(packedBonus)

        return result

    @classmethod
    def _getToolTip(cls, bonus):
        bonusTokens = bonus.getTokens()
        tooltipPackers = cls.__getTooltipsPackers()
        result = []
        for tokenID, _ in bonusTokens.iteritems():
            complexToken = parseComplexToken(tokenID)
            tokenType = cls.__getTokenBonusType(tokenID, complexToken)
            tooltipPacker = tooltipPackers.get(tokenType)
            if tooltipPacker is None:
                continue
            tooltip = tooltipPacker(tokenID, complexToken)
            result.append(createTooltipData(tooltip))

        return result

    @classmethod
    def __getTokenBonusType(cls, tokenID, complexToken):
        if complexToken.isDisplayable:
            return COMPLEX_TOKEN
        if tokenID.startswith(BATTLE_BONUS_X5_TOKEN):
            return BATTLE_BONUS_X5_TOKEN
        if tokenID.startswith(constants.LOOTBOX_TOKEN_PREFIX):
            return constants.LOOTBOX_TOKEN_PREFIX
        return TOKEN_TALISMAN_BONUS if tokenID.startswith(TOKEN_TALISMAN_BONUS) else ''

    @classmethod
    def __getTokenBonusPackers(cls):
        return {BATTLE_BONUS_X5_TOKEN: cls.__packBattleBonusX5Token,
         COMPLEX_TOKEN: cls.__packComplexToken,
         constants.LOOTBOX_TOKEN_PREFIX: cls.__packNYLootboxToken,
         TOKEN_TALISMAN_BONUS: cls.__packTalismanBonusToken}

    @classmethod
    def __getTooltipsPackers(cls):
        return {BATTLE_BONUS_X5_TOKEN: TokenBonusFormatter.getBattleBonusX5Tooltip,
         COMPLEX_TOKEN: cls.__getComplexToolTip,
         constants.LOOTBOX_TOKEN_PREFIX: cls.__packNYLootboxToolTip,
         TOKEN_TALISMAN_BONUS: cls.__packTalismanBonusToolTip}

    @classmethod
    def __packToken(cls, bonusPacker, bonus, *args):
        model = TokenBonusModel()
        cls._packCommon(bonus, model)
        return bonusPacker(model, bonus, *args)

    @classmethod
    def __packComplexToken(cls, model, bonus, complexToken, token):
        webCache = cls._eventsCache.prefetcher
        model.setValue(str(token.count))
        model.setUserName(i18n.makeString(webCache.getTokenInfo(complexToken.styleID)))
        model.setIconSmall(webCache.getTokenImage(complexToken.styleID, TOKEN_SIZES.SMALL))
        model.setIconBig(webCache.getTokenImage(complexToken.styleID, TOKEN_SIZES.BIG))
        return model

    @classmethod
    def __packNYLootboxToken(cls, model, bonus, complexToken, token):
        count = bonus.getCount()
        if count < 0:
            return
        else:
            lootbox = cls._itemsCache.items.tokens.getLootBoxByTokenID(token.id)
            if lootbox is None:
                return
            lootboxType = lootbox.getType()
            model.setUserName(lootbox.getUserName())
            model.setIconSmall(RES_ICONS.getLootBoxBonusIcon('small', lootboxType))
            model.setIconBig(RES_ICONS.getLootBoxBonusIcon('big', lootboxType))
            model.setValue(str(count))
            return model

    @classmethod
    def __packTalismanBonusToken(cls, model, bonus, complexToken, token):
        count = bonus.getCount()
        if count < 0:
            return None
        else:
            model.setUserName(TOKEN_TALISMAN_BONUS)
            model.setValue(str(count))
            return model

    @classmethod
    def __packBattleBonusX5Token(cls, model, bonus, *args):
        model.setValue(str(bonus.getCount()))
        return model

    @classmethod
    def __getComplexToolTip(cls, _, complexToken, *args):
        webCache = cls._eventsCache.prefetcher
        userName = i18n.makeString(webCache.getTokenInfo(complexToken.styleID))
        tooltip = makeTooltip(i18n.makeString(TOOLTIPS.QUESTS_BONUSES_TOKEN_HEADER, userName=userName), i18n.makeString(TOOLTIPS.QUESTS_BONUSES_TOKEN_BODY))
        return tooltip

    @classmethod
    def __packNYLootboxToolTip(cls, tokenId, *args):
        lootbox = cls._itemsCache.items.tokens.getLootBoxByTokenID(tokenId)
        return makeTooltip(header=lootbox.getUserName(), body=TOOLTIPS.QUESTS_BONUSES_LOOTBOXTOKEN_BODY)

    @classmethod
    def __packTalismanBonusToolTip(cls, tokenId, *args):
        return makeTooltip(header=backport.text(R.strings.tooltips.quests.bonuses.talismanBonusToken.header()), body=backport.text(R.strings.tooltips.quests.bonuses.talismanBonusToken.body()))


class ItemBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        bonusItems = bonus.getItems()
        result = []
        for item, count in sorted(bonusItems.iteritems(), key=lambda i: i[0]):
            if item is None or not count:
                continue
            result.append(cls._packSingleBonus(bonus, item, count))

        return result

    @classmethod
    def _packSingleBonus(cls, bonus, item, count):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(count))
        model.setItem(item.getGUIEmblemID())
        model.setOverlayType(item.getOverlayType())
        return model

    @classmethod
    def _getBonusModel(cls):
        return ItemBonusModel()

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for item, _ in sorted(bonus.getItems().iteritems(), key=lambda i: i[0]):
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=ItemsBonusFormatter.getTooltip(item), specialArgs=[item.intCD]))

        return tooltipData


class GoodiesBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for booster, count in sorted(bonus.getBoosters().iteritems(), key=lambda b: b[0].boosterID):
            if booster is None or not count:
                continue
            result.append(cls._packSingleBoosterBonus(bonus, booster, count))

        for demountkit, count in sorted(bonus.getDemountKits().iteritems()):
            if demountkit is None or not count:
                continue
            result.append(cls._packSingleDemountKitBonus(bonus, demountkit, count))

        return result

    @classmethod
    def _packSingleBoosterBonus(cls, bonus, booster, count):
        return cls._packIconBonusModel(bonus, booster.boosterGuiType, count)

    @classmethod
    def _packSingleDemountKitBonus(cls, bonus, demountkit, count):
        return cls._packIconBonusModel(bonus, demountkit.demountKitGuiType, count)

    @classmethod
    def _packIconBonusModel(cls, bonus, icon, count):
        model = IconBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(count))
        model.setIcon(icon)
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for booster in sorted(bonus.getBoosters().iterkeys(), key=lambda b: b.boosterID):
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.SHOP_BOOSTER, specialArgs=[booster.boosterID]))

        for demountkit in sorted(bonus.getDemountKits().iterkeys()):
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.AWARD_DEMOUNT_KIT, specialArgs=[demountkit.intCD]))

        return tooltipData


class BlueprintBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        model = BlueprintBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(bonus.getCount()))
        model.setType(bonus.getBlueprintName())
        model.setIcon(bonus.getImageCategory())
        return [model]

    @classmethod
    def _getToolTip(cls, bonus):
        return [TooltipData(tooltip=None, isSpecial=True, specialAlias=bonus.getBlueprintSpecialAlias(), specialArgs=[bonus.getBlueprintSpecialArgs()])]


class CrewBookBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for book, count in sorted(bonus.getItems()):
            if book is None or not count:
                continue
            result.append(cls._packSingleBonus(bonus, book, count))

        return result

    @classmethod
    def _packSingleBonus(cls, bonus, book, count):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(count))
        model.setIcon(book.getBonusIconName())
        return model

    @classmethod
    def _getBonusModel(cls):
        return IconBonusModel()

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for item, count in sorted(bonus.getItems()):
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.CREW_BOOK, specialArgs=[item.intCD, count]))

        return tooltipData


class CrewSkinBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for crewSkin, count, _, _ in sorted(bonus.getItems()):
            if crewSkin is None or not count:
                continue
            result.append(cls._packSingleBonus(bonus, crewSkin, count))

        return result

    @classmethod
    def _packSingleBonus(cls, bonus, crewSkin, count):
        model = IconBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(count))
        model.setIcon(str(crewSkin.itemTypeName + str(crewSkin.getRarity())))
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for item, _, _, _ in sorted(bonus.getItems()):
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.CREW_SKIN, specialArgs=[item.getID()]))

        return tooltipData


class CustomizationBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for item in bonus.getCustomizations():
            if item is None:
                continue
            result.append(cls._packSingleBonus(bonus, item))

        return result

    @classmethod
    def _packSingleBonus(cls, bonus, item):
        model = IconBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(item.get('value', 0)))
        model.setIcon(str(bonus.getC11nItem(item).itemTypeName))
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for item in bonus.getCustomizations():
            if item is None:
                continue
            itemCustomization = bonus.getC11nItem(item)
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD, specialArgs=CustomizationTooltipContext(itemCD=itemCustomization.intCD)))

        return tooltipData


class DossierBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for achievement in bonus.getAchievements():
            dossierIconName = achievement.getName()
            dossierValue = achievement.getValue()
            result.append(cls._packSingleBonus(bonus, dossierIconName, DOSSIER_ACHIEVEMENT_POSTFIX, dossierValue))

        for badge in bonus.getBadges():
            dossierIconName = DOSSIER_BADGE_ICON_PREFIX + str(badge.badgeID)
            dossierValue = 0
            result.append(cls._packSingleBonus(bonus, dossierIconName, DOSSIER_BADGE_POSTFIX, dossierValue))

        return result

    @classmethod
    def _packSingleBonus(cls, bonus, dossierIconName, dossierNamePostfix, dossierValue):
        model = IconBonusModel()
        model.setName(bonus.getName() + dossierNamePostfix)
        model.setIsCompensation(bonus.isCompensation())
        model.setValue(str(dossierValue))
        model.setIcon(dossierIconName)
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for achievement in bonus.getAchievements():
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BATTLE_STATS_ACHIEVS, specialArgs=[achievement.getBlock(), achievement.getName(), achievement.getValue()]))

        for badge in bonus.getBadges():
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BADGE, specialArgs=[badge.badgeID]))

        return tooltipData


class TankmenBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for _ in bonus.getTankmenGroups():
            result.append(cls._packSingleBonus(bonus))

        return result

    @classmethod
    def _packSingleBonus(cls, bonus):
        model = BonusModel()
        cls._packCommon(bonus, model)
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for group in bonus.getTankmenGroups().itervalues():
            if group['skills']:
                key = 'with_skills'
            else:
                key = 'no_skills'
            label = '#quests:bonuses/item/tankmen/%s' % key
            tooltipData.append(createTooltipData(makeTooltip(TOOLTIPS.getAwardHeader(bonus.getName()), i18n.makeString(label, **group))))

        return tooltipData


class VehiclesBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return cls._packVehicles(bonus, bonus.getVehicles())

    @classmethod
    def _getToolTip(cls, bonus):
        return cls._packTooltips(bonus, bonus.getVehicles())

    @classmethod
    def _packVehicles(cls, bonus, vehicles):
        packedVehicles = []
        for vehicle, vehInfo in vehicles:
            compensation = bonus.compensation(vehicle, bonus)
            if compensation:
                packer = SimpleBonusUIPacker()
                for bonusComp in compensation:
                    packedVehicles.extend(packer.pack(bonusComp))

            packedVehicles.append(cls._packVehicle(bonus, vehicle, vehInfo))

        return packedVehicles

    @classmethod
    def _packTooltips(cls, bonus, vehicles):
        packedTooltips = []
        for vehicle, vehInfo in vehicles:
            compensation = bonus.compensation(vehicle, bonus)
            if compensation:
                for bonusComp in compensation:
                    packedTooltips.extend(cls._packCompensationTooltip(bonusComp, vehicle))

            packedTooltips.append(cls._packTooltip(bonus, vehicle, vehInfo))

        return packedTooltips

    @classmethod
    def _packVehicle(cls, bonus, vehicle, vehInfo):
        rentDays = bonus.getRentDays(vehInfo)
        rentBattles = bonus.getRentBattles(vehInfo)
        rentWins = bonus.getRentWins(vehInfo)
        rentSeason = bonus.getRentSeason(vehInfo)
        isRent = rentDays or rentBattles or rentWins or rentSeason
        return cls._packVehicleBonusModel(bonus, vehicle, isRent)

    @classmethod
    def _packTooltip(cls, bonus, vehicle, vehInfo):
        tmanRoleLevel = bonus.getTmanRoleLevel(vehInfo)
        rentDays = bonus.getRentDays(vehInfo)
        rentBattles = bonus.getRentBattles(vehInfo)
        rentWins = bonus.getRentWins(vehInfo)
        rentSeason = bonus.getRentSeason(vehInfo)
        rentExpiryTime = cls._getRentExpiryTime(rentDays)
        return TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.AWARD_VEHICLE, specialArgs=[vehicle.intCD,
         tmanRoleLevel,
         rentExpiryTime,
         rentBattles,
         rentWins,
         rentSeason])

    @classmethod
    def _packCompensationTooltip(cls, bonusComp, vehicle):
        return SimpleBonusUIPacker().getToolTip(bonusComp)

    @staticmethod
    def _getRentExpiryTime(rentDays):
        if rentDays:
            rentExpiryTime = time_utils.getCurrentTimestamp()
            rentExpiryTime += rentDays * time_utils.ONE_DAY
        else:
            rentExpiryTime = 0
        return rentExpiryTime

    @staticmethod
    def _packVehicleBonusModel(bonus, vehicle, isRent):
        model = BonusModel()
        model.setName(bonus.getName() + VEHICLE_RENT_ICON_POSTFIX if isRent else bonus.getName())
        model.setIsCompensation(bonus.isCompensation())
        return model


class GroupsBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        model = IconBonusModel()
        cls._packCommon(bonus, model)
        model.setIcon('default')
        return [model]

    @classmethod
    def _getToolTip(cls, bonus):
        return [createTooltipData(makeTooltip(TOOLTIPS.getAwardHeader(bonus.getName()), TOOLTIPS.getAwardBody(bonus.getName())))]


class BonusUIPacker(object):

    def __init__(self, packers=None):
        self.__packers = packers or {}

    def pack(self, bonus):
        packer = self._getBonusPacker(bonus.getName())
        if packer:
            return packer.pack(bonus)
        _logger.error('Bonus packer for bonus type %s was not implemented yet.', bonus.getName())
        return []

    def getPackers(self):
        return self.__packers

    def _getBonusPacker(self, bonusName):
        return self.__packers.get(bonusName)

    def getToolTip(self, bonus):
        packer = self._getBonusPacker(bonus.getName())
        if packer:
            return packer.getToolTip(bonus)
        _logger.error('Bonus packer for bonus type %s was not implemented yet.', bonus.getName())
        return []


def getDefaultBonusPacker():
    return BonusUIPacker(getDefaultBonusPackersMap())


def packBonusModelAndTooltipData(bonuses, packer, model, tooltipData=None):
    bonusIndexTotal = 0
    bonusTooltipList = []
    for bonus in bonuses:
        if bonus.isShowInGUI():
            bonusList = packer.pack(bonus)
            if bonusList and tooltipData is not None:
                bonusTooltipList = packer.getToolTip(bonus)
            for bonusIndex, item in enumerate(bonusList):
                item.setIndex(bonusIndexTotal)
                model.addViewModel(item)
                if tooltipData is not None:
                    tooltipData[bonusIndexTotal] = bonusTooltipList[bonusIndex]
                bonusIndexTotal += 1

    return
