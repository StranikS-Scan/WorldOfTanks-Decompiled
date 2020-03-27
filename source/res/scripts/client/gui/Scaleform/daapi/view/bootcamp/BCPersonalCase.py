# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCPersonalCase.py
from gui.Scaleform.daapi.view.lobby.PersonalCase import PersonalCaseDataProvider, PersonalCase
from adisp import async
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.locale.MENU import MENU
from bootcamp.Bootcamp import g_bootcamp
from bootcamp.statistic.decorators import loggerTarget, loggerEntry, simpleLog
from bootcamp.statistic.logging_constants import BC_LOG_ACTIONS, BC_LOG_KEYS
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

    def getTabsButtons(self, _):
        return [{'index': SKILLS_TAB_INDEX,
          'label': MENU.TANKMANPERSONALCASE_TABSKILLS,
          'linkage': PERSONAL_CASE_SKILLS}]


@loggerTarget(logKey=BC_LOG_KEYS.BC_PERSONAL_CASE)
class BCPersonalCase(PersonalCase):

    def __init__(self, ctx=None):
        super(BCPersonalCase, self).__init__(ctx)
        self.tabIndex = 0
        self.isBootcamp = True
        self.dataProvider = BCPersonalCaseDataProvider(self.tmanInvID)

    @loggerEntry
    def _populate(self):
        super(BCPersonalCase, self)._populate()

    @simpleLog(action=BC_LOG_ACTIONS.CLOSE)
    def _dispose(self):
        super(BCPersonalCase, self)._dispose()
