# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/container_vews/skills_training/context.py
from constants import NEW_PERK_SYSTEM as NPS
from gui.impl.lobby.crew.container_vews.common.base_personal_case_context import BasePersonalCaseContext
from gui.impl.lobby.crew.crew_helpers.skill_helpers import getTmanNewSkillCount
from items.tankmen import MAX_SKILL_LEVEL

class SkillsTrainingViewContext(BasePersonalCaseContext):
    __slots__ = ('_role', '_hoveredSkill', '_selectedSkills', '_availableSkillsData', '_activeSkillsForTTC')

    def __init__(self, tankmanID, role):
        self._role = role
        self._hoveredSkill = None
        self._selectedSkills = []
        self._availableSkillsData = []
        self._activeSkillsForTTC = []
        super(SkillsTrainingViewContext, self).__init__(tankmanID)
        return

    @property
    def role(self):
        return self._role

    @property
    def isMajorQualification(self):
        return self._role == self.tankman.role

    @property
    def totalSkillsAmount(self):
        return NPS.MAX_MAJOR_PERKS if self.isMajorQualification else NPS.MAX_BONUS_SKILLS_PER_ROLE

    @property
    def areAllSkillsLearned(self):
        learnedSkillsAmount = self.tankman.skillsCount if self.isMajorQualification else self.tankman.bonusSkillsCountByRole[self._role]
        return learnedSkillsAmount == self.totalSkillsAmount

    @property
    def isAnySkillSelected(self):
        return self.selectedSkillsCount > 0

    @property
    def selectedSkills(self):
        return self._selectedSkills

    @property
    def selectedSkillsCount(self):
        return len(self._selectedSkills)

    @property
    def hoveredSkill(self):
        return self._hoveredSkill

    @property
    def activeSkillsForTTC(self):
        return self._activeSkillsForTTC

    @property
    def availableSkillsData(self):
        return self._availableSkillsData

    @property
    def skillsAmount(self):
        skillsCnt = self.selectedSkillsCount
        newSkillCnt, _ = getTmanNewSkillCount(self.tankman)
        newSkillCnt += self.tankman.newFreeSkillsCount
        if self.isMajorQualification:
            newSkillCnt = min(newSkillCnt, self.totalSkillsAmount)
            currSkillsAmount = self.tankman.skillsCount + skillsCnt
            availableSkillsAmount = newSkillCnt - skillsCnt
        else:
            currSkillsAmount = self.tankman.bonusSkillsCountByRole[self._role] + skillsCnt
            availableSkillsAmount = self.tankman.newBonusSkillsCountByRole[self._role] - skillsCnt
        return (currSkillsAmount, availableSkillsAmount)

    def update(self, tankmanID, updateRole=False):
        super(SkillsTrainingViewContext, self).update(tankmanID)
        if updateRole:
            self._role = self.tankman.role
        self._availableSkillsData = []
        if self.isMajorQualification:
            newSkillsCount, lastSkillLevel = getTmanNewSkillCount(self.tankman, withFree=True)
            for i in range(newSkillsCount):
                self._availableSkillsData.append((MAX_SKILL_LEVEL if i < newSkillsCount - 1 else lastSkillLevel.realSkillLvl, i < self.tankman.newFreeSkillsCount))

        else:
            learnedSkillsCount = self.tankman.bonusSkillsCountByRole[self._role]
            newSkillsCount = self.tankman.newBonusSkillsCountByRole[self._role]
            for i in range(newSkillsCount):
                self._availableSkillsData.append((self.tankman.bonusSkillsLevels[learnedSkillsCount + i], False))

    def clearSelection(self):
        self._selectedSkills = []
        self._updateActiveSkillsForTTC()

    def updateSelectedSkills(self, skillId):
        if skillId in self.selectedSkills:
            self.selectedSkills.remove(skillId)
        elif self.selectedSkillsCount < self.totalSkillsAmount:
            self.selectedSkills.append(skillId)
        self._updateActiveSkillsForTTC()

    def updateHoveredSkill(self, skillId):
        self._hoveredSkill = skillId
        self._updateActiveSkillsForTTC()

    def _updateActiveSkillsForTTC(self):
        self._activeSkillsForTTC = self._selectedSkills[:]
        if self._hoveredSkill is not None and self._hoveredSkill not in self._activeSkillsForTTC:
            self._activeSkillsForTTC.append(self._hoveredSkill)
        return
