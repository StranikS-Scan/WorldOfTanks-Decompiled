# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCPersonalCase.py
from gui.Scaleform.daapi.view.lobby.PersonalCase import PersonalCaseDataProvider, PersonalCase
from gui.Scaleform.genConsts.PERSONALCASECONST import PERSONALCASECONST
from gui.shared.utils.functions import makeTooltip
from gui.Scaleform.locale.MENU import MENU
from uilogging.deprecated.decorators import loggerTarget, loggerEntry, simpleLog
from uilogging.deprecated.bootcamp.constants import BC_LOG_ACTIONS, BC_LOG_KEYS
from uilogging.deprecated.bootcamp.loggers import BootcampUILogger
PERSONAL_CASE_SKILLS = 'PersonalCaseSkills'

class BCPersonalCaseDataProvider(PersonalCaseDataProvider):

    def getTabsButtons(self, showDocumentTab, showFreeSkillsTab):
        return [{'id': PERSONALCASECONST.SKILLS_TAB_ID,
          'label': MENU.TANKMANPERSONALCASE_TABSKILLS,
          'tooltip': makeTooltip(body=MENU.TANKMANPERSONALCASE_TABSKILLS),
          'linkage': PERSONAL_CASE_SKILLS}]


@loggerTarget(logKey=BC_LOG_KEYS.BC_PERSONAL_CASE, loggerCls=BootcampUILogger)
class BCPersonalCase(PersonalCase):

    def __init__(self, ctx=None):
        super(BCPersonalCase, self).__init__(ctx)
        self.tabIndex = 0
        self.isBootcamp = True
        self.dataProvider = BCPersonalCaseDataProvider(self.tmanInvID)

    @loggerEntry
    def _populate(self):
        super(BCPersonalCase, self)._populate()

    @simpleLog(action=BC_LOG_ACTIONS.CLOSE, logOnce=True, restrictions={'lesson_id': 3})
    def _dispose(self):
        super(BCPersonalCase, self)._dispose()
