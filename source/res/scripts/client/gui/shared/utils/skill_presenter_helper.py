# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/skill_presenter_helper.py
import typing
from debug_utils import LOG_WARNING
from gui.impl import backport
from gui.impl.gen import R
from items.components.component_constants import EMPTY_STRING
from items.tankmen import getSkillsConfig
if typing.TYPE_CHECKING:
    from items.readers.skills_readers import SkillDescrsArg
    from typing import List, Tuple

def getSkillIconName(skillName, customName=EMPTY_STRING):
    return customName if customName else skillName


def getSkillBigIconPath(skillName, customSkillName=EMPTY_STRING):
    iconName = getSkillIconName(skillName, customSkillName)
    root = R.images.gui.maps.icons.tankmen.skills.big.dyn(iconName)
    if root.isValid():
        return backport.image(root())
    LOG_WARNING('no {}.png image in gui.maps.icons.tankmen.skills.big'.format(iconName))
    return EMPTY_STRING


def getSkillDescrArgs(skillName):
    return getSkillsConfig().getSkill(skillName).uiSettings.descrArgs


def getSkillTypeName(skillName):
    return getSkillsConfig().getSkill(skillName).typeName


def getSkillUserName(skillName):
    return str(backport.text(R.strings.crew_perks.dyn(skillName).name()))


def getSkillUserDescription(skillName):
    return str(backport.text(R.strings.crew_perks.dyn(skillName).description()))


def getSkillMaxLvlDescription(skillName):
    return str(backport.text(R.strings.crew_perks.dyn(skillName).maxLvlDescription()))


def getSkillCurrentLvlDescription(skillName):
    return str(backport.text(R.strings.crew_perks.dyn(skillName).currentLvlDescription()))


def getSkillAltDescription(skillName):
    return str(backport.text(R.strings.crew_perks.dyn(skillName).alt.description()))


def getSkillAltInfo(skillName):
    return str(backport.text(R.strings.crew_perks.dyn(skillName).alt.info()))
