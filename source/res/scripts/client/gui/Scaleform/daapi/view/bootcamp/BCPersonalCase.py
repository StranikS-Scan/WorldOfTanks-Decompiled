# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCPersonalCase.py
from gui.Scaleform.daapi.view.lobby.PersonalCase import PersonalCaseDataProvider, PersonalCase
from adisp import async
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from debug_utils import LOG_DEBUG
from bootcamp.BootcampGarage import g_bootcampGarage
from gui.Scaleform.locale.MENU import MENU
from bootcamp.Bootcamp import g_bootcamp
SKILLS_TAB_INDEX = 2
PERSONAL_CASE_SKILLS = 'PersonalCaseSkills'

class BCPersonalCaseDataProvider(PersonalCaseDataProvider):

    @async
    def getSkillsData(self, callback):
        itemsCache = dependency.instance(IItemsCache)
        tankman = itemsCache.items.getTankman(self.tmanInvID)
        data = tankman.getSkillsToLearn()
        skillSixthSense = None
        skillComouflage = None
        for skills in data:
            for skill in skills['skills']:
                if skill['id'] == 'commander_sixthSense':
                    skillSixthSense = skill
                if skill['id'] == 'camouflage':
                    skillComouflage = skill
                skill['enabled'] = False

        skillsGroupsRemove = list()
        for skills in data:
            if skills['id'] == 'common':
                if skillComouflage is not None:
                    skills['skills'].remove(skillComouflage)
                    skills['skills'].insert(0, skillComouflage)
                if skillSixthSense is not None:
                    skillComouflage['enabled'] = False
                    skills['skills'].insert(0, skillSixthSense)
                scrollCountSkills = g_bootcamp.getContextIntParameter('scrollCountSkills')
                if len(skills['skills']) > scrollCountSkills:
                    del skills['skills'][scrollCountSkills:]
            skillsGroupsRemove.append(skills)

        for skills in skillsGroupsRemove:
            data.remove(skills)

        callback(data)
        return

    def getTabsButtons(self, _, __):
        return [{'index': SKILLS_TAB_INDEX,
          'label': MENU.TANKMANPERSONALCASE_TABSKILLS,
          'linkage': PERSONAL_CASE_SKILLS}]


class BCPersonalCase(PersonalCase):

    def __init__(self, ctx=None):
        LOG_DEBUG('BCPersonalCase.__init__')
        super(BCPersonalCase, self).__init__(ctx)
        self.tabIndex = 0
        self.dataProvider = BCPersonalCaseDataProvider(self.tmanInvID)
        self.__skillSelected = False
        self.__skillAdded = False
        itemsCache = dependency.instance(IItemsCache)
        self.__tman = itemsCache.items.getTankmanDossier(self.tmanInvID)

    def checkRole(self):
        return self.__tman.tmanDescr.role == 'commander'

    def onSkillClick(self, skillId):
        if self.checkRole() and not self.__skillSelected and skillId == 'commander_sixthSense':
            self.__skillSelected = True
            g_bootcampGarage.hidePrevShowNextHint()

    def addTankmanSkill(self, invengoryID, skillName):
        super(BCPersonalCase, self).addTankmanSkill(invengoryID, skillName)
        if self.checkRole() and skillName == 'commander_sixthSense':
            self.__skillAdded = True
            g_bootcampGarage.hideAllHints()
            g_bootcampGarage.runCustomAction('msgSkillsPerks')

    def _populate(self):
        LOG_DEBUG('BCPersonalCase._populate')
        super(BCPersonalCase, self)._populate()
        observer = self.app.bootcampManager.getObserver('BCPersonalCaseObserver')
        if observer:
            observer.onSkillClickEvent += self.onSkillClick
        if self.checkRole():
            g_bootcampGarage.runViewAlias('bootcampPresonalCase')

    def _dispose(self):
        super(BCPersonalCase, self)._dispose()
        g_bootcampGarage.runViewAlias('hangar')
        observer = self.app.bootcampManager.getObserver('BCPersonalCaseObserver')
        if observer:
            observer.onSkillClickEvent -= self.onSkillClick
