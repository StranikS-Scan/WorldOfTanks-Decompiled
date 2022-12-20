# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/frontline_skill_packer.py
import typing
from frontline.gui.impl.gen.view_models.views.lobby.views.skill_base_model import SkillBaseModel
from frontline.gui.impl.gen.view_models.views.lobby.views.skill_level_model import SkillLevelModel
from frontline.gui.impl.gen.view_models.views.lobby.views.skill_model import SkillModel
from frontline.gui.impl.gen.view_models.views.lobby.views.skill_param_model import SkillParamModel
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import createEpicParam
from gui.shared.tooltips.battle_ability_tooltip_params import g_battleAbilityTooltipMgr
from items import vehicles
from helpers import i18n
from gui.impl import backport
from gui.impl.gen import R
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.game_control.epic_meta_game_ctrl import EpicMetaGameSkill
TEMPLATE_DIR = R.strings.fl_skills_page.param.valueTemplate
TEMPLATE_DEFAULT = TEMPLATE_DIR.default()
TEMPLATE_SECONDS = TEMPLATE_DIR.seconds()
TEMPLATE_METERS = TEMPLATE_DIR.meters()
TEMPLATE_PERCENTS = TEMPLATE_DIR.percents()
TEMPLATE_PERCENTS_BY_SECOND = TEMPLATE_DIR.percentsBySecond()
SKILL_PARAM_TEMPLATES = {'FixedTextParam': TEMPLATE_DEFAULT,
 'DirectNumericTextParam': TEMPLATE_DEFAULT,
 'DirectSecondsTextParam': TEMPLATE_SECONDS,
 'DirectMetersTextParam': TEMPLATE_METERS,
 'MulDirectPercentageTextParam': TEMPLATE_PERCENTS,
 'AddDirectPercentageTextParam': TEMPLATE_PERCENTS_BY_SECOND,
 'MulReciprocalPercentageTextParam': TEMPLATE_PERCENTS,
 'AddReciprocalPercentageTextParam': TEMPLATE_PERCENTS,
 'ShellStunSecondsTextParam': TEMPLATE_SECONDS,
 'MultiMetersTextParam': TEMPLATE_METERS,
 'NestedMetersTextParam': TEMPLATE_METERS,
 'NestedSecondsTextParam': TEMPLATE_SECONDS,
 'MulNestedPercentageTextParam': TEMPLATE_PERCENTS,
 'AddNestedPercentageTextParam': TEMPLATE_PERCENTS,
 'NestedShellStunSecondsTextParam': TEMPLATE_SECONDS,
 'MulNestedPercentageTextTupleValueParam': TEMPLATE_PERCENTS}
HIDDEN_PARAMS = ['inactivationDelay', '#epic_battle:abilityInfo/params/fl_regenerationKit/minesDamageReduceFactor/value', 'projectilesNumber']
PLUS_SIGN = '+'
SKILL_PARAM_SIGN = {'increaseFactors/crewRolesFactor': PLUS_SIGN,
 'resupplyCooldownFactor': PLUS_SIGN,
 'resupplyHealthPointsFactor': PLUS_SIGN,
 'captureSpeedFactor': PLUS_SIGN,
 'captureBlockBonusTime': PLUS_SIGN}

def packBaseSkills(skills, skillsData):
    for skillData in skillsData:
        skill = SkillBaseModel()
        packSkillBaseModel(skill, skillData)
        skills.addViewModel(skill)


def packSkills(skills, skillsData, pointsAmount):
    for skillData in skillsData:
        skill = SkillModel()
        packSkillModel(skill, skillData, pointsAmount)
        skills.addViewModel(skill)


def packSkillModel(skill, skillData, pointsAmount):
    skillInfo = skillData.getSkillInfo()
    skill.setId(skillData.skillID)
    skill.setPrice(skillData.price)
    skill.setIcon(skillInfo.icon)
    skill.setName(skillInfo.name)
    skill.setShortDescription(skillInfo.shortDescr)
    skill.setLongDescription(skillInfo.longDescr)
    skill.setIsActivated(skillData.isActivated)
    skill.setIsDisabled(skillData.price > pointsAmount and not skillData.isActivated)
    levels = skill.getLevels()
    packSkillLevels(levels, skillData)


def packSkillBaseModel(skill, skillData):
    skillInfo = skillData.getSkillInfo()
    skill.setId(skillData.skillID)
    skill.setIcon(skillInfo.icon)
    skill.setName(skillInfo.name)


def packSkillLevels(levels, skillData):
    equipments = vehicles.g_cache.equipments()
    for _, skillLevelData in skillData.levels.iteritems():
        curLvlEq = equipments[skillLevelData.eqID]
        level = SkillLevelModel()
        levels.addViewModel(level)
        level.setId(skillLevelData.eqID)
        params = level.getParams()
        paramId = 0
        for tooltipIdentifier in curLvlEq.tooltipIdentifiers:
            if tooltipIdentifier in HIDDEN_PARAMS:
                continue
            param = createEpicParam(curLvlEq, tooltipIdentifier)
            if param:
                tooltipName, tooltipRenderer = g_battleAbilityTooltipMgr.getTooltipInfo(tooltipIdentifier)
                paramId += 1
                skillParam = SkillParamModel()
                skillParam.setId(tooltipIdentifier)
                skillParam.setName(i18n.makeString(tooltipName) if i18n.isValidKey(tooltipName) else '')
                skillParam.setValue(str(param))
                skillParam.setSign(SKILL_PARAM_SIGN.get(tooltipIdentifier, ''))
                skillParam.setValueTemplate(str(backport.text(TEMPLATE_DEFAULT if isinstance(param, str) else SKILL_PARAM_TEMPLATES.get(tooltipRenderer, TEMPLATE_DEFAULT))))
                params.addViewModel(skillParam)
