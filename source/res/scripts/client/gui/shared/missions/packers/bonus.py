# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/missions/packers/bonus.py
import logging
import typing
import constants
from adisp import adisp_async, adisp_process
from collections_common import g_collectionsRelatedItems
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
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
from gui.server_events.awards_formatters import AWARDS_SIZES, BATTLE_BONUS_X5_TOKEN, GOLD_MISSION, ItemsBonusFormatter, TOKEN_SIZES, TokenBonusFormatter, formatCountLabel, CREW_BONUS_X3_TOKEN
from gui.server_events.formatters import COMPLEX_TOKEN, TokenComplex, parseComplexToken
from gui.shared.gui_items.crew_skin import localizedFullName
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.gui_items.customization.c11n_items import Style
from gui.shared.money import Currency
from gui.shared.utils.functions import makeTooltip
from helpers import dependency, i18n, time_utils
from shared_utils import first
from skeletons.gui.game_control import ICollectionsSystemController
from skeletons.gui.server_events import IEventsCache
DOSSIER_BADGE_ICON_PREFIX = 'badge_'
DOSSIER_ACHIEVEMENT_POSTFIX = '_achievement'
DOSSIER_BADGE_POSTFIX = '_badge'
VEHICLE_RENT_ICON_POSTFIX = '_rent'
BACKPORT_TOOLTIP_CONTENT_ID = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()
if typing.TYPE_CHECKING:
    from typing import Dict, List, Callable
    from frameworks.wulf.view.array import Array
    from gui.goodies.goodie_items import BoosterUICommon, RecertificationForm, Booster
    from gui.server_events.bonuses import CustomizationsBonus, CrewSkinsBonus, TokensBonus, SimpleBonus, ItemsBonus, DossierBonus, VehicleBlueprintBonus, CrewBooksBonus, GoodiesBonus, TankmenBonus, VehiclesBonus, DogTagComponentBonus, BattlePassPointsBonus, CurrenciesBonus
    from gui.shared.gui_items.fitting_item import FittingItem
    from gui.shared.gui_items.Vehicle import Vehicle
_logger = logging.getLogger(__name__)

def getDefaultBonusPackersMap():
    simpleBonusPacker = SimpleBonusUIPacker()
    tokenBonusPacker = TokenBonusUIPacker()
    blueprintBonusPacker = BlueprintBonusUIPacker()
    wotPlusBonusPacker = WoTPlusBonusPacker()
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
     'lootBox': tokenBonusPacker,
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
     Currency.EQUIP_COIN: simpleBonusPacker,
     constants.PREMIUM_ENTITLEMENTS.BASIC: simpleBonusPacker,
     constants.PREMIUM_ENTITLEMENTS.PLUS: simpleBonusPacker,
     'currencies': CurrenciesBonusUIPacker,
     constants.WoTPlusBonusType.GOLD_BANK: wotPlusBonusPacker,
     constants.WoTPlusBonusType.IDLE_CREW_XP: wotPlusBonusPacker,
     constants.WoTPlusBonusType.EXCLUDED_MAP: wotPlusBonusPacker,
     constants.WoTPlusBonusType.FREE_EQUIPMENT_DEMOUNTING: wotPlusBonusPacker,
     constants.WoTPlusBonusType.EXCLUSIVE_VEHICLE: wotPlusBonusPacker,
     constants.WoTPlusBonusType.ATTENDANCE_REWARD: wotPlusBonusPacker,
     constants.WoTPlusBonusType.BATTLE_BONUSES: wotPlusBonusPacker,
     constants.WoTPlusBonusType.BADGES: wotPlusBonusPacker,
     constants.WoTPlusBonusType.ADDITIONAL_BONUSES: wotPlusBonusPacker,
     constants.WoTPlusBonusType.OPTIONAL_DEVICES_ASSISTANT: wotPlusBonusPacker}


def getLocalizedBonusName(name):
    labelStr = None
    localizedLabel = R.strings.quests.bonusName.dyn(name)
    if localizedLabel.exists():
        labelStr = backport.text(localizedLabel())
    else:
        _logger.warning("Localized text for the 'additional rewards tooltip' label for %s reward was not found.", name)
    return labelStr


class BaseBonusUIPacker(object):
    __collections = dependency.descriptor(ICollectionsSystemController)

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

    @classmethod
    def _isCollectionItem(cls, collectionItemID):
        return cls.__collections.isEnabled() and collectionItemID in g_collectionsRelatedItems.items


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
    _BATTLE_BONUS_X5_TOKEN_SOURCE = 'bonus_battle_task'
    _CREW_BONUS_X3_TOKEN_SOURCE = 'crew_bonus_x3'
    _GOLD_MISSION_TOKEN_SOURCE = 'gold_mission'

    @classmethod
    def _pack(cls, bonus):
        bonusTokens = bonus.getTokens()
        result = []
        bonusPackers = cls._getTokenBonusPackers()
        for tokenID, token in bonusTokens.iteritems():
            complexToken = parseComplexToken(tokenID)
            tokenType = cls._getTokenBonusType(tokenID, complexToken)
            specialPacker = bonusPackers.get(tokenType)
            if specialPacker is None:
                continue
            packedBonus = cls._packToken(specialPacker, bonus, complexToken, token)
            if packedBonus is not None:
                result.append(packedBonus)

        return result

    @classmethod
    def _getToolTip(cls, bonus):
        bonusTokens = bonus.getTokens()
        tooltipPackers = cls._getTooltipsPackers()
        result = []
        for tokenID, token in bonusTokens.iteritems():
            if not cls._isTokenForTooltipValid(tokenID):
                continue
            complexToken = parseComplexToken(tokenID)
            tokenType = cls._getTokenBonusType(tokenID, complexToken)
            result.append(tooltipPackers.get(tokenType)(complexToken, token))

        return result

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        for tokenID in bonus.getTokens():
            if not cls._isTokenForTooltipValid(tokenID):
                continue
            name = tokenID.split(':')[0]
            if name.endswith(GOLD_MISSION):
                result.append(R.views.lobby.battle_pass.tooltips.BattlePassGoldMissionTooltipView())
            result.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return result

    @classmethod
    def _isTokenForTooltipValid(cls, tokenID):
        complexToken = parseComplexToken(tokenID)
        tokenType = cls._getTokenBonusType(tokenID, complexToken)
        if tokenType == '':
            return False
        else:
            tooltipPacker = cls._getTooltipsPackers().get(tokenType)
            if tooltipPacker is None:
                _logger.warning('There is not a tooltip creator for a token bonus %s', tokenType)
                return False
            return True

    @classmethod
    def _getTokenBonusPackers(cls):
        return {BATTLE_BONUS_X5_TOKEN: cls.__packBonusQuestToken(BATTLE_BONUS_X5_TOKEN),
         CREW_BONUS_X3_TOKEN: cls.__packBonusQuestToken(CREW_BONUS_X3_TOKEN),
         COMPLEX_TOKEN: cls.__packComplexToken,
         YEAR_POINTS_TOKEN: cls.__packRankedToken,
         GOLD_MISSION: cls.__packGoldMissionToken}

    @classmethod
    def _packToken(cls, bonusPacker, bonus, *args):
        model = TokenBonusModel()
        cls._packCommon(bonus, model)
        return bonusPacker(model, bonus, *args)

    @classmethod
    def _getTokenBonusType(cls, tokenID, complexToken):
        if complexToken.isDisplayable:
            return COMPLEX_TOKEN
        if tokenID.startswith(BATTLE_BONUS_X5_TOKEN):
            return BATTLE_BONUS_X5_TOKEN
        if tokenID.startswith(CREW_BONUS_X3_TOKEN):
            return CREW_BONUS_X3_TOKEN
        if tokenID.startswith(YEAR_POINTS_TOKEN):
            return YEAR_POINTS_TOKEN
        return GOLD_MISSION if tokenID.split(':')[0].endswith(GOLD_MISSION) else ''

    @classmethod
    def _getTooltipsPackers(cls):
        return {BATTLE_BONUS_X5_TOKEN: cls.__getBonusFactorTooltip(BATTLE_BONUS_X5_TOKEN),
         CREW_BONUS_X3_TOKEN: cls.__getBonusFactorTooltip(CREW_BONUS_X3_TOKEN),
         COMPLEX_TOKEN: cls.__getComplexToolTip,
         YEAR_POINTS_TOKEN: cls.__getRankedPointToolTip,
         GOLD_MISSION: cls.__getGoldMissionTooltip}

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
    def __packBonusQuestToken(cls, name):

        def inner(model, bonus, *args):
            model.setName(name)
            model.setValue(str(bonus.getCount()))
            model.setIconSmall(backport.image(R.images.gui.maps.icons.quests.bonuses.dyn(AWARDS_SIZES.SMALL).dyn(name)()))
            model.setIconBig(backport.image(R.images.gui.maps.icons.quests.bonuses.dyn(AWARDS_SIZES.BIG).dyn(name)()))
            return model

        return inner

    @classmethod
    def __packGoldMissionToken(cls, model, bonus, *args):
        name = cls._GOLD_MISSION_TOKEN_SOURCE
        model.setName(name)
        model.setIconSmall(backport.image(R.images.gui.maps.icons.quests.bonuses.dyn(AWARDS_SIZES.SMALL).dyn(name)()))
        model.setIconBig(backport.image(R.images.gui.maps.icons.quests.bonuses.dyn(AWARDS_SIZES.BIG).dyn(name)()))
        return model

    @staticmethod
    def __getBonusFactorTooltip(name):

        def inner(*_):
            return createTooltipData(TokenBonusFormatter.getBonusFactorTooltip(name))

        return inner

    @classmethod
    def __getComplexToolTip(cls, complexToken, *_):
        webCache = cls._eventsCache.prefetcher
        userName = i18n.makeString(webCache.getTokenInfo(complexToken.styleID))
        description = webCache.getTokenDetailedInfo(complexToken.styleID)
        if description is None:
            description = backport.text(R.strings.tooltips.quests.bonuses.token.body())
        tooltip = makeTooltip(userName, description if description else None)
        return createTooltipData(tooltip)

    @classmethod
    def __getRankedPointToolTip(cls, *_):
        return createTooltipData(makeTooltip(header=backport.text(R.strings.tooltips.rankedBattleView.scorePoint.header()), body=backport.text(R.strings.tooltips.rankedBattleView.scorePoint.body())))

    @classmethod
    def __getGoldMissionTooltip(cls, complexToken, token):
        return TooltipData(tooltip=None, isSpecial=True, specialAlias=None, specialArgs=[token.id])


class ItemBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        bonusItems = bonus.getItems()
        result = []
        for item, count in sorted(bonusItems.iteritems(), key=cls._itemsSortFunction):
            if item is None or not count:
                continue
            result.append(cls._packSingleBonus(bonus, item, count))

        return result

    @staticmethod
    def _itemsSortFunction(item):
        return item[0]

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

        for form, count in sorted(bonus.getRecertificationForms().iteritems()):
            if form is None or not count:
                continue
            result.append(cls._packRecertificationFormsBonus(bonus, form, count))

        return result

    @classmethod
    def _packSingleBoosterBonus(cls, bonus, booster, count):
        return cls._packIconBonusModel(bonus, booster.getFullNameForResource(), count, booster.userName)

    @classmethod
    def _packSingleDemountKitBonus(cls, bonus, demountkit, count):
        return cls._packIconBonusModel(bonus, demountkit.demountKitGuiType, count, demountkit.userName)

    @classmethod
    def _packRecertificationFormsBonus(cls, bonus, form, count):
        return cls._packIconBonusModel(bonus, form.itemTypeName, count, form.userName)

    @classmethod
    def _packIconBonusModel(cls, bonus, icon, count, label):
        model = IconBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(count))
        model.setIcon(icon)
        model.setLabel(label)
        model.setTooltipContentId(str(cls.getContentId(bonus)[0]))
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for booster, _ in sorted(bonus.getBoosters().iteritems(), key=lambda b: b[0].boosterID):
            tooltipData.append(TooltipData(tooltip=TOOLTIPS_CONSTANTS.SHOP_BOOSTER, isSpecial=False, specialAlias=None, specialArgs=[booster.boosterID], isWulfTooltip=True))

        for demountkit in sorted(bonus.getDemountKits().iterkeys()):
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.AWARD_DEMOUNT_KIT, specialArgs=[demountkit.intCD]))

        for form in sorted(bonus.getRecertificationForms().iterkeys()):
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.EPIC_BATTLE_RECERTIFICATION_FORM_TOOLTIP, specialArgs=[form.intCD]))

        return tooltipData

    @classmethod
    def _getContentId(cls, bonus):
        tooltipData = []
        for _ in sorted(bonus.getBoosters().iterkeys(), key=lambda b: b.boosterID):
            tooltipData.append(BACKPORT_TOOLTIP_CONTENT_ID)

        for _ in sorted(bonus.getDemountKits().iterkeys()):
            tooltipData.append(BACKPORT_TOOLTIP_CONTENT_ID)

        for _ in sorted(bonus.getRecertificationForms().iterkeys()):
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


class ExtendedBlueprintBonusUIPacker(BlueprintBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        models = super(ExtendedBlueprintBonusUIPacker, cls)._pack(bonus)
        model = first(models)
        if model:
            model.setLabel(bonus.getLabel())
        return models


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
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(item.get('value', 0)))
        model.setIcon(str(bonus.getC11nItem(item).itemTypeName))
        model.setLabel(label)
        return model

    @classmethod
    def _getBonusModel(cls):
        return IconBonusModel()

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
        result += cls._packAchievements(bonus)
        result += cls._packBadges(bonus)
        return result

    @classmethod
    def _packAchievements(cls, bonus):
        return [ cls._packSingleAchievement(achievement, bonus) for achievement in bonus.getAchievements() ]

    @classmethod
    def _packSingleAchievement(cls, achievement, bonus):
        dossierIconName = achievement.getName()
        dossierValue = achievement.getValue()
        dossierLabel = achievement.getUserName()
        return cls._packSingleBonus(bonus, dossierIconName, DOSSIER_ACHIEVEMENT_POSTFIX, dossierValue, dossierLabel)

    @classmethod
    def _packBadges(cls, bonus):
        result = []
        for badge in bonus.getBadges():
            dossierIconName = DOSSIER_BADGE_ICON_PREFIX + str(badge.badgeID)
            dossierValue = 0
            dossierLabel = badge.getUserName()
            result.append(cls._packSingleBonus(bonus, dossierIconName, DOSSIER_BADGE_POSTFIX, dossierValue, dossierLabel))

        return result

    @classmethod
    def _packSingleBonus(cls, bonus, dossierIconName, dossierNamePostfix, dossierValue, dossierLabel, recordName=None):
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
        tooltipData += cls._getAchievementTooltip(bonus)
        tooltipData += cls._getBadgeTooltip(bonus)
        return tooltipData

    @classmethod
    def _getAchievementTooltip(cls, bonus):
        tooltipData = []
        for achievement in bonus.getAchievements():
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BATTLE_STATS_ACHIEVS, specialArgs=[achievement.getBlock(), achievement.getName(), achievement.getValue()]))

        return tooltipData

    @classmethod
    def _getBadgeTooltip(cls, bonus):
        tooltipData = []
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
    _SPECIAL_ALIAS = TOOLTIPS_CONSTANTS.AWARD_VEHICLE

    @classmethod
    def _pack(cls, bonus):
        return cls._packVehicles(bonus, bonus.getVehicles())

    @classmethod
    def _getToolTip(cls, bonus):
        return cls._packTooltips(bonus, bonus.getVehicles())

    @classmethod
    def _getCompensation(cls, vehicle, bonus):
        return bonus.compensation(vehicle, bonus)

    @classmethod
    def _packVehicles(cls, bonus, vehicles):
        packedVehicles = []
        for vehicle, vehInfo in vehicles:
            compensation = cls._getCompensation(vehicle, bonus)
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
            compensation = cls._getCompensation(vehicle, bonus)
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
        isSeniority = False
        return TooltipData(tooltip=None, isSpecial=True, specialAlias=cls._SPECIAL_ALIAS, specialArgs=[vehicle.intCD,
         tmanRoleLevel,
         rentExpiryTime,
         rentBattles,
         rentWins,
         rentSeason,
         rentCycle,
         isSeniority])

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
        model.setLabel(cls._getLabel(vehicle))
        return model

    @classmethod
    def _getContentId(cls, bonus):
        return [ BACKPORT_TOOLTIP_CONTENT_ID for _ in bonus.getVehicles() ]

    @classmethod
    def _createUIName(cls, bonus, isRent):
        return bonus.getName() + VEHICLE_RENT_ICON_POSTFIX if isRent else bonus.getName()

    @classmethod
    def _getLabel(cls, vehicle):
        return vehicle.userName


class DailyMissionsVehiclesBonusUIPacker(VehiclesBonusUIPacker):
    _SPECIAL_ALIAS = TOOLTIPS_CONSTANTS.EXTENDED_AWARD_VEHICLE

    @classmethod
    def _packTooltip(cls, bonus, vehicle, vehInfo):
        tooltipData = super(DailyMissionsVehiclesBonusUIPacker, cls)._packTooltip(bonus, vehicle, vehInfo)
        tooltipData.specialArgs.extend([bonus.getTmanRoleLevel(vehInfo) > 0, False, False])
        return tooltipData

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vehInfo, isRent, vehicle):
        model = super(DailyMissionsVehiclesBonusUIPacker, cls)._packVehicleBonusModel(bonus, vehInfo, isRent, vehicle)
        model.setValue(cls._getLabel(vehicle))
        return model

    @classmethod
    def _getLabel(cls, vehicle):
        return vehicle.shortUserName


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
        return model


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

    @adisp_async
    @adisp_process
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

    @adisp_async
    @adisp_process
    def requestToolTip(self, bonus, callback=None):
        packer = self._getBonusPacker(bonus.getName())
        if packer.isAsync():
            resultList = yield packer.asyncGetToolTip(bonus)
            callback(resultList)
        else:
            callback(self.getToolTip(bonus))


class WoTPlusBonusPacker(SimpleBonusUIPacker):

    @classmethod
    def _getBonusModel(cls):
        return IconBonusModel()

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = cls._getBonusModel()
        model.setName(bonus.getName())
        model.setLabel(label)
        model.setIcon(bonus.getIcon())
        return model


def getDefaultBonusPacker():
    return BonusUIPacker(getDefaultBonusPackersMap())


def getDailyMissionsBonusPacker():
    return BonusUIPacker(getDailyMissionsMapping())


def getDailyMissionsMapping():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'vehicles': DailyMissionsVehiclesBonusUIPacker()})
    return mapping


def packMissionsBonusModelAndTooltipData(bonuses, packer, model, tooltipData=None, sort=None):
    bonusIndexTotal = 0
    if tooltipData is not None:
        bonusIndexTotal = len(tooltipData)
    bonusTooltipList = []
    hasSort = sort is not None and callable(sort)
    for bonus in bonuses:
        if bonus.isShowInGUI():
            bonusList = packer.pack(bonus)
            if bonusList and tooltipData is not None:
                bonusTooltipList = packer.getToolTip(bonus)
            if bonusList and hasSort:
                if bonusTooltipList:
                    sortMethod = sort(bonus.getName())
                    merged = zip(bonusList, bonusTooltipList)
                    merged = sorted(merged, key=lambda x: x[0], cmp=sortMethod)
                    bonusList, bonusTooltipList = zip(*merged)
                    bonusList = list(bonusList)
                    bonusTooltipList = list(bonusTooltipList)
                else:
                    bonusList = sorted(bonusList, cmp=sort(bonus.getName()))
            for bonusIndex, item in enumerate(bonusList):
                item.setIndex(bonusIndexTotal)
                tooltipIdx = str(bonusIndexTotal)
                if hasattr(item, 'setTooltipId'):
                    item.setTooltipId(tooltipIdx)
                model.addViewModel(item)
                if tooltipData is not None:
                    tooltipData[tooltipIdx] = bonusTooltipList[bonusIndex]
                bonusIndexTotal += 1

    return
