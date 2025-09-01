# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/ls_helpers/bonuses_formatters.py
from collections import namedtuple
from constants import PREMIUM_ENTITLEMENTS
from items.components.c11n_constants import Rarity
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import CurtailingAwardsComposer
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.server_events.awards_formatters import AWARDS_SIZES, PreformattedBonus, AwardsPacker, getDefaultFormattersMap, ItemsBonusFormatter, SimpleBonusFormatter, PremiumDaysBonusFormatter, formatCountLabel, VehiclesBonusFormatter, TokenBonusFormatter, DossierBonusFormatter, PostProcessTags, GoodiesBonusFormatter, CustomizationsBonusFormatter, BattlePassBonusFormatter, CrewBooksBonusFormatter
from gui.shared.gui_items.customization.c11n_items import ProjectionDecal, Style
from gui.shared.money import Currency
from gui.server_events.awards_formatters import BATTLE_BONUS_X5_TOKEN, LABEL_ALIGN, TEXT_FORMATTERS, TEXT_ALIGNS
from gui.shared.utils.functions import makeTooltip
from gui.shared.formatters import text_styles
from last_stand.gui.ls_gui_constants import LS_RENT_VEHICLE_TOOLTIP
from last_stand_common.last_stand_constants import ArtefactsSettings
from gui.shared.missions.packers.bonus import DOSSIER_ACHIEVEMENT_POSTFIX, DOSSIER_BADGE_POSTFIX
from gui.shared.gui_items.customization import CustomizationTooltipContext
_IMAGE_FORMAT = '.png'
C11BonusArgs = namedtuple('C11BonusArgs', ['bonus',
 'item',
 'c11Item',
 'data'])

def getImgName(path):
    return '' if path is None else path.split('/')[-1].replace(_IMAGE_FORMAT, '').replace('-', '_')


class LSItemsBonusFormatter(ItemsBonusFormatter):
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


class LSCreditsBonusFormatter(SimpleBonusFormatter):

    @classmethod
    def _getLabel(cls, bonus):
        return str(bonus.getValue())


class LSMetaPremiumDaysBonusFormatter(PremiumDaysBonusFormatter):

    def _format(self, bonus):
        return [PreformattedBonus(bonusName=bonus.getName(), userName=self._getUserName(bonus), images=self._getImages(bonus), tooltip=bonus.getTooltip(), isCompensation=self._isCompensation(bonus), label='')]


class LSVehiclesBonusFormatter(VehiclesBonusFormatter):

    @classmethod
    def _getLabel(cls, vehicle):
        return vehicle.shortUserName

    def _getItems(self, bonus):
        return sorted(bonus.getVehicles(), key=lambda v: (bonus.isRentVehicle(v[1]), v[0].descriptor.type.shortUserString))

    def _appendFormattedVehicle(self, bonus, vehicle, vehInfo):
        rentDays = bonus.getRentDays(vehInfo)
        isRent = rentDays is not None
        return PreformattedBonus(bonusName=bonus.getName(), label=self._getVehicleLabel(bonus, vehicle, vehInfo), labelFormatter=self._getLabelFormatter(bonus), userName=self._getUserName(vehicle), images=self._getImages(vehicle, isRent), isSpecial=True, specialAlias=LS_RENT_VEHICLE_TOOLTIP, specialArgs=[vehicle.intCD, True], isCompensation=self._isCompensation(bonus)) if isRent else super(LSVehiclesBonusFormatter, self)._appendFormattedVehicle(bonus, vehicle, vehInfo)


class LSVehiclesAwardsBonusFormatter(VehiclesBonusFormatter):

    @classmethod
    def _getImages(cls, vehicle, isRent=False):
        result = {AWARDS_SIZES.SMALL: vehicle.iconSmall,
         AWARDS_SIZES.BIG: vehicle.icon}
        return result

    @classmethod
    def _getLabel(cls, vehicle):
        return vehicle.userName


class LSTokenBonusFormatter(TokenBonusFormatter):
    _KEY_ICON = backport.image(R.images.last_stand.gui.maps.icons.key.key_80x80())
    _BATTLE_VEHICLE_BONUS_X5_TOKEN_PREFIX1 = 'xpx5_'
    _BATTLE_VEHICLE_BONUS_X5_TOKEN_PREFIX2 = 'expx5'

    def _getFormattedBonus(self, tokenID, token, bonus):
        formatted = super(LSTokenBonusFormatter, self)._getFormattedBonus(tokenID, token, bonus)
        if tokenID.startswith(self._BATTLE_VEHICLE_BONUS_X5_TOKEN_PREFIX1) or tokenID.lower().startswith(self._BATTLE_VEHICLE_BONUS_X5_TOKEN_PREFIX2):
            formatted = self._formatVehicleBattleX5BonusToken(BATTLE_BONUS_X5_TOKEN, token, bonus)
        elif tokenID == ArtefactsSettings.KEY_TOKEN:
            bonuseValue = bonus.getValue()
            return PreformattedBonus(bonusName=tokenID.replace(':', '_'), images={AWARDS_SIZES.SMALL: '',
             AWARDS_SIZES.BIG: self._KEY_ICON}, label=bonuseValue.get(tokenID, {}).get('count'), userName=backport.text(R.strings.last_stand_lobby.bundleView.reward.artefact_key()), tooltip=R.views.last_stand.mono.lobby.tooltips.key_tooltip())
        return formatted

    def _formatVehicleBattleX5BonusToken(self, name, token, bonus):
        if token.count <= 0:
            return None
        else:
            bonusName = bonus.TOKENS
            return PreformattedBonus(bonusName=bonusName, label=self._formatBonusLabel(token.count), labelFormatter=TEXT_FORMATTERS.get(bonusName, text_styles.stats), images={AWARDS_SIZES.SMALL: backport.image(R.images.gui.maps.icons.quests.bonuses.small.dyn(name)()),
             AWARDS_SIZES.BIG: backport.image(R.images.gui.maps.icons.quests.bonuses.big.dyn(name)())}, tooltip=makeTooltip(header=backport.text(R.strings.last_stand_lobby.bundleView.tooltip.expVehicleX5.header()), body=backport.text(R.strings.last_stand_lobby.bundleView.tooltip.expVehicleX5.body())), align=TEXT_ALIGNS.get(bonusName, LABEL_ALIGN.CENTER))

    def _formatComplexToken(self, complexToken, token, bonus):
        return PreformattedBonus(bonusName=complexToken.styleID, images={AWARDS_SIZES.SMALL: '',
         AWARDS_SIZES.BIG: ''}, label='') if complexToken.styleID == ArtefactsSettings.ARTEFACT else super(LSTokenBonusFormatter, self)._formatComplexToken(complexToken, token, bonus)


class LSBattleResultBonusFormatter(LSTokenBonusFormatter):
    _KEY_ICON = backport.image(R.images.last_stand.gui.maps.icons.key.key_80x80())


class LSDossierBonusFormatter(DossierBonusFormatter):

    def _format(self, bonus):
        result = []
        for achievement in bonus.getAchievements():
            result.append(PreformattedBonus(label=self._getUserName(achievement), bonusName=bonus.getName() + DOSSIER_ACHIEVEMENT_POSTFIX, userName=self._getUserName(achievement), images=self._getImages(achievement), isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BATTLE_STATS_ACHIEVS, specialArgs=[achievement.getBlock(), achievement.getName(), achievement.getValue()], isCompensation=self._isCompensation(bonus)))

        for badge in bonus.getBadges():
            result.append(PreformattedBonus(label=self._getUserName(badge), bonusName=bonus.getName() + DOSSIER_BADGE_POSTFIX, userName=self._getUserName(badge), images=self._getBadgeImages(badge), isSpecial=True, specialAlias=self._getBadgeTooltipAlias(), specialArgs=[badge.badgeID], isCompensation=self._isCompensation(bonus), postProcessTags=(PostProcessTags.getBadgeTag(badge),)))

        return result


class LSCustomizationsBonusFormatter(CustomizationsBonusFormatter):
    _ORDER = ('style_3d', 'attachment', 'style', 'outfit', 'paint', 'camouflage', 'projectionDecal', 'decal', 'sequence', 'emblem', 'inscription', 'insignia', 'personalNumber', 'modification')

    @classmethod
    def _getOverlayType(cls, c11item):
        if cls._getItemTypeName(c11item) == 'attachment':
            result = {}
            for size in AWARDS_SIZES.ALL():
                result[size] = c11item.rarity

            return result
        return {}

    def _createCustomizationBonus(self, bonus, item, data):
        c11nItem = bonus.getC11nItem(item)
        return PreformattedBonus(bonusName=bonus.getName(), images=self._getImages(c11nItem), userName=self._getUserName(c11nItem), label=self._formatBonusLabel(item.get('value')), labelFormatter=self._getLabelFormatter(bonus), isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD, specialArgs=CustomizationTooltipContext(itemCD=data.get('intCD')), isCompensation=self._isCompensation(bonus), align=LABEL_ALIGN.RIGHT, itemTypeName=self._getItemTypeName(c11nItem), overlayType=self._getOverlayType(c11nItem))

    def _getSubtypePriority(self, c11item):
        if self._getItemTypeName(c11item) == 'attachment':
            if c11item.rarity in Rarity.ALL:
                return Rarity.ALL.index(c11item.rarity)
            return len(Rarity.ALL) + 1
        return c11item.buyPrices.itemPrice.price

    def _format(self, bonus):
        customizations = zip(bonus.getCustomizations(), bonus.getList())
        items = [ C11BonusArgs(bonus, item, bonus.getC11nItem(item), data) for item, data in customizations ]
        sortedC11Bonuses = sorted(items, cmp=self._compareFunc)
        return [ self._createCustomizationBonus(bonusData.bonus, bonusData.item, bonusData.data) for bonusData in sortedC11Bonuses ]

    def _compareFunc(self, bonusData1, bonusData2):
        c11nItem1 = bonusData1.c11Item
        c11nItem2 = bonusData2.c11Item
        return cmp((self._getPriority(self._getItemTypeName(c11nItem1)), self._getSubtypePriority(c11nItem1)), (self._getPriority(self._getItemTypeName(c11nItem2)), self._getSubtypePriority(c11nItem2)))

    def _getPriority(self, itemTypeName):
        return self._ORDER.index(itemTypeName) if itemTypeName in self._ORDER else len(self._ORDER) + 1


class LSAwardsCustomizationsBonusFormatter(LSCustomizationsBonusFormatter):

    @classmethod
    def _getUserName(cls, c11nItem):
        if isinstance(c11nItem, Style):
            return backport.text(R.strings.last_stand_lobby.rewardWindow.description.rewardType.style(), userName=c11nItem.userName)
        return backport.text(R.strings.last_stand_lobby.rewardWindow.description.rewardType.projection_decal(), userName=c11nItem.userName) if isinstance(c11nItem, ProjectionDecal) else super(LSAwardsCustomizationsBonusFormatter, cls)._getUserName(c11nItem)


class LSGoodiesBonusFormatter(GoodiesBonusFormatter):
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
    def _getImagesRecertificationForm(cls, form):
        result = {}
        for size in AWARDS_SIZES.ALL():
            result[size] = RES_ICONS.getBonusIcon(size, form.itemTypeName)

        return result

    @classmethod
    def _getMentoringLicenses(cls, form):
        result = {}
        for size in AWARDS_SIZES.ALL():
            result[size] = RES_ICONS.getBonusIcon(size, form.itemTypeName)

        return result

    @classmethod
    def _getDemountKitImages(cls, demountKit):
        result = {}
        for size in AWARDS_SIZES.ALL():
            result[size] = RES_ICONS.getBonusIcon(size, demountKit.demountKitGuiType)

        return result


class LSBattlePassBonusFormatter(BattlePassBonusFormatter):

    @classmethod
    def _getLabel(cls, bonus):
        return bonus.getCount()


class LSCrewBooksBonusFormatter(CrewBooksBonusFormatter):

    def _getItems(self, bonus):
        return reversed(bonus.getItems())


def getLSMetaFormattersMap():
    mapping = getDefaultFormattersMap()
    mapping.update({'items': LSItemsBonusFormatter(),
     Currency.CREDITS: LSCreditsBonusFormatter(),
     'vehicles': LSVehiclesBonusFormatter(),
     'battleToken': LSTokenBonusFormatter(),
     PREMIUM_ENTITLEMENTS.BASIC: LSMetaPremiumDaysBonusFormatter(),
     PREMIUM_ENTITLEMENTS.PLUS: LSMetaPremiumDaysBonusFormatter(),
     'dossier': LSDossierBonusFormatter(),
     'goodies': LSGoodiesBonusFormatter(),
     'battlePassPoints': LSBattlePassBonusFormatter(),
     'crewBooks': LSCrewBooksBonusFormatter(),
     'customizations': LSCustomizationsBonusFormatter()})
    return mapping


def getLSMetaAwardsFormattersMap():
    mapping = getLSMetaFormattersMap()
    mapping.update({'vehicles': LSVehiclesAwardsBonusFormatter(),
     'customizations': LSAwardsCustomizationsBonusFormatter()})
    return mapping


def getLSBattleResultFormattersMap():
    mapping = getLSMetaFormattersMap()
    mapping.update({'battleToken': LSBattleResultBonusFormatter()})
    return mapping


def getLSMetaAwardFormatter(isAwardsScreen=False):
    return AwardsPacker(getLSMetaAwardsFormattersMap()) if isAwardsScreen else AwardsPacker(getLSMetaFormattersMap())


def getLSBattleResultAwardFormatter():
    return AwardsPacker(getLSBattleResultFormattersMap())


class LSBonusesAwardsComposer(CurtailingAwardsComposer):

    def _packBonus(self, bonus, size=AWARDS_SIZES.SMALL):
        return bonus

    def _packMergedBonuses(self, mergedBonuses, size=AWARDS_SIZES.SMALL):
        mergedBonusCount = len(mergedBonuses)
        imgs = {AWARDS_SIZES.SMALL: RES_ICONS.getBonusIcon(AWARDS_SIZES.SMALL, 'default'),
         AWARDS_SIZES.BIG: RES_ICONS.getBonusIcon(AWARDS_SIZES.BIG, 'default')}
        return PreformattedBonus(bonusName='default', label=backport.text(R.strings.last_stand_lobby.reward.rest(), count=mergedBonusCount), images=imgs, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.ADDITIONAL_AWARDS, specialArgs=self._getShortBonusesData(mergedBonuses, size), userName='')
