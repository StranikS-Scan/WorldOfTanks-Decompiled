# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/lunar_ny/lunar_ny_bonuses_packers.py
from copy import deepcopy
import typing
from dossiers2.ui.achievements import ACHIEVEMENT_TYPE, ACHIEVEMENT_BLOCK
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.gen import R
from gui.impl.backport import TooltipData
from gui.impl.gen.view_models.views.lobby.lunar_ny.reward_view_model import RewardViewModel, RewardType
from gui.server_events.bonuses import getNonQuestBonuses, mergeBonuses
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.missions.packers.bonus import getDefaultBonusPackersMap, BaseBonusUIPacker, BACKPORT_TOOLTIP_CONTENT_ID, DossierBonusUIPacker, DOSSIER_ACHIEVEMENT_POSTFIX
from gui.shared.money import Currency
from gui.shared.utils.functions import getStringResourceFromPath
from items import lunar_ny
from items.components.lunar_ny_constants import CharmType
from lunar_ny.lunar_ny_constants import ENVELOPE_ENTITLEMENT_CODE_TO_TYPE, CHARM_TYPE_BY_TYPE_NAME
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus, CustomizationsBonus, DossierBonus, CharmsBonus, EntitlementBonus
    from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

def getLunarNYBonusPackerMap():
    mapping = {bKey:SimpleLunarNYBonusPacker() for bKey in getDefaultBonusPackersMap()}
    mapping.update({Currency.CREDITS: CurrencyLunarNYBonusPacker(),
     Currency.CRYSTAL: CurrencyLunarNYBonusPacker(),
     Currency.GOLD: CurrencyLunarNYBonusPacker(),
     Currency.BPCOIN: CurrencyLunarNYBonusPacker(),
     'customizations': CustomizationLunarNYBonusPacker(),
     'dossier': DossierLunarNYBonusPacker(),
     'charms': CharmLunarNYBonusPacker(),
     'tokens': EmptyLunarNYBonusPacker(),
     'battleToken': EmptyLunarNYBonusPacker(),
     'entitlements': EnvelopesLunarNYBonusPacker()})
    return mapping


def getLunarNYProgressionPackerMap():
    mapping = getLunarNYBonusPackerMap()
    mapping.update({'dossier': DossierLunarNYProgressionBonusPacker()})
    return mapping


def getLunarNYProgressionAwardPackerMap():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'dossier': DossierLunarNYProgressionAwardPacker()})
    return mapping


class EmptyLunarNYBonusPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return []

    @classmethod
    def _getToolTip(cls, bonus):
        return []

    @classmethod
    def _getContentId(cls, bonus):
        return []


class SimpleLunarNYBonusPacker(BaseBonusUIPacker):

    def packToolTip(self, bonusModel, index, contentId):
        bonusModel.setTooltipContentID(contentId)
        bonusModel.setTooltipID(index)

    @classmethod
    def _pack(cls, bonus):
        model = RewardViewModel()
        model.setRewardType(RewardType.SIMPLE)
        model.setRewardID(bonus.getName())
        model.setCount(1)
        return [model]

    @classmethod
    def _packCommon(cls, bonus, model):
        pass


class CurrencyLunarNYBonusPacker(SimpleLunarNYBonusPacker):

    @classmethod
    def _pack(cls, bonus):
        model = RewardViewModel()
        model.setRewardType(RewardType.CURRENCY)
        model.setRewardID(bonus.getName())
        model.setCount(bonus.getValue())
        return [model]


class CustomizationLunarNYBonusPacker(SimpleLunarNYBonusPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for item in bonus.getCustomizations():
            if item is None:
                continue
            result.append(cls.__packSingleBonus(bonus, item))

        return result

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
        return [BACKPORT_TOOLTIP_CONTENT_ID] * len([ b for b in bonus.getCustomizations() if b is not None ])

    @classmethod
    def __packSingleBonus(cls, bonus, item):
        itemCustomization = bonus.getC11nItem(item)
        model = RewardViewModel()
        model.setCount(item.get('value', 0))
        model.setRewardID(str(item.get('id', 0)))
        model.setRewardType(cls.__getRewardType(item.get('custType', '')))
        model.setName(getStringResourceFromPath(itemCustomization.descriptor.userKey)())
        return model

    @classmethod
    def __getRewardType(cls, itemTypeName):
        return RewardType.CUSTOMIZATIONDECAL if itemTypeName == 'projection_decal' else RewardType.SIMPLE


class DossierLunarNYBonusPacker(SimpleLunarNYBonusPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for badge in bonus.getBadges():
            result.append(cls.__packSingleBonus('badge_{}'.format(badge.badgeID), RewardType.BADGE, 1))

        for achievement in bonus.getAchievements():
            result.append(cls.__packSingleBonus(achievement.getIconName(), RewardType.ACHIEVEMENT, 1 if achievement.getType() == ACHIEVEMENT_TYPE.SINGLE else achievement.getValue()))

        return result

    @classmethod
    def __packSingleBonus(cls, dossierID, rewardType, count):
        model = RewardViewModel()
        model.setCount(count)
        model.setRewardID(dossierID)
        model.setRewardType(rewardType)
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = cls.__getBadgeToolTipData(bonus)
        tooltipData.extend(cls._getAchievementToolTipData(bonus))
        return tooltipData

    @classmethod
    def _getContentId(cls, bonus):
        return [BACKPORT_TOOLTIP_CONTENT_ID] * (len(bonus.getBadges()) + len(bonus.getAchievements()))

    @classmethod
    def _getAchievementToolTipData(cls, bonus):
        return [ TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BATTLE_STATS_ACHIEVS, specialArgs=[achievement.getBlock(), achievement.getName(), achievement.getValue()]) for achievement in bonus.getAchievements() ]

    @classmethod
    def __getBadgeToolTipData(cls, bonus):
        return [ TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BADGE, specialArgs=[badge.badgeID]) for badge in bonus.getBadges() ]


class DossierLunarNYProgressionBonusPacker(DossierLunarNYBonusPacker):

    @classmethod
    def _getAchievementToolTipData(cls, bonus):
        return [ TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.LUNAR_NY_PROGRESSION_ACHIEVS, specialArgs=[achievement.getBlock(), achievement.getName(), achievement.getValue()]) for achievement in bonus.getAchievements() ]


class DossierLunarNYProgressionAwardPacker(DossierBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for badge in bonus.getBadges():
            result.append(cls._packBadge(bonus, badge))

        for achievement in bonus.getAchievements():
            result.append(cls._packAchievement(bonus, achievement))

        return result

    @classmethod
    def _packAchievement(cls, bonus, achievement):
        dossierIconName = achievement.getIconName()
        dossierLabel = cls._getAchievementLabel(achievement)
        model = cls._packSingleBonus(bonus, dossierIconName, DOSSIER_ACHIEVEMENT_POSTFIX, 1, dossierLabel)
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for badge in bonus.getBadges():
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BADGE, specialArgs=[badge.badgeID]))

        for achievement in bonus.getAchievements():
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.LUNAR_NY_PROGRESSION_ACHIEVS, specialArgs=[achievement.getBlock(), achievement.getName(), achievement.getValue()]))

        return tooltipData

    @classmethod
    def _getContentId(cls, bonus):
        tooltipData = []
        for _ in bonus.getBadges():
            tooltipData.append(BACKPORT_TOOLTIP_CONTENT_ID)

        for _ in bonus.getAchievements():
            tooltipData.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return tooltipData


class CharmLunarNYBonusPacker(SimpleLunarNYBonusPacker):
    _CHARM_TYPE_MAP = {CharmType.RARE: RewardType.CHARMRARE,
     CharmType.COMMON: RewardType.CHARMCOMMON}

    @classmethod
    def _pack(cls, bonus):
        return [ cls.__packSingleBonus(charmID, charmCount) for charmID, charmCount in bonus.getCharms() ]

    @classmethod
    def __packSingleBonus(cls, charmID, charmCount):
        charmType = CHARM_TYPE_BY_TYPE_NAME[lunar_ny.g_cache.charms[charmID].type]
        model = RewardViewModel()
        model.setCount(charmCount)
        model.setRewardID(str(charmID))
        model.setRewardType(cls._CHARM_TYPE_MAP.get(charmType, RewardType.CHARMCOMMON))
        model.setName(R.strings.lunar_ny.charmName.num(charmID, default=R.invalid)())
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        return [ TooltipData(tooltip=None, isSpecial=False, specialAlias=None, specialArgs=[charmID]) for charmID, _ in bonus.getCharms() ]

    @classmethod
    def _getContentId(cls, bonus):
        return [ R.views.lobby.lunar_ny.CharmTooltip() for _ in bonus.getCharms() ]


class EnvelopesLunarNYBonusPacker(SimpleLunarNYBonusPacker):

    @classmethod
    def _pack(cls, bonus):
        value = bonus.getValue()
        if value.id in ENVELOPE_ENTITLEMENT_CODE_TO_TYPE:
            model = RewardViewModel()
            model.setCount(value.amount)
            model.setRewardID(str(ENVELOPE_ENTITLEMENT_CODE_TO_TYPE[value.id].value))
            model.setRewardType(RewardType.ENVELOPE)
            return [model]
        return []

    @classmethod
    def _getToolTip(cls, bonus):
        value = bonus.getValue()
        return [TooltipData(tooltip=None, isSpecial=False, specialAlias=None, specialArgs=[ENVELOPE_ENTITLEMENT_CODE_TO_TYPE[value.id]])] if value.id in ENVELOPE_ENTITLEMENT_CODE_TO_TYPE else None

    @classmethod
    def _getContentId(cls, bonus):
        value = bonus.getValue()
        return [R.views.lobby.lunar_ny.tooltips.EnvelopeTooltip()] if value.id in ENVELOPE_ENTITLEMENT_CODE_TO_TYPE else []


def composeOpenLootBoxesBonuses(bonusesList):
    res = []
    for bonuses in bonusesList:
        for key, value in bonuses.iteritems():
            res.extend(getNonQuestBonuses(key, value))

    return res


_PROGRESSION_BONUSES_ORDER = ('entitlements', 'dossier')
_LUNAR_ACHIEVEMENT_NAME = 'lunarNY2022Progression'

def _progressionBonusesKeyOrder(bonus):
    return _PROGRESSION_BONUSES_ORDER.index(bonus.getName()) if bonus.getName() in _PROGRESSION_BONUSES_ORDER else len(_PROGRESSION_BONUSES_ORDER)


def composeProgressionBonuses(bonuses, level):
    res = []
    bonuses = deepcopy(bonuses)
    dossier = bonuses.get('dossier', None)
    if dossier is not None:
        for d in dossier.itervalues():
            lunarAchieves = d.get((ACHIEVEMENT_BLOCK.TOTAL, _LUNAR_ACHIEVEMENT_NAME), None)
            if lunarAchieves is not None:
                lunarAchieves['value'] = level

    for key, value in bonuses.iteritems():
        res.extend(getNonQuestBonuses(key, value))

    res = mergeBonuses(res)
    res.sort(key=_progressionBonusesKeyOrder)
    return res
