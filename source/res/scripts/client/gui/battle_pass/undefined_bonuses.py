# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/undefined_bonuses.py
import typing
from collections import namedtuple
from shared_utils import findFirst, first
from nations import INDICES
from gui.impl.lobby.battle_pass.tooltips.battle_pass_undefined_style_view import BattlePassUndefinedStyleTooltip
from gui.impl.lobby.battle_pass.tooltips.battle_pass_undefined_tankman_view import BattlePassUndefinedTankmanTooltip
from gui.Scaleform.daapi.view.lobby.customization.shared import getSuitableText
from gui.Scaleform.genConsts.SKILLS_CONSTANTS import SKILLS_CONSTANTS as SKILLS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events.recruit_helper import getRecruitInfo
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import CustomizationsBonus, TmanTemplateTokensBonus
UndefinedStyleTooltipData = namedtuple('UndefinedStyleTooltipData', ['styleA',
 'imageA',
 'tankA',
 'styleB',
 'imageB',
 'tankB'])
UndefinedTmanTooltipData = namedtuple('UndefinedTmanTooltipData', ['imageA',
 'tankmanA',
 'skillsA',
 'imageB',
 'tankmanB',
 'skillsB'])
_CUSTOMIZATION_BONUS_NAME = 'customizations'
_TANKMAN_BONUS_NAME = 'tmanToken'

def makeUndefinedBonus(bonusA, bonusB):
    nameA, nameB = bonusA.getName(), bonusB.getName()
    if nameA == _CUSTOMIZATION_BONUS_NAME and nameB == _CUSTOMIZATION_BONUS_NAME:
        return UndefinedStyleBonus(bonusA, bonusB)
    return UndefinedTmanBonus(bonusA, bonusB) if nameA == _TANKMAN_BONUS_NAME and nameB == _TANKMAN_BONUS_NAME else UndefinedBonus(bonusA, bonusB)


def isUndefinedBonusTooltipData(tooltipData):
    return isinstance(tooltipData, (UndefinedTmanTooltipData, UndefinedStyleTooltipData))


def createUndefinedBonusTooltipWindow(tooltipData, parentWindow):
    if isinstance(tooltipData, UndefinedStyleTooltipData):
        return BattlePassUndefinedStyleTooltip(tooltipData, parentWindow)
    else:
        return BattlePassUndefinedTankmanTooltip(tooltipData, parentWindow) if isinstance(tooltipData, UndefinedTmanTooltipData) else None


def getStyleInfo(bonus):
    if bonus is None:
        return
    elif bonus.getName() != _CUSTOMIZATION_BONUS_NAME:
        return
    else:
        item = findFirst(lambda c: c.get('custType') == 'style', bonus.getCustomizations())
        return None if item is None else bonus.getC11nItem(item)


def getTankmanInfo(bonus):
    if bonus is None:
        return
    elif bonus.getName() != _TANKMAN_BONUS_NAME:
        return
    else:
        tmanToken = first(bonus.getValue().keys())
        return None if tmanToken is None else getRecruitInfo(tmanToken)


def getRecruitNation(recruitInfo):
    nation = first(recruitInfo.getNations())
    return INDICES.get(nation, 0)


class UndefinedBonus(object):

    def __init__(self, optionA, optionB):
        self._optionA = optionA
        self._optionB = optionB

    def getName(self):
        pass

    def getIcon(self):
        pass

    def getIconBySize(self, size):
        iconName = RES_ICONS.getBonusIcon(size, self.getName())
        if iconName is None:
            iconName = RES_ICONS.getBonusIcon(size, 'default')
        return iconName

    def isValidOptions(self):
        return False

    def isShowInGUI(self):
        return self.isValidOptions()

    def getNameForIcon(self):
        pass

    def getTooltip(self):
        return None


class UndefinedStyleBonus(UndefinedBonus):

    def isValidOptions(self):
        return self._optionA.getName() == _CUSTOMIZATION_BONUS_NAME and self._optionB.getName() == _CUSTOMIZATION_BONUS_NAME

    def getIcon(self):
        pass

    def getTooltip(self):
        styleA = getStyleInfo(self._optionA)
        styleB = getStyleInfo(self._optionB)
        return None if styleA is None or styleB is None else UndefinedStyleTooltipData(styleA.userName, styleA.texture, getSuitableText(styleA, formatVehicle=False), styleB.userName, styleB.texture, getSuitableText(styleB, formatVehicle=False))


class UndefinedTmanBonus(UndefinedBonus):

    def isValidOptions(self):
        return self._optionA.getName() == _TANKMAN_BONUS_NAME and self._optionB.getName() == _TANKMAN_BONUS_NAME

    def getIcon(self):
        pass

    def getTooltip(self):
        tankmanA = getTankmanInfo(self._optionA)
        tankmanB = getTankmanInfo(self._optionB)
        if tankmanA is None or tankmanB is None:
            return {}
        else:
            iconNameA, tankmanNameA, skillsA = self.__getDataByTankman(tankmanA)
            iconNameB, tankmanNameB, skillsB = self.__getDataByTankman(tankmanB)
            return UndefinedTmanTooltipData(iconNameA, tankmanNameA, skillsA, iconNameB, tankmanNameB, skillsB)

    @staticmethod
    def __getDataByTankman(tankman):
        nation = getRecruitNation(tankman)
        iconName = tankman.getIconByNation(nation)
        tankmanName = tankman.getFullUserNameByNation(nation)
        skills = tankman.getLearntSkills()
        newSkillCount, _ = tankman.getNewSkillCount(onlyFull=True)
        if newSkillCount > 0:
            skills += [SKILLS.TYPE_NEW_SKILL] * (newSkillCount - skills.count(SKILLS.TYPE_NEW_SKILL))
        return (iconName, tankmanName, skills)
