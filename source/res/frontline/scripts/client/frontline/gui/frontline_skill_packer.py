# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/frontline_skill_packer.py
import typing
from frontline.gui.impl.gen.view_models.views.lobby.views.skill_base_model import SkillBaseModel
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.game_control.epic_meta_game_ctrl import EpicMetaGameSkill

def packBaseSkills(skills, skillsData):
    for skillData in skillsData:
        skill = SkillBaseModel()
        packSkillBaseModel(skill, skillData)
        skills.addViewModel(skill)


def packSkillBaseModel(skill, skillData):
    skillInfo = skillData.getSkillInfo()
    skill.setId(skillData.skillID)
    skill.setIcon(skillInfo.icon)
    skill.setName(skillInfo.name)
