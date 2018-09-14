# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/DismissTankmanDialog.py
from adisp import process
from gui import makeHtmlString
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.shared.gui_items.serializers import packTankman
from helpers import i18n
from items import tankmen
from gui.Scaleform.daapi.view.meta.DismissTankmanDialogMeta import DismissTankmanDialogMeta
from gui.shared.utils.requesters.ItemsRequester import ItemsRequester

class DismissTankmanDialog(DismissTankmanDialogMeta):

    def __init__(self, meta, handler):
        super(DismissTankmanDialog, self).__init__(meta.getMessage(), meta.getTitle(), meta.getButtonLabels(), meta.getCallbackWrapper(handler))
        self.__meta = meta
        self.__tankman = self.__meta.getTankman()
        self.__controlNumber = None
        self.__inputChecker = None
        self.question = None
        return

    def _populate(self):
        super(DismissTankmanDialog, self)._populate()
        self.__prepareTankmanData()

    @process
    def __prepareTankmanData(self):
        items = yield ItemsRequester().request()
        dropSkillsCost = []
        for k in sorted(items.shop.dropSkillsCost.keys()):
            dropSkillsCost.append(items.shop.dropSkillsCost[k])

        skills_count = list(tankmen.ACTIVE_SKILLS)
        availableSkillsCount = len(skills_count) - len(self.__tankman.skills)
        hasNewSkills = self.__tankman.roleLevel == tankmen.MAX_SKILL_LEVEL and availableSkillsCount and (self.__tankman.descriptor.lastSkillLevel == tankmen.MAX_SKILL_LEVEL or not len(self.__tankman.skills))
        self.as_tankManS({'money': (items.stats.credits, items.stats.gold),
         'tankman': packTankman(self.__tankman),
         'dropSkillsCost': dropSkillsCost,
         'hasNewSkills': hasNewSkills,
         'newSkills': self.__tankman.newSkillCount,
         'defaultSavingMode': 0})
        if len(self.__tankman.skills) < 1:
            if self.__tankman.roleLevel < 100:
                self.question = i18n.makeString(DIALOGS.DISMISSTANKMAN_MESSAGE)
            else:
                self.__controlNumber = str(self.__tankman.roleLevel)
                self.question = makeHtmlString('html_templates:lobby/dialogs', 'dismissTankmanMain', {'roleLevel': str(self.__tankman.roleLevel)})
        else:
            if self.__tankman.skills[-1].isPerk:
                skillType = DIALOGS.PROTECTEDDISMISSTANKMAN_ADDITIONALMESSAGE_ISPERK
            else:
                skillType = DIALOGS.PROTECTEDDISMISSTANKMAN_ADDITIONALMESSAGE_ISABILLITY
            self.question = makeHtmlString('html_templates:lobby/dialogs', 'dismissTankmanAdditional', {'skillType': i18n.makeString(skillType),
             'skillName': self.__tankman.skills[-1].userName,
             'roleLevel': str(self.__tankman.skills[-1].level)})
            self.__controlNumber = str(self.__tankman.skills[-1].level)
        self.__updateInputChecker()

    def __updateInputChecker(self):
        if self.__inputChecker is not None:
            self.__inputChecker.setControlNumbers(str(self.__controlNumber))
            self.__inputChecker.questionBody = self.question
            self.__inputChecker.errorMsg = DIALOGS.PROTECTEDDISMISSTANKMAN_ERRORMESSAGE
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        self.__inputChecker = viewPy
        self.__updateInputChecker()

    def _dispose(self):
        super(DismissTankmanDialog, self)._dispose()
        self.__controlNumber = None
        self.__tankman = None
        self.__meta = None
        self.__inputChecker = None
        return
