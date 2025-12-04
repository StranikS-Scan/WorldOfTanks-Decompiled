# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/server_events/awards_formatters.py
import logging
from constants import PREMIUM_ENTITLEMENTS, LOOTBOX_TOKEN_PREFIX
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.awards_formatters import LABEL_ALIGN, EPIC_AWARD_SIZE, getDefaultFormattersMap, TmanTemplateBonusFormatter, AwardsPacker, CountableIntegralBonusFormatter, PreformattedBonus, formatCountLabel, SimpleBonusFormatter, BlueprintBonusFormatter, AWARDS_SIZES, RentVehiclesBonusFormatter, CrewBooksEpicBonusFormatter, getCompensationEpicFormattersMap, VehiclesBonusFormatter, CustomizationsBonusFormatter, TokenBonusFormatter, ItemsEpicBonusFormatter, PremiumDaysEpicBonusFormatter
from gui.server_events.formatters import parseComplexToken
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import Currency
from helpers import dependency
from new_year.gui.shared.ny_toy_info import NewYearCurrentToyInfo
from new_year.skeletons.new_year import INewYearController
from new_year_common.items.components.ny_constants import CurrentNYConstants
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
_logger = logging.getLogger(__name__)

def getNYFormatterMap():
    mapping = getDefaultFormattersMap()
    mapping.update({'vehicles': NYRentVehiclesBonusFormatter(),
     'tmanToken': TmanTemplateBonusFormatter(),
     'blueprints': BlueprintNYBonusFormatter(),
     'customizations': CustomizationsNYBonusFormatter(),
     CurrentNYConstants.TOYS: NewYearToyFormatter(False),
     CurrentNYConstants.FILLERS: NewYearFillersBonusFormatter()})
    return mapping


def getNYEpicFormatterMap():
    simpleNYEpicBonusFormatter = SimpleNYEpicBonusFormatter()
    premiumDaysNYEpicBonusFormatter = PremiumDaysNYEpicBonusFormatter()
    mapping = getDefaultFormattersMap()
    mapping.update({Currency.GOLD: simpleNYEpicBonusFormatter,
     Currency.CREDITS: simpleNYEpicBonusFormatter,
     PREMIUM_ENTITLEMENTS.BASIC: premiumDaysNYEpicBonusFormatter,
     PREMIUM_ENTITLEMENTS.PLUS: premiumDaysNYEpicBonusFormatter,
     'vehicles': VehiclesNYEpicBonusFormatter(),
     'tmanToken': TmanTemplateNYEpicBonusFormatter(),
     'blueprints': BlueprintNYEpicBonusFormatter(),
     'crewBooks': CrewBooksNYEpicBonusFormatter(),
     'slots': SlotNYEpicBonusFormatter(),
     'items': ItemsNYEpicBonusFormatter(),
     'customizations': CustomizationsNYEpicBonusFormatter(),
     CurrentNYConstants.TOYS: NewYearToyEpicFormatter(False)})
    return mapping


def getLootboxesAutoOpenAwardsPacker():
    return AwardsPacker(getLootboxesAutoOpenFormatterMap())


def getLootboxesAutoOpenFormatterMap():
    mapping = getNYFormatterMap()
    mapping.update({CurrentNYConstants.TOYS: NewYearToyFormatter(True)})
    return mapping


def getNewYearFormattersMap():
    countableIntegralBonusFormatter = CountableIntegralBonusFormatter()
    mapping = getDefaultFormattersMap()
    mapping.update({'tokens': NewYearTokenBonusFormatter(),
     'battleToken': NewYearTokenBonusFormatter(),
     'slots': countableIntegralBonusFormatter,
     'berths': countableIntegralBonusFormatter,
     'tmanToken': TmanTemplateBonusFormatter()})
    return mapping


def getPackRentNewYearAwardPacker():
    return AwardsPacker(getNewYearFormattersMap())


def getNYAwardsPacker():
    return AwardsPacker(getNYFormatterMap())


def getNYEpicAwardsPacker():
    return AwardsPacker(getNYEpicFormatterMap())


class NewYearToyFormatter(SimpleBonusFormatter):

    def __init__(self, needJoin):
        self.__needJoin = needJoin

    def _format(self, bonus):
        result = []
        for toyID, count in bonus.getValue().iteritems():
            if count['count'] > 0:
                if self.__needJoin:
                    result.append(self._toyFormat(bonus, toyID, count['count'], count['newCount']))
                else:
                    newCount = count.get('newCount', 0)
                    result.extend([self._toyFormat(bonus, toyID, 1, 1)] * newCount)
                    result.extend([self._toyFormat(bonus, toyID, 1, 0)] * (count['count'] - newCount))

        return result

    def _toyFormat(self, bonus, toyID, count, newCount):
        return PreformattedBonus(bonusName=bonus.getName(), images=self._getImages(toyID), label=self._getToyLabel(toyID, count, newCount), labelFormatter=self._getLabelFormatter(bonus), align=self._getLabelAlign(bonus), userName=self._getUserName(toyID), specialArgs=[toyID, count], newCount=newCount)

    @classmethod
    def _getLabelAlign(cls, bonus):
        return LABEL_ALIGN.RIGHT

    @classmethod
    def _getToyLabel(cls, toyID, count, newCount):
        return formatCountLabel(count)

    @classmethod
    def _getImages(cls, toyID):
        toyInfo = NewYearCurrentToyInfo(toyID)
        result = {}
        for size in AWARDS_SIZES.ALL():
            result[size] = backport.image(toyInfo.getIcon())

        return result

    @classmethod
    def _getUserName(cls, toyID):
        toyInfo = NewYearCurrentToyInfo(toyID)
        return backport.text(toyInfo.getName())


class NewYearToyEpicFormatter(NewYearToyFormatter):

    @classmethod
    def _getLabelFormatter(cls, bonus):
        return None

    @classmethod
    def _getLabelAlign(cls, bonus):
        return LABEL_ALIGN.CENTER

    @classmethod
    def _getToyLabel(cls, toyID, count, newCount):
        toyInfo = NewYearCurrentToyInfo(toyID)
        res = R.strings.ny.reward.label.megaToy if toyInfo.isMega() else R.strings.ny.reward.label.toy
        if bool(newCount):
            res = res.new
        return backport.text(res())

    @classmethod
    def _getImages(cls, toyID):
        toyInfo = NewYearCurrentToyInfo(toyID)
        size = EPIC_AWARD_SIZE
        return {size: backport.image(toyInfo.getIcon(size=size))}


class BlueprintNYBonusFormatter(BlueprintBonusFormatter):

    def _format(self, bonuses):
        bonus = [PreformattedBonus(bonusName=bonuses.getBlueprintName(), label=self._getLabel(bonuses), userName=bonuses.formatUserNameValue(), labelFormatter=self._getLabelFormatter(bonuses), images=self._getIcons(bonuses), tooltip=bonuses.getTooltip(), align=self._getLabelAlign(bonuses), isCompensation=self._isCompensation(bonuses), specialArgs=[bonuses.getBlueprintSpecialArgs()], isSpecial=True, specialAlias=bonuses.getBlueprintSpecialAlias())]
        return bonus

    @classmethod
    def _getLabel(cls, bonuses):
        return formatCountLabel(bonuses.getCount())

    @classmethod
    def _getLabelAlign(cls, bonuses):
        return LABEL_ALIGN.RIGHT

    def _getIcons(self, bonuses):
        res = {}
        iconName = bonuses.getImageCategory()
        for size in AWARDS_SIZES.ALL():
            sizeFolderResId = R.images.gui.maps.icons.blueprints.fragment.dyn(size, None)
            if sizeFolderResId is None and not sizeFolderResId.exists():
                res[size] = ''
            iconResId = sizeFolderResId.dyn(iconName, None)
            if iconResId is None and not iconResId.exists():
                res[size] = ''
            res[size] = backport.image(iconResId())

        return res


class BlueprintNYEpicBonusFormatter(BlueprintNYBonusFormatter):

    @classmethod
    def _getLabel(cls, bonuses):
        try:
            label = bonuses.getEpicAwardLabel()
        except NameError:
            _logger.error('Wrong blueprint bonus type: %s', bonuses.getBlueprintName())
            label = ''

        return label

    @classmethod
    def _getLabelFormatter(cls, bonuses):
        return None

    @classmethod
    def _getLabelAlign(cls, bonuses):
        return LABEL_ALIGN.CENTER

    def _getIcons(self, item):
        size = EPIC_AWARD_SIZE
        image = backport.image(R.images.gui.maps.icons.blueprints.fragment.s360x270.dyn(item.getImageCategory())())
        return {size: image}


class CrewBooksNYEpicBonusFormatter(CrewBooksEpicBonusFormatter):

    @classmethod
    def _getLabel(cls, count):
        if count == 1:
            label = backport.text(R.strings.ny.reward.label.crewbook())
        else:
            label = backport.text(R.strings.ny.reward.label.crewbooks(), count=count)
        return label

    @classmethod
    def _getLabelFormatter(cls, bonus):
        return None

    @classmethod
    def _getLabelAlign(cls, count):
        return LABEL_ALIGN.CENTER


class NYRentVehiclesBonusFormatter(RentVehiclesBonusFormatter):

    @classmethod
    def _getLabel(cls, vehicle):
        return vehicle.userName


class NewYearFillersBonusFormatter(CountableIntegralBonusFormatter):

    def _format(self, bonus):
        return [PreformattedBonus(bonusName=bonus.getName(), label=formatCountLabel(bonus.getValue()), userName=self._getUserName(bonus), labelFormatter=self._getLabelFormatter(bonus), images=self._getImages(bonus), isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.NY_FILLERS, specialArgs=[])]


class PremiumDaysNYEpicBonusFormatter(PremiumDaysEpicBonusFormatter):

    @classmethod
    def _getLabel(cls, bonus):
        count = bonus.getValue()
        if count == 1:
            label = backport.text(R.strings.ny.reward.label.premiumDay())
        else:
            label = backport.text(R.strings.ny.reward.label.premiumDays(), count=count)
        return label


class SimpleNYEpicBonusFormatter(SimpleBonusFormatter):

    @classmethod
    def _getLabelFormatter(cls, bonus):
        return None

    @classmethod
    def _getLabelAlign(cls, bonus):
        return LABEL_ALIGN.CENTER

    @classmethod
    def _getImages(cls, bonus):
        size = EPIC_AWARD_SIZE
        return {size: RES_ICONS.getBonusIcon(size, bonus.getName())}

    @classmethod
    def _getCompensationFormattersMap(cls):
        return getCompensationEpicFormattersMap()


class VehiclesNYEpicBonusFormatter(VehiclesBonusFormatter):

    @classmethod
    def _getLabel(cls, vehicle):
        return vehicle.shortUserName

    @classmethod
    def _getLabelFormatter(cls, bonus):
        return None

    @classmethod
    def _getImages(cls, vehicle, isRent=False):
        size = EPIC_AWARD_SIZE
        return {size: RES_ICONS.getVehicleAwardIcon(size)}

    @classmethod
    def _getCompensationFormatter(cls):
        return SimpleNYEpicBonusFormatter()


class CustomizationsNYBonusFormatter(CustomizationsBonusFormatter):

    @classmethod
    def _getImage(cls, c11nItem, size):
        iconName = c11nItem.itemTypeName
        return RES_ICONS.getBonusIcon(size, iconName)

    def _makePostprocessTags(self, c11nItem):
        return c11nItem.itemTypeName


class CustomizationsNYEpicBonusFormatter(CustomizationsBonusFormatter):

    @classmethod
    def _formatBonusLabel(cls, c11nItem, count):
        label = c11nItem.userName
        if c11nItem.itemTypeName == 'style':
            res = R.strings.ny.reward.label.style.c_3d if c11nItem.is3D else R.strings.ny.reward.label.style.c_2d
            label = backport.text(res(), name=label)
        return label

    @classmethod
    def _getLabelFormatter(cls, bonus):
        return None

    @classmethod
    def _getImages(cls, c11nItem):
        size = EPIC_AWARD_SIZE
        result = {size: cls._getImage(c11nItem, size)}
        return result


class TmanTemplateNYEpicBonusFormatter(TmanTemplateBonusFormatter):

    @classmethod
    def _getImages(cls, imageName):
        size = EPIC_AWARD_SIZE
        return {size: RES_ICONS.getBonusIcon(size, imageName)}


class NewYearTokenBonusFormatter(TokenBonusFormatter):
    _nyController = dependency.descriptor(INewYearController)

    def _format(self, bonus):
        result = []
        for tokenID, token in bonus.getTokens().iteritems():
            complexToken = parseComplexToken(tokenID)
            if complexToken.isDisplayable:
                result.append(self._formatComplexToken(complexToken, token, bonus))
            if tokenID.startswith(LOOTBOX_TOKEN_PREFIX):
                formatted = self._formatLootBoxToken(tokenID, token, bonus)
                if formatted is None:
                    _logger.error('Received wrong loot box token from server: %s', tokenID)
                else:
                    result.append(formatted)

        return result


class SlotNYEpicBonusFormatter(CountableIntegralBonusFormatter):

    @classmethod
    def _getLabel(cls, bonus):
        count = bonus.getValue()
        if count == 1:
            label = backport.text(R.strings.quests.bonusName.slots())
        else:
            label = backport.text(R.strings.ny.reward.label.slots(), count=count)
        return label

    @classmethod
    def _getLabelFormatter(cls, bonus):
        return None

    @classmethod
    def _getLabelAlign(cls, bonus):
        return LABEL_ALIGN.CENTER

    @classmethod
    def _getImages(cls, bonus):
        size = EPIC_AWARD_SIZE
        return {size: RES_ICONS.getBonusIcon(size, bonus.getName())}


class ItemsNYEpicBonusFormatter(ItemsEpicBonusFormatter):

    @classmethod
    def _formatBonusLabel(cls, item, count):
        label = ''
        if item.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER:
            if count == 1:
                label = backport.text(R.strings.ny.reward.label.booster())
            else:
                label = backport.text(R.strings.ny.reward.label.boosters(), count=count)
        elif item.itemTypeID == GUI_ITEM_TYPE.EQUIPMENT:
            if count == 1:
                label = item.descriptor.i18n.shortString
            else:
                res = R.strings.ny.reward.label.equipment.dyn(item.name)
                if res.exists():
                    label = backport.text(res(), count=count)
        return label

    @classmethod
    def _getLabelFormatter(cls, bonus):
        return None

    @classmethod
    def _getImages(cls, item):
        size = EPIC_AWARD_SIZE
        name = getNYItemBonusResName(item, EPIC_AWARD_SIZE)
        return {size: RES_ICONS.getBonusIcon(size, name)}


def getNYItemBonusResName(item, size):
    nyItemBonusResPostfix = '_ny'
    name = item.getGUIEmblemID()
    if R.images.gui.maps.icons.quests.bonuses.dyn(size).dyn(name + nyItemBonusResPostfix).exists():
        name += nyItemBonusResPostfix
    return name
