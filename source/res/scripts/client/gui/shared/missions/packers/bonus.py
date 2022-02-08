# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/missions/packers/bonus.py
import logging
import typing
import constants
from adisp import async, process
from gui.dog_tag_composer import dogTagComposer
from gui.impl import backport
from gui.impl.backport import TooltipData, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.blueprint_bonus_model import BlueprintBonusModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from gui.ranked_battles.constants import YEAR_POINTS_TOKEN
from gui.server_events.awards_formatters import TOKEN_SIZES, BATTLE_BONUS_X5_TOKEN, ItemsBonusFormatter, TokenBonusFormatter, formatCountLabel, AWARDS_SIZES
from gui.server_events.formatters import COMPLEX_TOKEN, parseComplexToken, TokenComplex
from gui.shared.gui_items.crew_skin import localizedFullName
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.gui_items.customization.c11n_items import Style
from gui.shared.money import Currency
from gui.shared.utils.functions import makeTooltip
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from helpers import i18n, dependency
from skeletons.gui.server_events import IEventsCache
from helpers import time_utils
DOSSIER_BADGE_ICON_PREFIX = 'badge_'
DOSSIER_ACHIEVEMENT_POSTFIX = '_achievement'
DOSSIER_BADGE_POSTFIX = '_badge'
VEHICLE_RENT_ICON_POSTFIX = '_rent'
BACKPORT_TOOLTIP_CONTENT_ID = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()
if typing.TYPE_CHECKING:
    from typing import Dict, List
    from frameworks.wulf.view.array import Array
    from gui.goodies.goodie_items import BoosterUICommon
    from gui.server_events.bonuses import CustomizationsBonus, CrewSkinsBonus, TokensBonus, SimpleBonus, ItemsBonus, DossierBonus, VehicleBlueprintBonus, CrewBooksBonus, GoodiesBonus, TankmenBonus, VehiclesBonus, DogTagComponentBonus, BattlePassPointsBonus
    from gui.shared.gui_items.fitting_item import FittingItem
    from gui.shared.gui_items.Vehicle import Vehicle
_logger = logging.getLogger(__name__)

def getDefaultBonusPackersMap():
    simpleBonusPacker = SimpleBonusUIPacker()
    tokenBonusPacker = TokenBonusUIPacker()
    blueprintBonusPacker = BlueprintBonusUIPacker()
    return {'battlePassPoints': BattlePassPointsBonusPacker(),
     'battleToken': tokenBonusPacker,
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
     'dogTagComponents': DogTagComponentsUIPacker(),
     Currency.CREDITS: simpleBonusPacker,
     Currency.CRYSTAL: simpleBonusPacker,
     Currency.GOLD: simpleBonusPacker,
     Currency.BPCOIN: simpleBonusPacker,
     constants.PREMIUM_ENTITLEMENTS.BASIC: simpleBonusPacker,
     constants.PREMIUM_ENTITLEMENTS.PLUS: simpleBonusPacker}


def getLocalizedBonusName(name):
    labelStr = None
    localizedLabel = R.strings.quests.bonusName.dyn(name)
    if localizedLabel.exists():
        labelStr = backport.text(localizedLabel())
    else:
        _logger.warning("Localized text for the 'additional rewards tooltip' label for %s reward was not found.", name)
    return labelStr


class BaseBonusUIPacker(object):

    @classmethod
    def pack(cls, bonus):
        return cls._pack(bonus)

    @classmethod
    def getToolTip(cls, bonus):
        return cls._getToolTip(bonus)

    @classmethod
    def getContentId(cls, bonus):
        return cls._getContentId(bonus)

    def isAsync(self):
        return False

    def asyncPack(self, bonus, callback=None):
        pass

    def asyncGetToolTip(self, bonus, callback=None):
        pass

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

    @classmethod
    def _getContentId(cls, bonus):
        return [BACKPORT_TOOLTIP_CONTENT_ID]


class SimpleBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        label = getLocalizedBonusName(bonus.getName())
        return [cls._packSingleBonus(bonus, label if label else '')]

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(bonus.getValue()))
        model.setLabel(label)
        return model

    @classmethod
    def _getBonusModel(cls):
        return BonusModel()


class TokenBonusUIPacker(BaseBonusUIPacker):
    _eventsCache = dependency.descriptor(IEventsCache)
    _RANKED_TOKEN_SOURCE = 'rankedPoint'

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
                _logger.warning('There is not a tooltip creator for a token bonus %s', tokenType)
                continue
            tooltip = tooltipPacker(complexToken)
            result.append(createTooltipData(tooltip))

        return result

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        bonusTokens = bonus.getTokens()
        for _ in bonusTokens:
            result.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return result

    @classmethod
    def __getTokenBonusType(cls, tokenID, complexToken):
        if complexToken.isDisplayable:
            return COMPLEX_TOKEN
        if tokenID.startswith(BATTLE_BONUS_X5_TOKEN):
            return BATTLE_BONUS_X5_TOKEN
        return YEAR_POINTS_TOKEN if tokenID.startswith(YEAR_POINTS_TOKEN) else ''

    @classmethod
    def __getTokenBonusPackers(cls):
        return {BATTLE_BONUS_X5_TOKEN: cls.__packBattleBonusX5Token,
         COMPLEX_TOKEN: cls.__packComplexToken,
         YEAR_POINTS_TOKEN: cls.__packRankedToken}

    @classmethod
    def __getTooltipsPackers(cls):
        return {BATTLE_BONUS_X5_TOKEN: TokenBonusFormatter.getBattleBonusX5Tooltip,
         COMPLEX_TOKEN: cls.__getComplexToolTip,
         YEAR_POINTS_TOKEN: cls.__getRankedPointToolTip}

    @classmethod
    def __packToken(cls, bonusPacker, bonus, *args):
        model = TokenBonusModel()
        cls._packCommon(bonus, model)
        return bonusPacker(model, bonus, *args)

    @classmethod
    def __packComplexToken(cls, model, bonus, complexToken, token):
        webCache = cls._eventsCache.prefetcher
        labelStr = i18n.makeString(webCache.getTokenInfo(complexToken.styleID))
        model.setValue(str(token.count))
        model.setUserName(labelStr)
        model.setIconSmall(webCache.getTokenImage(complexToken.styleID, TOKEN_SIZES.SMALL))
        model.setIconBig(webCache.getTokenImage(complexToken.styleID, TOKEN_SIZES.BIG))
        model.setLabel(labelStr)
        return model

    @classmethod
    def __packRankedToken(cls, model, bonus, *args):
        model.setUserName(backport.text(R.strings.tooltips.rankedBattleView.scorePoint.short.header()))
        model.setIconSmall(backport.image(R.images.gui.maps.icons.quests.bonuses.dyn(AWARDS_SIZES.SMALL).dyn(cls._RANKED_TOKEN_SOURCE)()))
        model.setIconBig(backport.image(R.images.gui.maps.icons.quests.bonuses.dyn(AWARDS_SIZES.BIG).dyn(cls._RANKED_TOKEN_SOURCE)()))
        model.setLabel(formatCountLabel(bonus.getCount()))
        return model

    @classmethod
    def __packBattleBonusX5Token(cls, model, bonus, *args):
        model.setValue(str(bonus.getCount()))
        return model

    @classmethod
    def __getComplexToolTip(cls, complexToken):
        webCache = cls._eventsCache.prefetcher
        userName = i18n.makeString(webCache.getTokenInfo(complexToken.styleID))
        tooltip = makeTooltip(i18n.makeString(TOOLTIPS.QUESTS_BONUSES_TOKEN_HEADER, userName=userName), i18n.makeString(TOOLTIPS.QUESTS_BONUSES_TOKEN_BODY))
        return tooltip

    @classmethod
    def __getRankedPointToolTip(cls, *_):
        return makeTooltip(header=backport.text(R.strings.tooltips.rankedBattleView.scorePoint.header()), body=backport.text(R.strings.tooltips.rankedBattleView.scorePoint.body()))


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
        model.setLabel(item.userName)
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

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        for _, _ in sorted(bonus.getItems().iteritems(), key=lambda i: i[0]):
            result.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return result


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
        return cls._packIconBonusModel(bonus, booster.boosterGuiType, count, booster.fullUserName)

    @classmethod
    def _packSingleDemountKitBonus(cls, bonus, demountkit, count):
        return cls._packIconBonusModel(bonus, demountkit.demountKitGuiType, count, demountkit.userName)

    @classmethod
    def _packIconBonusModel(cls, bonus, icon, count, label):
        model = IconBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(count))
        model.setIcon(icon)
        model.setLabel(label)
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for booster in sorted(bonus.getBoosters().iterkeys(), key=lambda b: b.boosterID):
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.SHOP_BOOSTER, specialArgs=[booster.boosterID]))

        for demountkit in sorted(bonus.getDemountKits().iterkeys()):
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.AWARD_DEMOUNT_KIT, specialArgs=[demountkit.intCD]))

        return tooltipData

    @classmethod
    def _getContentId(cls, bonus):
        tooltipData = []
        for _ in sorted(bonus.getBoosters().iterkeys(), key=lambda b: b.boosterID):
            tooltipData.append(BACKPORT_TOOLTIP_CONTENT_ID)

        for _ in sorted(bonus.getDemountKits().iterkeys()):
            tooltipData.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return tooltipData


class BlueprintBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(bonus.getCount()))
        model.setType(bonus.getBlueprintName())
        model.setIcon(bonus.getImageCategory())
        return [model]

    @classmethod
    def _getToolTip(cls, bonus):
        return [TooltipData(tooltip=None, isSpecial=True, specialAlias=bonus.getBlueprintSpecialAlias(), specialArgs=[bonus.getBlueprintSpecialArgs()])]

    @classmethod
    def _getBonusModel(cls):
        return BlueprintBonusModel()


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
        model.setLabel(book.userName)
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

    @classmethod
    def _getContentId(cls, bonus):
        tooltipData = []
        for _, _ in sorted(bonus.getItems()):
            tooltipData.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return tooltipData


class CrewSkinBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for crewSkin, count, _, _ in sorted(bonus.getItems()):
            if crewSkin is None or not count:
                continue
            label = localizedFullName(crewSkin)
            result.append(cls._packSingleBonus(bonus, crewSkin, count, label))

        return result

    @classmethod
    def _packSingleBonus(cls, bonus, crewSkin, count, label):
        model = IconBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(count))
        model.setIcon(str(crewSkin.itemTypeName + str(crewSkin.getRarity())))
        model.setLabel(label)
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for item, _, _, _ in sorted(bonus.getItems()):
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.CREW_SKIN, specialArgs=[item.getID()]))

        return tooltipData

    @classmethod
    def _getContentId(cls, bonus):
        tooltipData = []
        for _ in sorted(bonus.getItems()):
            tooltipData.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return tooltipData


class CustomizationBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for item in bonus.getCustomizations():
            if item is None:
                continue
            label = getLocalizedBonusName(bonus.getC11nItem(item).itemTypeName)
            result.append(cls._packSingleBonus(bonus, item, label if label else ''))

        return result

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = IconBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(item.get('value', 0)))
        model.setIcon(str(bonus.getC11nItem(item).itemTypeName))
        model.setLabel(label)
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

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        for b in bonus.getCustomizations():
            if b is not None:
                result.extend(super(CustomizationBonusUIPacker, cls)._getContentId(b))

        return result


class Customization3Dand2DbonusUIPacker(CustomizationBonusUIPacker):
    _3D_STYLE_ICON_NAME = 'style_3d'

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        packed = super(Customization3Dand2DbonusUIPacker, cls)._packSingleBonus(bonus, item, label)
        customization = bonus.getC11nItem(item)
        is3Dstyle = isinstance(customization, Style) and customization.is3D
        if is3Dstyle:
            packed.setIcon(cls._3D_STYLE_ICON_NAME)
        return packed


class DossierBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for achievement in bonus.getAchievements():
            dossierIconName = achievement.getName()
            dossierValue = achievement.getValue()
            dossierLabel = achievement.getUserName()
            result.append(cls._packSingleBonus(bonus, dossierIconName, DOSSIER_ACHIEVEMENT_POSTFIX, dossierValue, dossierLabel))

        for badge in bonus.getBadges():
            dossierIconName = DOSSIER_BADGE_ICON_PREFIX + str(badge.badgeID)
            dossierValue = 0
            dossierLabel = badge.getUserName()
            result.append(cls._packSingleBonus(bonus, dossierIconName, DOSSIER_BADGE_POSTFIX, dossierValue, dossierLabel))

        return result

    @classmethod
    def _packSingleBonus(cls, bonus, dossierIconName, dossierNamePostfix, dossierValue, dossierLabel):
        model = IconBonusModel()
        model.setName(bonus.getName() + dossierNamePostfix)
        model.setIsCompensation(bonus.isCompensation())
        model.setValue(str(dossierValue))
        model.setIcon(dossierIconName)
        model.setLabel(dossierLabel)
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for achievement in bonus.getAchievements():
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BATTLE_STATS_ACHIEVS, specialArgs=[achievement.getBlock(), achievement.getName(), achievement.getValue()]))

        for badge in bonus.getBadges():
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BADGE, specialArgs=[badge.badgeID]))

        return tooltipData

    @classmethod
    def _getContentId(cls, bonus):
        tooltipData = []
        for _ in bonus.getAchievements():
            tooltipData.extend(super(DossierBonusUIPacker, cls)._getContentId(bonus))

        for _ in bonus.getBadges():
            tooltipData.extend(super(DossierBonusUIPacker, cls)._getContentId(bonus))

        return tooltipData


class TankmenBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for group in bonus.getTankmenGroups().itervalues():
            result.append(cls._packSingleBonus(bonus, cls._getLabel(group)))

        return result

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = BonusModel()
        cls._packCommon(bonus, model)
        model.setLabel(label)
        return model

    @classmethod
    def _getLabel(cls, group):
        if group['skills']:
            key = 'with_skills'
        else:
            key = 'no_skills'
        label = '#quests:bonuses/item/tankmen/%s' % key
        return i18n.makeString(label, **group)

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for group in bonus.getTankmenGroups().itervalues():
            tooltipData.append(createTooltipData(makeTooltip(TOOLTIPS.getAwardHeader(bonus.getName()), cls._getLabel(group))))

        return tooltipData

    @classmethod
    def _getContentId(cls, bonus):
        return [ BACKPORT_TOOLTIP_CONTENT_ID for _ in bonus.getTankmenGroups().itervalues() ]


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

            packedVehicles.append(cls._packVehicle(bonus, vehInfo, vehicle))

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
    def _packCompensationTooltip(cls, bonusComp, vehicle):
        return SimpleBonusUIPacker().getToolTip(bonusComp)

    @classmethod
    def _packVehicle(cls, bonus, vehInfo, vehicle):
        rentDays = bonus.getRentDays(vehInfo)
        rentBattles = bonus.getRentBattles(vehInfo)
        rentWins = bonus.getRentWins(vehInfo)
        rentSeason = bonus.getRentSeason(vehInfo)
        rentCycle = bonus.getRentCycle(vehInfo)
        isRent = rentDays or rentBattles or rentWins or rentSeason or rentCycle
        return cls._packVehicleBonusModel(bonus, vehInfo, isRent, vehicle)

    @classmethod
    def _packTooltip(cls, bonus, vehicle, vehInfo):
        tmanRoleLevel = bonus.getTmanRoleLevel(vehInfo)
        rentDays = bonus.getRentDays(vehInfo)
        rentBattles = bonus.getRentBattles(vehInfo)
        rentWins = bonus.getRentWins(vehInfo)
        rentSeason = bonus.getRentSeason(vehInfo)
        rentCycle = bonus.getRentCycle(vehInfo)
        rentExpiryTime = cls._getRentExpiryTime(rentDays)
        return TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.AWARD_VEHICLE, specialArgs=[vehicle.intCD,
         tmanRoleLevel,
         rentExpiryTime,
         rentBattles,
         rentWins,
         rentSeason,
         rentCycle])

    @staticmethod
    def _getRentExpiryTime(rentDays):
        if rentDays:
            rentExpiryTime = time_utils.getCurrentTimestamp()
            rentExpiryTime += rentDays * time_utils.ONE_DAY
        else:
            rentExpiryTime = 0.0
        return rentExpiryTime

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vehInfo, isRent, vehicle):
        model = BonusModel()
        model.setName(cls._createUIName(bonus, isRent))
        model.setIsCompensation(bonus.isCompensation())
        model.setLabel(vehicle.userName)
        return model

    @classmethod
    def _getContentId(cls, bonus):
        return [ BACKPORT_TOOLTIP_CONTENT_ID for _ in bonus.getVehicles() ]

    @classmethod
    def _createUIName(cls, bonus, isRent):
        return bonus.getName() + VEHICLE_RENT_ICON_POSTFIX if isRent else bonus.getName()


class DogTagComponentsUIPacker(BaseBonusUIPacker):

    @classmethod
    def _getBonusModel(cls):
        return IconBonusModel()

    @classmethod
    def _pack(cls, bonus):
        return [ cls._packDogTag(bonus, dogTagRecord) for dogTagRecord in bonus.getUnlockedComponents() ]

    @classmethod
    def _packDogTag(cls, bonus, dogTagRecord):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        model.setIcon(dogTagComposer.getComponentImage(dogTagRecord.componentId, dogTagRecord.grade))
        model.setLabel(dogTagComposer.getComponentTitle(dogTagRecord.componentId))
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        return [ cls._getDogTagTooltip(dogTagRecord) for dogTagRecord in bonus.getUnlockedComponents() ]

    @classmethod
    def _getContentId(cls, bonus):
        return [ BACKPORT_TOOLTIP_CONTENT_ID for _ in bonus.getUnlockedComponents() ]

    @classmethod
    def _getDogTagTooltip(cls, dogTagRecord):
        return TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.DOG_TAGS_INFO, specialArgs=[dogTagRecord.componentId])


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


class BattlePassPointsBonusPacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(bonus.getCount()))
        model.setLabel(label)
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        return [TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BATTLE_PASS_POINTS, specialArgs=[])]


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

    def getContentId(self, bonus):
        packer = self._getBonusPacker(bonus.getName())
        if packer:
            return packer.getContentId(bonus)
        _logger.error('Bonus packer for bonus type %s was not implemented yet.', bonus.getName())
        return []


class AsyncBonusUIPacker(BonusUIPacker):

    @async
    @process
    def requestData(self, bonus, callback=None):
        packer = self._getBonusPacker(bonus.getName())
        if packer:
            if packer.isAsync():
                resultList = yield packer.asyncPack(bonus)
                callback(resultList)
            else:
                callback(self.pack(bonus))
        else:
            callback([])

    @async
    @process
    def requestToolTip(self, bonus, callback=None):
        packer = self._getBonusPacker(bonus.getName())
        if packer.isAsync():
            resultList = yield packer.asyncGetToolTip(bonus)
            callback(resultList)
        else:
            callback(self.getToolTip(bonus))


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
