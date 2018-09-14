# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/awards_formatters.py
from collections import namedtuple
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.server_events.formatters import parseComplexToken, TOKEN_SIZES
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import getRoleUserName
from gui.shared.utils.functions import makeTooltip
from helpers import time_utils, i18n, dependency
from shared_utils import CONST_CONTAINER
from skeletons.gui.server_events import IEventsCache

class AWARDS_SIZES(CONST_CONTAINER):
    SMALL = 'small'
    BIG = 'big'


class LABEL_ALIGN(CONST_CONTAINER):
    RIGHT = 'right'
    CENTER = 'center'


AWARD_IMAGES = {AWARDS_SIZES.SMALL: {'credits': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_SMALL_CREDITS,
                      'gold': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_SMALL_GOLD,
                      'creditsFactor': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_SMALL_CREDITS,
                      'freeXP': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_SMALL_FREEEXP,
                      'freeXPFactor': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_SMALL_FREEEXP,
                      'tankmenXP': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_SMALL_TANKMENXP,
                      'tankmenXPFactor': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_SMALL_TANKMENXP,
                      'xp': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_SMALL_EXP,
                      'xpFactor': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_SMALL_EXP,
                      'dailyXPFactor': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_SMALL_FREEEXP},
 AWARDS_SIZES.BIG: {'credits': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_CREDITS,
                    'gold': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_GOLD,
                    'creditsFactor': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_CREDITS,
                    'freeXP': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_FREEXP,
                    'freeXPFactor': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_FREEXP,
                    'tankmenXP': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_TANKMENXP,
                    'tankmenXPFactor': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_TANKMENXP,
                    'xp': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_EXP,
                    'xpFactor': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_EXP,
                    'dailyXPFactor': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_FREEXP}}

def _getMultiplierFormatter(formatter):

    def wrapper(text):
        return formatter('x{}'.format(text))

    return wrapper


TEXT_FORMATTERS = {'credits': text_styles.credits,
 'gold': text_styles.gold,
 'creditsFactor': _getMultiplierFormatter(text_styles.credits),
 'freeXP': text_styles.expText,
 'freeXPFactor': _getMultiplierFormatter(text_styles.expText),
 'tankmenXP': text_styles.expText,
 'tankmenXPFactor': _getMultiplierFormatter(text_styles.expText),
 'xp': text_styles.expText,
 'xpFactor': _getMultiplierFormatter(text_styles.expText),
 'dailyXPFactor': _getMultiplierFormatter(text_styles.expText)}
TEXT_ALIGNS = {'creditsFactor': LABEL_ALIGN.RIGHT,
 'freeXPFactor': LABEL_ALIGN.RIGHT,
 'tankmenXPFactor': LABEL_ALIGN.RIGHT,
 'dailyXPFactor': LABEL_ALIGN.RIGHT,
 'xpFactor': LABEL_ALIGN.RIGHT}

def getDefaultAwardFormatter():
    simpleBonusFormatter = SimpleBonusFormatter()
    countableIntegralBonusFormatter = CountableIntegralBonusFormatter()
    tokenBonusFormatter = TokenBonusFormatter()
    return AwardsPacker({'strBonus': simpleBonusFormatter,
     'gold': simpleBonusFormatter,
     'credits': simpleBonusFormatter,
     'freeXP': simpleBonusFormatter,
     'xp': simpleBonusFormatter,
     'tankmenXP': simpleBonusFormatter,
     'xpFactor': simpleBonusFormatter,
     'creditsFactor': simpleBonusFormatter,
     'freeXPFactor': simpleBonusFormatter,
     'tankmenXPFactor': simpleBonusFormatter,
     'dailyXPFactor': simpleBonusFormatter,
     'slots': countableIntegralBonusFormatter,
     'berths': countableIntegralBonusFormatter,
     'premium': PremiumDaysBonusFormatter(),
     'vehicles': VehiclesBonusFormatter(),
     'meta': simpleBonusFormatter,
     'tokens': tokenBonusFormatter,
     'potapovToken': PotapovTokenBonusFormatter(),
     'potapovTankmen': PotapovTankmenBonusFormatter(),
     'battleToken': tokenBonusFormatter,
     'tankmen': TankmenBonusFormatter(),
     'customizations': CustomizationsBonusFormatter(),
     'goodies': GoodiesBonusFormatter(),
     'items': ItemsBonusFormatter(),
     'dossier': DossierBonusFormatter()})


def _formatCountLabel(count):
    return 'x{}'.format(count) if count > 1 else ''


_PreformattedBonus = namedtuple('_PreformattedBonus', 'label userName images tooltip labelFormatter specialArgs specialAlias isSpecial isCompensation align')

class PreformattedBonus(_PreformattedBonus):

    def getImage(self, size):
        return self.images.get(size, '')

    def getFormattedLabel(self, formatter=None):
        formatter = formatter or self.labelFormatter
        return formatter(self.label) if formatter else self.label


PreformattedBonus.__new__.__defaults__ = (None,
 None,
 None,
 None,
 None,
 None,
 None,
 False,
 False,
 LABEL_ALIGN.CENTER)

class QuestsBonusComposer(object):

    def __init__(self, awardsFormatter=None):
        self.__bonusFormatter = awardsFormatter or getDefaultAwardFormatter()

    def _packBonuses(self, preformattedBonuses, size):
        result = []
        for b in preformattedBonuses:
            result.append(self._packBonus(b, size))

        return result

    def getPreformattedBonuses(self, bonuses):
        return self.__bonusFormatter.format(bonuses)

    def getFormattedBonuses(self, bonuses, size=AWARDS_SIZES.SMALL):
        preformattedBonuses = self.getPreformattedBonuses(bonuses)
        return self._packBonuses(preformattedBonuses, size)

    def _packBonus(self, bonus, size=AWARDS_SIZES.SMALL):
        return {'label': bonus.getFormattedLabel(),
         'imgSource': bonus.getImage(size),
         'tooltip': bonus.tooltip,
         'isSpecial': bonus.isSpecial,
         'specialAlias': bonus.specialAlias,
         'specialArgs': bonus.specialArgs,
         'align': bonus.align}


class AwardsPacker(object):

    def __init__(self, formatters=None):
        self.__formatters = formatters or {}

    def format(self, bonuses):
        preformattedBonuses = []
        for b in bonuses:
            if b.isShowInGUI():
                formatter = self.__getBonusFormatter(b.getName())
                if formatter:
                    preformattedBonuses.extend(formatter.format(b))

        return preformattedBonuses

    def __getBonusFormatter(self, bonusName):
        bonusFormatter = self.__formatters.get(bonusName)
        return bonusFormatter


class AwardFormatter(object):

    def format(self, bonus):
        return self._format(bonus)

    def _format(self, bonus):
        return None


class SimpleBonusFormatter(AwardFormatter):

    def _format(self, bonus):
        return [PreformattedBonus(label=self._getLabel(bonus), userName=self._getUserName(bonus), labelFormatter=self._getLabelFormatter(bonus), images=self._getImages(bonus), tooltip=bonus.getTooltip(), align=self._getLabelAlign(bonus), isCompensation=self._isCompensation(bonus))]

    @classmethod
    def _getUserName(cls, bonus):
        return i18n.makeString(QUESTS.getBonusName(bonus.getName()))

    @classmethod
    def _getLabel(cls, bonus):
        return bonus.formatValue()

    @classmethod
    def _getLabelFormatter(cls, bonus):
        return TEXT_FORMATTERS.get(bonus.getName(), text_styles.stats)

    @classmethod
    def _getLabelAlign(cls, bonus):
        return TEXT_ALIGNS.get(bonus.getName(), LABEL_ALIGN.CENTER)

    @classmethod
    def _getImages(cls, bonus):
        result = {}
        for size in AWARDS_SIZES.ALL():
            result[size] = AWARD_IMAGES.get(size, {}).get(bonus.getName())

        return result

    @classmethod
    def _isCompensation(cls, bonus):
        return bonus.isCompensation()


class CountableIntegralBonusFormatter(SimpleBonusFormatter):

    def _format(self, bonus):
        return [PreformattedBonus(label=_formatCountLabel(bonus.getValue()), userName=self._getUserName(bonus), labelFormatter=self._getLabelFormatter(bonus), images=self._getImages(bonus), tooltip=bonus.getTooltip(), align=LABEL_ALIGN.RIGHT, isCompensation=self._isCompensation(bonus))]

    @classmethod
    def _getLabelFormatter(cls, bonus):
        return text_styles.stats

    @classmethod
    def _getImages(cls, bonus):
        result = {}
        for size in AWARDS_SIZES.ALL():
            result[size] = RES_ICONS.getBonusIcon(size, bonus.getName())

        return result


class PotapovTokenBonusFormatter(SimpleBonusFormatter):

    def _format(self, bonus):
        return [PreformattedBonus(userName=self._getUserName(bonus), label=_formatCountLabel(bonus.formatValue()), images=self._getImages('reward_sheet'), tooltip=bonus.getTooltip(), labelFormatter=self._getLabelFormatter(bonus), align=LABEL_ALIGN.RIGHT)]

    @classmethod
    def _getImages(cls, imageID):
        result = {}
        for size in AWARDS_SIZES.ALL():
            result[size] = RES_ICONS.getBonusIcon(size, imageID)

        return result


class PremiumDaysBonusFormatter(SimpleBonusFormatter):

    def _format(self, bonus):
        return [PreformattedBonus(userName=self._getUserName(bonus), images=self._getImages(bonus), tooltip=bonus.getTooltip(), isCompensation=self._isCompensation(bonus))]

    @classmethod
    def _getImages(cls, bonus):
        result = {}
        for size in AWARDS_SIZES.ALL():
            result[size] = RES_ICONS.getPremiumDaysAwardIcon(size, bonus.getValue())

        return result


class TokenBonusFormatter(SimpleBonusFormatter):
    eventsCache = dependency.descriptor(IEventsCache)

    def _format(self, bonus):
        result = []
        for tokenID, token in bonus.getTokens().iteritems():
            complexToken = parseComplexToken(tokenID)
            if complexToken.isDisplayable:
                userName = i18n.makeString(self._getUserName(complexToken.styleID))
                tooltip = makeTooltip(i18n.makeString(TOOLTIPS.QUESTS_BONUSES_TOKEN_HEADER, userName=userName), i18n.makeString(TOOLTIPS.QUESTS_BONUSES_TOKEN_BODY))
                result.append(PreformattedBonus(images=self.__getTokenImages(complexToken.styleID), label=_formatCountLabel(token.count), userName=self._getUserName(tokenID), labelFormatter=self._getLabelFormatter(bonus), tooltip=tooltip, align=LABEL_ALIGN.RIGHT, isCompensation=self._isCompensation(bonus)))

        return result

    def _getUserName(self, styleID):
        webCache = self.eventsCache.prefetcher
        return webCache.getTokenInfo(styleID)

    def __getTokenImages(self, styleID):
        result = {}
        webCache = self.eventsCache.prefetcher
        for awardSizeKey, awardSizeVlaue in AWARDS_SIZES.getIterator():
            for tokenSizeKey, tokenSizeValue in TOKEN_SIZES.getIterator():
                if awardSizeKey == tokenSizeKey:
                    result[awardSizeVlaue] = webCache.getTokenImage(styleID, tokenSizeValue)

        return result


class VehiclesBonusFormatter(SimpleBonusFormatter):

    def _format(self, bonus):
        result = []
        for vehicle, vehInfo in bonus.getVehicles():
            compensation = bonus.compensation(vehicle)
            if compensation:
                formatter = SimpleBonusFormatter()
                for bonus in compensation:
                    result.extend(formatter.format(bonus))

            tmanRoleLevel = bonus.getTmanRoleLevel(vehInfo)
            rentDays = bonus.getRentDays(vehInfo)
            rentBattles = bonus.getRentBattles(vehInfo)
            rentWins = bonus.getRentWins(vehInfo)
            if rentDays:
                rentExpiryTime = time_utils.getCurrentTimestamp()
                rentExpiryTime += rentDays * time_utils.ONE_DAY
            else:
                rentExpiryTime = 0
            result.append(PreformattedBonus(userName=self._getUserName(vehicle), images=self._getImages(rentDays or rentBattles or rentWins), isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.AWARD_VEHICLE, specialArgs=[vehicle.intCD,
             tmanRoleLevel,
             rentExpiryTime,
             rentBattles,
             rentWins], isCompensation=self._isCompensation(bonus)))

        return result

    def _getUserName(self, vehicle):
        return vehicle.userName

    @classmethod
    def _getImages(cls, rent):
        result = {}
        for size in AWARDS_SIZES.ALL():
            if rent:
                image = RES_ICONS.getRentVehicleAwardIcon(size)
            else:
                image = RES_ICONS.getVehicleAwardIcon(size)
            result[size] = image

        return result


class DossierBonusFormatter(SimpleBonusFormatter):

    def _format(self, bonus):
        result = []
        for achievement in bonus.getAchievements():
            result.append(PreformattedBonus(userName=self._getUserName(achievement), images=self._getImages(achievement), isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BATTLE_STATS_ACHIEVS, specialArgs=[achievement.getBlock(), achievement.getName(), achievement.getValue()], isCompensation=self._isCompensation(bonus)))

        return result

    @classmethod
    def _getUserName(cls, achievement):
        return achievement.getUserName()

    @classmethod
    def _getImages(cls, achievement):
        return {AWARDS_SIZES.SMALL: achievement.getSmallIcon(),
         AWARDS_SIZES.BIG: achievement.getSmallIcon()}


class TankmenBonusFormatter(SimpleBonusFormatter):

    def _format(self, bonus):
        result = []
        for group in bonus.getTankmenGroups().itervalues():
            if group['skills']:
                key = 'with_skills'
            else:
                key = 'no_skills'
            label = '#quests:bonuses/item/tankmen/%s' % key
            result.append(PreformattedBonus(userName=self._getUserName(key), images=self._getImages(bonus), tooltip=makeTooltip(TOOLTIPS.getAwardHeader(bonus.getName()), i18n.makeString(label, **group)), isCompensation=self._isCompensation(bonus)))

        return result

    @classmethod
    def _getUserName(cls, key):
        return i18n.makeString('#quests:bonusName/tankmen/%s' % key)

    @classmethod
    def _getImages(cls, bonus):
        result = {}
        for size in AWARDS_SIZES.ALL():
            result[size] = RES_ICONS.getBonusIcon(size, bonus.getName())

        return result


class PotapovTankmenBonusFormatter(SimpleBonusFormatter):

    def _format(self, bonus):
        result = []
        for tmanInfo in bonus.getTankmenData():
            if tmanInfo.isFemale:
                bonusID = 'tankwoman'
                username = i18n.makeString('#quests:bonuses/item/tankwoman')
                tooltip = makeTooltip(TOOLTIPS.AWARDITEM_TANKWOMEN_HEADER, TOOLTIPS.AWARDITEM_TANKWOMEN_BODY)
            else:
                bonusID = 'tankman'
                username = i18n.makeString('#quests:bonuses/tankmen/description', value=getRoleUserName(tmanInfo.role))
                tooltip = makeTooltip(i18n.makeString(QUESTS.BONUSES_TANKMEN_DESCRIPTION, value=getRoleUserName(tmanInfo.role)))
            result.append(PreformattedBonus(userName=username, images=self._getImages(bonusID), tooltip=tooltip))

        return result

    @classmethod
    def _getImages(cls, imageID):
        result = {}
        for size in AWARDS_SIZES.ALL():
            result[size] = RES_ICONS.getBonusIcon(size, imageID)

        return result


class CustomizationsBonusFormatter(SimpleBonusFormatter):

    def _format(self, bonus):
        result = []
        for item, data in zip(bonus.getCustomizations(), bonus.getList()):
            result.append(PreformattedBonus(images=self._getImages(item), userName=self._getUserName(item), isSpecial=True, label=_formatCountLabel(item.get('value')), labelFormatter=self._getLabelFormatter(bonus), specialAlias=TOOLTIPS_CONSTANTS.CUSTOMIZATION_ITEM, specialArgs=[ data[o] for o in bonus.INFOTIP_ARGS_ORDER ], align=LABEL_ALIGN.RIGHT, isCompensation=self._isCompensation(bonus)))

        return result

    @classmethod
    def _getImages(cls, item):
        result = {}
        for size in AWARDS_SIZES.ALL():
            result[size] = RES_ICONS.getBonusIcon(size, item.get('custType'))

        return result

    @classmethod
    def _getUserName(cls, item):
        return i18n.makeString('#quests:bonusName/%s' % item.get('custType'))


class GoodiesBonusFormatter(SimpleBonusFormatter):

    def _format(self, bonus):
        result = []
        for booster, count in bonus.getBoosters().iteritems():
            if booster is not None:
                result.append(PreformattedBonus(images=self._getImages(booster), isSpecial=True, label=_formatCountLabel(count), labelFormatter=self._getLabelFormatter(bonus), userName=self._getUserName(booster), specialAlias=TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO, specialArgs=[booster.boosterID], align=LABEL_ALIGN.RIGHT, isCompensation=self._isCompensation(bonus)))

        return result

    @classmethod
    def _getImages(cls, booster):
        result = {}
        for size in AWARDS_SIZES.ALL():
            result[size] = RES_ICONS.getBonusIcon(size, booster.boosterGuiType)

        return result

    @classmethod
    def _getUserName(cls, booster):
        return booster.fullUserName


class ItemsBonusFormatter(SimpleBonusFormatter):

    def _format(self, bonus):
        result = []
        for item, count in bonus.getItems().iteritems():
            if item is not None and count:
                if item.itemTypeID == GUI_ITEM_TYPE.EQUIPMENT and 'avatar' in item.tags:
                    alias = TOOLTIPS_CONSTANTS.BATTLE_CONSUMABLE
                elif item.itemTypeID == GUI_ITEM_TYPE.SHELL:
                    alias = TOOLTIPS_CONSTANTS.AWARD_SHELL
                else:
                    alias = TOOLTIPS_CONSTANTS.AWARD_MODULE
                result.append(PreformattedBonus(images=self._getImages(item), isSpecial=True, label=_formatCountLabel(count), labelFormatter=self._getLabelFormatter(bonus), userName=self._getUserName(item), specialAlias=alias, specialArgs=[item.intCD], align=LABEL_ALIGN.RIGHT, isCompensation=self._isCompensation(bonus)))

        return result

    @classmethod
    def _getUserName(cls, item):
        return item.userName

    @classmethod
    def _getImages(cls, item):
        result = {}
        for size in AWARDS_SIZES.ALL():
            result[size] = RES_ICONS.getBonusIcon(size, item.getGUIEmblemID())

        return result
