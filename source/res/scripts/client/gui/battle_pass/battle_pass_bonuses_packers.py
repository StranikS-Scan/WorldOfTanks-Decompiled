# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/battle_pass_bonuses_packers.py
import logging
import typing
from contextlib import contextmanager
from gui.impl.backport import TooltipData
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.impl.gen.view_models.common.missions.bonuses.extended_icon_bonus_model import ExtendedIconBonusModel
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.missions.packers.bonus import BonusUIPacker, getDefaultBonusPackersMap, BaseBonusUIPacker, DossierBonusUIPacker
from gui.server_events.recruit_helper import getRecruitInfo
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from shared_utils import first
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus, TmanTemplateTokensBonus, CustomizationsBonus, PlusPremiumDaysBonus, DossierBonus
    from gui.battle_pass.undefined_bonuses import UndefinedBonus
_logger = logging.getLogger(__name__)

def getBattlePassBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'undefined': UndefinedBonusPacker(),
     'tmanToken': TmanTemplateBonusPacker(),
     'customizations': BattlePassCustomizationsBonusPacker(),
     'premium_plus': BattlePassPremiumDaysPacker(),
     'dossier': BattlePassDossierBonusPacker()})
    return BonusUIPacker(mapping)


def packBonusModelAndTooltipData(bonuses, bonusModelsList, tooltipData=None, isLocked=False):
    bonusIndexTotal = 0
    if tooltipData is not None:
        bonusIndexTotal = len(tooltipData)
    packer = getBattlePassBonusPacker()
    for bonus in bonuses:
        if bonus.isShowInGUI():
            bonusList = packer.pack(bonus)
            bonusTooltipList = []
            if bonusList and tooltipData is not None:
                bonusTooltipList = packer.getToolTip(bonus)
            for bonusIndex, item in enumerate(bonusList):
                item.setIndex(bonusIndex)
                item.setIsLocked(isLocked)
                bonusModelsList.addViewModel(item)
                if tooltipData is not None and bonusTooltipList:
                    tooltipIdx = str(bonusIndexTotal)
                    item.setTooltipId(tooltipIdx)
                    tooltipData[tooltipIdx] = bonusTooltipList[bonusIndex]
                    bonusIndexTotal += 1

    return


def changeBonusTooltipData(bonusData, tooltipData):
    packer = getBattlePassBonusPacker()
    for bonus, tooltipId in bonusData:
        tooltip = first(packer.getToolTip(bonus))
        tooltipData[tooltipId] = tooltip


class UndefinedBonusPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus):
        model = IconBonusModel()
        model.setName(bonus.getNameForIcon())
        model.setIcon(bonus.getIcon())
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        return [bonus.getTooltip()]


class _BattlePassFinalBonusPacker(BaseBonusUIPacker):
    __finalAwardId = None

    @classmethod
    def setFinalAwardId(cls, awardId):
        cls.__finalAwardId = awardId

    @classmethod
    def _injectAwardID(cls, item):
        if cls.__finalAwardId is not None:
            item.setIcon('_'.join([item.getIcon(), str(cls.__finalAwardId)]))
        return


class TmanTemplateBonusPacker(_BattlePassFinalBonusPacker):

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
        recruitInfo = getRecruitInfo(tokenID)
        if recruitInfo is None:
            return
        else:
            if recruitInfo.isFemale():
                bonusImageName = 'tankwoman'
            else:
                bonusImageName = 'tankman'
            model = ExtendedIconBonusModel()
            cls._packCommon(bonus, model)
            model.setIcon(bonusImageName)
            model.setUserName(recruitInfo.getFullUserName())
            cls._injectAwardID(model)
            return model

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED, specialArgs=[tokenID]))

        return tooltipData


class BattlePassCustomizationsBonusPacker(_BattlePassFinalBonusPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for item, data in zip(bonus.getCustomizations(), bonus.getList()):
            if item is None:
                continue
            result.append(cls._packSingleBonus(bonus, item, data))

        return result

    @classmethod
    def _packSingleBonus(cls, bonus, item, data):
        model = ExtendedIconBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(data.get('value', '')))
        model.setIcon(str(bonus.getC11nItem(item).itemTypeName))
        model.setUserName(bonus.getC11nItem(item).userName)
        cls._injectAwardID(model)
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for item, _ in zip(bonus.getCustomizations(), bonus.getList()):
            if item is None:
                continue
            itemCustomization = bonus.getC11nItem(item)
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD, specialArgs=[itemCustomization.intCD, False]))

        return tooltipData


class BattlePassPremiumDaysPacker(BaseBonusUIPacker):
    _ICONS_AVAILABLE = (1, 2, 3, 7, 14, 30, 90, 180, 360)

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus):
        days = bonus.getValue()
        model = BonusModel()
        if days in cls._ICONS_AVAILABLE:
            model.setName(bonus.getName())
        else:
            model.setName('premium_universal')
        model.setIsCompensation(bonus.isCompensation())
        model.setValue(str(bonus.getValue()))
        return model


class BattlePassDossierBonusPacker(DossierBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for achievement in bonus.getAchievements():
            dossierIconName = achievement.getName()
            dossierValue = achievement.getValue()
            dossierNamePostfix = '_achievement'
            userName = achievement.getUserName()
            result.append(cls._packSingleBonus(bonus, dossierIconName, dossierNamePostfix, dossierValue, userName))

        for badge in bonus.getBadges():
            dossierIconName = 'badge_' + str(badge.badgeID)
            dossierValue = 0
            dossierNamePostfix = '_badge'
            userName = badge.getUserName()
            result.append(cls._packSingleBonus(bonus, dossierIconName, dossierNamePostfix, dossierValue, userName))

        return result

    @classmethod
    def _packSingleBonus(cls, bonus, dossierIconName, dossierNamePostfix, dossierValue, userName=''):
        model = ExtendedIconBonusModel()
        model.setName(bonus.getName() + dossierNamePostfix)
        model.setIsCompensation(bonus.isCompensation())
        model.setValue(str(dossierValue))
        model.setIcon(dossierIconName)
        model.setUserName(userName)
        return model


@contextmanager
def finalAwardsInjection(finalAwardID):
    _BattlePassFinalBonusPacker.setFinalAwardId(finalAwardID)
    yield
    _BattlePassFinalBonusPacker.setFinalAwardId(None)
    return
