# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/hw_helpers/bonuses_formatters.py
from __future__ import absolute_import
from collections import namedtuple
from constants import PREMIUM_ENTITLEMENTS
from halloween.skeletons.halloween_twitch_con_controller import IHalloweenTwitchConController
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK
from helpers import dependency
from gui.server_events.recruit_helper import getRecruitInfo
from items.components.c11n_constants import Rarity
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import CurtailingAwardsComposer
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.server_events.awards_formatters import AWARDS_SIZES, PreformattedBonus, AwardsPacker, getDefaultFormattersMap, ItemsBonusFormatter, SimpleBonusFormatter, PremiumDaysBonusFormatter, formatCountLabel, VehiclesBonusFormatter, TokenBonusFormatter, DossierBonusFormatter, PostProcessTags, GoodiesBonusFormatter, CustomizationsBonusFormatter, BattlePassBonusFormatter, CrewBooksBonusFormatter, TmanTemplateBonusFormatter
from gui.shared.gui_items.customization.c11n_items import ProjectionDecal, Style
from gui.shared.money import Currency
from gui.server_events.awards_formatters import BATTLE_BONUS_X5_TOKEN, LABEL_ALIGN, TEXT_FORMATTERS, TEXT_ALIGNS
from gui.shared.utils.functions import makeTooltip
from gui.shared.formatters import text_styles
from halloween.gui.halloween_gui_constants import HALLOWEEN_CAROUSEL_VEHICLE_TOOLTIP
from halloween_common.halloween_constants import ArtefactsSettings
from gui.shared.missions.packers.bonus import DOSSIER_ACHIEVEMENT_POSTFIX, DOSSIER_BADGE_POSTFIX
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from halloween_common.halloween_constants import HWStoryChoiceSettings
_IMAGE_FORMAT = '.png'
_IMAGE_FORMAT_EXTEND = '.extend.png'
C11BonusArgs = namedtuple('C11BonusArgs', ['bonus',
 'item',
 'c11Item',
 'data'])

def getImgName(path):
    if path is None:
        return ''
    else:
        return path.split('/')[-1].replace(_IMAGE_FORMAT_EXTEND, '').replace('-', '_') if path.endswith(_IMAGE_FORMAT_EXTEND) else path.split('/')[-1].replace(_IMAGE_FORMAT, '').replace('-', '_')


def formatTokenBonusName(tokenID):
    return tokenID.replace(':', '_')


class HWItemsBonusFormatter(ItemsBonusFormatter):
    _OPTIONAL_DEVICE_TYPE = 'optionalDevice'
    _TROPHY_DEVICE_TYPE = 'trophyDevice'
    _MODERNIZED_DEVICE_TYPE = 'modernizedDevice'
    _CREW_BATTLE_BOOSTER_TYPE = 'crewBattleBooster'
    _DEVICE_BATTLE_BOOSTER_TYPE = 'deviceBattleBooster'
    _CONSUMABLE_TYPE = 'consumable'
    _SUBTYPE_ORDER = [_TROPHY_DEVICE_TYPE,
     _MODERNIZED_DEVICE_TYPE,
     _OPTIONAL_DEVICE_TYPE,
     _CREW_BATTLE_BOOSTER_TYPE,
     _DEVICE_BATTLE_BOOSTER_TYPE,
     _CONSUMABLE_TYPE]

    def _getItemSubType(self, item):
        subType = ''
        if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
            subType = self._OPTIONAL_DEVICE_TYPE
            if item.isTrophy:
                subType = self._TROPHY_DEVICE_TYPE
            elif item.isModernized:
                subType = self._MODERNIZED_DEVICE_TYPE
        elif item.itemTypeID == GUI_ITEM_TYPE.EQUIPMENT:
            subType = self._CONSUMABLE_TYPE
        elif item.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER:
            subType = self._DEVICE_BATTLE_BOOSTER_TYPE
            if item.isCrewBooster():
                subType = self._CREW_BATTLE_BOOSTER_TYPE
        return subType

    def _formatBonusLabel(self, count):
        return formatCountLabel(count)

    def _getItemSortKey(self, item):
        subtype = self._getItemSubType(item)
        if subtype in self._SUBTYPE_ORDER:
            position = self._SUBTYPE_ORDER.index(subtype)
        else:
            position = len(self._SUBTYPE_ORDER) + 1
        return (position, item)

    def _getItems(self, bonus):
        return sorted(bonus.getItems().items(), key=lambda i: self._getItemSortKey(i[0]))


class HWCreditsBonusFormatter(SimpleBonusFormatter):

    @classmethod
    def _getLabel(cls, bonus):
        return str(bonus.getValue())


class HWMetaPremiumDaysBonusFormatter(PremiumDaysBonusFormatter):

    def _format(self, bonus):
        return [PreformattedBonus(bonusName=bonus.getName(), userName=self._getUserName(bonus), images=self._getImages(bonus), tooltip=bonus.getTooltip(), isCompensation=self._isCompensation(bonus), label='')]


class HWVehiclesBonusFormatter(VehiclesBonusFormatter):

    @classmethod
    def _getLabel(cls, vehicle):
        return vehicle.shortUserName

    def _getItems(self, bonus):
        return sorted(bonus.getVehicles(), key=lambda v: bonus.isRentVehicle(v[1]))

    def _appendFormattedVehicle(self, bonus, vehicle, vehInfo):
        rentDays = bonus.getRentDays(vehInfo)
        isRent = rentDays is not None
        return PreformattedBonus(bonusName=bonus.getName(), label=self._getVehicleLabel(bonus, vehicle, vehInfo), labelFormatter=self._getLabelFormatter(bonus), userName=self._getUserName(vehicle), images=self._getImages(vehicle, isRent), isSpecial=True, specialAlias=HALLOWEEN_CAROUSEL_VEHICLE_TOOLTIP, tooltip=str(R.views.halloween.mono.lobby.tooltips.vehicle_tooltip()), specialArgs=[vehicle.intCD, True], isCompensation=self._isCompensation(bonus)) if isRent else super(HWVehiclesBonusFormatter, self)._appendFormattedVehicle(bonus, vehicle, vehInfo)


class HWVehiclesAwardsBonusFormatter(VehiclesBonusFormatter):

    @classmethod
    def _getImages(cls, vehicle, isRent=False):
        result = {AWARDS_SIZES.SMALL: vehicle.iconSmall,
         AWARDS_SIZES.BIG: vehicle.icon}
        return result

    @classmethod
    def _getLabel(cls, vehicle):
        return vehicle.userName


class HWFakeTokenMedalBonusFormatter(TokenBonusFormatter):
    _FAKE_MEDAL_ICON = backport.image(R.images.halloween.gui.maps.icons.achievement.c_48x48.hw_fake_medal())

    def _getFormattedBonus(self, tokenID, token, bonus):
        tokens = self.itemsCache.items.tokens
        hasToken1 = tokens.getTokenCount(HWStoryChoiceSettings.OPTION_1)
        hasToken2 = tokens.getTokenCount(HWStoryChoiceSettings.OPTION_2)
        medalID = 1 if hasToken1 else (2 if hasToken2 else None)
        if medalID:
            medal = HWStoryChoiceSettings.MEDAL_FORMAT.format(medalID)
            return PreformattedBonus(bonusName='dossier' + DOSSIER_ACHIEVEMENT_POSTFIX, images={AWARDS_SIZES.SMALL: backport.image(R.images.gui.maps.icons.achievement.dyn(medal)()),
             AWARDS_SIZES.BIG: backport.image(R.images.gui.maps.icons.achievement.c_80x80.dyn(medal)())}, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BATTLE_STATS_ACHIEVS, specialArgs=[ACHIEVEMENT_BLOCK.SINGLE, medal, 1])
        else:
            return PreformattedBonus(label='', bonusName=HWStoryChoiceSettings.MEDAL_BONUS_NAME, images={AWARDS_SIZES.SMALL: self._FAKE_MEDAL_ICON,
             AWARDS_SIZES.BIG: self._FAKE_MEDAL_ICON}, tooltip=makeTooltip(header=backport.text(R.strings.halloween_tooltips.bonuses.hw_fake_choice_medal.header()), body=backport.text(R.strings.halloween_tooltips.bonuses.hw_fake_choice_medal.body())))


class HWTokenBonusFormatter(TokenBonusFormatter):
    _KEY_ICON = backport.image(R.images.halloween.gui.maps.icons.key.key_80x80())
    _BATTLE_VEHICLE_BONUS_X5_TOKEN_PREFIX1 = 'xpx5_'
    _BATTLE_VEHICLE_BONUS_X5_TOKEN_PREFIX2 = 'expx5'

    def _getFormattedBonus(self, tokenID, token, bonus):
        formatted = super(HWTokenBonusFormatter, self)._getFormattedBonus(tokenID, token, bonus)
        if tokenID == ArtefactsSettings.CREW_100:
            return self._crewFormattedBonus(tokenID)
        if tokenID.startswith(self._BATTLE_VEHICLE_BONUS_X5_TOKEN_PREFIX1) or tokenID.lower().startswith(self._BATTLE_VEHICLE_BONUS_X5_TOKEN_PREFIX2):
            formatted = self._formatVehicleBattleX5BonusToken(BATTLE_BONUS_X5_TOKEN, token, bonus)
        elif tokenID == ArtefactsSettings.KEY_TOKEN:
            bonuseValue = bonus.getValue()
            return PreformattedBonus(bonusName=formatTokenBonusName(tokenID), images={AWARDS_SIZES.SMALL: '',
             AWARDS_SIZES.BIG: self._KEY_ICON}, label=str(bonuseValue.get(tokenID, {}).get('count')), userName=backport.text(R.strings.halloween_lobby.keyCard.name()), tooltip=R.views.halloween.mono.lobby.tooltips.key_tooltip())
        return formatted

    def _formatVehicleBattleX5BonusToken(self, name, token, bonus):
        if token.count <= 0:
            return None
        else:
            bonusName = bonus.TOKENS
            return PreformattedBonus(bonusName=bonusName, label=self._formatBonusLabel(token.count), labelFormatter=TEXT_FORMATTERS.get(bonusName, text_styles.stats), images={AWARDS_SIZES.SMALL: backport.image(R.images.gui.maps.icons.quests.bonuses.small.dyn(name)()),
             AWARDS_SIZES.BIG: backport.image(R.images.gui.maps.icons.quests.bonuses.big.dyn(name)())}, tooltip=makeTooltip(header=backport.text(R.strings.halloween_lobby.bundleView.tooltip.expVehicleX5.header()), body=backport.text(R.strings.halloween_lobby.bundleView.tooltip.expVehicleX5.body())), align=TEXT_ALIGNS.get(bonusName, LABEL_ALIGN.CENTER))

    def _formatComplexToken(self, complexToken, token, bonus):
        return PreformattedBonus(bonusName=complexToken.styleID, images={AWARDS_SIZES.SMALL: '',
         AWARDS_SIZES.BIG: ''}, label='') if complexToken.styleID == ArtefactsSettings.ARTEFACT else super(HWTokenBonusFormatter, self)._formatComplexToken(complexToken, token, bonus)

    def _crewFormattedBonus(self, tokenID):
        return PreformattedBonus(bonusName=tokenID.replace(':', '_'), images={AWARDS_SIZES.SMALL: '',
         AWARDS_SIZES.BIG: ''}, label='')


class HWCerfTokenBonusFormatter(TokenBonusFormatter):
    twitchConCtrl = dependency.descriptor(IHalloweenTwitchConController)

    def _getFormattedBonus(self, tokenID, token, bonus):
        recruitInfo = [ getRecruitInfo(t) for c in self.twitchConCtrl.commanders() for r in c.bonuses for t in r.getTokens() ]
        bonusIcons = R.images.gui.maps.icons.quests.bonuses
        imgName = 'tankman_twitch' if any((info and not info.isFemale() for info in recruitInfo)) else 'tankwoman_twitch'
        return PreformattedBonus(bonusName=bonus.getName(), images={AWARDS_SIZES.SMALL: backport.image(bonusIcons.dyn(AWARDS_SIZES.SMALL).dyn(imgName)()),
         AWARDS_SIZES.BIG: backport.image(bonusIcons.dyn(AWARDS_SIZES.BIG).dyn(imgName)())}, label='', tooltip=makeTooltip(header=backport.text(R.strings.halloween_lobby.bundleView.tooltip.cerfToken.header()), body=backport.text(R.strings.halloween_lobby.bundleView.tooltip.cerfToken.body())))


class HWBattleResultBonusFormatter(HWTokenBonusFormatter):
    _KEY_ICON = backport.image(R.images.halloween.gui.maps.icons.key.key_80x80())


class HWDossierBonusFormatter(DossierBonusFormatter):

    def _format(self, bonus):
        result = []
        for achievement in bonus.getAchievements():
            result.append(PreformattedBonus(label=self._getUserName(achievement), bonusName=bonus.getName() + DOSSIER_ACHIEVEMENT_POSTFIX, userName=self._getUserName(achievement), images=self._getImages(achievement), isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BATTLE_STATS_ACHIEVS, specialArgs=[achievement.getBlock(), achievement.getName(), achievement.getValue()], isCompensation=self._isCompensation(bonus)))

        for badge in bonus.getBadges():
            result.append(PreformattedBonus(label=self._getUserName(badge), bonusName=bonus.getName() + DOSSIER_BADGE_POSTFIX, userName=self._getUserName(badge), images=self._getBadgeImages(badge), isSpecial=True, specialAlias=self._getBadgeTooltipAlias(), specialArgs=[badge.badgeID], isCompensation=self._isCompensation(bonus), postProcessTags=(PostProcessTags.getBadgeTag(badge),)))

        return result


class HWCustomizationsBonusFormatter(CustomizationsBonusFormatter):
    _ORDER = ('style_3d', 'attachment', 'style', 'outfit', 'paint', 'camouflage', 'projectionDecal', 'decal', 'sequence', 'emblem', 'inscription', 'insignia', 'personalNumber', 'modification')

    def _getSubtypePriority(self, c11item):
        if self._getItemTypeName(c11item) == 'attachment':
            if c11item.rarity in Rarity.ALL:
                return Rarity.ALL.index(c11item.rarity)
            return len(Rarity.ALL) + 1
        return c11item.buyPrices.itemPrice.price

    def _format(self, bonus):
        result = []
        for item, data in zip(bonus.getCustomizations(), bonus.getList()):
            c11nItem = bonus.getC11nItem(item)
            if isinstance(c11nItem, Style) and c11nItem.isLockedOnVehicle:
                continue
            result.append(C11BonusArgs(bonus, item, c11nItem, data))

        sortedC11Bonuses = sorted(result, key=self._getPriority)
        return [ self._createCustomizationBonus(bonusData.bonus, bonusData.item, bonusData.data) for bonusData in sortedC11Bonuses ]

    def _getPriority(self, bonus):
        itemTypeName = self._getItemTypeName(bonus.c11Item)
        priority = self._ORDER.index(itemTypeName) if itemTypeName in self._ORDER else len(self._ORDER) + 1
        subPriority = self._getSubtypePriority(bonus.c11Item)
        return (priority, subPriority)


class HWAwardsCustomizationsBonusFormatter(HWCustomizationsBonusFormatter):

    @classmethod
    def _getUserName(cls, c11nItem):
        if isinstance(c11nItem, Style):
            return backport.text(R.strings.halloween_lobby.rewardWindow.description.rewardType.style(), userName=c11nItem.userName)
        return backport.text(R.strings.halloween_lobby.rewardWindow.description.rewardType.projection_decal(), userName=c11nItem.userName) if isinstance(c11nItem, ProjectionDecal) else super(HWAwardsCustomizationsBonusFormatter, cls)._getUserName(c11nItem)


class HWGoodiesBonusFormatter(GoodiesBonusFormatter):
    _BOOSTERS_ORDER = ['booster_credits', 'booster_xp', 'booster_free_xp_and_crew_xp']

    def _getBoosterSortKey(self, item):
        position = len(self._BOOSTERS_ORDER) + 1
        for subtype in self._BOOSTERS_ORDER:
            if item.boosterGuiType.startswith(subtype):
                position = self._BOOSTERS_ORDER.index(subtype)
                break

        return (position,
         not item.getIsPremium(),
         item.isExpirable,
         item)

    def _getBoosters(self, bonus):
        return sorted(bonus.getBoosters().items(), key=lambda i: self._getBoosterSortKey(i[0]))

    @classmethod
    def _getIcons(cls, item):
        result = {}
        for size in AWARDS_SIZES.ALL():
            result[size] = RES_ICONS.getBonusIcon(size, item.itemTypeName)

        return result

    @classmethod
    def _getImagesRecertificationForm(cls, form):
        return cls._getIcons(form)

    @classmethod
    def _getMentoringLicenses(cls, item):
        return cls._getIcons(item)

    @classmethod
    def _getDemountKitImages(cls, demountKit):
        result = {}
        for size in AWARDS_SIZES.ALL():
            result[size] = RES_ICONS.getBonusIcon(size, demountKit.demountKitGuiType)

        return result


class HWBattlePassBonusFormatter(BattlePassBonusFormatter):

    @classmethod
    def _getLabel(cls, bonus):
        return bonus.getCount()


class HWCrewBooksBonusFormatter(CrewBooksBonusFormatter):

    def _getItems(self, bonus):
        return reversed(bonus.getItems())


class HWTmanTemplateBonusFormatter(TmanTemplateBonusFormatter):

    def _format(self, bonus):
        result = []
        for tokenID, token in bonus.getTokens().items():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                formatted = self.__formatTmanTemplateToken(tokenID, token, bonus)
                if formatted is not None:
                    result.append(formatted)

        return result

    def __formatTmanTemplateToken(self, tokenID, _, bonus):
        recruitInfo = getRecruitInfo(tokenID)
        if recruitInfo is None:
            return
        else:
            images = {}
            iconName = recruitInfo.getDynIconName()
            for size in AWARDS_SIZES.ALL():
                images[size] = backport.image(R.images.gui.maps.icons.tankmen.icons.big.dyn(iconName)())

            nameStr = recruitInfo.getFullUserNameByNation(nationID=None)
            return PreformattedBonus(bonusName=bonus.getName(), userName=nameStr, label='', images=images, labelFormatter=self._getLabelFormatter(bonus), align=self._getLabelAlign(bonus), specialAlias=TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED, specialArgs=[tokenID], isSpecial=True)


def getHWMetaFormattersMap():
    mapping = getDefaultFormattersMap()
    mapping.update({'items': HWItemsBonusFormatter(),
     Currency.CREDITS: HWCreditsBonusFormatter(),
     'vehicles': HWVehiclesBonusFormatter(),
     'battleToken': HWTokenBonusFormatter(),
     'cerfToken': HWCerfTokenBonusFormatter(),
     HWStoryChoiceSettings.FAKE_MEDAL: HWFakeTokenMedalBonusFormatter(),
     PREMIUM_ENTITLEMENTS.BASIC: HWMetaPremiumDaysBonusFormatter(),
     PREMIUM_ENTITLEMENTS.PLUS: HWMetaPremiumDaysBonusFormatter(),
     'dossier': HWDossierBonusFormatter(),
     'goodies': HWGoodiesBonusFormatter(),
     'battlePassPoints': HWBattlePassBonusFormatter(),
     'crewBooks': HWCrewBooksBonusFormatter(),
     'customizations': HWCustomizationsBonusFormatter()})
    return mapping


def getAwardsHWMetaFormattersMap():
    mapping = getHWMetaFormattersMap()
    mapping.update({'vehicles': HWVehiclesAwardsBonusFormatter(),
     'customizations': HWAwardsCustomizationsBonusFormatter()})
    return mapping


def getHWTwitchFormattersMap():
    mapping = getHWMetaFormattersMap()
    mapping.update({'tmanToken': HWTmanTemplateBonusFormatter()})
    return mapping


def getHWBattleResultFormattersMap():
    mapping = getHWMetaFormattersMap()
    mapping.update({'battleToken': HWBattleResultBonusFormatter()})
    return mapping


def getHWMetaAwardFormatter(isAwardsScreen=False):
    return AwardsPacker(getAwardsHWMetaFormattersMap()) if isAwardsScreen else AwardsPacker(getHWMetaFormattersMap())


def getHWTwitchAwardFormatter():
    return AwardsPacker(getHWTwitchFormattersMap())


def getHWBattleResultAwardFormatter():
    return AwardsPacker(getHWBattleResultFormattersMap())


class HalloweenBonusesAwardsComposer(CurtailingAwardsComposer):

    def _packBonus(self, bonus, size=AWARDS_SIZES.SMALL):
        return bonus

    def _packMergedBonuses(self, mergedBonuses, size=AWARDS_SIZES.SMALL):
        mergedBonusCount = len(mergedBonuses)
        imgs = {AWARDS_SIZES.SMALL: RES_ICONS.getBonusIcon(AWARDS_SIZES.SMALL, 'default'),
         AWARDS_SIZES.BIG: RES_ICONS.getBonusIcon(AWARDS_SIZES.BIG, 'default')}
        return PreformattedBonus(bonusName='default', label=backport.text(R.strings.halloween_lobby.reward.rest(), count=mergedBonusCount), images=imgs, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.ADDITIONAL_AWARDS, specialArgs=self._getShortBonusesData(mergedBonuses, size), userName='')
